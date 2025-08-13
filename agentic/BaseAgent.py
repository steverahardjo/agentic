from agentic.prompt_constructor import PromptConstructor
from typing import Callable, List
from agentic.AgentMemory import MemoryEngine
from agentic.tools.code_runner import CodeRunner
from llm.LLM import LanguageModel

import json

runner = CodeRunner(3)
class BaseAgent:
    def __init__(self, name:str, description:str = "", prompt:PromptConstructor=None, memory = MemoryEngine, retries:int = 3, output_field = None, funcs = List[Callable]):
        self.description = description
        self.name=name
        self.prompt = prompt if prompt else PromptConstructor(prompt_name=name, process_type="default")
        self.memory = memory
        self.funcs=funcs
        self.retries=retries
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
    {"role": "user", "content": user_input}]
        # Call the language model
        res = llm_inst.get_result(package)
        res = json.loads(res)
        func_name = res.get("func_name")
        params = res.get("params", [])
        print(func_name, params)
        return self.run_selected_func(self.func_map[func_name], params)
         
    def run_selected_func(self, func: Callable, params:List):
        """
        Run a specific function with the provided arguments.
        """
        if func is not runner.run_python:
            f = func(*params)
            return runner.run_python(f)
        else:
            print(params)
            return runner.run_python(params[0])
        
if __name__ == "__main__":
    def agent_webscraping(url: str, max_pages: int = 1) -> str:
        """Scrape the content of a webpage given its URL and optional maximum pages."""
        return "dummy result"
    def addition(a: int, b: int) -> int:
        """Add two integers."""
        return a + b
    pc = PromptConstructor(
        prompt_desc="Use only ONE tool to process the given link and return results",
        process_type="WebScrapingTask",
        prompt_name="WebScraperPrompt"
    )

    webscraper=BaseAgent(
        name="WebScraperAgent",
        description="An agent that scrapes web content using provided tools.",
        prompt=pc,
        funcs=[agent_webscraping, addition]
    )
    webscraper.run("Who write this newspaper headline: https://www.freemalaysiatoday.com/category/business/2025/08/12/wall-street-futures-steady-as-investors-brace-for-crucial-inflation-data")

