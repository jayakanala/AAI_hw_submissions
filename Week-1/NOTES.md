# Week 1 — What is an AI Agent?

**Dates:** May 20 – Jun 1

---

## Core Concepts

### 1. AI Agent vs Chatbot

A regular chatbot takes input → produces output. Done.

An **AI Agent** takes input → reasons → decides what to do → acts → observes the result → reasons again → repeats until the goal is achieved.

The key difference: **agents take actions in the world**. A chatbot answers. An agent does things.

---

### 2. The ReAct Loop

ReAct = **Re**asoning + **Act**ing. It's the core loop inside almost every agent.

```
User Input
    ↓
[THOUGHT]  → model reasons: "I need to find the price. Let me call get_price()"
    ↓
[ACTION]   → model calls a tool: get_price("iPhone 15")
    ↓
[OBSERVATION] → tool returns: "₹79,900"
    ↓
[THOUGHT]  → model reasons: "Now I have the price. I can answer."
    ↓
Final Answer
```

Each loop: Think → Act → Observe → Repeat.

This continues until the model decides it has enough information to answer.

---

### 3. Tools

Tools are functions the agent can call. Without tools, an agent is just a chatbot.

Examples:
- `search_web(query)` — search Google
- `get_weather(city)` — fetch weather
- `send_email(to, subject, body)` — send an email
- `run_code(code)` — execute Python

You define the tool, tell the model what it does, and the model decides *when* to call it.

---

### 4. Memory

| Type | What it is | Example |
|------|-----------|---------|
| **Short-term** | The current conversation | Chat history in one session |
| **Long-term** | Persisted across sessions | A file, database, or vector store |
| **In-context** | Everything in the current prompt | Documents you paste in |

Week 1: don't worry too much about memory yet. Just know it exists.

---

### 5. Planning

Some agents plan before acting. Instead of immediately calling tools, they:
1. Break the goal into steps
2. Execute each step
3. Adjust if something fails

Example: "Research AI trends and write a report" → an agent might plan:
- Step 1: Search for recent AI papers
- Step 2: Summarise each one
- Step 3: Write the report

---

## Resources

### Course
- [HuggingFace AI Agents Course – Unit 1](https://huggingface.co/learn/agents-course) ← **start here**

### Reading (pick one)
- [What are AI Agents? – LangChain blog](https://blog.langchain.dev/what-is-an-agent/) (~15 min)

### Videos (pick one)
- [AI Jason – What are AI Agents?](https://youtube.com/@AIJasonZ) ← great no-code intro
- [Sam Witteveen – AI Agents in 2025 Overview](https://youtube.com/@SamWitteveen)

### Notebooks (run in Google Colab — no setup needed)
- [GenAI_Agents by Nir Diamant](https://github.com/NirDiamant/GenAI_Agents) ← pick any notebook and run it

---

## Week 1 Deliverable

**Task:** Build a simple domain-specific AI agent with 3 tools.

Reference implementation is in [`sample/sales_agent.py`](sample/sales_agent.py).

Your job:
1. Read through the sample code and understand every line
2. Pick a different domain (e.g. travel agent, fitness agent, food agent)
3. Create 3 tools relevant to your domain
4. Build your agent and test it with 3 different queries
5. Submit in `submissions/your-name/`

**No need for a real API** — mock tools (fake data) are completely fine for Week 1.

---

## Key Takeaways

- Agents = LLM + tools + a loop
- The ReAct loop is: Think → Act → Observe → Repeat
- Tools give agents the ability to *do* things, not just *say* things
- Memory and planning are extensions you'll build in later weeks
