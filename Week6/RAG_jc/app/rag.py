"""
RAG agent definition: tools, LangGraph state machine, and SQLite checkpointer.

Covers the "Semantic Retrieval -> Context Injection -> Answer Generation"
stages of the pipeline, plus a few utility tools (calculator, stock price,
web search) the assistant can call alongside the RAG tool.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Annotated, Optional, TypedDict

import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from embeddings import llm
from loader import get_retriever, get_thread_metadata

# -------------------
# Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch the latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage.
    """
    api_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not api_key:
        return {"error": "ALPHAVANTAGE_API_KEY is not set in the environment."}

    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    )
    response = requests.get(url, timeout=10)
    return response.json()


@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant chunks from the PDF uploaded for this chat thread.
    Always pass the current thread_id when calling this tool.
    """
    retriever = get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    results = retriever.invoke(query)
    context = [doc.page_content for doc in results]
    metadata = [doc.metadata for doc in results]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": get_thread_metadata(thread_id).get("filename"),
    }


tools = [get_stock_price, calculator, rag_tool]
llm_with_tools = llm.bind_tools(tools)


# -------------------
# State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# -------------------
# Nodes
# -------------------
def chat_node(state: ChatState, config=None):
    """LLM node that may answer directly or request a tool call."""
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
        content=(
            "You are a helpful assistant. For questions about the uploaded PDF, call "
            "the `rag_tool` and include the thread_id "
            f"`{thread_id}`. You can also use the web search, stock price, and "
            "calculator tools when helpful. If no document is available, ask the user "
            "to upload a PDF."
        )
    )

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}


tool_node = ToolNode(tools)

# -------------------
# Checkpointer
# -------------------
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(_DATA_DIR, exist_ok=True)
_DB_PATH = os.path.join(_DATA_DIR, "chatbot.db")

conn = sqlite3.connect(database=_DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)


# -------------------
# Helpers
# -------------------
def retrieve_all_threads():
    """Return every thread_id known to the checkpointer."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def thread_document_metadata(thread_id: str) -> dict:
    return get_thread_metadata(thread_id)
