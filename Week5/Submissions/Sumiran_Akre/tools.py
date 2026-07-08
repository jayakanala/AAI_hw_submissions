from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from typing import Annotated, List
import os

@tool
def web_search(query: str) -> str:
    """Search the web for the given query to retrieve relevant articles, key facts, and recent updates."""
    t_a_key = os.getenv("TAVILY_API_KEY")
    if not t_a_key:
        return f"Warning: TAVILY_API_KEY is not configured. (Simulated Search Result for '{query}'): Artificial Intelligence (AI) in healthcare is transforming diagnostics, treatment planning, patient care, and administrative workflows. Key topics include predictive analytics, robotic surgery, natural language processing for electronic health records, and AI-driven drug discovery."
    try:
        search = TavilySearch(tavily_api_key=t_a_key)
        results = search.invoke(query)
        
        formatted_results = []
        if isinstance(results, dict) and "results" in results:
            items = results["results"]
        elif isinstance(results, list):
            items = results
        else:
            items = []
            
        for r in items:
            if isinstance(r, dict):
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                url = r.get("url", "")
                formatted_results.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n")
                
        res_str = "\n".join(formatted_results)
        if not res_str:
            res_str = str(results)
            
        if len(res_str) > 2500:
            res_str = res_str[:2500] + "... (truncated)"
        return res_str
    except Exception as e:
        return f"Error executing search: {str(e)}"

@tool
def web_scraper(url: str) -> str:
    """Scrape the content of a specific web URL to retrieve its full text content."""
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        content = "\n".join([doc.page_content for doc in docs])
        if len(content) > 4000:
            content = content[:4000] + "... (truncated)"
        return content
    except Exception as e:
        return f"Error scraping website: {str(e)}"

research_tools = [web_search, web_scraper]

@tool
def save_draft(content: str, filename: str = "draft.txt") -> str:
    """Save the written draft to a file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Draft successfully saved to {filename}"
    except Exception as e:
        return f"Error saving draft: {str(e)}"

review_tools = [save_draft]
