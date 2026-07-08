from langgraph.graph import StateGraph, START, END
from state_and_prompts import MainState
from nodes import chat_node, research_node, writing_node, review_node, final_node, review_router

def build_graph():
    """ Builds and returns the compiled graph."""
    workflow = StateGraph(MainState)

    workflow.add_node("chat_node", chat_node)
    workflow.add_node("research_node", research_node)
    workflow.add_node("writing_node", writing_node)
    workflow.add_node("review_node", review_node)
    workflow.add_node("final_node", final_node)

    workflow.add_edge(START, "chat_node")
    workflow.add_edge("chat_node", "research_node")
    workflow.add_edge("research_node", "writing_node")
    workflow.add_edge("writing_node", "review_node")
    
    workflow.add_conditional_edges(
        "review_node", 
        review_router, 
        {
            "writing_node": "writing_node", 
            "final_node": "final_node"
        }
    )
    workflow.add_edge("final_node", END)

    return workflow.compile()