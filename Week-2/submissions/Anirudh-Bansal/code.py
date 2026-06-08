import os
import requests
from urllib.parse import quote
from typing import Callable, Any

from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
)

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)
from datetime import datetime
import pytz
MAX_STEPS = 10

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY environment variable is not set."
    )

class CurrencyInput(BaseModel):
    from_currency: str
    to_currency: str
    amount: float = 1.0

    @field_validator(
        "from_currency",
        "to_currency",
    )
    @classmethod
    def normalize_currency(cls, v: str):
        return v.strip().upper()
    
class GetTime(BaseModel):
    city: str

    @field_validator("city")
    @classmethod
    def validate_city(cls, v:str):
        v = v.strip()
        if not v:
            raise ValueError("City cannot be empty")
        
        return v


def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
) -> str:

    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{from_currency}",
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":
            return "Currency API returned an error."

        rate = data["rates"].get(to_currency)

        if rate is None:
            return f"Unsupported currency: {to_currency}"

        converted = round(amount * rate, 2)

        return (
            f"{amount} {from_currency} = "
            f"{converted} {to_currency}"
        )

    except requests.RequestException as e:
        return f"Currency conversion failed: {str(e)}"
    

def get_time_city(city: str) -> str:
    try:
        # Step 1: Get lat/lon + timezone from geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city.strip()}&count=1&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        results = geo_data.get("results")
        if not results:
            return f"Could not find geographic data for city: {city}"

        timezone = results[0].get("timezone")
        if not timezone:
            return f"Could not determine timezone for city: {city}"

        # Step 2: Use pytz to get current time (no external API needed!)
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            return f"The current live date and time in {city} is: {current_time}"
        except pytz.UnknownTimeZoneError:
            return f"Unknown timezone: {timezone}"

    except Exception as e:
        return f"Time lookup failed: {str(e)}"


class Tool:

    def __init__(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        func: Callable[..., str],
    ):
        self.name = name
        self.description = description
        self.input_model = input_model
        self.func = func

    def run(
        self,
        raw_input: dict[str, Any]
    ) -> str:

        try:
            validated = self.input_model(
                **raw_input
            )

            return self.func(
                **validated.model_dump()
            )

        except ValidationError as e:
            return (
                "Validation Error:\n"
                f"{str(e)}"
            )

        except Exception as e:
            return (
                f"Tool Execution Error: {e}"
            )

    def to_groq_tool(self):

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters":
                    self.input_model.model_json_schema(),
            },
        }

TOOLS = [    Tool(
        "convert_currency", (
            "Convert currency using live exchange rates. "
            "For multiple target currencies, call "
            "the tool once per currency."
        ),CurrencyInput, convert_currency,
    ),
    Tool("get_time","A tool that returns current time of an input city", GetTime, get_time_city)]


TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}

# --------------------------------------------------
# MODEL
# --------------------------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

llm_with_tools = llm.bind_tools(
    [tool.to_groq_tool() for tool in TOOLS]
)

# --------------------------------------------------
# AGENT
# --------------------------------------------------

class ResearchAgent:

    def run(
        self,
        user_message: str
    ) -> str:

        messages = [
            HumanMessage(
                content=user_message
            )
        ]

        for step in range(MAX_STEPS):

            response = llm_with_tools.invoke(
                messages
            )

            messages.append(response)

            if not response.tool_calls:
                return str(response.content)

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(
                    f"\n[Tool] "
                    f"{tool_name}"
                )
                print(
                    f"[Args] "
                    f"{tool_args}"
                )

                tool = TOOL_MAP.get(tool_name)

                if not tool:
                    result = (
                        f"Unknown tool: "
                        f"{tool_name}"
                    )
                else:
                    result = tool.run(
                        tool_args
                    )

                print(
                    f"[Result] "
                    f"{result}"
                )

                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"],
                    )
                )

        return (
            "Stopped after reaching "
            f"{MAX_STEPS} tool iterations."
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    agent = ResearchAgent()

    while True:

        query = input(
            "\nYou: "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
        }:
            break

        answer = agent.run(query)

        print(
            f"\nAgent: "
            f"{answer}"
        )
