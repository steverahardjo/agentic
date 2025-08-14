from agentic.prompt_constructor import PromptConstructor
from typing import Callable, List
from agentic.AgentMemory import MemoryEngine
from agentic.tools.code_runner import CodeRunner
from llm.LLM import LanguageModel

import json

runner = CodeRunner(3)
class BaseAgent:
    def __init__(self, name:str, description:str = "", prompt:PromptConstructor=None, memory = MemoryEngine, retries:int = 3, temp:int=0, funcs = List[Callable]):
        self.description = description
        self.name=name
        self.prompt = prompt if prompt else PromptConstructor(prompt_name=name, process_type="default")
        self.memory = memory
        self.funcs=funcs
        self.retries=retries
        self.temp =temp
        self.func_map = self._create_func_map(funcs)
        
    def _create_func_map(self, funcs:List[Callable]):
        """
        Creates a dictionary mapping function names (as strings) to callables.
        """
        return {f.__name__: f for f in funcs}
        
    def run(self, user_input: str, llm_inst: LanguageModel):
        """
        Run the agent: parse functions, build prompt, call LLM, and execute selected function.
        Retries the function execution up to `max_retries` times if it fails.
        """
        # Parse all functions
        for x in self.funcs:
            self.prompt.parse_func(x)
        
        # Build the system prompt
        system_prompt = self.prompt.build_template()
        package = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        print(system_prompt)
        # Call the language model
        res = llm_inst.get_result(package, temp = self.temp)

        if self.funcs is None:
            return res
        else:
            return self.run_selected_func(res)
    
         
    def run_selected_func(self, params = str):
        """
        Run a specific function with the provided arguments.
        """
        print(params)
        try:
            parsed = json.loads(params)
        except json.JSONDecodeError:
            raise KeyError("Unable to decode json result into workable dict")
        func = self.func_map[parsed.get("func_name")]
        params = parsed.get("params", [])
        return func(*params)
