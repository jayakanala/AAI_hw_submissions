"""
Week 2 — Sample Implementation
Domain: Research Agent

Demonstrates:
- Typed tool inputs with Pydantic
- Real API calls (no hardcoded data)
- Tool class pattern with auto-generated Claude definitions
- Graceful error handling in tools

Run:
    pip install anthropic pydantic requests
    export ANTHROPIC_API_KEY=your_key_here
    python research_agent.py
"""

import requests
import anthropic
from pydantic import BaseModel, field_validator
from typing import Callable, Any


# ─────────────────────────────────────────────
# TOOL INPUT SCHEMAS (Pydantic)
#
# Why Pydantic?
# Claude sends tool inputs as raw dicts.
# Pydantic validates types at runtime and
# raises a clear error if something's wrong.
# ─────────────────────────────────────────────

class WeatherInput(BaseModel):
    city: str

    @field_validator("city")
    @classmethod
    def city_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("city cannot be empty")
        return v.strip()


class SearchInput(BaseModel):
    query: str
    max_results: int = 3

    @field_validator("max_results")
    @classmethod
    def clamp_results(cls, v: int) -> int:
        return max(1, min(v, 10))   # keep between 1 and 10


class CurrencyInput(BaseModel):
    from_currency: str   # e.g. "USD"
    to_currency: str     # e.g. "INR"
    amount: float = 1.0

    @field_validator("from_currency", "to_currency")
    @classmethod
    def uppercase(cls, v: str) -> str:
        return v.upper().strip()


# ─────────────────────────────────────────────
# REAL API FUNCTIONS
#
# Each function:
# - Makes a real HTTP call
# - Has a timeout (never skip this)
# - Returns a string (what Claude reads back)
# - Never crashes — catches exceptions and
#   returns an error string instead
# ─────────────────────────────────────────────

def get_weather(city: str) -> str:
    """Fetch real weather from wttr.in (free, no API key)."""
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3",
            timeout=5,
        )
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Could not fetch weather for {city}: {e}"


def search_web(query: str, max_results: int = 3) -> str:
    """Search using DuckDuckGo Instant Answer API (free, no API key)."""
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("RelatedTopics", [])[:max_results]
        texts = [r["Text"] for r in results if "Text" in r]

        if not texts:
            abstract = data.get("AbstractText", "")
            return abstract if abstract else "No results found."

        return "\n".join(f"• {t}" for t in texts)
    except requests.RequestException as e:
        return f"Search failed: {e}"


def convert_currency(from_currency: str, to_currency: str, amount: float = 1.0) -> str:
    """Convert currency using exchangerate-api (free tier, no key needed)."""
    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{from_currency}",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return f"Currency API error: {data.get('error-type', 'unknown')}"

        rate = data["rates"].get(to_currency)
        if rate is None:
            return f"Currency '{to_currency}' not found."

        converted = round(amount * rate, 2)
        return f"{amount} {from_currency} = {converted} {to_currency} (rate: {rate})"
    except requests.RequestException as e:
        return f"Currency conversion failed: {e}"


# ─────────────────────────────────────────────
# TOOL CLASS
#
# Wraps a function + its Pydantic schema.
# run() validates inputs before calling the function.
# to_claude_definition() generates the JSON schema
# Claude needs — automatically from the Pydantic model.
# ─────────────────────────────────────────────

class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        func: Callable[..., str],
    ) -> None:
        self.name = name
        self.description = description
        self.input_model = input_model
        self.func = func

    def run(self, raw_input: dict[str, Any]) -> str:
        """Validate inputs with Pydantic, then call the function."""
        try:
            validated = self.input_model(**raw_input)
            return self.func(**validated.model_dump())
        except Exception as e:
            return f"Tool '{self.name}' failed: {e}"

    def to_claude_definition(self) -> dict[str, Any]:
        """Auto-generate Claude tool definition from Pydantic model."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_model.model_json_schema(),
        }


# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────

TOOLS: list[Tool] = [
    Tool(
        name="get_weather",
        description=(
            "Get the current weather for a city. "
            "Always use this tool when the user asks about weather — do not guess."
        ),
        input_model=WeatherInput,
        func=get_weather,
    ),
    Tool(
        name="search_web",
        description=(
            "Search the web for recent information on a topic. "
            "Use this for current events, news, or anything that requires up-to-date information."
        ),
        input_model=SearchInput,
        func=search_web,
    ),
    Tool(
        name="convert_currency",
        description=(
            "Convert an amount from one currency to another using live exchange rates. "
            "Use this for any currency conversion question."
        ),
        input_model=CurrencyInput,
        func=convert_currency,
    ),
]

TOOL_MAP: dict[str, Tool] = {t.name: t for t in TOOLS}


# ─────────────────────────────────────────────
# AGENT
# ─────────────────────────────────────────────

class ResearchAgent:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic()
        self.tool_definitions = [t.to_claude_definition() for t in TOOLS]

    def run(self, user_message: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_message}
        ]

        print(f"\nUser: {user_message}")

        while True:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=(
                    "You are a helpful research assistant. "
                    "Use tools to find real information. "
                    "Never guess — if you need data, call the relevant tool."
                ),
                tools=self.tool_definitions,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if block.type == "text":
                        return block.text

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  → {block.name}({block.input})")
                    result = TOOL_MAP[block.name].run(block.input)
                    print(f"  ← {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agent = ResearchAgent()

    queries = [
        "What's the weather like in Mumbai and Delhi right now?",
        "Convert 5000 INR to USD and EUR.",
        "Search for recent news about open source LLMs and summarise what you find.",
    ]

    for query in queries:
        answer = agent.run(query)
        print(f"\nAgent: {answer}")
        print("─" * 60)
