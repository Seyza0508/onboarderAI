from __future__ import annotations

import httpx

from app.core.config import settings


class AnthropicProvider:
    def __init__(self, model_name: str, api_key: str) -> None:
        self.model_name = model_name
        self.api_key = api_key

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "max_tokens": 500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        with httpx.Client(timeout=settings.llm_request_timeout_seconds) as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        content = data.get("content", [])
        if not content:
            return "No response content returned by Anthropic."
        return content[0].get("text", "")
