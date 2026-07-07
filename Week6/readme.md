# RAG-based Document Question Answering Agent

## Overview

This project implements a **Retrieval-Augmented Generation (RAG)** application that allows users to upload a **PDF** or **text document** and ask natural language questions about its contents. Instead of relying only on the language model's internal knowledge, the application retrieves relevant document chunks and uses them as context to generate accurate, grounded answers.

**Bonus:** The project is designed to support exposing functionality through the **Model Context Protocol (MCP)** as a tool for external AI assistants.

---

## Features

* Upload PDF documents
* Upload plain text (`.txt`) documents
* Automatic text extraction
* Document chunking
* Vector embedding generation
* Semantic search using vector similarity
* Context-aware question answering using RAG
* Clean and modular code structure
* Optional MCP tool integration

---

## Tech Stack

* Python
* LangChain
* FAISS / ChromaDB (Vector Store)
* Sentence Transformers / OpenAI Embeddings
* FastAPI (if applicable)
* PyPDF / PyPDF2
* MCP (Bonus)

---

## Project Workflow

```text
Upload Document
        │
        ▼
Extract Text
        │
        ▼
Split into Chunks
        │
        ▼
Generate Embeddings
        │
        ▼
Store in Vector Database
        │
        ▼
User asks a Question
        │
        ▼
Retrieve Relevant Chunks
        │
        ▼
LLM Generates Context-Aware Answer
```

---

## Project Structure

```text
project/
│
├── app/
│   ├── main.py
│   ├── rag.py
│   ├── loader.py
│   ├── embeddings.py
│   └── utils.py
│
├── data/
│
├── uploads/
│
├── requirements.txt
│
└── README.md
```

> The exact folder structure may vary depending on the implementation.

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

---

## Running the Project

If using FastAPI:

```bash
uvicorn app.main:app --reload
```

If using Streamlit:

```bash
streamlit run app.py
```

---

## How to Use

1. Start the application.
2. Upload a PDF or text document.
3. Wait for the document to be indexed.
4. Enter a question related to the uploaded document.
5. The application retrieves relevant context and generates an answer.

---

## Example Questions

* Summarize the uploaded document.
* What are the key points discussed?
* Who are the main stakeholders?
* Explain the methodology described.
* What conclusions does the document present?

---

## RAG Pipeline

1. Document Upload
2. Text Extraction
3. Chunking
4. Embedding Generation
5. Vector Storage
6. Semantic Retrieval
7. Context Injection
8. Answer Generation

---

## Bonus: MCP Tool

The project can expose its question-answering functionality as an MCP tool, enabling compatible AI assistants to query uploaded documents through the Model Context Protocol.

---

## Future Improvements

* Support multiple uploaded documents
* Conversation memory
* Source citation with page numbers
* Hybrid search (keyword + semantic)
* OCR support for scanned PDFs
* Streaming responses
* User authentication
* Cloud deployment

---

## Conclusion

This project demonstrates how Retrieval-Augmented Generation (RAG) can be used to build a document-aware AI assistant capable of answering questions accurately by retrieving relevant information from uploaded files before generating responses.
