from agentic.base_agent import BaseAgent
from typing import Dict, List, Union
from pydantic import BaseModel, ConfigDict
from agentic.memory import MemoryEngine


class END:
    """Marker class indicating the end of a circuit execution chain."""
    pass


class Interrupt:
    """Marker class used to interrupt circuit execution prematurely."""
    pass


class Circuit(BaseModel):
    """
    A lightweight orchestration layer for chaining multiple agentic components
    (BaseAgents) into a linear or branching execution pipeline.

    Attributes:
        name (str): Unique name for the circuit.
        desc (str): Optional description of what the circuit does.
        connections (Dict[BaseAgent, List[Union[BaseAgent, END]]]):
            Mapping of each agent to its downstream agent(s) or END marker.

    Example:
        circuit = Circuit(
            name="research_pipeline",
            desc="Sequential execution: researcher -> summarizer -> END",
            connections={
                research_agent: [summarizer_agent],
                summarizer_agent: [END]
            }
        )
        circuit.run("Explain transformer architectures")
    """

    name: str
    desc: str
    connections: Dict[BaseAgent, List[Union[BaseAgent, END]]]
    model_config = ConfigDict(from_attributes = True)

    def attach_modelInst(self) -> None:
        """
        Attach a shared model instance (LLM client) to all agents in the circuit.
        This ensures consistent model configuration across the pipeline.

        Expected Usage:
            circuit.model_inst = oai_client
            circuit.attach_modelInst()
        """
        for agent, downstream_agents in self.connections.items():
            # Assign shared model to current agent
            agent.model_inst = self.model_inst
            for downstream_agent in downstream_agents:
                # Skip END markers
                if downstream_agent is not END:
                    downstream_agent.model_inst = self.model_inst

    def overload_mem(self, memory: MemoryEngine) -> None:
        """
        Overload (inject) a shared memory engine into all agents in the circuit.

        Args:
            memory (MemoryEngine): Shared memory backend instance to attach.

        Usage:
            shared_memory = InMemory()
            circuit.overload_mem(shared_memory)
        """
        for agent in self.connections.keys():
            agent.memory = memory

    def run(self, messages: str, temp: int = 0):
        """
        Execute the circuit sequentially, passing messages through each agent
        according to the defined connection map.

        Args:
            messages (str): Input text or query passed to the first agent.
            temp (int): Temperature value forwarded to each agent (optional).

        Returns:
            str: Final output from the last agent in the circuit.
        """
        # Start with the first agent in the connection map
        current_agent = next(iter(self.connections))
        visited = set()

        while current_agent and current_agent not in visited:
            visited.add(current_agent)
            # Run the current agent with the provided message
            result = current_agent.run(messages, temp=temp)
            downstream = self.connections.get(current_agent, [])

            if not downstream:
                print(f"[Circuit] No downstream agents after {current_agent.name}, stopping.")
                break

            if END in downstream:
                print("[Circuit] Reached END of circuit.")
                break

            # Move to the next connected agent
            current_agent = downstream[0]

        return result
