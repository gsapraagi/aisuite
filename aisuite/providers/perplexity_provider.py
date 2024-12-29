import os
import requests
from aisuite.provider import Provider, LLMError
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ChatCompletionMessage:
    content: str = ""
    role: str = "assistant"

@dataclass
class ChatCompletionChoice:
    message: ChatCompletionMessage = field(default_factory=lambda: ChatCompletionMessage())
    finish_reason: Optional[str] = None
    index: int = 0

@dataclass
class ChatCompletionResponse:
    choices: List[ChatCompletionChoice] = field(default_factory=lambda: [ChatCompletionChoice()])
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'ChatCompletionResponse':
        """Create a ChatCompletionResponse from an API response."""
        instance = cls()
        choice = response["choices"][0]
        instance.choices[0].message.content = choice["message"]["content"]
        instance.choices[0].message.role = choice["message"]["role"]
        instance.choices[0].finish_reason = choice["finish_reason"]
        instance.choices[0].index = choice["index"]
        return instance

class PerplexityProvider(Provider):
    BASE_URL = 'https://api.perplexity.ai/chat/completions'
    DEFAULT_MODEL = "llama-3.1-sonar-large-128k-online"
    
    def __init__(self, **config):
        api_key = config.get("api_key") or os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError(
                "Perplexity API key is missing. Please provide it in the config or set the PERPLEXITY_API_KEY environment variable."
            )

        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    @property
    def default_model(self) -> str:
        return self.DEFAULT_MODEL

    def chat_completions_create(self, model, messages, **kwargs):
        kwargs.setdefault("temperature", 0.75)
        kwargs.setdefault("max_tokens", 8000)

        try:
            response = requests.post(
                self.BASE_URL, 
                headers=self.headers, 
                json={"model": model, "messages": messages, **kwargs}
            )
            response.raise_for_status()
            return ChatCompletionResponse.from_api_response(response.json())
        except requests.exceptions.HTTPError as e:
            raise LLMError(f"An error occurred: {e.response.text}") from e
