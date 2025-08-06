from typing import Callable, Dict, Any, get_type_hints
from pydantic import BaseModel, Field


class PromptField(BaseModel):
    name: str
    type: Any
    desc: str = ""


class PromptConstructor(BaseModel):
    prompt_name: str
    process_type: str
    input_fields: Dict[str, PromptField] = {}
    output_fields: Dict[str, PromptField] = {}
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

    def summary(self):
        return {
            "prompt_name": self.prompt_name,
            "type": self.process_type,
            "inputs": {k: v.dict() for k, v in self.input_fields.items()},
            "outputs": {k: v.dict() for k, v in self.output_fields.items()},
        }
          
