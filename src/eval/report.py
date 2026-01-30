"""Report generation utilities for baseline vs agent comparison."""

from __future__ import annotations

from typing import Dict, List, Optional


def _truncate(text: str, limit: int = 160) -> str:
    """Shorten long text blocks for report tables."""
    text = text.replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _index_records(records: List[Dict]) -> Dict[str, Dict]:
    """Create a quick lookup map by example id."""
    return {r["id"]: r for r in records}


def generate_compare_report(
    baseline_records: List[Dict],
    agent_records: List[Dict],
    metrics_baseline: Dict,
    metrics_agent: Dict,
    metrics_ablation: Optional[Dict[str, Dict]] = None,
) -> str:
    """Generate a Markdown report comparing agent vs baseline results."""
    lines = []
    lines.append("# Agent vs Baseline Comparison\n")

    lines.append("## Metrics\n")
    lines.append("| System | Accuracy | Macro-F1 | Invalid Rate | n |")
    lines.append("|---|---:|---:|---:|---:|")
    lines.append(
        f"| Baseline | {metrics_baseline['accuracy']:.4f} | {metrics_baseline['macro_f1']:.4f} | {metrics_baseline['invalid_rate']:.4f} | {metrics_baseline['n']} |"
    )
    lines.append(
        f"| Agent | {metrics_agent['accuracy']:.4f} | {metrics_agent['macro_f1']:.4f} | {metrics_agent['invalid_rate']:.4f} | {metrics_agent['n']} |"
    )

    if metrics_ablation:
        for name, met in metrics_ablation.items():
            lines.append(
                f"| {name} | {met['accuracy']:.4f} | {met['macro_f1']:.4f} | {met['invalid_rate']:.4f} | {met['n']} |"
            )

    acc_delta = (metrics_agent["accuracy"] - metrics_baseline["accuracy"]) * 100
    f1_delta = (metrics_agent["macro_f1"] - metrics_baseline["macro_f1"]) * 100
    lines.append("\n## Absolute Improvement (Agent - Baseline)\n")
    lines.append(f"- Accuracy: {acc_delta:.2f} pp")
    lines.append(f"- Macro-F1: {f1_delta:.2f} pp")

    lines.append("\n## Error Analysis\n")
    base_idx = _index_records(baseline_records)
    agent_idx = _index_records(agent_records)

    base_wrong_agent_right = []
    base_right_agent_wrong = []

    for ex_id, b in base_idx.items():
        a = agent_idx.get(ex_id)
        if not a:
            continue
        if (not b["correct"]) and a["correct"]:
            base_wrong_agent_right.append((b, a))
        if b["correct"] and (not a["correct"]):
            base_right_agent_wrong.append((b, a))

    lines.append("\n### Top-10: Baseline Wrong / Agent Correct\n")
    for b, a in base_wrong_agent_right[:10]:
        lines.append(
            f"- {b['id']}: {_truncate(b['question'])} | gold={b['label']} | baseline={b['prediction']} | agent={a['prediction']}"
        )

    lines.append("\n### Top-10: Baseline Correct / Agent Wrong\n")
    for b, a in base_right_agent_wrong[:10]:
        lines.append(
            f"- {b['id']}: {_truncate(b['question'])} | gold={b['label']} | baseline={b['prediction']} | agent={a['prediction']}"
        )

    return "\n".join(lines) + "\n"
