from BaseAgent import BaseAgent
from llm.LLM import LanguageModel
import enum
from typing import Dict, List
from pydantic import BaseModel

class Marker(enum.Enum):
    STOP = "stop"

class Circuit(BaseModel):
    name: str
    desc: str
    model_inst: LanguageModel
    connections: Dict[BaseAgent, List[BaseAgent]]

    def attach_modelInst(self):
        # Iterate over each agent and its downstream connections
        for agent, downstream_agents in self.connections.items():
            # Attach the model instance to the agent itself
            agent.model_inst = self.model_inst
            # Attach the model instance to downstream agents
            for downstream_agent in downstream_agents:
                downstream_agent.model_inst = self.model_inst

    def run(self, )
