from typing import List, Optional
from pydantic import BaseModel
from jinja2 import Template
from agentic.Tooling import BaseTooling
    
class PromptConstructor(BaseModel):
    """
    Constructs structured prompts for language model agents.
    """
    model_config = {"arbitrary_types_allowed": True}
    task_description: str
    input_schema: List[str]
    output_schema: Optional[str]
    constraints: Optional[str] = ""
    tools_allowed: List[BaseTooling] = None
    system_prompt: str = ""
    user_prompt: str = ""

    def construct_prompt(self) -> Template:
        """
        Constructs a static Jinja2 template for the LLM prompt.
        """
        input_schema_str = ", ".join(self.input_schema)

        # Inject tool capabilities as prompt text (if any)
        tool_descriptions = ""
        if self.tools_allowed is not None:
            tool_descriptions = "\n".join(
                t.inject_prompt() for t in self.tools_allowed
            )
        template_text = f"""
Give me {self.task_description}

Outlined in here:
question: {input_schema_str}
answer: {self.output_schema or "None"}
the result should be in this format of: {self.constraints or "Free-form"}

################
Background Knowledge you need to use:
{{{{ memory }}}}
################
Tool you can use:
{{{{ tooling_desc }}}}

Tool Descriptions:
{tool_descriptions}

################
Input: {{{{ user_command }}}}
"""
        return Template(template_text)

    def get_toolList(self, tools:List[BaseTooling])->None:
        self.tools_allowed = tools

    def fill_prompt(self, input: str, memory: Optional[str] = "") -> str:
        """
        Renders the Jinja2 template using actual values.
        """
        template = self.construct_prompt()
        tool_desc = "\n".join(t.tooling_name for t in (self.tools_allowed or []))

        rendered = template.render(
            user_command=input.strip(),
            memory=memory or "",
            tooling_desc=tool_desc.strip()
        )
        self.user_prompt = rendered
        return self.user_prompt

    def format_openai(self):
        return [
            {"role":"system", "content": self.system_prompt},
            {"role":"assistant", "content":self.user_prompt}
        ]
    def inject_tools(self)->List[dict]|None:
        lst=[]
        if self._tools_allowed is not None:
            for x in self._tools_allowed:
                lst.append(x.openai_toolcall())
            return lst
        else:
            return None
        
