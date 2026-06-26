# Multi-Agent Research Crew

## Objective

Build a **3-agent crew** where each agent performs a specific task and collaborates with the others to produce a final output.

The workflow consists of:

**Researcher → Writer → Reviewer**

## Topic

**Artificial Intelligence in Healthcare**

## Agents

### 1. Researcher

* Collects information about the given topic.
* Identifies important facts and key points.
* Passes the research findings to the Writer.

### 2. Writer

* Organizes the research into a clear and structured article.
* Ensures the content is coherent and easy to understand.
* Sends the draft to the Reviewer.

### 3. Reviewer

* Reviews the written content.
* Checks for clarity, grammar, and completeness.
* Suggests improvements and produces the final version.

## Workflow

```text
User Topic
     │
     ▼
Researcher
     │
     ▼
Writer
     │
     ▼
Reviewer
     │
     ▼
Final Output
```

## Technologies Used

* Python
* CrewAI
* Large Language Model (LLM)

## Project Structure

```text
.
├── agents.py
├── tasks.py
├── crew.py
├── main.py
├── requirements.txt
└── README.md
```

## File Description

### `agents.py`

Defines the three agents:

* Researcher
* Writer
* Reviewer

Each agent is assigned a specific role, goal, and responsibility.

### `tasks.py`

Defines the tasks assigned to each agent and specifies the order in which they are executed.

### `crew.py`

Creates the crew by combining the agents and their tasks into a collaborative workflow.

### `main.py`

The entry point of the application. It accepts the topic from the user, runs the crew, and displays the final output.

### `requirements.txt`

Lists all required Python libraries.

### `README.md`

Contains the project documentation and setup instructions.

## How to Run

1. Clone the repository.

```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the dependencies.

```bash
pip install -r requirements.txt
```

3. Run the project.

```bash
python main.py
```

## Learning Outcomes

Through this assignment, the following concepts were implemented:

* Multi-agent collaboration
* Role-based task delegation
* Sequential task execution
* AI-generated research, writing, and review workflow
    