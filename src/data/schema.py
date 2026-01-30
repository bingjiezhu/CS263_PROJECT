"""Schema definitions for normalized task examples used across the pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TaskExample:
    """Normalized example record shared by loaders, models, and evaluators."""

    id: str
    task_type: str
    question: str
    label: str
    choices: Optional[List[str]] = None
    context: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataclass to a JSON-serializable dictionary."""
        data = asdict(self)
        # Always materialize meta to simplify downstream code.
        if self.meta is None:
            data["meta"] = {}
        return data
