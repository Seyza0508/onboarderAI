from __future__ import annotations

import logging

from app.core.config import settings
from app.llm.providers.anthropic_provider import AnthropicProvider
from app.llm.providers.mock_provider import MockProvider
from app.llm.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class LlmClient:
    def __init__(self, provider_name: str, model_name: str, api_key: str | None = None) -> None:
        provider_name = provider_name.lower().strip()
        resolved_api_key = (api_key or "").strip()

        if provider_name == "openai":
            resolved_api_key = resolved_api_key or (settings.openai_api_key or "")
            if resolved_api_key:
                self.provider = OpenAIProvider(model_name=model_name, api_key=resolved_api_key)
                return
            logger.warning("OpenAI provider configured without API key; falling back to mock provider")

        if provider_name == "anthropic":
            resolved_api_key = resolved_api_key or (settings.anthropic_api_key or "")
            if resolved_api_key:
                self.provider = AnthropicProvider(model_name=model_name, api_key=resolved_api_key)
                return
            logger.warning("Anthropic provider configured without API key; falling back to mock provider")

        self.provider = MockProvider(model_name="mock-v1")

    @property
    def model_name(self) -> str:
        return self.provider.model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            return self.provider.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        except Exception as exc:  # pragma: no cover - network/provider failure path
            logger.exception("LLM provider call failed; falling back to mock output: %s", exc)
            fallback = MockProvider(model_name="mock-fallback-v1")
            self.provider = fallback
            return fallback.generate(system_prompt=system_prompt, user_prompt=user_prompt)
