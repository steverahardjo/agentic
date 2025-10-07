from prompt_constructor import PromptConstructor, PromptField
from typing import Callable, Dict, Any
from AgentMemory import MemoryEngine
from tools.code_runner import CodeRunner

runner = CodeRunner(3)
class BaseAgent:
    def __init__(self, name:str, description:str = "", prompt:PromptConstructor=None, memory = MemoryEngine, retries:int = 3, temp:int=0, funcs = List[Callable]):
        self.description = description
        self.name=name
        self.prompt = prompt if prompt else PromptConstructor(prompt_name=name, process_type="default")
        self.memory = memory
        self.funcs=funcs       
    def run(self, user_input:str):
        """
        This method should be overridden by subclasses to implement the agent's behavior.
        """
        for x in self.funcs:
            self.prompt.parse_func(x)
            
    def run_selected_func(self, func: Callable, params:List, **kwargs):
        """
        Run a specific function with the provided arguments.
        """
        for key,value in args:
        f = func(*param)
        return runner.run_python(f)
        
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
