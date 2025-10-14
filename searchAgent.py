from langchain_tavily import TavilySearch
from typing import *
from langgraph.prebuilt import create_react_agent
from helper import agent_system_prompt
from langchain_openai import ChatOpenAI
from messageState import State
from langgraph.types import Command
from langchain.output_parsers import JsonOutputToolsParser
from langchain.schema import HumanMessage
import json

class searchAgentNode():
     def __init__(self):
        self.search_tool = TavilySearch(max_results=5,include_raw_content=False,)
        self.llm = ChatOpenAI(model="gpt-4o-mini",
               )
        self.web_search_agent = create_react_agent(
         self.llm,
         tools=[ self.search_tool ],
         prompt=agent_system_prompt(f"""
        You are the Researcher. You can ONLY perform research 
        by using the provided search tool (tavily_tool). 
        When you have found the necessary information, end your output.  
        Do NOT attempt to take further actions.
        return **only with valid JSON**:
            {{
          "results: <results[]>"
}}
                                                             
        """),
        
        )
     def __call__(self, state: State) ->Command[Literal["SearchAgent"]]:
        # Combine the text contents
        agent_query= state.get("agent_query")
        json_agent = self.web_search_agent
        result=json_agent.invoke({"messages":agent_query}) 
        result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content,
        name="web_researcher"
        )
        
        goto = "executor"
        return Command(
           update={ "messages": result["messages"]
                   }
             ,
            goto=goto
        )
        
     
    

     
     