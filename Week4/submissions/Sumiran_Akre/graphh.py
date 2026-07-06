from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages, BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated, List, Literal
import os, json
from dotenv import load_dotenv
from tools import tool
import sqlite3

conn = sqlite3.connect("agent_db.sqlite", check_same_thread=False)

load_dotenv()

class ResearchState(TypedDict):
    messages : Annotated[List[BaseMessage], add_messages]
    menu : str
    user : str

tools_node = ToolNode(tool)

model = ChatGroq(model_name = "openai/gpt-oss-120b", api_key=os.getenv("groq"))
model_with_tools = model.bind_tools(tool)

#==============================================
##NODE FUNCTIONS
#==============================================
def get_user(state: ResearchState):
    if state.get("user"):
        return {}
    user = input("Enter your name: ")
    return {"user": user}

def display_menu(state: ResearchState):
    if state.get("menu"):
        return {}

    try:
        with open("menu.json", "r") as f:
            menu = json.load(f)
    except Exception as e:
        print(f"Error loading menu: {e}")
        return

    menu_by_type = {}
    for item in menu:
        t = item.get("type", "Other")
        if t not in menu_by_type:
            menu_by_type[t] = []
        menu_by_type[t].append(item)

    width = 75
    print("=" * width)
    print("O U R   M E N U".center(width))
    print("=" * width)
    
    category_order = ['Soup', 'Salad', 'Starter', 'Main Course', 'Bread', 'Dessert', 'Beverage']
    all_categories = list(menu_by_type.keys())
    categories = [c for c in category_order if c in all_categories]
    for c in all_categories:
        if c not in categories:
            categories.append(c)

    for category in categories:
        items = menu_by_type[category]
        print(f"\n--- {category.upper()} ---".center(width))
        print("-" * width)
        for item in items:
            name = item.get("name", "Unknown")
            price = item.get("price", 0.0)
            qty = item.get("quantity", "")
            cat = item.get("category", "")
            prep = item.get("prep_time", "")
            
            details = []
            if cat:
                details.append(cat)
            if qty:
                details.append(qty)
            if prep:
                details.append(f"Prep: {prep}")
            
            details_str = ", ".join(details)
            left_side = f"* {name} ({details_str})"
            right_side = f"Rs. {price:.2f}"
            
            space_left = width - len(left_side) - len(right_side) - 2
            if space_left > 0:
                print(f" {left_side}{' ' * space_left}{right_side} ")
            else:
                print(f" {left_side} - {right_side} ")
    print("\n" + "=" * width)
    return {"menu" : json.dumps(menu)}

def chat_node(state: ResearchState):
    messages = state["messages"]
    system_instructions = (
        "You are a helpful restaurant booking assistant. "
        "Before calling any tool, check the menu to make sure the item exists. "
        "If the user misspelled a dish name (e.g., 'paneer buter' instead of 'Paneer Butter Masala'), "
        "correct it automatically to the correct menu name before calling the tool."
    )
    system_msg = [SystemMessage(content=system_instructions)]
    
    if state.get("user"):
        system_msg.append(SystemMessage(content=f"System context: The user's name is {state['user']}. Please address them by name when appropriate."))
        
    response = model_with_tools.invoke(system_msg + messages)
    return {"messages": [response]}

#============================================
##GRAPH
#============================================
graph = StateGraph(ResearchState)

graph.add_node("get_user", get_user)
graph.add_node("menu", display_menu)
graph.add_node("llm", chat_node)
graph.add_node("tools", tools_node)

graph.add_edge(START, "get_user")
graph.add_edge("get_user", "menu")
graph.add_edge("menu", "llm")
graph.add_conditional_edges("llm", tools_condition)
graph.add_edge("tools", "llm")

graph = graph.compile(checkpointer=SqliteSaver(conn))


        
            

        

