"""Pytest configuration for deterministic imports and seeding."""

import os
import sys
from pathlib import Path

# Add src/ to sys.path so tests can import the package without installation.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Ensure deterministic hashing in tests.
os.environ.setdefault("PYTHONHASHSEED", "0")
