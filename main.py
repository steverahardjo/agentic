from agentic.prompt_constructor import PromptConstructor
from agentic.tools.mcp_connector import MCPConnector
from agentic.fields import Field


# Example: define a local function tool
def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarizes a given text into a concise version."""
    return text[:max_length] + "..." if len(text) > max_length else text


# Example: create a dummy MCP connector
class DummyMCP(MCPConnector):
    def __init__(self, name):
        self.name = name

    def list_tools(self):
        return [
            {"name": "search_papers", "description": "Searches for academic papers related to a topic."},
            {"name": "fetch_author_info", "description": "Fetches author details from citation databases."}
        ]


# Initialize PromptConstructor (matches your constructor exactly)
research_prompt = PromptConstructor(
    role="You are an AI Research Foresight Agent specializing in identifying emerging academic trends.",
    task_description=(
        "Analyze a given seminal paper and its related recent works to identify underexplored future research directions. "
        "Each identified area should be novel, have strong potential, and reflect diversity across types of innovation."
    ),
    output_requirements=(
        "Generate a list of at least 10 distinct future research areas, each with rationale. "
        "Include novelty, potential impact, and diversity of directions."
    ),
    format_description="Numbered list with titles and short rationales (2–4 sentences each).",
    input_fields={
        "seminal_paper": Field(str, "Details of a key foundational paper (title, abstract, DOI, contributions)."),
        "recent_citing_papers": Field(list, "A list of recent papers citing or extending the seminal paper."),
    },
    output_fields={
        "future_research_areas": Field(list, "List of at least 10 distinct future research areas, each with rationale."),
        "potential_authors": Field(list, "Optional section listing relevant authors for each area."),
    },
)

# Add tools: local function + MCP connector
dummy_mcp = DummyMCP("exa_demo_mcp")
research_prompt.parse_func(summarize_text)
research_prompt.parse_mcp(dummy_mcp)

# Render prompt
print("=== Rendered Prompt ===\n")
print(research_prompt.render_prompt())

# Summary of what’s included
print("\n=== Prompt Summary ===\n")
print(research_prompt.summary())
