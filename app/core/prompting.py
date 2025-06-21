from pydantic import BaseModel
from typing import Dict, Any
from copy import deepcopy


class PromptPayload(BaseModel):
    """Payload for prompt processing containing template key, output format, and inputs."""
    
    prompt_key: str
    output_format: BaseModel
    inputs: Dict[str, Any]


class PromptTemplate:
    """Template for structured prompts with instructions and variable substitution."""
    
    def __init__(self, name: str, instructions: str, prompt: str) -> None:
        """Initialize a prompt template.
        
        Args:
            name: Template identifier
            instructions: Instructions for the model
            prompt: Prompt template with placeholders
        """
        self.name = name
        self.instructions = instructions.strip()
        self.prompt = prompt.strip()

    def render(self, **kwargs) -> "PromptTemplate":
        """Render the template with provided variables.
        
        Args:
            **kwargs: Variables to substitute in the prompt
            
        Returns:
            New template instance with rendered prompt
        """
        rendered = deepcopy(self)
        rendered.prompt = self.prompt.format(**kwargs)
        return rendered


class PromptRunner:
    """Runner for executing prompts using OpenAI client."""
    
    def __init__(self, client, model: str) -> None:
        """Initialize the prompt runner.
        
        Args:
            client: OpenAI client instance
            model: Model name to use for generation
        """
        self.client = client
        self.model = model

    def generate(self, template: PromptTemplate, output_format: BaseModel, **inputs) -> Any:
        """Generate response using a prompt template.
        
        Args:
            template: Prompt template to use
            output_format: Expected output format
            **inputs: Variables for template rendering
            
        Returns:
            Parsed response in the specified format
        """
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
    """Processor for handling prompt templates and generation."""
    
    def __init__(self, generator: PromptRunner, templates: Dict[str, PromptTemplate]) -> None:
        """Initialize the prompt processor.
        
        Args:
            generator: Prompt runner instance
            templates: Dictionary of available templates
        """
        self.generator = generator
        self.templates = templates

    def process(self, payload: PromptPayload) -> Any:
        """Process a prompt payload using the appropriate template.
        
        Args:
            payload: Prompt payload containing template key and inputs
            
        Returns:
            Generated response
        """
        template = self.templates[payload.prompt_key]
        return self.generator.generate(template, payload.output_format, **payload.inputs)

            
