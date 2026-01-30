"""Baseline (non-agent) inference that uses a single LLM call per example."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from data.schema import TaskExample
from llm.openai_compat import OpenAICompatClient
from llm.parsing import extract_choice, extract_label
from systems.prompts import BASELINE_SYSTEM, build_user_prompt
from utils.cache import DiskCache, make_cache_key


def _predict_one(
    example: TaskExample,
    client: OpenAICompatClient,
    model: str,
    temperature: float,
    cache: Optional[DiskCache] = None,
) -> Dict[str, Any]:
    """Run a single-shot prediction with optional caching."""
    user_prompt = build_user_prompt(example.question, example.choices, example.context)
    messages = [
        {"role": "system", "content": BASELINE_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    cache_key = None
    if cache is not None:
        cache_key = make_cache_key({"model": model, "messages": messages, "temperature": temperature})
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    content, _ = client.chat(model=model, messages=messages, temperature=temperature)

    # Choose the parsing strategy based on whether we have explicit choices.
    if example.choices:
        pred = extract_choice(content, example.choices) or "INVALID"
    else:
        pred = extract_label(content) or "INVALID"

    record = {
        "id": example.id,
        "task_type": example.task_type,
        "question": example.question,
        "choices": example.choices,
        "label": example.label,
        "prediction": pred,
        "correct": pred == example.label,
        "raw_response": content,
        "meta": example.meta or {},
    }

    if cache is not None and cache_key is not None:
        cache.set(cache_key, record)

    return record


def run_baseline(
    examples: List[TaskExample],
    client: OpenAICompatClient,
    model: str,
    temperature: float = 0.0,
    cache: Optional[DiskCache] = None,
) -> List[Dict[str, Any]]:
    """Run the baseline on a list of examples."""
    outputs = []
    for ex in examples:
        outputs.append(_predict_one(ex, client, model, temperature, cache=cache))
    return outputs
