"""Deterministic seeding utilities for Python and NumPy."""

from __future__ import annotations

import os
import random
from typing import Optional

import numpy as np


def set_seed(seed: Optional[int]) -> None:
    """Set RNG seeds for reproducibility across common libraries."""
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
