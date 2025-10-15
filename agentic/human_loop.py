from typing import Dict, List, Union, Optional
from pydantic import BaseModel
from circuit import Circuit
from base_agent import BaseAgent
from memory import MemoryEngine
# ==== Core Markers ====
class END:
    """Marker for circuit termination"""
    pass


class BaseHIL:
    def __init__(self, query: str, llm_inst=None):
        self.query = query
        self.llm_inst = llm_inst

    def interrupt(self, machine_output: str) -> str:
        """Base method to handle human-in-the-loop interaction"""
        pass

    def set_llm(self, llm_inst) -> None:
        """Set LLM instance if needed"""
        self.llm_inst = llm_inst

    def __diverge_branch__(self, circuit:Circuit)->List[BaseAgent]:
        """
        Identify interruptor that diverge to a multiple agents and their branches
        """
        return circuit.connections[self]
    
    def __converge_branch__(self, circuit:Circuit)->List[BaseAgent]:
        """
        Identify interruptor that converge from multiple agents
        """
        pass

    def send_to_user(self, message: str) -> str:
        """Placeholder for sending message to human user and getting response."""
        print(self.interrupt)
        return input("Your response: ")
    
    def post_process(self, response: str) -> str:
        """Optional post-processing of user response."""

class ApprovalHIL(BaseHIL):
    def interrupt(self, machine_output: str) -> bool:
        """Ask for human approval (yes/no) using LLM proxy or human-in-the-loop."""
        system_prompt = self.context if hasattr(self, "context") else ""
        prompt = f"{self.query}\nOutput: {machine_output}\nIs this acceptable? (yes/no)"
        response = self.llm_inst.get_result([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        return self._normalize_response(response)

    def llm_decision(self, user_input: str) -> bool:
        """Use LLM to decide approval based on user input."""
        system_prompt = (self.context + "\n") if hasattr(self, "context") else ""
        system_prompt += f"{self.query}\nPlease respond strictly with 'yes' or 'no'."
        response = self.llm_inst.get_result([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ])
        return self._normalize_response(response)

    def _inject_context(self, prev_output: str) -> None:
        """Inject previous output into the query template if needed."""
        if hasattr(self, "context") and "{previous_output}" in self.context:
            self.context = self.context.replace("{previous_output}", prev_output)

    def _normalize_response(self, response: str) -> bool:
        """Normalize LLM/human response to boolean yes/no."""
        resp = response.lower().strip()
        return resp.startswith("y")
    
    
class RouterHIL(BaseHIL):
    def __init__(self, query: str, options: Optional[List[str]] = None, llm_inst=None):
        super().__init__(query, llm_inst)
        self.options = options or []

    def set_routes_from_circuit(self, circuit: Circuit) -> None:
        """
        Discover available routes from the circuit's connections dynamically.
        """
        downstream = circuit.connections.get(self, [])
        # Exclude END marker and extract agent names
        self.options:List[BaseAgent] = [
            getattr(agent, "name", str(agent)) 
            for agent in downstream if not isinstance(agent, END)
        ]

    def interrupt(self, machine_output: str) -> str:
        """
        Ask for human/LLM routing decision from available options.
        Returns the chosen option as a string (agent name).
        """
        if not self.options:
            raise ValueError("RouterHIL has no options set. Call set_routes_from_circuit first.")
        user_input = input(
            f"Background: {machine_output}\n"
            f"Current output from previous agent: {machine_output}\n"
            f"Available routes:\n"
            + "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(self.options))
            + f"\n{self.query}"
        )

        try:
            # normalize input
            choice = self._normalize_choice(user_input)

            # If user entered a valid number, map to option
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.options):
                    return self.options[idx]

            # If direct match with option
            if choice in self.options:
                return choice

            print("Invalid input. Falling back to LLM instance for closest match...")
            llm_response = self.llm_inst.get_result([
                {"role": "system", "content": "return the closest match numerically (i.e. 1, 2, 3) just once, no alphabet"},
                {"role": "user", "content": user_input}
            ])
            return self._normalize_choice(llm_response)

        except Exception as e:
            print(f"Error normalizing choice: {e}. Returning raw input.")
            return user_input.strip()
        
    def _normalize_choice(self, response: str) -> str:
        """
        Normalize LLM/human response into one of the valid options.
        """
        resp = response.strip().lower()
        for option in self.options:
            if option.lower() in resp:
                return option
        return resp

class ConvergenceHIL(BaseHIL):
    ###todo unsure how to implement
    def __init__(self, query: str, llm_inst=None):
        super().__init__(query, llm_inst)

    def interrupt(self, machine_outputs: List[str], command_to_user:str=None) -> str:
        """Ask for human input to synthesize or summarize multiple machine outputs."""
        pass
class HijackHIL(BaseHIL):
    def interrupt(self, machine_output: str) -> str:
        """Ask for human input to modify or hijack the machine output."""
        input_string = f"{self.query}\nCurrent output: {machine_output}\nPlease provide your modification:"
        response = input(input_string + "\nYour input:  ")
        return self.post_process(response)
    

    def post_process(self, response: str) -> str:
        """
        THIS SHOULD BE OVERRIDEN BY USER TO DIRECTLY PASS AS FLOW OR TO MemoryEngine
        Optional post-processing of user response."""
        return response.strip()
