from agentic.tools.searcher import agent_webscraping
from llm.LLM import OpenAIClient
from agentic.prompt_constructor import PromptConstructor
from agentic.BaseAgent import BaseAgent

OPENAI_API_KEY = "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"
o_inst = OpenAIClient("ai", "", "gpt-4o")

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
    res=webscraper.run("Who write this newspaper headline: https://www.freemalaysiatoday.com/category/business/2025/08/12/wall-street-futures-steady-as-investors-brace-for-crucial-inflation-data", o_inst)
    print(res)

