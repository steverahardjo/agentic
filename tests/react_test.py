from llm.LLM import OpenAIClient
from agentic.tools.code_runner import CodeRunner
from agentic.tools.db_connector import GcalendarConnector
from agentic.memory import InMemory
from agentic.preset_agents.react_agent import ReactPrompt
coder= CodeRunner(3)
calendar = GcalendarConnector("token.json")
oai = OpenAIClient("oai", "", "gpt-4o")
inMem = InMemory("inmemory_1", "webscraper")

if __name__ == "__main__":

    def addition(x:int, y:int):
        """Function are created to add two integers, x and y as listed here """
        return x+y
    pc = ReactPrompt(
        prompt_desc="Summarize for me my google calendar",
        process_type="ExtractTask",
        prompt_name="extract task"
    )
    print(pc.build_template)