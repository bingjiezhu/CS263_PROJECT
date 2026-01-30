"""Parsing helpers for extracting labels from LLM outputs."""

from __future__ import annotations

import re
from typing import List, Optional

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _strip_fences(text: str) -> str:
    """Remove Markdown code fences so parsing is more robust."""
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\n?", "", text)
        text = re.sub(r"```$", "", text).strip()
    return text


def extract_choice(text: str, choices: Optional[List[str]] = None) -> Optional[str]:
    """Extract a multiple-choice letter from a free-form response."""
    if not text:
        return None
    text = _strip_fences(text)
    upper = text.upper()

    # Compute the allowed letter set from the choices if provided.
    allowed_letters = list(LETTERS[: len(choices)]) if choices else list(LETTERS)

    # Look for explicit markers like "FINAL: A" or "ANSWER: B".
    m = re.search(r"(?:FINAL|ANSWER)\s*[:\-]?\s*([A-Z])\b", upper)
    if m:
        letter = m.group(1)
        if letter in allowed_letters:
            return letter

    # Fallback to any isolated letter token in the output.
    matches = re.findall(r"\b([A-Z])\b", upper)
    for letter in matches:
        if letter in allowed_letters:
            return letter

    # As a final fallback, match choice text in the output.
    if choices:
        for i, choice in enumerate(choices):
            if choice and choice.lower() in text.lower():
                return LETTERS[i] if i < len(LETTERS) else str(i)
    return None


def extract_choice_strict(text: str, choices: Optional[List[str]] = None) -> Optional[str]:
    """Extract a multiple-choice letter with stricter formatting rules."""
    if not text:
        return None
    text = _strip_fences(text).strip()
    upper = text.upper()

    allowed_letters = list(LETTERS[: len(choices)]) if choices else list(LETTERS)

    # Prefer explicit markers to avoid accidental matches.
    m = re.search(r"(?:FINAL ANSWER|FINAL|ANSWER|CHOICE)\s*[:\-]?\s*([A-Z])\b", upper)
    if m:
        letter = m.group(1)
        if letter in allowed_letters:
            return letter

    # Accept lines that reduce to exactly one allowed letter.
    for line in upper.splitlines():
        cleaned = re.sub(r"[^A-Z]", "", line.strip())
        if len(cleaned) == 1 and cleaned in allowed_letters:
            return cleaned
    return None


def extract_label(text: str, label_set: Optional[List[str]] = None) -> Optional[str]:
    """Extract a label from text, optionally constrained by a label set."""
    if not text:
        return None
    text = _strip_fences(text).strip()
    if not label_set:
        return text
    lower = text.lower()
    for label in label_set:
        if label.lower() in lower:
            return label
    return None
