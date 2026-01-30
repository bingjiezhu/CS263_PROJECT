"""Provider configuration helpers for Gemini, Ollama, and manual modes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

from .openai_compat import ManualClient, OpenAICompatClient


@dataclass
class ProviderConfig:
    """Resolved provider settings used by both OpenAI SDK and FinRobot."""

    provider: str
    base_url: str
    api_key: str
    model: str


def load_provider_config(cfg: Dict[str, Any]) -> ProviderConfig:
    """Build a ProviderConfig from YAML config + environment variables."""
    provider = cfg.get("provider", "gemini")
    base_url = cfg.get("base_url")
    model = cfg.get("model")

    if provider == "gemini":
        env_name = cfg.get("gemini_api_key_env", "GEMINI_API_KEY")
        api_key = os.environ.get(env_name, "").strip()
        if not api_key:
            raise ValueError(
                f"Missing Gemini API key. Please set env {env_name} or update config."
            )
        if not base_url:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    elif provider == "ollama":
        api_key = "ollama"
        if not base_url:
            base_url = "http://localhost:11434/v1/"
    elif provider == "manual":
        api_key = "manual"
        if not base_url:
            base_url = "manual"
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    if not model:
        raise ValueError("Model name must be specified in config")

    return ProviderConfig(provider=provider, base_url=base_url, api_key=api_key, model=model)


def make_openai_client(pcfg: ProviderConfig, timeout: int = 60) -> OpenAICompatClient:
    """Create a compatible client (manual or OpenAI SDK)."""
    if pcfg.provider == "manual":
        return ManualClient(base_url=pcfg.base_url, api_key=pcfg.api_key, timeout=timeout)
    return OpenAICompatClient(base_url=pcfg.base_url, api_key=pcfg.api_key, timeout=timeout)


def make_autogen_config(
    pcfg: ProviderConfig, temperature: float = 0.0, max_tokens: int | None = None
) -> Dict[str, Any]:
    """Build an AutoGen LLM config from the resolved provider settings."""
    config = {
        "config_list": [
            {
                "model": pcfg.model,
                "api_key": pcfg.api_key,
                "base_url": pcfg.base_url,
            }
        ],
        "temperature": temperature,
    }
    if max_tokens is not None:
        config["max_tokens"] = max_tokens
    return config
