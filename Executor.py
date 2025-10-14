from typing import *
from langgraph.graph.message import MessageGraph
from langchain.schema import HumanMessage
from messageState import State
from langchain_openai import ChatOpenAI
from searchAgent import searchAgentNode
from langgraph.types import Command
from messageState import State,executor_prompt
import json


class Executor():
   
    def __init__(self):
        self.search_agent = searchAgentNode()
        self.llm = ChatOpenAI(model="gpt-4o-mini",
                )
       
    def __call__(self, state: State) -> Command[Literal["SearchAgent", "SummarizationAgent"]]:
        llm_reply=self.llm.invoke(executor_prompt(state).content)
       
        if not state.get("replan_flag"):
           parsed= json.loads(llm_reply.content) 
           state["enabled_agents"] = parsed["goto"]
           state["agent_query"]=parsed["query"]
           state["current_step"]=parsed["current agent step number"]
           state["plan"]=parsed
        return Command(
         update=state,
         goto=state.get("enabled_agents")
        )   
       
        
       
