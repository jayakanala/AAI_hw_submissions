# Research Assistant using LangGraph

## Objective

Build a research assistant using **LangGraph** that demonstrates:

* Stateful agent execution
* Persistent memory
* Human-in-the-loop approval before important actions

## Features

* **Stateful Agent**

  * Maintains the flow of conversation using LangGraph state management.
  * Keeps track of previous interactions during execution.

* **Persistent Memory**

  * Stores conversation history.
  * Uses previous messages to generate context-aware responses.

* **Human-in-the-Loop**

  * Pauses execution before performing an important action.
  * Waits for user approval before continuing.

## Workflow

```text
User Query
    │
    ▼
Load Previous Memory
    │
    ▼
Process Request
    │
    ▼
Need User Approval?
    │
 ┌──┴──┐
 │     │
No    Yes
 │     │
 ▼     ▼
Reply  Pause & Ask User
           │
           ▼
     User Approval
           │
           ▼
     Continue Execution
```

## Technologies Used

* Python
* LangGraph

## Project Structure

```text
.
├── app.py
├── graph.py
├── memory.py
├── requirements.txt
└── README.md
```

## How to Run

1. Clone the repository.

```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required packages.

```bash
pip install -r requirements.txt
```

3. Run the application.

```bash
python app.py
```

## Learning Outcomes

Through this assignment, the following LangGraph concepts were implemented:

* Building stateful agent workflows
* Managing persistent conversation memory
* Implementing human-in-the-loop approval in agent execution
