import inspect
from typing import Callable, Dict, Any
from pydantic import BaseModel, Field
from jinja2 import Template

class PromptField(BaseModel):
    name: str
    type: Any
    desc: str = ""

class FunctionTool(BaseModel):
    name: str
    fields: Dict[str, PromptField] = Field(default_factory=dict)
    description: str = ""

class PromptConstructor(BaseModel):
    prompt_desc: str
    process_type: str
    prompt_name: str = "DefaultPrompt"

    input_fields: Dict[str, PromptField] = Field(default_factory=dict)
    output_fields: Dict[str, PromptField] = Field(default_factory=dict)
    tools: Dict[str, FunctionTool] = Field(default_factory=dict)
    template_str: str = ""

    def parse_func(self, func: Callable):
        """
        Parse a Python function and add it as a tool with inputs.
        Each parameter becomes an input field.
        Capture the function's docstring as tool description.
        """
        sig = inspect.signature(func)
        self.input_fields = {}
        self.output_fields = {}
        
        tool_fields = {}
        for name, param in sig.parameters.items():
            annotation = param.annotation if param.annotation != inspect._empty else str
            field = PromptField(name=name, type=annotation)
            self.input_fields[name] = field
            tool_fields[name] = field

        # Add tool
        func_doc = func.__doc__ or "No description"
        self.tools[func.__name__] = FunctionTool(
            name=func.__name__,
            fields=tool_fields,
            description=func_doc.strip()
        )

        # Output field
        return_annotation = sig.return_annotation if sig.return_annotation != inspect._empty else str
        self.output_fields["result"] = PromptField(name="result", type=return_annotation)

    def build_template(self):
        lines = [f"Prompt Name: {self.prompt_name}", f"Process Type: {self.process_type}", ""]
        lines.append(f"Description: {self.prompt_desc}")

        # Inputs
        lines.append("\nInputs:")
        for f in self.input_fields.values():
            lines.append(f"- {f.name} ({f.type.__name__})")

        # Outputs
        lines.append("\nOutputs:")
        for f in self.output_fields.values():
            lines.append(f"- {f.name} ({f.type.__name__})")

        # Tools section
        if self.tools:
            lines.append("\n" + "*"*50)
            lines.append("TOOLS AVAILABLE")
            lines.append("*"*50)
            for tool_name, tool in self.tools.items():
                lines.append(f"[Tool] {tool_name} - {tool.description}")
                for f in tool.fields.values():
                    lines.append(f"   Param: {f.name} ({f.type.__name__})")
            lines.append("*"*50)
            lines.append('Sample Output of tools: {"func_name": "function_name", "params": [param1, param2]}')

        self.template_str = "\n".join(lines)
        return self.template_str

    def render_prompt(self, **kwargs) -> str:
        if not self.template_str:
            self.build_template()
        template = Template(self.template_str)
        return template.render(**kwargs)
    def giveInput(self, name: str, desc: str = "", type_hint: Any = str):
        """
        Add or update an input field.
        :param name: Name of the input variable
        :param desc: Description of the input
        :param type_hint: Python type of the input (default: str)
        """
        if name in self.input_fields:
            # Update description and type if already exists
            self.input_fields[name].desc = desc
            self.input_fields[name].type = type_hint
        else:
            # Create new input field
            self.input_fields[name] = PromptField(name=name, type=type_hint, desc=desc)

    def giveOutput(self, name: str, desc: str = "", type_hint: Any = str):
        """
        Add or update an output field.
        :param name: Name of the output variable
        :param desc: Description of the output
        :param type_hint: Python type of the output (default: str)
        """
        if name in self.output_fields:
            self.output_fields[name].desc = desc
            self.output_fields[name].type = type_hint
        else:
            self.output_fields[name] = PromptField(name=name, type=type_hint, desc=desc)

# ===== Example usage =====

def agent_webscraping(url: str, max_pages: int = 1) -> str:
    """Scrape the content of a webpage given its URL and optional maximum pages."""
    return "dummy result"

def addition(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

if __name__ == "__main__":
    pc = PromptConstructor(
        prompt_desc="Use only ONE tool to process the given link and return results",
        process_type="WebScrapingTask",
        prompt_name="WebScraperPrompt"
    )

    # Automatically parse your function as a tool
    pc.parse_func(agent_webscraping)

    # Build and print template
    template_text = pc.build_template()
    print(template_text)

    # Render prompt with actual inputs
    rendered_prompt = pc.render_prompt(url="https://www.example.com", max_pages=2)
    print("\n=== Rendered Prompt ===\n", rendered_prompt)
