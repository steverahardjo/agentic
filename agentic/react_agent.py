from typing import Optional, List, Callable
from pydantic import Field
from agentic.BaseAgent import BaseAgent
from agentic.prompt_constructor import PromptConstructor
from agentic.AgentMemory import MemoryEngine
from llm.LLM import LanguageModel
import re

# === ReAct Prompt Rules ===
react_rules = """
You are an AI assistant that follows the ReAct reasoning + acting framework.

You must always respond in exactly one of the following formats:
(1) Thought
Thought: <your reasoning here>
(2) Action
Action: {"func_name": "function_name", "params": [param1, param2]}
(3) FINISHED
[FINISHED]<result of the action>

Never combine Thought + Action, Thought + Observation, or Action + Observation in the same step.
Always choose only ONE of the three formats.
"""


# === Prompt Constructor ===
class ReactPrompt(PromptConstructor):
    prompt_name: str = Field(default="react_prompt")
    prompt_command: str = Field(default=react_rules)
    
# Single shared ReactPrompt instance
react_prompt = ReactPrompt()


# === React Agent ===
class ReactAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        description: str = "",
        memory: Optional[MemoryEngine] = None,
        funcs: Optional[List[Callable]] = None,
        prompt:ReactPrompt = react_prompt
    ):
        super().__init__(
            name=name,
            description=description,
            memory=memory,
            funcs=funcs,
            prompt=prompt,
        )
        self.max_iter = 5

    def run(
        self,
        user_input: str,
        llm_inst: Optional[LanguageModel] = None,
        temp: int = 0,
        debug_mode:bool = False
    ) -> str:
        """Run the ReAct agent loop until [FINISHED] or max_iter is reached."""
        curr_iter = 0
        result = ""

        while curr_iter < self.max_iter:
            result = super().run(
                user_input=user_input,
                llm_inst=llm_inst,
                debug_mode=debug_mode,
                temp=temp,
            )
            self.memory.add(self.name, result)
            print("number run is in ", curr_iter)

            if result.strip().startswith("[FINISHED]") or curr_iter == 3:
                break
            curr_iter += 1
        return result
    

    def _run_selected_func(self, params: str) -> None:
        """Run a specific function with the provided arguments."""
        print(params)
        match = re.search(r"Action:\s*({.*})", params, re.DOTALL)
        if match:
            return super()._run_selected_func(match.group(1))
