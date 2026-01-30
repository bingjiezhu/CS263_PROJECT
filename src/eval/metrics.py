"""Metric implementations for classification-style evaluation."""

from __future__ import annotations

from typing import Dict, List


def accuracy(y_true: List[str], y_pred: List[str]) -> float:
    """Compute accuracy as correct / total."""
    if not y_true:
        return 0.0
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true)


def macro_f1(y_true: List[str], y_pred: List[str]) -> float:
    """Compute unweighted macro-F1 across all observed labels."""
    labels = sorted(set(y_true) | set(y_pred))
    if not labels:
        return 0.0
    f1s = []
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        if tp == 0 and fp == 0 and fn == 0:
            f1s.append(0.0)
            continue
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        if precision + recall == 0:
            f1s.append(0.0)
        else:
            f1s.append(2 * precision * recall / (precision + recall))
    return sum(f1s) / len(f1s)


def compute_metrics(records: List[Dict[str, str]]) -> Dict[str, float]:
    """Compute summary metrics from a list of prediction records."""
    y_true = [r["label"] for r in records]
    y_pred = [r["prediction"] for r in records]
    invalid = sum(1 for p in y_pred if p == "INVALID")
    return {
        "accuracy": accuracy(y_true, y_pred),
        "macro_f1": macro_f1(y_true, y_pred),
        "n": len(records),
        "invalid_rate": invalid / len(records) if records else 0.0,
    }
