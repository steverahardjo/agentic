from typing import Callable, List, Optional, Union
from agentic.prompt_constructor import PromptConstructor
from agentic.memory import MemoryEngine
from agentic.tools.code_runner import CodeRunner
from llm.LLM import LanguageModel
import json
from agentic.tools.mcp_connector import MCPConnector

runner = CodeRunner(3)


class BaseAgent:
    def __init__(
        self,
        name: str,
        description: str = "",
        prompt: Optional[PromptConstructor] = None,
        memory: Optional[MemoryEngine] = None,
        funcs: Optional[Union[List[Callable], List[MCPConnector]]] = None):
        
        self.name = name
        self.description = description
        self.prompt = prompt if prompt else PromptConstructor(prompt_name=name, process_type="default")
        self.memory = memory
        self.funcs = funcs or []
        self.func_map = self.__create_func_map(self.funcs)
        self.llm_inst: Optional[LanguageModel] = None

    def __create_func_map(self, funcs: List[Callable]):
        """Creates a dictionary mapping function names to callables."""
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
            if callable(func):
                self.prompt.parse_func(func)
            elif isinstance(func, MCPConnector):
                tools = func.list_tools()
                for tool in tools:
                    self.prompt.parse_mcp(tool)

        system_prompt = self.prompt.render_prompt()
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

        # Store in memory
        if self.memory is not None:
            self.memory.add(agent_id=self.name, item=res)

        # If no functions, just return result
        if not self.funcs:
            return res

        # Try structured execution
        if isinstance(res, str) and res.strip().startswith("{") and res.strip().endswith("}"):
            try:
                return self._run_selected_func(res)
            except Exception:
                return res
        else:
            return res

    def _run_selected_func(self, params: str):
        """Run a specific function with the provided arguments."""
        try:
            parsed = json.loads(params)
        except json.JSONDecodeError:
            raise KeyError("Unable to decode json result into workable dict of " + params)

        func = self.func_map.get(parsed.get("func_name"))
        if not func:
            return params
        return func(*parsed.get("params", []))

    def attach_model_inst(self, model_inst: LanguageModel):
        """Attach a language model instance for later use."""
        self.llm_inst = model_inst

    def __str__(self):
        return f"Agent<{self.name}>\n Description: {self.description}\n Functions: {[f.__name__ for f in self.funcs]}"