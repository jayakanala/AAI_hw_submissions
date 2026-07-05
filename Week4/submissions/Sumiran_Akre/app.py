from graphh import graph, display_menu
import json
from langgraph.types import Command
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    
    user_name = input("Enter your name : ")
    CONFIG = {"configurable": {"thread_id": f"thread_{user_name}"}}
    display_menu({})
    with open("menu.json", "r") as f:
        menu = json.load(f)
    graph.update_state(CONFIG, {"user": user_name, "menu": json.dumps(menu)})
    
    while True:
        user_inp = input("You : ")
        if user_inp.lower() in ["bye", "quit"]:
            break
        response = graph.invoke({"messages": [HumanMessage(content=user_inp)]}, config=CONFIG)

        last_msg = response["messages"][-1]
        if getattr(last_msg, "tool_calls", None):
            print("[ TOOL CALLED ]", last_msg.tool_calls[0]["name"])
            print("[  TOOL ARGS  ]", last_msg.tool_calls[0]["args"])
        
        while True:
            state = graph.get_state(CONFIG)
            interrupt_found = False
            for task in state.tasks:
                if task.interrupts:
                    interrupt_found = True
                    for intr in task.interrupts:
                        if isinstance(intr.value, dict) and intr.value.get("type") == "order_food":
                            order = intr.value
                            print("\n" + "="*40)
                            print("         ORDER APPROVAL REQUIRED         ")
                            print("="*40)
                            
                            dish_names = order.get('dish_name')
                            prices = order.get('price')
                            total_prices = order.get('total_price')
                            quantity = order.get('quantity')
                            
                            if isinstance(dish_names, list) and isinstance(prices, list) and isinstance(total_prices, list):
                                for d, p, tp in zip(dish_names, prices, total_prices):
                                    print(f"Dish Name  : {d}")
                                    print(f"Quantity   : {quantity}")
                                    print(f"Price      : Rs. {p:.2f}")
                                    print(f"Total      : Rs. {tp:.2f}")
                                    print("-" * 40)
                            else:
                                print(f"Dish Name  : {dish_names}")
                                print(f"Quantity   : {quantity}")
                                print(f"Price      : Rs. {prices}")
                                print(f"Total      : Rs. {total_prices}")
                                
                            print("="*40)
                            ans = input("Approve this order? (yes/no): ").strip().lower()
                            decision = "approve" if ans in ["yes", "y", "approve"] else "reject"
                            response = graph.invoke(Command(resume=decision), CONFIG)
                            
                        elif isinstance(intr.value, dict) and intr.value.get("type") == "generate_bill":
                            bill = intr.value.get("bill")
                            print("\n" + "="*40)
                            print("          BILL APPROVAL REQUIRED         ")
                            print("="*40)
                            print(bill)
                            print("="*40)
                            ans = input("Approve this bill? (yes/no): ").strip().lower()
                            decision = "approve" if ans in ["yes", "y", "approve"] else "reject"
                            response = graph.invoke(Command(resume=decision), CONFIG)
                    break
            if not interrupt_found:
                break
        
        print("="*60)
        print("Bot :", response["messages"][-1].content)
        print("="*60)
    