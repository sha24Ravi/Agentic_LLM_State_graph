# Initialize state
from prompts import PlannerNode
from Executor import Executor
from searchAgent import searchAgentNode
from summarizer import summarizeAgent
from langgraph.graph import StateGraph,START
from messageState import State,plan_prompt
from dotenv import load_dotenv
from langchain.schema import HumanMessage
import os
load_dotenv()  # Loads .env file

api_key = os.getenv("tavily_api_key")

graph=StateGraph(state_schema=State)

# Step 1: Planner
planner_node = PlannerNode()      
executor_node = Executor()
search_node = searchAgentNode()
summary_node= summarizeAgent()
graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)  
graph.add_node("SearchAgent",search_node)
graph.add_node("SummarizationAgent",summary_node)
graph.add_edge(START, "planner")
query = "Identify current regulatory changes for the financial services industry in the US."
print(f"Query: {query}")

state = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "enabled_agents": ["SearchAgent", "SummarizationAgent"],
        }
final_state = graph.compile()
final_state.invoke(state)


