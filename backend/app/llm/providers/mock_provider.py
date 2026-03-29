from __future__ import annotations


class MockProvider:
    def __init__(self, model_name: str = "mock-v1") -> None:
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        del system_prompt
        return f"[Mock LLM Synthesis]\n{user_prompt}"
