from typing import Callable, Dict, Any, get_type_hints
from pydantic import BaseModel, Field
from jinja2 import Template


class PromptField(BaseModel):
    name: str
    type: Any
    desc: str = ""


class PromptConstructor(BaseModel):
    system_template = Template()
    prompt_name: str
    process_type: str
    tools_expl_str: str = ""

    def parse_func(self, func: Callable, input_descs: Dict[str, str] = {}, output_descs: Dict[str, str] = {}):
        type_hints = get_type_hints(func)

        for name, typ in type_hints.items():
            if name == 'return':
                # Treat return annotation as output
                self.output_fields[name] = PromptField(
                    name=name,
                    type=typ,
                    desc=output_descs.get(name, "")
                )
            else:
                # Treat all other annotations as input
                self.input_fields[name] = PromptField(
                    name=name,
                    type=typ,
                    desc=input_descs.get(name, "")
                )

    def giveInput(self, name:str, desc:str = ""):
        self.template.add
