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
        
    def __create_func_map(self, funcs: List[Callable]):
        """Creates a dictionary mapping function names (as strings) to callables."""
        return {f.__name__: f for f in funcs}
    
    def run(
        self,
        user_input: str,
        llm_inst: Optional[LanguageModel] = None,
        temp: int = 0,
        debug_mode: bool = False
    ):
        """Run the agent: parse functions, build prompt, call LLM, and execute selected function."""
        # Parse all functions into the system prompt
        for func in self.funcs:
            self.prompt.parse_func(func)

        system_prompt = self.prompt.render_prompt()

        # Build message history
        package = [{"role": "system", "content": system_prompt}]
        package.append({"role": "user", "content": user_input})

        # Retrieve past memory
        if self.memory is not None:
            retrieved = self.memory.retrieve(self.name, "")
            if isinstance(retrieved, list):
                retrieved = " ".join(map(str, retrieved))
            if retrieved:
                package.append({"role": "system", "content": f"Observation: {retrieved}"})

        if debug_mode:
            return package
        
        res = (llm_inst or self.llm_inst).get_result(package, temp=temp)

        if not self.funcs:
            if self.memory is not None:
                self.memory.add(agent_id=self.name, item=res)
            return res
        
        if isinstance(res, str) and res.strip().startswith("{") and res.strip().endswith("}"):
            try:
                return self._run_selected_func(res)
            except Exception:
                return res
