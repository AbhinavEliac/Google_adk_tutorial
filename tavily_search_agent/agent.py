from google.adk.agents.llm_agent import Agent
from google.adk.tools.langchain_tool import LangchainTool 
from langchain_tavily import TavilySearch


# 1) Create Tavily Search Tool
tavily_search = TavilySearch(
    max_results = 5,
    topic = "general"
)

# 2) Wrap it so ADK can use it
tavily_tool = LangchainTool(tool = tavily_search)

# 3) Give it to the agent like any tool 
root_agent = Agent(
    model='gemini-3.8-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge from tavily search whenever necessary for web search',
    tools = [tavily_tool]
)
