import inspect
from typing import Callable, Dict, Any
from pydantic import BaseModel, PrivateAttr, Field
from jinja2 import Template

class PromptField(BaseModel):
    """
    Represents a single field in the prompt or tool specification.
    
    Attributes:
        name (str): Name of the field.
        type (Any): Python type hint for the field (e.g., str, int).
        desc (str): Optional description of what the field represents.
    """
    name: str
    type: Any
    desc: str = ""

class FunctionTool(BaseModel):
    """
    Represents a tool (Python function) that can be used in the prompt.

    Attributes:
        name (str): Name of the tool (usually the function name).
        fields (Dict[str, PromptField]): Dictionary of input fields for the tool.
        description (str): Short description of the tool (from docstring).
    """
    name: str
    fields: Dict[str, PromptField] = Field(default_factory=dict)
    description: str = ""

class PromptConstructor(BaseModel):
    """
    Constructs structured prompts for LLMs with tools and input/output specifications.

    Attributes:
        prompt_desc (str): General description of what the prompt should accomplish.
        prompt_name (str): Optional name for the prompt.
        rules (str): Optional additional rules to include in the prompt.
        input_fields (Dict[str, PromptField]): Fields the LLM expects as input.
        output_fields (Dict[str, PromptField]): Fields the LLM should output.
        tools (Dict[str, FunctionTool]): Tools (functions) available for the LLM.
        template_str (str): Cached template string.
    """
    prompt_name: str = Field("DefaultPrompt", description = "A name for the prompt instance we created")
    prompt_command:str = Field("No particular command", description = "added command to be added into builtin")
    input_fields: Dict[str, PromptField] = Field(default_factory=dict, description = "  ")
    output_fields: Dict[str, PromptField] = Field(default_factory=dict)
    _tools: Dict[str, FunctionTool] = PrivateAttr(default_factory=dict)
    template_str: str = ""

    def parse_func(self, func: Callable):
        """
        Parse a Python function and register it as a tool for the prompt.

        Each function parameter becomes an input field. The function's return type
        becomes an output field. The function's docstring is used as tool description.

        Args:
            func (Callable): Python function to register as a tool.

        Example:
            def add(a: int, b: int) -> int:
                "Adds two numbers."
                return a + b

            pc.parse_func(add)
        """
        sig = inspect.signature(func)
        self.input_fields = {}
        self.output_fields = {}

        # Collect input parameters
        tool_fields = {}
        for name, param in sig.parameters.items():
            annotation = param.annotation if param.annotation != inspect._empty else str
            field = PromptField(name=name, type=annotation)
            self.input_fields[name] = field
            tool_fields[name] = field

        # Register tool
        func_doc = func.__doc__ or "No description"
        self._tools[func.__name__] = FunctionTool(
            name=func.__name__,
            fields=tool_fields,
            description=func_doc.strip()
        )

        # Set output field
        return_annotation = sig.return_annotation if sig.return_annotation != inspect._empty else str
        self.output_fields["result"] = PromptField(name="result", type=return_annotation)

    def _build_template(self) -> str:
        """
        Build a structured prompt template string including inputs, outputs, and tools.

        Returns:
            str: The constructed prompt template.
        """
        lines = [f"Prompt Name: {self.prompt_name}", ""]
        lines.append(f"### Description: \n {self.prompt_command}")
        
        # Inputs section
        lines.append("\nInputs:")
        for f in self.input_fields.values():
            lines.append(f"- {f.name} ({f.type.__name__}) - {f.desc}")

        # Outputs section
        lines.append("\nOutputs:")
        for f in self.output_fields.values():
            lines.append(f"- {f.name} ({f.type.__name__}) - {f.desc}")

        # Tools section
        if self._tools:
            lines.append("\n" + "*"*50)
            lines.append("TOOLS AVAILABLE")
            lines.append("*"*50)
            for tool_name, tool in self._tools.items():
                lines.append(f"[Tool] {tool_name} - {tool.description}")
                for f in tool.fields.values():
                    lines.append(f"   Param: {f.name} ({f.type.__name__}) - {f.desc}")
            lines.append("*"*50)
            lines.append(
                'Always output tool usage in this format: \n'
                '{"func_name": "function_name", "params": [param1, param2]}\n'
                'Do not output lists inside lists. Do not write function call syntax.'
            )

        self.template_str = "\n".join(lines)
        return self.template_str

    def render_prompt(self, **kwargs) -> str:
        """
        Render the prompt template using Jinja2 with actual input values.

        Args:
            **kwargs: Key-value pairs corresponding to input fields.

        Returns:
            str: Rendered prompt string with values inserted.
        """
        if not self.template_str:
            self._build_template()
        template = Template(self.template_str)
        return template.render(**kwargs)

    def giveInput(self, name: str, desc: str = "", type_hint: Any = str):
        """
        Add or update an input field.

        Args:
            name (str): Name of the input variable.
            desc (str): Description of the input field.
            type_hint (Any): Python type of the input.
        """
        if name in self.input_fields:
            self.input_fields[name].desc = desc
            self.input_fields[name].type = type_hint
        else:
            self.input_fields[name] = PromptField(name=name, type=type_hint, desc=desc)

    def giveOutput(self, name: str, desc: str = "", type_hint: Any = str):
        """
        Add or update an output field.

        Args:
            name (str): Name of the output variable.
            desc (str): Description of the output field.
            type_hint (Any): Python type of the output.
        """
        if name in self.output_fields:
            self.output_fields[name].desc = desc
            self.output_fields[name].type = type_hint
        else:
            self.output_fields[name] = PromptField(name=name, type=type_hint)
    
