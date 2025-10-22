# Copyright 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PromptConstructor: ADK-style structured prompt generator with parsing support."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Union
from jinja2 import Template


# ---------------------------------------------------------------------
# Field representation
# ---------------------------------------------------------------------
@dataclass
class Field:
    """Represents a single input or output field."""
    name: str
    type: Any = str
    desc: str = ""
    example: Optional[str] = None


# ---------------------------------------------------------------------
# PromptConstructor class
# ---------------------------------------------------------------------
class PromptConstructor:
    """
    Construct and render ADK-compliant prompts.
    Supports FunctionTools and MCPTools through `parse()` and `parse_mcp()`.

    Structure:
      Role:
      Inputs:
      Core Task:
      Output Requirements:
      Format: (optional)
      Resources: (optional)
    """

    def __init__(
        self,
        role: str,
        task_description: str,
        output_requirements: str,
        format_description: str = "",
        input_fields: Optional[Dict[str, Field]] = None,
        output_fields: Optional[Dict[str, Field]] = None,
        resource_tools: Optional[Dict[str, Any]] = None,
        template_str: Optional[str] = None,
    ):
        self.role = role
        self.task_description = task_description
        self.output_requirements = output_requirements
        self.format_description = format_description
        self.input_fields = input_fields or {}
        self.output_fields = output_fields or {}
        self.resource_tools = resource_tools or {}
        self.template_str = template_str

    # -----------------------------------------------------------------
    # Parsing standard callable-based tools
    # -----------------------------------------------------------------
    def parse_func(self, funcs: Optional[List[Any]] = None) -> None:
        """
        Parse standard Python callables into FunctionTool-like entries.
        Each callable is expected to have a __name__, __doc__, and type hints.
        """
        if not funcs:
            return

        for fn in funcs:
            fn_name = getattr(fn, "__name__", "unknown_func")
            fn_desc = (fn.__doc__ or "").strip()
            fields = {}

            # Extract type hints for parameters
            annotations = getattr(fn, "__annotations__", {})
            for name, typ in annotations.items():
                if name == "return":
                    continue
                fields[name] = Field(name=name, type=typ, desc="")

            self.resource_tools[fn_name] = {
                "name": fn_name,
                "description": fn_desc,
                "fields": fields
            }

    # -----------------------------------------------------------------
    # Parsing MCP-based tools
    # -----------------------------------------------------------------
    def parse_mcp(self, mcps: Optional[List[Any]] = None) -> None:
        """
        Parse MCPTools (multi-call protocol tools).
        Expected attributes: name, description, fields (dict of Field-like items).
        """
        if not mcps:
            return

        for mcp in mcps:
            tool_name = getattr(mcp, "name", "unknown_mcp")
            tool_desc = getattr(mcp, "description", "")
            tool_fields = getattr(mcp, "fields", {})

            self.resource_tools[tool_name] = {
                "name": tool_name,
                "description": tool_desc,
                "fields": tool_fields
            }

    # -----------------------------------------------------------------
    # Render ADK-structured prompt
    # -----------------------------------------------------------------
    def render_prompt(self) -> str:
        """
        Render the ADK-structured prompt using Jinja2.
        """

        default_template = Template("""
Role: {{ role }}

Inputs:
{% if inputs %}
{% for field in inputs.values() %}
{{ field.name }}: {{ field.desc }}{% if field.example %} (e.g., {{ field.example }}){% endif %}
{{ "{{" }}{{ field.name }}{{ "}}" }}
{% endfor %}
{% else %}
(No structured inputs specified.)
{% endif %}

Core Task:
{{ task_description }}

Output Requirements:
{{ output_requirements }}

{% if format_description %}
Format:
{{ format_description }}
{% endif %}

{% if outputs %}
Expected Outputs:
{% for field in outputs.values() %}
- {{ field.name }} ({{ field.type.__name__ }}): {{ field.desc }}
{% endfor %}
{% endif %}

{% if tools %}
Resources:
{% for tool in tools.values() %}
- {{ tool.name }}: {{ tool.description }}
  {% if tool.fields %}
  Parameters:
  {% for field in tool.fields.values() %}
    - {{ field.name }} ({{ field.type.__name__ }}): {{ field.desc }}
  {% endfor %}
  {% endif %}
{% endfor %}
{% endif %}
""")

        tmpl = Template(self.template_str) if self.template_str else default_template

        return tmpl.render(
            role=self.role,
            inputs=self.input_fields,
            outputs=self.output_fields,
            task_description=self.task_description,
            output_requirements=self.output_requirements,
            format_description=self.format_description,
            tools=self.resource_tools
        ).strip()
