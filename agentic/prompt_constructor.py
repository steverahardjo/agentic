from typing import Callable, Dict, Any, get_type_hints
from pydantic import BaseModel, Field
from jinja2 import Template


class PromptField(BaseModel):
    name: str
    type: Any
    desc: str = ""


class PromptConstructor(BaseModel):
    prompt_name: str
    process_type: str
    tools_expl_str: str = ""

    # Store input/output fields as dict of PromptField, initialized empty
    input_fields: Dict[str, PromptField] = Field(default_factory=dict)
    output_fields: Dict[str, PromptField] = Field(default_factory=dict)

    # You can keep a template string that you build incrementally
    template_str: str = ""

    def parse_func(self, func: Callable, input_descs: Dict[str, str] = {}, output_descs: Dict[str, str] = {}):
        type_hints = get_type_hints(func)
        # Clear previous fields
        self.input_fields = {}
        self.output_fields = {}

        for name, typ in type_hints.items():
            if name == "return":
                # Use 'result' as output field name or you can customize
                output_name = "result"
                self.output_fields[output_name] = PromptField(
                    name=output_name,
                    type=typ,
                    desc=output_descs.get(output_name, "")
                )
            else:
                self.input_fields[name] = PromptField(
                    name=name,
                    type=typ,
                    desc=input_descs.get(name, "")
                )

    def giveInput(self, name: str, desc: str = ""):
        # Add or update input field description, default type is str
        if name in self.input_fields:
            self.input_fields[name].desc = desc
        else:
            self.input_fields[name] = PromptField(name=name, type=str, desc=desc)
    
    def giveOutput(self, name:str, desc:str = ""):
        # Add or update output field description, default type is str
        if name in self.output_fields:
            self.output_fields[name].desc = desc
        else:
            self.output_fields[name] = PromptField(name=name, type=str, desc=desc)

    def build_template(self):
        """
        Build a Jinja2 template string from input fields.
        For example, a simple template could list inputs.
        """
        lines = [f"Process type: {self.process_type}", f"Prompt name: {self.prompt_name}", ""]
        lines.append("Inputs:")
        for f in self.input_fields.values():
            lines.append(f"- {f.name} ({f.type.__name__}): {f.desc}")
        lines.append("")
        lines.append("Outputs:")
        for f in self.output_fields.values():
            lines.append(f"- {f.name} ({f.type.__name__}): {f.desc}")

        # You can customize the template string further or load from external source
        self.template_str = "\n".join(lines)
        return self.template_str

    def render_prompt(self, **kwargs) -> str:
        """
        Render the built template with given input values (kwargs).
        """
        if not self.template_str:
            self.build_template()

        template = Template(self.template_str)
        return template.render(**kwargs)
    
    def load_jpg(self, file_path: str):
        """
        Placeholder for loading a JPG file.
        This could be extended to actually read and process the image.
        """
        template_str = """
        <!DOCTYPE html>
        <html>
        <head><title>Image Example</title></head>
        <body>
        <h1>Here is your image:</h1>
        <img src="{{ image_url }}" alt="Image" />
        </body>
        </html>
        """
        template = Template(template_str)
        return template.render(image_url=file_path) 


# Example usage:

def example_function(name: str, age: int) -> bool:
    """Dummy example function"""
    return age > 18


if __name__ == "__main__":
    pc = PromptConstructor(prompt_name="ExamplePrompt", process_type="CheckAge")
    pc.parse_func(example_function, input_descs={"name": "Person's name", "age": "Person's age"},
                  output_descs={"result": "Is person adult?"})

    pc.giveInput("location", "Person's location")

    print(pc.build_template())

    prompt_text = pc.render_prompt(name="Steve", age=25, location="Malaysia")
    print("\nRendered Prompt:\n", prompt_text)
