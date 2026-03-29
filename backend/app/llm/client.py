from __future__ import annotations

from app.llm.providers.anthropic_provider import AnthropicProvider
from app.llm.providers.mock_provider import MockProvider
from app.llm.providers.openai_provider import OpenAIProvider


class LlmClient:
    def __init__(self, provider_name: str, model_name: str) -> None:
        provider_name = provider_name.lower()
        if provider_name == "openai":
            self.provider = OpenAIProvider(model_name=model_name)
        elif provider_name == "anthropic":
            self.provider = AnthropicProvider(model_name=model_name)
        else:
            self.provider = MockProvider(model_name=model_name)

    @property
    def model_name(self) -> str:
        return self.provider.model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return self.provider.generate(system_prompt=system_prompt, user_prompt=user_prompt)
