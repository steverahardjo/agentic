from agentic.prompt_constructor import PromptConstructor
from agentic.BaseAgent import BaseAgent
from llm.LLM import OpenAIClient
from agentic.tools.searcher import agent_webscraping
from agentic.tools.code_runner import CodeRunner
OPENAI_API_KEY = "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"


coder= CodeRunner(3)

oai = OpenAIClient("oai", "", "gpt-4o", OPENAI_API_KEY)
if __name__ == "__main__":

    def addition(x, y):
        return x+y
    pc = PromptConstructor(
        prompt_desc="Use only ONE tool to process the given link and return results",
        process_type="CodingTask",
        prompt_name="Coding task"
    )

    webscraper=BaseAgent(
        name="CodingTask",
        description="An agent to write and run coding task",
        prompt=pc,
        funcs=[agent_webscraping, addition, coder.run_python]
    )
    res=webscraper.run("write me a solve and test cases runned of palindrome longest substring", oai)
    print(res)
