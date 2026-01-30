"""Prompt templates for baseline and FinRobot agent roles."""

from __future__ import annotations

from typing import List, Optional

# Baseline system instruction kept short to avoid distracting the model.
BASELINE_SYSTEM = (
    "You are a careful financial reasoning assistant. "
    "Answer using only the given question and choices. "
    "Do not use external tools or knowledge bases."
)

BASELINE_USER_TEMPLATE = """Question:
{question}

{context_block}{choices_block}

Answer format: {answer_format}
Return only the answer. No explanation.
"""

# Closed-book role prompts for the minimal agent setting.
PLANNER_SYSTEM = (
    "Role: Planner. Create a short plan, then hand off to the Solver. "
    "Closed-book: use only the given question/choices/context. "
    "Do NOT call external tools or data sources."
)

SOLVER_SYSTEM = (
    "Role: Solver. Provide reasoning and propose a final answer letter. "
    "Closed-book: use only the given question/choices/context."
)

CRITIC_SYSTEM = (
    "Role: Critic. Check the solver's reasoning, find mistakes, and if needed propose a correction. "
    "Closed-book: use only the given question/choices/context."
)

FINAL_SYSTEM = (
    "Role: Final. Decide the single best answer letter based on prior steps. "
    "Return exactly two lines: 'Answer: <LABEL>' and 'TERMINATE'."
)

# Tool-enabled prompts used when full FinRobot mode is requested.
PLANNER_SYSTEM_FULL = (
    "Role: Planner. Create a short plan, decide whether tools are needed, then hand off to the Solver. "
    "You MAY call tools if they help answer the question."
)

SOLVER_SYSTEM_FULL = (
    "Role: Solver. Provide reasoning and propose a final answer letter. "
    "You MAY call tools if they help answer the question."
)

CRITIC_SYSTEM_FULL = (
    "Role: Critic. Check the solver's reasoning, find mistakes, and if needed propose a correction. "
    "You MAY call tools if they help validate the answer."
)

FINAL_SYSTEM_FULL = (
    "Role: Final. Decide the single best answer letter based on prior steps. "
    "Return exactly two lines: 'Answer: <LABEL>' and 'TERMINATE'."
)


def format_choices(choices: Optional[List[str]]) -> str:
    """Format a multiple-choice list as labeled lines."""
    if not choices:
        return ""
    lines = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, c in enumerate(choices):
        tag = letters[i] if i < len(letters) else str(i)
        lines.append(f"{tag}. {c}")
    return "Choices:\n" + "\n".join(lines)


def build_user_prompt(question: str, choices: Optional[List[str]], context: Optional[str] = None) -> str:
    """Build the base user prompt used by baseline and agent roles."""
    choices_block = format_choices(choices)
    if choices_block:
        choices_block += "\n"
    context_block = ""
    if context:
        context_block = f"Context:\n{context}\n\n"
    answer_format = "A/B/C/D" if choices and len(choices) <= 4 else "LETTER"
    if not choices:
        answer_format = "LABEL"
    return BASELINE_USER_TEMPLATE.format(
        question=question,
        context_block=context_block,
        choices_block=choices_block,
        answer_format=answer_format,
    ).strip()


def build_agent_prompt(
    question: str,
    choices: Optional[List[str]],
    context: Optional[str] = None,
    strict: bool = False,
) -> str:
    """Build a stricter agent prompt that enumerates valid labels."""
    base = build_user_prompt(question, choices, context)
    if not choices:
        return base + "\n\nReturn only the label."
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    valid = ", ".join(list(letters[: len(choices)]))
    if strict:
        return base + f"\n\nValid labels: {valid}\nReturn exactly two lines:\nAnswer: <LABEL>\nTERMINATE"
    return base + f"\n\nValid labels: {valid}\nReturn only one label."
