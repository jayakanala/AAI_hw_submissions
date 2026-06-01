"""
Train ticket agent
here the agent works on the start station and end station that user gives to give the available routes with ticket availability and prices
right now it works only for one sided travel i.e. it works for pune to hyderabad and not from hyderabad to pune
will add this later on
also the price of the ticket is decided by the start and end station as the price of travel between 2 stations might be different
"""

import requests
import json
import re

#tools

def normalise_station_name(name: str) -> str:
    """normalise the station name that the llm provides"""
    station_list=["pune", "hadapsar", "daund", "kurudwadi", "solapur", "dharashiv", "latur", "hyderabad"]
    for stations in station_list:
        if stations in name:
            return stations
    return False

def search_stations (start_station: str, end_station: str):
    """searches the routes which can be used"""
    station_list={
        "pune solapur": ["pune", "hadapsar", "daund", "kurudwadi", "solapur"],
        "pune hyderabad": ["pune", "daund", "kurudwadi", "dharashiv", "latur", "hyderabad"]
    }

    start_s= normalise_station_name(start_station.lower())
    end_s= normalise_station_name(end_station.lower())

    if(start_s and end_s):
        routes=[]

        for keyword, products in station_list.items():
            if start_s in products and end_s in products:
                routes.append(keyword)
        if not routes:
            return f"{start_s} station and {end_s} station are not together in any of the given route data"
        else:
            return routes
    else:
        return f"Either one or both of the stations are not in our database"

def check_ticket_availability(train_route: list) -> dict:
    """checks tickets available for the next 3 days"""
    tickets_available={
        "pune solapur": {"day1": 25, "day2": 56, "day3":97},
        "pune hyderabad": {"day1": 0, "day2": 12, "day3": 42}
    }
    availabe_tickets={}

    for route in train_route:
        if route in tickets_available.keys():
            availabe_tickets[route] = tickets_available[route]
    return availabe_tickets

def ticket_prices(train_route: list, start_station: str, end_station: str) -> dict:
    """gives the price for ticket on all routes that can be taken"""
    route_prices= {
        "pune solapur": [["pune", "hadapsar", "daund", "kurudwadi", "solapur"],[70,30,55,25]],
        "pune hyderabad": [["pune", "daund", "kurudwadi", "dharashiv", "latur", "hyderabad"],[90,50,100,120,105]]
    }

    start_s= normalise_station_name(start_station.lower())
    end_s= normalise_station_name(end_station.lower())
    prices={}

    for route in train_route:
        total=0
        start_ind=route_prices[route][0].index(start_s)
        end_ind=route_prices[route][0].index(end_s)
        if start_ind > end_ind:
            return f"Travel from {start_s} to {end_s} is not supported yet\nmodel right now works for one sided travel only"
        else:
            for i in range(start_ind, end_ind):
                total+=route_prices[route][1][i]
            prices[route]=total
    return prices




Tools = {
    "search_stations": search_stations,
    "check_ticket_availability": check_ticket_availability,
    "ticket_prices": ticket_prices
}




#agent

class rail_agent:
    def __init__(self):
        self.system="""
you are a rail ticketing assistant.

available tools:
1. search_stations(start_station, end_station)
-find the train routes which have the following station in it

2. check_ticket_availability(train_route)
-check ticket availability across the train routes we got from search_stations(start_station, end_station)
-remember to pass exact train routes list (even capitalization, spacing and format) that we got as output from search_stations(start_station, end_station)
-Example:
TOOL: check_ticket_availability
ARGS: {
    "train_route": ["pune solapur", "pune hyderabad"]
}
where the output from the search_stations(start_station, end_station) function was ["pune solapur", "pune hyderabad"]

3. ticket_prices(train_route: list, start_station: str, end_station: str)
-check ticket prices in all the routes that we got output in search_stations(start_station, end_station)
-Example:
TOOL: ticket_prices
ARGS: {
    "train_route": ["pune solapur", "pune hyderabad"], "start_station": "start station by user", "end_station": "end station by user"
}
where the output from the search_stations(start_station, end_station) function was ["pune solapur", "pune hyderabad"]

if a tool is required reply EXACTLY:
    
TOOL: tool_name
ARGS: {"parameter1":"value"}

do not explain anything when calling tools

while giving the final answer mention all the things like
-train routes that have both the start and end stationns on the route
-train routes that have tickets available on asked days(if not mentioned by user give the data for all 3 days)
-ticket prices on all routes on the days asked and mention if any route has tickets unavailable on some day
"""

    def ask_ollama(self, prompt):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:4b",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]
    
    def run(self, user_message):
        conversation= f"""
{self.system}

User:
{user_message}
"""
        while True:
            output= self.ask_ollama(conversation)
            print("\nModel: ")
            print(output)

            tool_match=re.search(
                r"TOOL:\s*(\w+)\s*ARGS:\s*(\{.*\})",
                output,
                re.DOTALL
            )

            if not tool_match:
                return output
            
            tool_name= tool_match.group(1)
            args= json.loads(tool_match.group(2))
            result= Tools[tool_name](**args)

            print(f"\nrunning {tool_name}")
            print("Result: ",result)

            conversation += f"""

Assistant:
{output}

Tool Results:
{result}
"""
            
#demo
if __name__ == "__main__":
    agent = rail_agent()

    queries = [
        "i need to go to kurudwadi by train from pune, find me a train route and check ticket availabity on next 2 days and give the number of tickets available on each days with the ticket price",
        "i need to go to solapur from hadapsar, find me a train route and price with ticket availability",
        "give me ticket prices if i want to go from daund to latur"
    ]

    for query in queries:
        answer = agent.run(query)
        print(f"\nAgent: {answer}")
        print("-" * 60)
        print("\nFINAL ANSWER:")
        print(answer)
        print("-" * 60)