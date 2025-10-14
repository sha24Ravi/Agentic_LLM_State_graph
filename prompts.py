from typing import *
from langgraph.graph.message import MessageGraph
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph
from messageState import State,plan_prompt
from langchain_openai import ChatOpenAI
from langgraph.types import Command
import json

class PlannerNode():
  def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini",
                )
  def __call__(self,state:State)->Command[Literal["SearchAgent"]]:
   
    llm_reply=self.llm.invoke(plan_prompt(state).content)
    state["plan"]=llm_reply.content
    state["messages"].append("🧠 Planner created plan successfully.")
    state["replan_flag"] = False 
    state["current_step"]=1

    return Command(
       update=state,
       goto="executor"
    )
    
