from typing import List, Dict, Any, Optional
from langgraph.graph.message import MessagesState
from langchain.schema import HumanMessage

import json
class State(MessagesState):
    user_query: Optional[str]
    enabled_agents: Optional[List[str]] = ["SearchAgent", "SummarizationAgent"]
    plan: Optional[Dict[str, Dict[str, Any]]] = {}
    current_step: int = 1
    replan_flag: Optional[bool] = False
    agent_query: Optional[str] = None


def _get_enabled_agents(state: State| None = None) -> List[str]:
    
     baseline = ["SearchAgent", "SummarizationAgent"]
     enabeled_list=state.get("enabled_agents")
     if not state:
        return baseline
     if hasattr(state, "get"):
      val = state.get("enabled_agents")
     else:
      val = getattr(state, "enabled_agents", None)

      if isinstance(val,List) and val:
         filtered_list= [a for a in val if a in enabeled_list]
         return filtered_list
     return baseline

def get_agent_list()-> Dict[str, Dict[str, Any]]:
     AGENTS = {
    "SearchAgent": {
       "name": "Web Researcher",
        "capability": "Fetch public data via Tavily web search",
         "use_when": "Public information, news, current events, or external facts are needed",
        
    },
    "SummarizationAgent": {
       "name": "Summarizer",
        "capability": "Summarize and explain research data",
        "use_when": "After Web Researcher has created a research"
    }
}
     return AGENTS    
def format_agent_list_for_planning(state: State | None = None) -> str:
     description= get_agent_list()
     enabled_list=_get_enabled_agents(state)
   
     agent_list=[]
     for agent_key, details in description.items():
        if agent_key not in enabled_list:
            continue
        agent_list.append(f"  • `{agent_key}` – {details['capability']}")
     return "\n".join(agent_list) 

def get_agent_guidelines_for_planning(state:State)->str:
    descriptions= get_agent_list()
    enabled_list=_get_enabled_agents(state)
    guidelines=[]
    if "SearchAgent" in enabled_list:
        guidelines.append(f"- Use `SearchAgent` for {descriptions['SearchAgent']['use_when'].lower()}.")    
    if "SummarizationAgent" in enabled_list:
        guidelines.append(f"- Use `SummarizationAgent` for {descriptions['SummarizationAgent']['use_when'].lower()}.")    
    return guidelines    

def plan_prompt(state: State) -> HumanMessage:
   
   replan_flag   = state.get("replan_flag", False)
   user_query    = state.get("user_query")
   prior_plan    = state.get("plan") or {}
   replan_reason = state.get("last_reason", "")
   agent_list=format_agent_list_for_planning(state)
   state["enabled_agents"]=agent_list
   planner_agent_enum={"web_researcher | chart_generator"}
   agent_guidelines=get_agent_guidelines_for_planning(state)
   prompt = f"""
        You are the **Planner** in a multi‑agent system.  Break the user's request
        into a sequence of numbered steps (1, 2, 3, …).  **There is no hard limit on
        step count** as long as the plan is concise and each step has a clear goal.

        You may decompose the user's query into sub-queries, each of which is a
        separate step.  Break the query into the smallest possible sub-queries
        so that each sub-query is answerable with a single data source.
        For example, if the user's query is "What were the key
        action items in the last quarter, and what was a recent news story for 
        each of them?", you may break it into steps:

        1. Fetch the key action items in the last quarter.
        2. Fetch a recent news story for the first action item.
        3. Fetch a recent news story for the second action item.
        4. Fetch a recent news story for the last action item

        Here is a list of available agents you can call upon to execute the tasks in your plan. You may call only one agent per step.

        {agent_list}

        Return **ONLY** valid JSON (no markdown, no explanations) in this form:

        {{
        "1": {{
            "agent": "{planner_agent_enum}",
            "action": "string",
        }},
        "2": {{ ... }},
        "3": {{ ... }}
        }}

        Guidelines:
        {agent_guidelines}
        """
   if replan_flag:
        prompt += f"""
        The current plan needs revision because: {replan_reason}

        Current plan:
        {json.dumps(prior_plan, indent=2)}

        When replanning:
        - Focus on UNBLOCKING the workflow rather than perfecting it.
        - Only modify steps that are truly preventing progress.
        - Prefer simpler, more achievable alternatives over complex rewrites.
        """

   else:
        prompt += "\nGenerate a new plan from scratch."

   prompt += f'\nUser query: "{user_query}"'
   return HumanMessage(content=prompt)     


def executor_prompt(state:State)->HumanMessage:

 
 MAX_REPLANS=2
 
 executor_prompt = f"""
You are the **Executor** in a multi-agent system. Available agents: SearchAgent, SummarizationAgent.

Current state: {state}
Current step: {state.get("current_step")}
Previous agent output: {state.get("agent_query")}
Replan flag: {state.get("replan_flag")}
enabled_agent:{state.get("enabled_agents")}

**Tasks**
1. Decide if the current plan needs revision → "replan": true|false
2. Decide which agent to run next → "goto": "SearchAgent" or "SummarizationAgent"
3. Give a one-sentence justification → "reason"
4. Write the exact query/action the chosen agent should perform → "query"
5. Write the exact agent number chosen -> "stepcurrent_step"

Respond **only with valid JSON**:

{{
  "replan": <true|false>,
  "goto": "<SearchAgent|SummarizationAgent>",
  "reason": "<one sentence explanation>",
  "query": "<text for agent to perform>",
  "current agent step number":<1 | 2>"
}}
"""
 return HumanMessage(content=executor_prompt)  