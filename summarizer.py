from langchain_tavily import TavilySearch
from typing import Literal, Optional, List, Dict, Any, Type
from langgraph.prebuilt import create_react_agent
from helper import agent_system_prompt
from langchain_openai import ChatOpenAI
from messageState import State
from langgraph.types import Command
from langgraph.graph import END
from langchain.output_parsers import JsonOutputToolsParser
from langchain.schema import HumanMessage

class summarizeAgent():
 def __init__(self):
    self.llm = ChatOpenAI(model="gpt-4o-mini",
                )
    self.chart_summary_agent = create_react_agent(
    self.llm,
    tools=[],  # Add image processing tools if available/needed.
    prompt=agent_system_prompt(
        "You can only generate image captions. You are working with a researcher colleague and a chart generator colleague. "
        + "Your task is to generate a standalone, concise summary for the provided results from state.The summary should be no more than 3 sentences and should not mention the chart itself."
    ),
      )
 def __call__(self, state: State) -> Command:
    result = self.chart_summary_agent.invoke(state)
    goto = END
    print(result["messages"][-1].content)
    return Command(
        update={
            # share internal message history of chart agent with other agents
            "messages": result["messages"],
            "final_answer": result["messages"][-1].content,
        },
        goto=goto,
    )
    