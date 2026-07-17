"""
Embedding model and LLM initialization.

Centralizes the Groq chat model and the HuggingFace sentence-transformer
embeddings so every other module (loader, rag) shares one instance.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Create a .env file (see .env.example) "
        "and add your Groq API key before running the app."
    )

# Chat model used for both plain answers and tool-calling
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

# Embedding model used to vectorize PDF chunks for retrieval
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
