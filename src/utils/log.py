"""Logging helpers used across the evaluation pipeline."""

from __future__ import annotations

import logging
import os
from typing import Optional


def setup_logger(log_path: Optional[str] = None) -> logging.Logger:
    """Configure a single logger with optional file output."""
    logger = logging.getLogger("finrobot_pixiu_eval")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
