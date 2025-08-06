from typing import List
from agentic.Tooling import BaseTooling
from agentic.promp_constructor import PromptConstructor

# CORRECT: as a type annotation
tools: List[BaseTooling] = []

# CORRECT: in function argument
def foo(tools: List[BaseTooling]):
    for x in tools:
        print(x.tooling_name)

def calorie_calc(x, y):
    pass

x=BaseTooling(
    "123",
    "calorie_calc",
    "a number in calorie notation",
    "counting",
    None,
    calorie_calc
)

def scraper():
    pass

y=BaseTooling(
    "abc",
    "html_scaper",
    "scraping html format file",
    "scraper",
    None,
    scraper
)

PromptConstructor(
    
)

@tooling()
gcal.fetch_calendarpoint()
