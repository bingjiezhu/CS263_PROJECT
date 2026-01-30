"""OpenAI-compat client adapters for Gemini, Ollama, and manual input."""

from __future__ import annotations

import sys
import time
from typing import Any, Dict, List, Optional, Tuple


class OpenAICompatClient:
    """Thin wrapper around the OpenAI SDK using a custom base_url."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        """Initialize an OpenAI-compatible client with custom base_url."""
        self.base_url = base_url
        self.api_key = api_key
        try:
            from openai import OpenAI
            import openai as openai_errors
        except Exception as exc:
            raise ImportError(
                "OpenAI SDK is required. Install with `pip install openai`."
            ) from exc
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
        self._retry_exceptions = (
            openai_errors.APIConnectionError,
            openai_errors.APITimeoutError,
            openai_errors.APIError,
            openai_errors.APIStatusError,
            openai_errors.InternalServerError,
            openai_errors.RateLimitError,
        )

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Tuple[str, Any]:
        """Run a chat completion and return content plus the raw response."""
        attempts = 0
        delay = 1.0
        while True:
            try:
                resp = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                break
            except self._retry_exceptions:
                attempts += 1
                if attempts >= 3:
                    raise
                time.sleep(delay)
                delay *= 2
        content = resp.choices[0].message.content if resp.choices else ""
        return content or "", resp


def _read_multiline() -> str:
    """Collect multiple lines from stdin until a sentinel line is received."""
    lines: List[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


class ManualClient:
    """Manual client for human-in-the-loop runs without an API."""

    def __init__(self, base_url: str = "manual", api_key: str = "manual", timeout: int = 60):
        """Initialize the manual client with a placeholder base_url and key."""
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Tuple[str, Any]:
        """Print the prompt and wait for a human response."""
        print("\n" + "=" * 80)
        print("[MANUAL MODE] Please provide a response. End with a single line: END")
        print("=" * 80)
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            print(f"\n[{role.upper()}]\n{content}")
        print("\n[RESPONSE]")
        response = _read_multiline()
        if not response:
            print("[MANUAL MODE] Empty response received.", file=sys.stderr)
        return response, {"manual": True}
