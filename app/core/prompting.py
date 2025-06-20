from pydantic import BaseModel
from typing import Dict, Any
from copy import deepcopy
from typing import Dict

class PromptPayload(BaseModel):
    prompt_key: str
    output_format: BaseModel
    inputs: Dict[str, Any]


class PromptTemplate:
    def __init__(self, name: str, instructions: str, prompt: str):
        self.name = name
        self.instructions = instructions.strip()
        self.prompt = prompt.strip()

    def render(self, **kwargs) -> "PromptTemplate":
        rendered = deepcopy(self)
        rendered.prompt = self.prompt.format(**kwargs)
        return rendered



class PromptRunner:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def generate(self, template: PromptTemplate, output_format: BaseModel, **inputs) -> Any:
        rendered = template.render(**inputs)

        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=rendered.instructions,
                input=rendered.prompt,
                text_format=output_format
            )
            return response.output_parsed

        except Exception as e:
            print(f"[GENERATION ERROR] Template: '{template.name}' | Error: {e}")
            return {}


class PromptProcessor:
    def __init__(self, generator: PromptRunner, templates: Dict[str, PromptTemplate]):
        self.generator = generator
        self.templates = templates

    def process(self, payload: PromptPayload) -> Any:
        template = self.templates[payload.prompt_key]
        return self.generator.generate(template, payload.output_format, **payload.inputs)

            
