from graph import build_graph
from langchain_core.messages import HumanMessage
import os

if __name__ == "__main__":
    while True:
        print("=" * 60)
        print("  Welcome to the Multi-Agent Research Crew (LangGraph)  ".center(60, "="))
        print("=" * 60)
        
        topic = input("Enter the research topic : ").strip()

        if topic.lower() in ["bye", "quit", "exit"]:
            print("Thank you for using the Multi-Agent Research Crew. Goodbye!")
            break    
        
        print(f"\nInitiating crew for topic: '{topic}'...\n")
        
        app = build_graph()
        
        initial_state = {"messages": [HumanMessage(content=topic)]}
        for event in app.stream(initial_state):
            for node_name, state_update in event.items():
                print(f"\n[Node: {node_name.upper()} started]")
                if node_name == "chat_node":
                    print(f"[ AGENT ] : {state_update['messages'][-1].content}")
                elif node_name == "research_node" and "research_notes" in state_update:
                    print("-" * 40)
                    print("Research Findings (Snippet):")
                    notes = state_update["research_notes"][-1]
                    snippet = notes[:300] + "..." if len(notes) > 300 else notes
                    print(snippet)
                    print("-" * 40)
                elif node_name == "writing_node" and "draft" in state_update:
                    print("-" * 40)
                    print("Written Draft (Snippet):")
                    draft = state_update["draft"][-1]
                    snippet = draft[:300] + "..." if len(draft) > 300 else draft
                    print(snippet)
                    print("-" * 40)
                elif node_name == "review_node" and "review" in state_update:
                    review_data = state_update["review"]
                    print("=" * 60)
                    print("FINAL POLISHED ARTICLE".center(60))
                    print("=" * 60)
                    print(review_data.get("wordicts", ""))
                    print("=" * 60)
                    print(f"Review Score: {review_data.get('score', 'N/A')}/10")
                    if review_data.get("suggestions"):
                        print("Suggestions: " + ", ".join(review_data.get("suggestions", [])))
                    print("=" * 60)
                elif node_name == "final_node":
                    print(f"[ AGENT ] : {state_update['messages'][-1].content}")
                print(f"\n[Node: {node_name.upper()} completed]")

