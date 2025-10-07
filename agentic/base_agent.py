<<<<<<< HEAD
from agentic.prompt_constructor import PromptConstructor
from typing import Callable, List, Optional
from agentic.memory import MemoryEngine
from agentic.tools.code_runner import CodeRunner
from llm.LLM import LanguageModel
import json
import enum

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

=======
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
        
>>>>>>> 900dd12 (tidy file name convention, add a Human in Loop)
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
<<<<<<< HEAD
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

class InterruptType(enum.Enum):
    MACHINE_REVIEW = "review"    # human reviews everything
    CONFIRM = "confirm"          # human approves/rejects
    EDIT = "edit"                # human directly edits output
    OVERRIDE = "override"        # human provides final answer, ignoring machine
    FEEDBACK = "feedback"        # human gives comments, system stores them
    CHOOSE_FUNC = "choose_func"  # human decides which function/tool to run
    DELAY = "delay"              # pause execution until human says continue


class HumanInterrupt:
    def __init__(
        self,
        agent_after,          # BaseAgent instance
        query: str,
        interrupt_type: InterruptType = InterruptType.CONFIRM,
        llm_inst: Optional[LanguageModel] = None
    ):
        self.agent_after = agent_after
        self.query = query
        self.interrupt_type = interrupt_type
        self.llm_inst = llm_inst

    # -------------------
    # 1. STATIC RUN
    # -------------------
    def run_static(self, machine_output: str) -> str:
        """Static interruption handling: human-only interaction, no LLM."""
        try:
            if self.interrupt_type == InterruptType.CONFIRM:
                confirm = input(f"Confirm result? (y/n)\nResult: {machine_output}\n> ").strip().lower()
                if confirm == "y":
                    return machine_output
                else:
                    raise ValueError("Human rejected confirmation")

            elif self.interrupt_type == InterruptType.EDIT:
                print(f"Original output: {machine_output}")
                edited = input("Enter corrected version:\n> ")
                if not edited.strip():
                    raise ValueError("Empty edit not allowed")
                return edited

            elif self.interrupt_type == InterruptType.MACHINE_REVIEW:
                print("\n=== MACHINE REVIEW ===")
                print(f"Query: {self.query}")
                print(f"Machine Output:\n{machine_output}")
                decision = input("Accept [a], Reject [r], or Edit [e]?\n> ").strip().lower()
                if decision == "a":
                    return machine_output
                elif decision == "r":
                    raise ValueError("Rejected by human")
                elif decision == "e":
                    return input("Enter corrected version:\n> ")
                else:
                    raise ValueError("Invalid choice in review mode")

            else:
                return machine_output

        except Exception as e:
            # If static fails, we’ll escalate to LLM
            print(f"[Static interruption failed: {e}]")
            return None

    # -------------------
    # 2. LLM RUN (Fallback)
    # -------------------
    def run_llm(self, machine_output: str) -> str:
        """Use LLM to resolve interruptions if static handling fails."""
        if not self.llm_inst:
            return f"[No LLM available, returning machine output]\n{machine_output}"

        package = [
            {"role": "system", "content": "You are a human-overseer assistant. Resolve conflicts or corrections when a human rejects or fails to decide."},
            {"role": "user", "content": f"Query: {self.query}\nMachine Output: {machine_output}\nInstruction: Decide the final result or fix it."}
        ]
        return self.llm_inst.get_result(package, temp=0)

    # -------------------
    # 3. MASTER RUN
    # -------------------
    def run(self, machine_output: str) -> str:
        """Try static run first, then fall back to LLM if needed."""
        result = self.run_static(machine_output)
        if result is None:  # static failed
            return self.run_llm(machine_output)
        return result
=======
>>>>>>> 900dd12 (tidy file name convention, add a Human in Loop)
