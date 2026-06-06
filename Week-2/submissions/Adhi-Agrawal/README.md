# BookStore AI Agent
## Overview
BookStore AI Agent is a tool-calling AI assistant that helps users search for books and retrieve book information using real-world APIs. The project uses Ollama for tool calling, Pydantic for input validation, and external APIs to fetch live book data.

## Features
- Search books by title
- Get details of a specific book
- Retrieve book information using Google Books API
- Typed tool inputs using Pydantic
- Tool class pattern for reusable tools
- Graceful API error handling
- No hardcoded book data

## APIs Used
1. OpenLibrary API
2. Google Books API

## Technologies
- Python
- Ollama
- Pydantic
- Requests

## Sample Run 1
### Input
```text
Suggest some python books
```

### Output
```text
User: Suggest some python books
 → search_books
 ← [
  "Automate the Boring Stuff with Python",
  "Python for Beginners : 2 Books in 1",
  "Think Python"
]

Agent: Here are some book recommendations on Python programming: "Automate the Boring Stuff with Python", "Python for Beginners : 2 Books in 1", and "Think Python".
```

---

## Sample Run 2
### Input
```text
Tell me about Atomic Habits
```

### Output
```text
User: Tell me about Atomic Habits
 → get_book_details
 ← {
  "title": "Atomic Habits",
  "author": "James Clear"
}

Agent: "Atomic Habits" by James Clear is a self-help book that teaches readers how to create good habits and break bad ones. It focuses on the power of small, incremental changes in behavior, which can lead to significant improvements over time.
```

---

## Sample Run 3
### Input
```text
Give Google books detail for clean code.
```

### Output
```text
User: Give Google books detail for clean code.
 → get_google_book_info
 ← {
  "title": "Clean Code",
  "author": "Robert C. Martin"
}

Agent: The book "Clean Code" is written by Robert C. Martin.
```

---

## How to Run
### Install Dependencies

```bash
pip install -r requirements.txt
```
### Run the Agent

```bash
python bookstore_agent.py
```

---
