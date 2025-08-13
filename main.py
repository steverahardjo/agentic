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
        process_type="WebScrapingTask",
        prompt_name="WebScraperPrompt"
    )

    webscraper=BaseAgent(
        name="WebScraperAgent",
        description="An agent that scrapes web content using provided tools.",
        prompt=pc,
        funcs=[agent_webscraping, addition, coder.run_python]
    )
    res=webscraper.run("who is this person in 100 words: https://en.wikipedia.org/wiki/Wong_Kar-wai", oai)
    print(res)
