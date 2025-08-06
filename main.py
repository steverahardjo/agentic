from agentic.BaseAgent import Agent
from llm.LLM import OpenAIClient
from agentic.prompt_constructor import PromptConstructor
from agentic.tools.db_connector import GcalendarConnector
from agentic.Tooling import tooling, BaseTooling

main_background ="""
current_time: 2025-08-04T17:12:00+08:00
owner: Steve Rahardjo
work_in: Data Analytics (Intern at SynergyXYZ)
hobbies: History, Watching youtube, Building agentic tools
"""

# Instantiate your LLM client
openai = OpenAIClient("o_ai_client1", "", "gpt-4o")

# Instantiate the tool
gcal = GcalendarConnector("token.json")

# Define the tool function and register it
@tooling(
    tooling_id="001",
    tooling_name="calendar_fetcher",
    output_struct="List[Dict[str, Any]]",
    description="Fetches calendar events between two ISO8601 date strings",
    input_schema={
        "start": {
            "type": "string",
            "description": "ISO8601 start datetime (e.g., 2025-08-04T00:00:00)"
        },
        "end": {
            "type": "string",
            "description": "ISO8601 end datetime (e.g., 2025-08-10T23:59:59)"
        }
    },
    tags=["calendar", "productivity"]
)
def calendar_fetch_fn(inputs: dict):
    start = inputs["start"]
    end = inputs["end"]
    return gcal.fetch_calendarPoint(start, end)

# Create the PromptConstructor
schedule_constructor = PromptConstructor(
    task_description="Fetch all the schedule I have within a date range",
    input_schema=["start", "end"],
    output_schema="List of meetings with main subjects and day",
    constraints="",
    tools_allowed=[calendar_fetch_fn.tool],
    system_prompt=main_background
)

# Instantiate the Agent
cal_retriever = Agent(
    agent_id="cal_retriever",
    agent_desc="Agent using the Google Calendar tool to retrieve schedule information.",
    llm_inst=openai,
    signature=schedule_constructor,
    memory=None
)

# Run a sample query
if __name__ == "__main__":
    result = cal_retriever.run("Give me all of the schedule last semester in Monash", 0)
    print(result)

