# RAG-based Document Question Answering Agent

## Overview
This project implements a **Retrieval-Augmented Generation (RAG)** application that allows users to upload a **PDF** document and ask natural language questions about its contents. Instead of relying only on the language model's internal knowledge, the application retrieves relevant document chunks and uses them as context to generate accurate, grounded answers.

The agent is also equipped with a calculator tool, a live stock price tool, and a web search tool, and it decides on its own (via LangGraph) when to call each one.

---

## Features
* Upload PDF documents per chat thread
* Automatic text extraction (PyPDF)
* Document chunking (recursive character splitter)
* Vector embedding generation (HuggingFace sentence-transformers)
* Semantic search using FAISS similarity search
* Context-aware question answering using RAG
* Multi-turn conversation memory via a SQLite checkpointer (LangGraph)
* Multiple chat threads, browsable from the sidebar
* Bonus tools: calculator, stock price lookup, web search
* Clean, modular code structure

---

## Tech Stack
* Python
* Streamlit (UI)
* LangGraph (agent / state machine + persistence)
* LangChain (document loading, splitting, tools)
* FAISS (vector store)
* HuggingFace Sentence Transformers (embeddings)
* Groq (`llama-3.3-70b-versatile` LLM)
* PyPDF (PDF parsing)

---

## Project Workflow
```text
Upload PDF
    │
    ▼
Extract Text (loader.py)
    │
    ▼
Split into Chunks (loader.py)
    │
    ▼
Generate Embeddings (embeddings.py)
    │
    ▼
Store in Vector Database (FAISS, per thread)
    │
    ▼
User asks a Question
    │
    ▼
Retrieve Relevant Chunks (rag_tool in rag.py)
    │
    ▼
LLM Generates Context-Aware Answer (chat_node in rag.py)
```

---

## Project Structure
```text
project/
│
├── app/
│   ├── main.py          # Streamlit UI / entry point
│   ├── rag.py            # Tools, LangGraph state machine, SQLite checkpointer
│   ├── loader.py          # PDF loading, chunking, per-thread FAISS retrievers
│   └── embeddings.py       # Groq LLM + HuggingFace embeddings setup
│
├── data/                  # SQLite checkpoint DB (chatbot.db) lives here
│
├── uploads/               # Reserved for persisted uploads (PDFs are currently
│                           # processed from a temp file and not kept on disk)
│
├── requirements.txt
├── .env.example
└── README.md
```
> Note: the original template also listed a `utils.py`; here that role is
> filled by `app/utils.py`, which holds small shared helpers like
> `generate_thread_id()`.

---

## Installation
Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate it:

Windows:
```bash
venv\Scripts\activate
```

Linux / macOS:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up your environment variables:
```bash
copy .env.example .env      # Windows
# or
cp .env.example .env        # Linux / macOS
```
Then edit `.env` and add your `GROQ_API_KEY` (and optionally `ALPHAVANTAGE_API_KEY`).

---

## Running the Project
This is a Streamlit app. From the project root, run:
```bash
streamlit run app/main.py
```

---

## How to Use
1. Start the application.
2. Upload a PDF from the sidebar — it's indexed for the current chat thread.
3. Wait for the "✅ PDF indexed" status to appear.
4. Ask a question in the chat box.
5. The agent retrieves relevant context from the PDF (via `rag_tool`) and generates an answer. It can also use the calculator, stock price, or web search tools when appropriate.
6. Use "New Chat" to start a fresh thread, or click a past thread in the sidebar to resume it.

---

## Example Questions
* Summarize the uploaded document.
* What are the key points discussed?
* Who are the main stakeholders?
* Explain the methodology described.
* What is 15% of 240? *(calculator tool)*
* What's the current price of AAPL? *(stock price tool)*

---

## RAG Pipeline
1. Document Upload
2. Text Extraction
3. Chunking
4. Embedding Generation
5. Vector Storage (per thread, in-memory FAISS)
6. Semantic Retrieval
7. Context Injection
8. Answer Generation

---

## Bonus: MCP Tool
The `rag_tool` in `app/rag.py` is already isolated as a standalone LangChain
`@tool`. It can be re-exposed through the Model Context Protocol (MCP) by
wrapping it with an MCP server (e.g. `fastmcp` or the official `mcp` SDK) so
external AI assistants can query the same indexed documents.

---

## Future Improvements
* Support multiple uploaded documents per thread
* Persist uploaded PDFs to `uploads/` instead of a temp file
* Source citation with page numbers in the UI
* Hybrid search (keyword + semantic)
* OCR support for scanned PDFs
* User authentication
* Cloud deployment

---

## Conclusion
This project demonstrates how Retrieval-Augmented Generation (RAG) can be
used to build a document-aware AI assistant capable of answering questions
accurately by retrieving relevant information from an uploaded PDF before
generating a response — with LangGraph handling tool orchestration and
conversation persistence.
