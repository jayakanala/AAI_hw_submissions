import os
import json
import difflib
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.types import interrupt

load_dotenv()
with open("menu.json", "r") as f:
    menu = json.load(f)

def get_closest_dish_name(query: str, cutoff: float = 0.6) -> str | None:
    """Finds the closest matching dish name from the menu."""
    menu_names = [item["name"] for item in menu]
    matches = difflib.get_close_matches(query, menu_names, n=1, cutoff=cutoff)
    return matches[0] if matches else None


@tool
def get_menu(category:list = []):
    '''Get the Menu'''
    menu_dict = {'Bread' :[], 'Main Course' :[], 'Beverage' :[], 'Soup' :[], 'Salad' :[], 'Dessert' :[], 'Starter' :[]}
    for item in menu:
        menu_dict[item["type"]].append(item)
    if category == []:
        return menu_dict
    else:
        result = []
        for item in category:
            if item in menu_dict.keys():
                result.append(menu_dict[item])
        return result

def _search_dish(query: str) -> str:
    """Search for a dish on the menu by name or keyword."""
    try:
        query_lower = query.lower()
        matches = [
            item for item in menu 
            if query_lower in item.get("name", "").lower() or query_lower in item.get("description", "").lower() or query_lower in item.get("type", "").lower() or query_lower in item.get("category", "").lower() or query_lower in str(item.get("price", 0)).lower()
        ]
        if not matches:
            closest_name = get_closest_dish_name(query)
            if closest_name:
                matches = [item for item in menu if item.get("name") == closest_name]
        if not matches:
            return f"No dishes found matching '{query}'."
        return matches
    except Exception as e:
        return f"An error occurred: {e}"

@tool
def search_dish(query: str) -> str:
    """Search for a dish on the menu by name or keyword."""
    return _search_dish(query)
    
@tool 
def order_food(dish_name:list, quantity: int = 1) -> dict:
    ''' Place the order for customer '''
    order = []
    for item in dish_name:
        dish = _search_dish(item)
        order.append(dish)
        
    if isinstance(order, list) and len(order) > 0:
        decision = interrupt({
            "type": "order_food",
            "dish_name": [item[0]["name"] for item in order],
            "quantity": quantity,
            "price": [item[0]["price"] for item in order],
            "total_price": [item[0]["price"] * quantity for item in order]
        })
        
        if decision in ["yes", "y", "approve"]:
            return {
                "dish": dish,
                "quantity": quantity,
                "status": "ordered"
            }
        else:
            return {
                "status": "cancelled",
                "message": f"Order for {quantity}x {dish[0]['name']} was rejected/cancelled."
            }

    return {
        "status": "error",
        "message": f"No dishes found matching '{dish_name}'."
    }
   

@tool
def generate_bill(order:list):
    ''' Generate the bill of the order made by the customer '''
    from datetime import datetime
    
    order_items = []
    if isinstance(order, dict):
        if "order" in order:
            order_items = order["order"]
        elif "items" in order:
            order_items = order["items"]
        else:
            order_items = [order]
    elif isinstance(order, list):
        order_items = order
    
    subtotal = 0
    width = 48
    border = "=" * width
    divider = "-" * width
    
    bill = []
    bill.append(border)
    bill.append("B L U E   B I T E S".center(width))
    bill.append("123 Culinary Boulevard, Food Street".center(width))
    bill.append("GSTIN: 27AAAAA1111A1Z1".center(width))
    bill.append(divider)
    
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")
    bill_no = f"BB-{now.strftime('%d%H%M%S')}"
    
    date_time_line = f" Date: {date_str:<15} Time: {time_str}"
    bill.append(date_time_line + " " * (width - len(date_time_line)))
    bill_no_line = f" Bill No: {bill_no}"
    bill.append(bill_no_line + " " * (width - len(bill_no_line)))
    bill.append(divider)
    
    bill.append(f" {'Item Name':<22} {'Qty':^4} {'Price':>8} {'Total':>9} ")
    bill.append(divider)
    
    for item in order_items:
        if not isinstance(item, dict):
            continue
        
        if "dish" in item:
            dish_info = item["dish"]
            if isinstance(dish_info, list) and len(dish_info) > 0:
                dish = dish_info[0]
            elif isinstance(dish_info, dict):
                dish = dish_info
            else:
                continue
                
            name = dish.get("name", "Unknown Item")
            price = dish.get("price", 0.0)
            qty = item.get("quantity", 1)
        else:
            name = item.get("name") or item.get("dish_name") or "Unknown Item"
            price = item.get("price") or item.get("price_per_item") or item.get("pricePerItem") or 0.0
            qty = item.get("quantity") or item.get("qty") or 1
            
        item_total = price * qty
        subtotal += item_total
        
        if len(name) > 22:
            display_name = name[:19] + "..."
        else:
            display_name = name
            
        bill.append(f" {display_name:<22} {qty:^4} {price:>8.2f} {item_total:>9.2f} ")
        
    bill.append(divider)
    cgst = subtotal * 0.09
    sgst = subtotal * 0.09
    grand_total = subtotal + cgst + sgst
    
    bill.append(f"  {'Subtotal:':<32} {subtotal:>12.2f} ")
    bill.append(f"  {'CGST (9%):':<32} {cgst:>12.2f} ")
    bill.append(f"  {'SGST (9%):':<32} {sgst:>12.2f} ")
    bill.append(divider)
    bill.append(f"  {'Grand Total:':<32} {grand_total:>12.2f} ")
    bill.append(border)
    bill.append("Thank you for dining with us!".center(width))
    bill.append("Visit Us Again!".center(width))
    bill.append(border)
    
    bill_text = "\n".join(bill)
    decision = interrupt({
        "type": "generate_bill",
        "bill": bill_text
    })
    
    if decision in ["yes", "y", "approve"]:
        return bill_text
    else:
        return "Bill generation was rejected/cancelled. Ask the user what else do they want to order?"

@tool
def get_hardcopy(bill:str):
    ''' Get the hardcopy of the bill '''
    with open("bill.txt", "w") as f:
        f.write(bill)
    return "Hardcopy of the bill has been generated."

tool = [get_menu, search_dish, order_food, generate_bill, get_hardcopy]

# order = []
# order.append(order_food("Paneer Butter Masala", 2))
# order.append(order_food("Butter Chicken", 1))
# print(generate_bill(order))
    

