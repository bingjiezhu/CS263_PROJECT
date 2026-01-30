"""Dataset loading utilities for HuggingFace-hosted benchmarks."""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List

from .adapters import adapt_example
from .schema import TaskExample


def _load_hf_dataset(ds_cfg: Dict[str, Any]):
    """Load a HuggingFace dataset split, with fallbacks if the split is missing."""
    from datasets import load_dataset

    path = ds_cfg["hf_path"]
    name = ds_cfg.get("hf_name")
    split = ds_cfg.get("split", "test")
    splits_to_try = [split, "validation", "train"]
    last_err = None
    for sp in splits_to_try:
        try:
            if name:
                return load_dataset(path, name, split=sp)
            return load_dataset(path, split=sp)
        except Exception as exc:
            last_err = exc
            continue
    if last_err:
        raise last_err
    raise ValueError(f"Failed to load dataset {path}")


def load_examples(cfg: Dict[str, Any]) -> List[TaskExample]:
    """Load and normalize examples according to eval_config.yaml."""
    datasets_cfg = cfg.get("datasets", [])
    if not datasets_cfg:
        raise ValueError("No datasets configured in eval_config.yaml")

    seed = int(cfg.get("seed", 42))
    max_samples = cfg.get("max_samples")
    max_per_ds = cfg.get("max_samples_per_dataset")

    rng = random.Random(seed)
    examples: List[TaskExample] = []

    # Compute per-dataset sampling budget when not explicitly set.
    per_limit = None
    if max_per_ds is not None:
        per_limit = int(max_per_ds)
    elif max_samples is not None:
        per_limit = int(math.ceil(int(max_samples) / len(datasets_cfg)))

    for ds_cfg in datasets_cfg:
        if ds_cfg.get("enabled", True) is False:
            continue
        ds = _load_hf_dataset(ds_cfg)
        ds_len = len(ds)

        # Sample deterministically to keep runs reproducible.
        if per_limit is None or per_limit >= ds_len:
            indices = list(range(ds_len))
        else:
            indices = rng.sample(range(ds_len), per_limit)

        # Preserve deterministic ordering across Python versions.
        indices = list(indices)
        indices.sort()

        for local_idx, idx in enumerate(indices):
            ex = ds[int(idx)]
            adapted = adapt_example(ex, local_idx, ds_cfg, features=getattr(ds, "features", None))
            if adapted is None:
                continue
            examples.append(adapted)

    # Apply a final truncation if total examples exceed the limit.
    if max_samples is not None and len(examples) > int(max_samples):
        rng.shuffle(examples)
        examples = examples[: int(max_samples)]

    return examples
