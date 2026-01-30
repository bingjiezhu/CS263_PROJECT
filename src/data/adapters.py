"""Adapters that map heterogeneous dataset records into TaskExample objects."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .schema import TaskExample

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _first_present(example: Dict[str, Any], candidates: Iterable[str]) -> Optional[str]:
    """Return the first field name that exists in the example."""
    for key in candidates:
        if key in example and example[key] is not None:
            return key
    return None


def _infer_label_names(features: Any, label_field: str) -> Optional[List[str]]:
    """Infer string labels from HuggingFace dataset features when available."""
    if features is None:
        return None
    try:
        feat = features.get(label_field)
    except Exception:
        feat = None
    if feat is None:
        return None
    names = getattr(feat, "names", None)
    if names:
        return list(names)
    return None


def _normalize_choices(raw_choices: Any) -> Optional[List[str]]:
    """Normalize choices into a list of strings."""
    if raw_choices is None:
        return None
    if isinstance(raw_choices, (list, tuple)):
        return [str(c) for c in raw_choices]
    if isinstance(raw_choices, str):
        # Fallback: split on common separators.
        for sep in ["|", "\n", ";"]:
            if sep in raw_choices:
                return [c.strip() for c in raw_choices.split(sep) if c.strip()]
        return [raw_choices.strip()]
    return None


def _label_to_index(label_val: Any, choices: List[str]) -> Optional[int]:
    """Convert a label value into a choice index."""
    if label_val is None or choices is None:
        return None
    if isinstance(label_val, bool):
        return int(label_val)
    if isinstance(label_val, float) and label_val.is_integer():
        label_val = int(label_val)
    if isinstance(label_val, int):
        if 0 <= label_val < len(choices):
            return label_val
    if isinstance(label_val, str):
        stripped = label_val.strip()
        # Handle letter labels like "A" or "B".
        if len(stripped) == 1 and stripped.isalpha():
            idx = LETTERS.find(stripped.upper())
            if 0 <= idx < len(choices):
                return idx
        # Handle numeric strings.
        if stripped.isdigit():
            idx = int(stripped)
            if 0 <= idx < len(choices):
                return idx
        # Fallback to exact text match.
        lower = stripped.lower()
        for i, c in enumerate(choices):
            if c.lower() == lower:
                return i
    return None


def _index_to_letter(idx: int) -> str:
    """Convert an index into a letter label, or a number if too many choices."""
    if idx < 0:
        return ""
    if idx >= len(LETTERS):
        # Fallback to numeric labels if choice count exceeds alphabet.
        return str(idx)
    return LETTERS[idx]


def adapt_example(
    example: Dict[str, Any],
    idx: int,
    ds_cfg: Dict[str, Any],
    features: Any = None,
) -> Optional[TaskExample]:
    """Adapt a raw dataset example to the unified TaskExample schema."""
    question_field = ds_cfg.get("question_field") or _first_present(
        example, ["query", "question", "text", "prompt"]
    )
    context_field = ds_cfg.get("context_field") or _first_present(
        example, ["context", "passage", "background"]
    )
    choices_field = ds_cfg.get("choices_field") or _first_present(
        example, ["choices", "options", "candidates", "answers"]
    )
    label_field = ds_cfg.get("label_field") or _first_present(
        example, ["gold", "label", "answer", "target"]
    )
    id_field = ds_cfg.get("id_field") or _first_present(example, ["id", "qid", "uid"])

    if question_field is None:
        return None

    question = str(example[question_field]).strip()
    context = None
    if context_field:
        context_val = example.get(context_field)
        if context_val is not None:
            context = str(context_val).strip()

    raw_choices = example.get(choices_field) if choices_field else None
    choices = _normalize_choices(raw_choices)

    # Infer label names from features when choices are missing.
    if choices is None and label_field:
        label_names = _infer_label_names(features, label_field)
        if label_names:
            choices = label_names

    label_val = example.get(label_field) if label_field else None
    label_type = ds_cfg.get("label_type")

    label_idx = None
    if choices:
        if label_type == "index":
            label_idx = _label_to_index(label_val, choices)
        elif label_type == "string":
            label_idx = _label_to_index(label_val, choices)
        else:
            label_idx = _label_to_index(label_val, choices)

    if choices and label_idx is not None:
        label = _index_to_letter(label_idx)
        label_text = choices[label_idx]
    else:
        label = "" if label_val is None else str(label_val).strip()
        label_text = None

    if not label:
        return None

    dataset_prefix = ds_cfg.get("name", "dataset")
    if id_field and example.get(id_field) is not None:
        example_id = f"{dataset_prefix}-{example.get(id_field)}"
    else:
        example_id = f"{dataset_prefix}-{idx}"

    meta = {
        "dataset": ds_cfg.get("name"),
        "hf_path": ds_cfg.get("hf_path"),
        "split": ds_cfg.get("split"),
        "label_text": label_text,
        "label_index": label_idx,
    }

    return TaskExample(
        id=example_id,
        task_type=ds_cfg.get("task_type", "classification"),
        question=question,
        choices=choices,
        context=context,
        label=label,
        meta=meta,
    )
