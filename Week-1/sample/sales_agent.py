"""
Week 1 — Sample Implementation
Domain: Sales Agent

A sales agent that helps customers find products, check prices,
and see what's currently in stock.

Run:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
    python sales_agent.py
"""

import anthropic

# ─────────────────────────────────────────────
# TOOLS — functions the agent can call
# ─────────────────────────────────────────────

def search_products(query: str) -> str:
    """Search the product catalog by keyword."""
    catalog = {
        "laptop": ["Dell XPS 13", "MacBook Air M2", "Lenovo ThinkPad X1"],
        "phone": ["iPhone 15", "Samsung Galaxy S24", "OnePlus 12"],
        "headphones": ["Sony WH-1000XM5", "AirPods Pro", "Bose QC45"],
        "tablet": ["iPad Pro", "Samsung Galaxy Tab S9", "Xiaomi Pad 6"],
    }
    query_lower = query.lower()
    for keyword, products in catalog.items():
        if keyword in query_lower:
            return f"Found {len(products)} products: {', '.join(products)}"
    return "No products found. Try: laptop, phone, headphones, tablet."


def get_product_price(product_name: str) -> str:
    """Get the price and any active discount for a product."""
    prices = {
        "Dell XPS 13": {"price": 89999, "discount": 10},
        "MacBook Air M2": {"price": 114900, "discount": 0},
        "Lenovo ThinkPad X1": {"price": 129999, "discount": 15},
        "iPhone 15": {"price": 79900, "discount": 5},
        "Samsung Galaxy S24": {"price": 74999, "discount": 8},
        "OnePlus 12": {"price": 64999, "discount": 12},
        "Sony WH-1000XM5": {"price": 29990, "discount": 20},
        "AirPods Pro": {"price": 24900, "discount": 0},
        "Bose QC45": {"price": 26900, "discount": 10},
    }
    product = prices.get(product_name)
    if not product:
        return f"Product '{product_name}' not found in price list."
    original = product["price"]
    discount = product["discount"]
    final = int(original * (1 - discount / 100))
    if discount > 0:
        return f"₹{original:,} → ₹{final:,} after {discount}% discount"
    return f"₹{original:,} (no active discount)"


def check_stock(product_name: str) -> str:
    """Check how many units of a product are available."""
    stock = {
        "Dell XPS 13": 12,
        "MacBook Air M2": 3,
        "Lenovo ThinkPad X1": 0,
        "iPhone 15": 25,
        "Samsung Galaxy S24": 8,
        "OnePlus 12": 15,
        "Sony WH-1000XM5": 0,
        "AirPods Pro": 30,
        "Bose QC45": 6,
    }
    units = stock.get(product_name)
    if units is None:
        return f"Product '{product_name}' not found in inventory."
    if units == 0:
        return f"{product_name} is OUT OF STOCK."
    if units <= 5:
        return f"Only {units} units left — low stock!"
    return f"{units} units available."


# ─────────────────────────────────────────────
# TOOL REGISTRY
# Maps tool name → (function, Claude tool definition)
# ─────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_product_price": get_product_price,
    "check_stock": check_stock,
}

TOOL_DEFINITIONS = [
    {
        "name": "search_products",
        "description": "Search the product catalog using a keyword like 'laptop' or 'phone'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_product_price",
        "description": "Get the price and active discount for a specific product by its exact name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Exact product name"}
            },
            "required": ["product_name"],
        },
    },
    {
        "name": "check_stock",
        "description": "Check the inventory/stock level for a specific product.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Exact product name"}
            },
            "required": ["product_name"],
        },
    },
]


# ─────────────────────────────────────────────
# AGENT — ReAct loop
# ─────────────────────────────────────────────

class SalesAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.system = (
            "You are a helpful sales assistant. "
            "Help customers find products, check prices, and verify stock availability. "
            "Always check stock before recommending a product. "
            "Be concise and friendly."
        )

    def run(self, user_message: str) -> str:
        messages = [{"role": "user", "content": user_message}]

        print(f"\nUser: {user_message}")

        while True:
            # THOUGHT — model reasons and decides what to do next
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=self.system,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            # No more tool calls — return the final answer
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if block.type == "text":
                        return block.text

            # ACTION + OBSERVATION — execute each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  → Calling: {block.name}({block.input})")
                    result = TOOL_FUNCTIONS[block.name](**block.input)
                    print(f"  ← Result:  {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed observations back so the model can reason again
            messages.append({"role": "user", "content": tool_results})


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agent = SalesAgent()

    queries = [
        "I'm looking for a good laptop. What do you have and what's the best deal?",
        "Is the Sony WH-1000XM5 available? How much does it cost?",
        "Which phones are in stock and under ₹70,000?",
    ]

    for query in queries:
        answer = agent.run(query)
        print(f"\nAgent: {answer}")
        print("-" * 60)
