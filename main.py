from agentic.prompt_constructor import PromptConstructor
from llm.LLM import OpenAIClient
from agentic.tools.searcher import agent_webscraping
from agentic.tools.code_runner import CodeRunner
from agentic.tools.db_connector import GcalendarConnector
from agentic.AgentMemory import InMemory
from agentic.react_agent import ReactAgent, ReactPrompt
from agentic.BaseAgent import BaseAgent

OPENAI_API_KEY = "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"
coder= CodeRunner(3)
calendar = GcalendarConnector("token.json")
oai = OpenAIClient("oai", "", "gpt-4o", OPENAI_API_KEY)
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
    webscraper_ori = BaseAgent(
        name="webscraper_2",
        description= "Summarize what I'm asking in 100 words",
        funcs = [agent_webscraping, addition, calendar.fetch_calendarPoint],
        prompt= pc
    )
    webscraper=ReactAgent(
        name="webscraper",
        memory=inMem,
        description="Summarize what I'm asking in 100 words",
        funcs=[agent_webscraping, addition, calendar.fetch_calendarPoint],
    )
    question="Using this link,  https://zig.guide/language-basics/structs/, Teach me about struct of zig in 100 words"
    print(webscraper.run(question, oai, 0))
    #print(agent_webscraping("https://en.wikipedia.org/wiki/Indonesian_National_Revolution"))


