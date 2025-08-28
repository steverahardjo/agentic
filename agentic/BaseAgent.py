from agentic.prompt_constructor import PromptConstructor
from typing import Callable, List, Optional
from agentic.AgentMemory import MemoryEngine
from agentic.tools.code_runner import CodeRunner
from llm.LLM import LanguageModel
import json

runner = CodeRunner(3)

class BaseAgent:
    def __init__(
        self,
        name: str,
        description: str = "",
        prompt: Optional[PromptConstructor] = None,
        memory: Optional[MemoryEngine] = None,
        funcs: Optional[List[Callable]] = None
    ):
        self.name = name
        self.description = description
        self.prompt = prompt if prompt else PromptConstructor(prompt_name=name, process_type="default")
        self.memory = memory
        self.funcs = funcs or []
        self.func_map = self.__create_func_map(self.funcs)
        self.llm_inst: Optional[LanguageModel] = None

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
            return package  # show full prompt for debugging

        # Run the model
        res = (llm_inst or self.llm_inst).get_result(package, temp=temp)

        # If no tools, just return plain text
        if not self.funcs:
            if self.memory is not None:
                self.memory.add(agent_id=self.name, item=res)
            return res

        # Detect Action format before running a function
        if isinstance(res, str) and res.strip().startswith("{") and res.strip().endswith("}"):
            try:
                return self._run_selected_func(res)
            except Exception:
                return res  # fallback
        else:
            return res



    def _run_selected_func(self, params: str) -> None:
        """Run a specific function with the provided arguments."""
        try:
            parsed = json.loads(params)
        except json.JSONDecodeError:
            raise KeyError("Unable to decode json result into workable dict of "+ params)

        func = self.func_map.get(parsed.get("func_name"))
        if not func:
            return params
        return func(*parsed.get("params", []))

    def attach_model_inst(self, model_inst: LanguageModel) -> None:
        """Attach a language model instance for later use."""
        self.llm_inst = model_inst
