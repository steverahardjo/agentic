from typing import Optional, Callable, Any
from functools import wraps
import json

class BaseTooling:
    def __init__(
        self,
        tooling_id: str,
        tooling_name: str,
        output_struct: str,
        description: Optional[str] = None,
        input_schema: Optional[dict] = None,
        fn: Optional[Callable] = None,
        tags: Optional[list[str]] = None,
    ):
        self.tooling_id = tooling_id
        self.tooling_name = tooling_name
        self.output_struct = output_struct
        self.description = description or tooling_name
        self.input_schema = input_schema or {}
        self.fn = fn
        self.tags = tags or []

    def run(self, func_call = str) -> Any:
        inputs =json.loads(func_call["arguments"]) 
        if self.fn is None:
            raise RuntimeError("No function connected to this tooling.")
        for key in self.input_schema:
            if key not in inputs:
                raise ValueError(f"Missing input: {key}")
        return self.fn(inputs)

    def inject_prompt(self) -> str:
        return (
            f"{self.tooling_name}: {self.description}\n"
            f"Input schema: {self.input_schema}\n"
            f"Output schema: {self.output_struct}"
        )

    def as_dict(self):
        return {
            "tooling_id": self.tooling_id,
            "tooling_name": self.tooling_name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_struct": self.output_struct,
            "tags": self.tags,
            "fn_name": self.fn.__name__ if self.fn else None,
        }

    def openai_toolcall(self) -> dict:
        return {
        "type": "function", 
        "name": self.tooling_id,
        "description": self.description,
        "parameters": {
            "type": "object",
            "properties": {
                key: {
                    "type": self.input_schema[key].get("type", "string"),
                    "description": self.input_schema[key].get("description", ""),
                }
                for key in self.input_schema
            },
            "required": list(self.input_schema.keys()),
            "additionalProperties": False
            },
        }

    @staticmethod
    def from_dict(data: dict, fn_registry: Optional[dict] = None):
        if fn_registry is None:
            fn_registry = {}

        fn = None
        if "fn_name" in data and data["fn_name"]:
            fn = fn_registry.get(data["fn_name"])
            if fn is None:
                raise ValueError(f"Function '{data['fn_name']}' not found in registry.")

        return BaseTooling(
            tooling_id=data["tooling_id"],
            tooling_name=data["tooling_name"],
            description=data.get("description"),
            input_schema=data.get("input_schema", {}),
            output_struct=data.get("output_struct", "Unknown"),
            fn=fn,
            tags=data.get("tags", []),
        )

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

TOOL_REGISTRY = {}

def tooling(
    tooling_id: str,
    tooling_name: str,
    output_struct: str,
    description: str = None,
    input_schema: dict = None,
    tags: list[str] = None,
):
    def decorator(fn):
        tool = BaseTooling(
            tooling_id=tooling_id,
            tooling_name=tooling_name,
            output_struct=output_struct,
            description=description,
            input_schema=input_schema,
            fn=fn,
            tags=tags,
        )
        TOOL_REGISTRY[tooling_id] = tool

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.tool = tool
        return wrapper
    return decorator
