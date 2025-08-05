from openai import OpenAI
import uuid
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


# Define your tool (function schema)
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia"
                }
            },
            "required": ["location"]
        }
    }
}]

# Call the chat model with tools
response = client.chat.completions.create(
    model="gpt-4-1106-preview",  # or "gpt-4o", "gpt-3.5-turbo-1106"
    messages=[
        {"role": "user", "content": "What is the weather like in Paris today?"}
    ],
    tools=tools,
    tool_choice="auto"  # optional: "auto" or {"type": "function", "function": {"name": "get_weather"}}
)

# Check tool call from assistant
assistant_message = response.choices[0].message
print(assistant_message)

if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        print("Tool Call Name:", tool_call.function.name)
        print("Tool Call Arguments:", tool_call.function.arguments)
