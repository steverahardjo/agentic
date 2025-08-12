from prompt_constructor import PromptConstructor, PromptField
from typing import Callable, Dict, Any
from AgentMemory import MemoryEngine
from tools.code_runner import CodeRunner

runner = CodeRunner(3, )
class BaseAgent:
    def __init__(self, name:str, description:str = "", prompt:PromptConstructor=None, memory = MemoryEngine, retries:int = 3, output_fields = None):
        self.name = name
        self.description = description
        self.prompt = prompt if prompt else PromptConstructor(prompt_name=name, process_type="default")
        self.memory = memory if memory else MemoryEngine(memory_id=name, allowed_agent=[name])

    def run(self, *args, **kwargs):
        """
        This method should be overridden by subclasses to implement the agent's behavior.
        """
        raise NotImplementedError("Subclasses must implement the run method.")
    
    def run_selected_func(self, func: Callable, *args, **kwargs):
        """
        Run a specific function with the provided arguments.
        """
