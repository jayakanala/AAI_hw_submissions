"""
Document loading, chunking, and per-thread vector-store management.

Handles the "Extract Text -> Split into Chunks -> Generate Embeddings ->
Store in Vector Database" stages of the RAG pipeline described in the README.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embeddings import embeddings

# One retriever + metadata entry per chat thread, keyed by thread_id (str)
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if one has been built."""
    if thread_id and thread_id in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_id]
    return None


def get_thread_metadata(thread_id: Optional[str]) -> dict:
    """Return summary info (filename, page/chunk counts) for a thread."""
    return _THREAD_METADATA.get(str(thread_id), {})


def thread_has_document(thread_id: str) -> bool:
    return str(thread_id) in _THREAD_RETRIEVERS


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Extract text from a PDF, chunk it, embed the chunks, and build a FAISS
    retriever scoped to the given chat thread.

    Returns a summary dict (filename, page count, chunk count) for the UI.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        _THREAD_RETRIEVERS[str(thread_id)] = retriever
        summary = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
        _THREAD_METADATA[str(thread_id)] = summary
        return summary
    finally:
        # FAISS keeps the chunked text in memory, so the temp file is safe to remove.
        try:
            os.remove(temp_path)
        except OSError:
            pass
