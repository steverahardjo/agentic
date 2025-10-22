from agentic.prompt_constructor import PromptConstructor
from llm.LLM import OpenAIClient
from agentic.tools.searcher import agent_webscraping
from agentic.tools.code_runner import CodeRunner
from agentic.tools.db_connector import GcalendarConnector

from agentic.memory import InMemory
from agentic.preset_agents.react_agent import ReactAgent, ReactPrompt
from agentic.base_agent import BaseAgent

from typing import Literal


CategoryType = Literal[
    "Wars and Conflicts",
    "Politics and Governance",
    "Science and Innovation",
    "Cultural and Artistic Movements",
    "Exploration and Discovery",
    "Economic Events",
    "Social Movements",
    "Man-Made Disasters and Accidents",
    "Natural Disasters and Climate",
    "Sports and Entertainment",
    "Famous Personalities and Achievements"
]

# Create the prompt
cla_prompt = PromptConstructor(
    prompt_desc="Classify a historical event based on its description.",
    process_type="Classification",
    prompt_name="event_classifier"
)

# Define the input
cla_prompt.giveInput("text", "A sentence or paragraph describing a historical event.")

# Define the output (classification label)
cla_prompt.giveOutput(
    "category",
    "Predicted category of the event. Must be one of: "
    "Wars and Conflicts, Politics and Governance, Science and Innovation, "
    "Cultural and Artistic Movements, Exploration and Discovery, Economic Events, "
    "Social Movements, Man-Made Disasters and Accidents, Natural Disasters and Climate, "
    "Sports and Entertainment, Famous Personalities and Achievements."
)
