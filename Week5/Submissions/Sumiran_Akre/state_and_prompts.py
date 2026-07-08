from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# State Schemas
class Review(TypedDict):
    wordicts : str
    score : float
    suggestions : List[str]

class MainState(TypedDict):
    """ This is the state of the graph."""
    messages: Annotated[List[BaseMessage], add_messages]
    research_notes: List[str]
    draft: List[str]
    review: Review
    retry_count: int


# ==========================================
# 1. Lead Coordinator Prompts
# ==========================================
QUERY_CLASSIFICATION_PROMPT = """You are the Lead Coordinator for the Multi-Agent Research Crew. 
Your job is to analyze the user's research topic and define a clear, structured research plan.

Please output:
1. The target research topic.
2. The key objectives of the research (what aspects we need to investigate).
3. A list of suggested search terms for the research agent to run.

Keep your response professional and focused."""


# ==========================================
# 2. Research Agent Prompts
# ==========================================
RESEARCH_PROMPT = """You are a research agent. Your task is to gather detailed research findings on the given topic using your available web search and web scraper tools.
Please search for recent developments, statistics, key applications, and challenges. Once you obtain the search results, synthesize them into structured research notes."""

RESEARCH_SYNTHESIS_PROMPT = """We have completed the search queries. Please synthesize all retrieved search findings above into comprehensive, structured research notes. Do not request any more tools."""


# ==========================================
# 3. Writing Agent Prompts & Templates
# ==========================================
WRITING_FORMATTING_GUIDELINES = """
Formatting Guidelines for the Article:
- Use standard Markdown headers: '#' for the main title, '##' for main sections, and '###' for subsections. Do NOT use plain bold text (e.g. '**Introduction**') for section headers.
- Structure key findings, challenges, and future outlook with clear bullet points or numbered lists.
- If applicable, summarize comparisons, metrics, or key facts in a neat Markdown table.
- Include a brief overview/summary abstract at the very beginning.
"""

WRITING_INITIAL_PROMPT_TEMPLATE = """You are a WRITING AGENT. Your task is to write a comprehensive, clear, and well-organized article on the topic: "{topic}" based on the research notes.

## Research Notes:
{research_notes}

{formatting_guidelines}

Ensure the article includes:
- A compelling title (using '#')
- An abstract/summary (at the very beginning)
- An introduction (using '##')
- Key findings and applications (using '##' and '###')
- Challenges and future outlook (using '##' and '###')
- A brief conclusion (using '##')"""

WRITING_REWRITE_PROMPT_TEMPLATE = """You are a WRITING AGENT. Your task is to REWRITE and improve the article draft on the topic "{topic}" based on the reviewer's feedback.

## Research Notes:
{research_notes}

## Previous Draft:
{previous_draft}

## Reviewer Feedback to Address:
{feedback}

{formatting_guidelines}

Rewrite the article addressing all suggestions and following the formatting guidelines. Provide the complete updated article draft."""


# ==========================================
# 4. Reviewer Agent Prompts
# ==========================================
REVIEW_PROMPT = """You are a REVIEWER AGENT. Your task is to review the article draft for grammar, clarity, readability, and completeness.
You must return the final polished article along with a review score and suggestions.
"""

REVIEW_FALLBACK_PROMPT = """You are a REVIEWER AGENT. Review the article draft for grammar, clarity, readability, and completeness.
You must output your response in JSON format matching this schema:
{
  "wordicts": "Your detailed review or final polished text",
  "score": 8.5,  // A float score between 0.0 and 10.0 representing your evaluation of the draft
  "suggestions": ["suggestion 1", "suggestion 2"]  // Specific improvement suggestions
}
Only output valid JSON. Do not include markdown formatting or backticks around the JSON."""
