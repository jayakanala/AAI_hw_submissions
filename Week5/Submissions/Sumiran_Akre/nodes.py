from config import *
from state_and_prompts import *
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from tools import web_search, web_scraper, save_draft

def chat_node(state: MainState):
    """ This node generates the LLM response."""
    messages = [
        SystemMessage(content=QUERY_CLASSIFICATION_PROMPT), 
        HumanMessage(content=state['messages'][-1].content)
    ]
    response = chat_model.invoke(messages)
        
    return {'messages' : [response]}

def research_node(state: MainState):
    """ This node performs research using Tavily and scraping tools."""
    messages = [
        SystemMessage(content=RESEARCH_PROMPT), 
        HumanMessage(content=state['messages'][-1].content)
    ]

    current_messages = list(messages)
    max_iterations = 4
    iteration = 0
    
    response = research_model_with_tools.invoke(current_messages)
    
    while response.tool_calls and iteration < max_iterations:
        current_messages.append(response)
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f" ---> [ TOOL ] == {tool_name}")
            print(f" ---> [ ARGS ] == {tool_args}")
            
            if tool_name == "web_search":
                result = web_search.invoke(tool_args)
            elif tool_name == "web_scraper":
                result = web_scraper.invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"
                
            current_messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_name
            ))
        
        iteration += 1
        response = research_model_with_tools.invoke(current_messages)
        
    if response.tool_calls or not response.content.strip():
        current_messages.append(response)
        if response.tool_calls:
            for tc in response.tool_calls:
                current_messages.append(ToolMessage(
                    content="System notice: Maximum search depth reached. Please proceed with summarizing current findings.",
                    tool_call_id=tc["id"],
                    name=tc["name"]
                ))
        current_messages.append(HumanMessage(content=RESEARCH_SYNTHESIS_PROMPT))
        response = research_model.invoke(current_messages)
        
    return {'messages' : [response], 'research_notes' : [response.content]}

def writing_node(state: MainState):
    """ This node performs writing or rewriting of the article using Groq."""
    review = state.get('review')
    drafts = state.get('draft', [])
    research_notes = "\n".join(state.get('research_notes', []))
    topic = state['messages'][0].content
    
    if review and review.get('score', 0) < 7.5 and state.get('retry_count', 0) < 3:
        feedback = f"Previous Review Score: {review.get('score')}\nSuggestions: {', '.join(review.get('suggestions', []))}\nVerdict: {review.get('wordicts')}"
        previous_draft = drafts[-1] if drafts else ""
        
        prompt_content = WRITING_REWRITE_PROMPT_TEMPLATE.format(
            topic=topic,
            research_notes=research_notes,
            previous_draft=previous_draft,
            feedback=feedback,
            formatting_guidelines=WRITING_FORMATTING_GUIDELINES
        )
    else:
        prompt_content = WRITING_INITIAL_PROMPT_TEMPLATE.format(
            topic=topic,
            research_notes=research_notes,
            formatting_guidelines=WRITING_FORMATTING_GUIDELINES
        )
        
    messages = [
        SystemMessage(content=prompt_content),
        HumanMessage(content="Please write/rewrite the article.")
    ]
    
    response = writing_model.invoke(messages)
    return {'messages' : [response], 'draft' : [response.content]}

def review_node(state: MainState):
    """ This node performs review using Groq."""
    draft = "\n".join(state.get('draft', []))
    query = state['messages'][0].content
    
    messages = [
        SystemMessage(content=REVIEW_PROMPT), 
        HumanMessage(content=f"Original Query: {query}\n\nDraft Article:\n{draft}")
    ]
    
    retry_count = state.get('retry_count', 0)
    
    try:
        structured_reviewer = review_model.with_structured_output(Review)
        review_output = structured_reviewer.invoke(messages)
        score = review_output.get('score', 0)
        
        next_retry = retry_count + 1 if score < 7.5 else retry_count
        
        response_msg = AIMessage(content=f"Review Score: {score}/10\nVerdict:\n{review_output.get('wordicts', '')}")
        return {'messages' : [response_msg], 'review' : review_output, 'retry_count': next_retry}
    except Exception as e:
        print(f" ---> Structured output failed, falling back to JSON parsing: {e}")
        fallback_messages = [
            SystemMessage(content=REVIEW_FALLBACK_PROMPT),
            HumanMessage(content=f"Original Query: {query}\n\nDraft Article:\n{draft}")
        ]
        
        try:
            response = review_model.invoke(fallback_messages)
            import json
            clean_content = response.content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:]
            if clean_content.startswith("```"):
                clean_content = clean_content[3:]
            if clean_content.endswith("```"):
                clean_content = clean_content[:-3]
            clean_content = clean_content.strip()
            
            review_output = json.loads(clean_content)
        except Exception as json_err:
            print(f" ---> JSON fallback parsing failed: {json_err}")
            review_output = {
                "wordicts": response.content if 'response' in locals() else "Failed to parse review.",
                "score": 8.0,
                "suggestions": ["Improve formatting and structure of the document."]
            }
        
        score = review_output.get('score', 0)
        next_retry = retry_count + 1 if score < 7.5 else retry_count
        
        response_msg = AIMessage(content=f"Review Score: {score}/10\nVerdict:\n{review_output.get('wordicts', '')}")
        return {'messages' : [response_msg], 'review' : review_output, 'retry_count': next_retry}

def review_router(state: MainState):
    """ Routes the workflow back to writing_node if score is less than 7.5 and max retries not reached. """
    review = state.get('review', {})
    score = review.get('score', 0)
    retry_count = state.get('retry_count', 0)
    
    if score < 7.5 and retry_count < 3:
        return "writing_node"
    else:
        return "final_node"

def final_node(state: MainState):
    """ Outputs the final file using save_draft. """
    drafts = state.get('draft', [])
    final_draft = drafts[-1] if drafts else ""
    
    result_md = save_draft.invoke({"content": final_draft, "filename": "draft.md"})
    
    response_msg = AIMessage(content=f"Final Draft saved to draft.md. Results: {result_md}")
    return {'messages': [response_msg]}
