import inspect
from typing import List, Dict

from agentic.prompt_constructor import PromptConstructor
from llm.LLM import OpenAIClient
from agentic.tools.searcher import agent_webscraping
from agentic.tools.code_runner import CodeRunner
from agentic.tools.db_connector import GcalendarConnector
from agentic.memory import InMemory
from agentic.react_agent import ReactAgent, ReactPrompt
from agentic.base_agent import BaseAgent

# 🚨 NEVER hardcode API keys directly in code
# Use environment variables or a .env loader instead.
OPENAI_API_KEY = "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Example tool
def average_three(a, b, c):
    return (a + b + c) / 3

# Initialize LLM client
client = OpenAIClient(
    llm_inst_id="openai_client_1",
    encoder_model="text-embedding-ada-002",
    decoder_model="gpt-4o",
    api_key=OPENAI_API_KEY
)

# Inspect the agent_webscraping function to describe it automatically
sig = inspect.signature(agent_webscraping)
params_desc = []
for name, param in sig.parameters.items():
    if param.default is inspect.Parameter.empty:
        params_desc.append(f"{name} (required)")
    else:
        params_desc.append(f"{name} (optional, default={param.default})")
params_str = ", ".join(params_desc)

# Create a formatted tool description
tool_description = f"1. {{name: web_scraping, params: [{params_str}]}}"

# Build prompt
prompt_str = f"""
Here is the format of the task:
- Input: A text of something that has a link
- Output: Return structured output showing which function and parameters to use.
- Description: Use only ONE tool you are given.
######################
Tools you can use:
{tool_description}

Output sample:
{{func_name:addition, params:[12, 5]}}
"""

messages: List[Dict[str, str]] = [
    {"role": "system", "content": prompt_str},
    {"role": "user", "content": "Who wrote this newspaper headline: https://www.freemalaysiatoday.com/category/business/2025/08/12/wall-street-futures-steady-as-investors-brace-for-crucial-inflation-data"},
]

# Call OpenAI client
result = client.get_result(messages)
print("🔹 Model Output:", result)


def addition(x, y):
    return x + y

# Initialize components
inMem = InMemory()
calendar = GcalendarConnector()

pc = ReactPrompt(
    prompt_desc="Summarize my Google Calendar",
    process_type="ExtractTask",
    prompt_name="extract_task"
)

# Base agent
webscraper_ori = BaseAgent(
    name="webscraper_2",
    description="Summarize what I'm asking in 100 words",
    funcs=[agent_webscraping, addition, calendar.fetch_calendarPoint],
    prompt=pc
)

# React agent (stateful)
webscraper = ReactAgent(
    name="webscraper",
    memory=inMem,
    description="Summarize what I'm asking in 100 words",
    funcs=[agent_webscraping, addition, calendar.fetch_calendarPoint],
)

question = "Using this link, https://zig.guide/language-basics/structs/, teach me about structs in Zig in 100 words."
print(webscraper.run(question, client, 0, True))
# Example: agent_webscraping("https://en.wikipedia.org/wiki/Indonesian_National_Revolution")

