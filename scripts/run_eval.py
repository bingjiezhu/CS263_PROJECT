#!/usr/bin/env python3
"""CLI entrypoint to run the evaluation pipeline."""

from __future__ import annotations

import argparse
import os
import sys

import yaml

# Ensure src is importable when running without installation.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from eval.runner import run_eval  # noqa: E402


def _load_dotenv(path: str) -> None:
    """Load a simple key=value .env file into the process environment."""
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def main() -> None:
    """Parse CLI args and execute a run."""
    parser = argparse.ArgumentParser(description="Run FinRobot vs baseline evaluation")
    parser.add_argument("--config", required=True, help="Path to eval_config.yaml")
    args = parser.parse_args()

    # Load optional .env files from repo root or parent directory.
    _load_dotenv(os.path.join(ROOT, ".env"))
    _load_dotenv(os.path.abspath(os.path.join(ROOT, os.pardir, ".env")))

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    run_dir = run_eval(cfg)
    print(f"Outputs saved to: {run_dir}")


if __name__ == "__main__":
    main()
