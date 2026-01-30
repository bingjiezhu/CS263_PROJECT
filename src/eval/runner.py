"""Evaluation runner that orchestrates baseline, agent, and ablation runs."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List

from tqdm import tqdm

from data.loader import load_examples
from eval.metrics import compute_metrics
from eval.report import generate_compare_report
from llm.providers import load_provider_config, make_autogen_config, make_openai_client
from systems import baseline_direct, finrobot_agent
from utils.cache import DiskCache
from utils.log import setup_logger
from utils.seed import set_seed


def _write_json(path: str, data: Dict[str, Any]) -> None:
    """Write a JSON file with deterministic formatting."""
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)


def _write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    """Write a JSONL file where each line is a single record."""
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=True) + "\n")


def _slugify(text: str, max_len: int = 80) -> str:
    """Convert a string into a filesystem-friendly slug."""
    if not text:
        return "run"
    text = text.strip().lower()
    text = text.replace(os.sep, "-")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if not text:
        text = "run"
    return text[:max_len]


def _write_run_readme(path: str, cfg: Dict[str, Any], run_id: str, n_examples: int) -> None:
    """Write a Markdown summary of the run configuration and datasets."""
    lines: List[str] = []
    lines.append("# Run Metadata")
    lines.append("")
    lines.append(f"- Run ID: {run_id}")
    lines.append(f"- Timestamp: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## Model and Provider")
    lines.append(f"- provider: {cfg.get('provider')}")
    lines.append(f"- model: {cfg.get('model')}")
    lines.append(f"- base_url: {cfg.get('base_url')}")
    lines.append(f"- temperature: {cfg.get('temperature', 0.0)}")
    lines.append(f"- seed: {cfg.get('seed')}")
    lines.append(f"- max_samples: {cfg.get('max_samples')}")
    lines.append(f"- max_samples_per_dataset: {cfg.get('max_samples_per_dataset')}")
    lines.append(f"- total_examples_loaded: {n_examples}")
    lines.append(f"- use_cache: {cfg.get('use_cache', True)}")
    lines.append("")
    lines.append("## Datasets")
    datasets = cfg.get("datasets", []) or []
    for ds in datasets:
        if ds.get("enabled", True) is False:
            continue
        lines.append(
            f"- name: {ds.get('name')} | hf_path: {ds.get('hf_path')} | split: {ds.get('split')} | task_type: {ds.get('task_type')}"
        )
        lines.append(
            f"  fields: question={ds.get('question_field')} | choices={ds.get('choices_field')} | label={ds.get('label_field')} | label_type={ds.get('label_type')}"
        )
    lines.append("")
    lines.append("## Systems")
    lines.append(f"- run_baseline: {cfg.get('run_baseline', True)}")
    lines.append(f"- run_agent: {cfg.get('run_agent', True)}")
    ablations = cfg.get("ablations", []) or []
    lines.append(f"- ablations: {', '.join(ablations) if ablations else 'none'}")
    if "agent_no_critic" in ablations:
        lines.append("  - agent_no_critic: disables the Critic step (Planner → Solver → Final only)")
    lines.append("")
    lines.append("## FinRobot Config")
    fincfg = cfg.get("finrobot", {}) or {}
    lines.append(f"- mode: {fincfg.get('mode', 'minimal')}")
    lines.append(f"- workflow: {fincfg.get('workflow', 'group_chat')}")
    lines.append(f"- enable_tools: {fincfg.get('enable_tools', False)}")
    lines.append(f"- toolsets: {fincfg.get('toolsets', [])}")
    lines.append(f"- max_turns: {fincfg.get('max_turns', 6)}")
    lines.append(f"- retry_on_invalid: {fincfg.get('retry_on_invalid', True)}")
    lines.append(f"- max_retries: {fincfg.get('max_retries', 1)}")
    lines.append(f"- manual_mode: {fincfg.get('manual_mode', False)}")
    rag_cfg = fincfg.get("rag", {}) or {}
    lines.append(f"- rag_enabled: {rag_cfg.get('enabled', False)}")
    code_cfg = fincfg.get("code_execution", {}) or {}
    lines.append(f"- code_execution_enabled: {code_cfg.get('enabled', False)}")
    lines.append("")
    lines.append("See config_snapshot.yaml for the full configuration.")
    lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def run_eval(cfg: Dict[str, Any]) -> str:
    """Run the evaluation pipeline and return the output directory path."""
    seed = cfg.get("seed")
    set_seed(seed)

    provider_cfg = load_provider_config(cfg)
    client = make_openai_client(provider_cfg)
    llm_config = make_autogen_config(provider_cfg, temperature=cfg.get("temperature", 0.0))

    examples = load_examples(cfg)
    if not examples:
        raise ValueError("No examples loaded. Please check dataset configuration.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_names = []
    for ds in cfg.get("datasets", []) or []:
        if ds.get("enabled", True) is False:
            continue
        hf_path = ds.get("hf_path")
        if hf_path:
            name = hf_path.split("/")[-1]
        else:
            name = ds.get("name") or "dataset"
        dataset_names.append(name)
    datasets_slug = _slugify("+".join(dataset_names))
    model_slug = _slugify(provider_cfg.model)
    provider_slug = _slugify(provider_cfg.provider)
    run_id = f"{provider_slug}-{model_slug}__{datasets_slug}__n{len(examples)}__{timestamp}"
    output_root = cfg.get("output_dir", "outputs/runs")
    run_dir = os.path.join(output_root, run_id)
    os.makedirs(run_dir, exist_ok=True)

    logger = setup_logger(os.path.join(run_dir, "run.log"))
    logger.info("Run ID: %s", run_id)
    logger.info("Loaded %d examples", len(examples))

    # Snapshot the effective config for reproducibility.
    with open(os.path.join(run_dir, "config_snapshot.yaml"), "w") as f:
        import yaml

        yaml.safe_dump(cfg, f, sort_keys=False)
    _write_run_readme(os.path.join(run_dir, "README.md"), cfg, run_id, len(examples))

    use_cache = bool(cfg.get("use_cache", True))

    results: Dict[str, List[Dict[str, Any]]] = {}
    metrics: Dict[str, Dict[str, Any]] = {}

    if cfg.get("run_baseline", True):
        logger.info("Running baseline...")
        cache = DiskCache(os.path.join(run_dir, "cache_baseline.json")) if use_cache else None
        outputs = []
        for ex in tqdm(examples, desc="baseline"):
            outputs.append(
                baseline_direct.run_baseline(
                    [ex],
                    client,
                    provider_cfg.model,
                    cfg.get("temperature", 0.0),
                    cache=cache,
                )[0]
            )
        results["baseline"] = outputs
        metrics["baseline"] = compute_metrics(outputs)
        _write_jsonl(os.path.join(run_dir, "baseline.jsonl"), outputs)
        _write_json(os.path.join(run_dir, "metrics_baseline.json"), metrics["baseline"])

    finrobot_cfg = cfg.get("finrobot", {})
    if provider_cfg.provider == "manual":
        finrobot_cfg = {**finrobot_cfg, "manual_mode": True}
        logger.info("Manual mode enabled for FinRobot agent.")

    if cfg.get("run_agent", True):
        logger.info("Running FinRobot agent...")
        cache = DiskCache(os.path.join(run_dir, "cache_agent.json")) if use_cache else None
        outputs = []
        for ex in tqdm(examples, desc="agent"):
            outputs.append(
                finrobot_agent.run_agent(
                    [ex],
                    llm_config,
                    cfg.get("temperature", 0.0),
                    no_critic=False,
                    cache=cache,
                    finrobot_config=finrobot_cfg,
                )[0]
            )
        results["agent"] = outputs
        metrics["agent"] = compute_metrics(outputs)
        _write_jsonl(os.path.join(run_dir, "agent.jsonl"), outputs)
        _write_json(os.path.join(run_dir, "metrics_agent.json"), metrics["agent"])

    # Optional ablations to isolate architectural contributions.
    ablations = cfg.get("ablations", []) or []
    metrics_ablation: Dict[str, Dict[str, Any]] = {}
    for ab in ablations:
        if ab == "agent_no_critic":
            logger.info("Running ablation: agent_no_critic...")
            cache = DiskCache(os.path.join(run_dir, "cache_agent_no_critic.json")) if use_cache else None
            outputs = []
            for ex in tqdm(examples, desc="agent_no_critic"):
                outputs.append(
                    finrobot_agent.run_agent(
                        [ex],
                        llm_config,
                        cfg.get("temperature", 0.0),
                        no_critic=True,
                        cache=cache,
                        finrobot_config=finrobot_cfg,
                    )[0]
                )
            results["agent_no_critic"] = outputs
            metrics_ablation["agent_no_critic"] = compute_metrics(outputs)
            _write_jsonl(os.path.join(run_dir, "agent_no_critic.jsonl"), outputs)
            _write_json(
                os.path.join(run_dir, "metrics_agent_no_critic.json"),
                metrics_ablation["agent_no_critic"],
            )

    # Produce a comparison report if both baseline and agent exist.
    if "baseline" in results and "agent" in results:
        report = generate_compare_report(
            baseline_records=results["baseline"],
            agent_records=results["agent"],
            metrics_baseline=metrics["baseline"],
            metrics_agent=metrics["agent"],
            metrics_ablation=metrics_ablation if metrics_ablation else None,
        )
        with open(os.path.join(run_dir, "compare.md"), "w") as f:
            f.write(report)

    logger.info("Run complete. Outputs saved to %s", run_dir)
    return run_dir
