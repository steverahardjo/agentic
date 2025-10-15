from agentic.base_agent import BaseAgent
from llm.LLM import LanguageModel
from typing import Dict, List, Union
from pydantic import BaseModel
from agentic.memory import MemoryEngine


class END:
    """Marker for circuit termination"""
    pass

class Interrupt:
    """Marker for interrupting circuit execution"""
    pass


class Circuit(BaseModel):
    name: str
    desc: str
    connections: Dict[BaseAgent, List[Union[BaseAgent, END]]]

    def attach_modelInst(self) -> None:
        """
        Option to overload the model_inst of agents inside the circuit
        """
        # Attach the same model to all agents
        for agent, downstream_agents in self.connections.items():
            agent.model_inst = self.model_inst
            for downstream_agent in downstream_agents:
                if downstream_agent is not END:
                    downstream_agent.model_inst = self.model_inst

    def overload_mem(self, memory: MemoryEngine) -> None:
        """
        Option to overload memory engine being used in agents inside a circuit
        """
        # Attach shared memory engine to all agents
        for agent in self.connections.keys():
            agent.memory = memory

    def run(self, messages:str, temp:int=0):
        current_agent = next(iter(self.connections))
        visited = set()
        while current_agent and current_agent not in visited:
            visited.add(current_agent)
            result = current_agent.run(messages, temp = temp)
            if current_agent in self.interrupting:
                print(f"Execution interrupted at {current_agent}")
                break
            downstream = self.connections.get(current_agent, [])

            if not downstream:
                print(f"No downstream agents after {current_agent}, stopping.")
                break
            if END in downstream:
                print("Reached END of circuit.")
                break
            current_agent = downstream[0]
            
        return result
