from typing import Optional, List, Callable, Union
from pydantic import Field
from agentic.BaseAgent import BaseAgent
from agentic.prompt_constructor import PromptConstructor
from agentic.AgentMemory import MemoryEngine
from llm.LLM import LanguageModel
import re

# === ReAct Prompt Rules ===
react_rules = """
You are an AI assistant that follows the ReAct framework.

You must always respond in exactly one of the following formats:

(1) Thought
Thought: <your reasoning here>

(2) Action
{"func_name": "function_name", "params": [param1, param2]}

(3) FINISHED
[FINISHED]<final answer here>

Rules:
- Never mix Thought + Action, Thought + Observation, or Action + Observation.
- Never output "Thought" twice in a row. After a Thought, either take an Action or Finish.
- When the task is complete or no further tool use is required, stop
- Always use the latest Observation to plan your next step.
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
        prompt: ReactPrompt = react_prompt
    ):
        super().__init__(
            name=name,
            description=description,
            memory=memory,
            funcs=funcs,
            prompt=prompt,
        )
        self.max_iter = 5
        self.loop_flag = True  # loop control

        # Map of callable actions for ReAct
        self.func_map["stop"] = self.stop

    def stop(self):
        """Stop the agent loop immediately."""
        self.loop_flag = True
        print(f"[STOP] {self.name} loop has been stopped.")
        self.logging(result="[STOP] stop() called")

    def run(
        self,
        user_input: str,
        llm_inst: Optional[LanguageModel] = None,
        temp: int = 0,
        debug_mode: bool = False
    ) -> str:
        """Run the ReAct agent loop until [FINISHED], stop is called, or max_iter is reached."""
        curr_iter = 0
        final_result: str = ""
        self.loop_flag = True  # reset loop at start

        while curr_iter < self.max_iter and self.loop_flag:
            # Call parent run to get the LLM result
            result = super().run(
                user_input=user_input,
                llm_inst=llm_inst,
                temp=temp
            )

            # Normalize result
            content = result.get("content", "") if isinstance(result, dict) else str(result)

            # Store in memory
            if self.memory:
                self.memory.add(self.name, content)

            # Debug logging
            if debug_mode:
                print(f"Iteration {curr_iter}")
                print(content)

            # Log to trace file
            self.logging(result=content, no_iter=curr_iter)

            final_result = content
            curr_iter += 1

            # Stop if [FINISHED] or stop() is called
            if content.strip().startswith("[FINISHED]"):
                self.stop()
                break

        return final_result

    def logging(self, prompt: str = None, result: str = None, no_iter: int = 0):
        """Append logs to [agent_name].trace"""
        log = f"Iteration {no_iter}\n" + "*" * 50 + "\n"
        if prompt:
            log += f"Prompt:\n{prompt}\n"
        if result:
            log += f"Result:\n{result}\n"
        with open(f"{self.name}.trace", "a") as file:
            file.write(log)
