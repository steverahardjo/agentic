from agentic.tools.searcher import agent_webscraping
from llm.LLM import OpenAIClient
import inspect
from typing import List, Dict

OPENAI_API_KEY = "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"

def average_three(a, b, c):
    return (a+b+c)/3


client = OpenAIClient(
    llm_inst_id="openai_client_1",
    encoder_model="text-embedding-ada-002",
    decoder_model="gpt-4o",
    api_key=OPENAI_API_KEY
)
# Get signature of your tool function
sig = inspect.signature(agent_webscraping)

# Extract parameters info as a string for prompt
params_desc = []
for name, param in sig.parameters.items():
    if param.default is inspect.Parameter.empty:
        params_desc.append(f"{name} (required)")
    else:
        params_desc.append(f"{name} (optional, default={param.default})")
params_str = ", ".join(params_desc)

# Build the tool description for the prompt
tool_description = f"1. {{name: web_scraping, params: [{params_str}]}}"

# Build full prompt with description including tool info
prompt_str = f"""
Here is the format of the task:
- Input: A text of something that has a link
- Output: return a 
- Description: use only ONE tool you are given
######################
Tools you can use:
{tool_description}

Output sample:
{{func_name:addition, params:[12, 5]}}
"""

# Prepare chat messages for OpenAIClient
messages: List[Dict[str, str]] = [
    {"role": "system", "content": prompt_str},
    {"role": "user", "content": "Who write this newspaper headline: https://www.freemalaysiatoday.com/category/business/2025/08/12/wall-street-futures-steady-as-investors-brace-for-crucial-inflation-data"},
]

# Call your client with the prompt messages
result = client.get_result(messages)
print(result)

