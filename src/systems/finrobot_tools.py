"""Utilities to select FinRobot toolkits based on environment and availability."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class ToolkitSpec:
    """Metadata describing a FinRobot toolkit and its required env keys."""

    name: str
    module: str
    attr: str
    env_keys: List[str]


def _safe_get_attr(module_path: str, attr: str) -> Any:
    """Import a module attribute safely, returning None on failure."""
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    except Exception:
        return None


def _has_env(keys: List[str]) -> bool:
    """Return True when all required environment variables are present."""
    if not keys:
        return True
    return all(os.environ.get(k) for k in keys)


def _default_toolsets() -> List[str]:
    """Default toolsets enabled when config requests auto-selection."""
    return [
        "finnhub",
        "fmp",
        "sec",
        "yfinance",
        "reddit",
        "finnlp",
        "analysis",
        "charting",
        "report_charting",
        "reportlab",
        "text",
        "quant",
        "coding",
        "ipython",
    ]


def _tool_specs() -> Dict[str, ToolkitSpec]:
    """Registry of known FinRobot toolkits and their import paths."""
    return {
        "finnhub": ToolkitSpec(
            name="finnhub",
            module="finrobot.data_source.finnhub_utils",
            attr="FinnHubUtils",
            env_keys=["FINNHUB_API_KEY"],
        ),
        "fmp": ToolkitSpec(
            name="fmp",
            module="finrobot.data_source.fmp_utils",
            attr="FMPUtils",
            env_keys=["FMP_API_KEY"],
        ),
        "sec": ToolkitSpec(
            name="sec",
            module="finrobot.data_source.sec_utils",
            attr="SECUtils",
            env_keys=["SEC_API_KEY"],
        ),
        "yfinance": ToolkitSpec(
            name="yfinance",
            module="finrobot.data_source.yfinance_utils",
            attr="YFinanceUtils",
            env_keys=[],
        ),
        "reddit": ToolkitSpec(
            name="reddit",
            module="finrobot.data_source.reddit_utils",
            attr="RedditUtils",
            env_keys=["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"],
        ),
        "finnlp": ToolkitSpec(
            name="finnlp",
            module="finrobot.data_source.finnlp_utils",
            attr="FinNLPUtils",
            env_keys=[],
        ),
        "analysis": ToolkitSpec(
            name="analysis",
            module="finrobot.functional.analyzer",
            attr="ReportAnalysisUtils",
            env_keys=["SEC_API_KEY", "FMP_API_KEY"],
        ),
        "charting": ToolkitSpec(
            name="charting",
            module="finrobot.functional.charting",
            attr="MplFinanceUtils",
            env_keys=[],
        ),
        "report_charting": ToolkitSpec(
            name="report_charting",
            module="finrobot.functional.charting",
            attr="ReportChartUtils",
            env_keys=[],
        ),
        "reportlab": ToolkitSpec(
            name="reportlab",
            module="finrobot.functional.reportlab",
            attr="ReportLabUtils",
            env_keys=[],
        ),
        "text": ToolkitSpec(
            name="text",
            module="finrobot.functional.text",
            attr="TextUtils",
            env_keys=[],
        ),
        "quant": ToolkitSpec(
            name="quant",
            module="finrobot.functional.quantitative",
            attr="BackTraderUtils",
            env_keys=[],
        ),
        "coding": ToolkitSpec(
            name="coding",
            module="finrobot.functional.coding",
            attr="CodingUtils",
            env_keys=[],
        ),
        "ipython": ToolkitSpec(
            name="ipython",
            module="finrobot.functional.coding",
            attr="IPythonUtils",
            env_keys=[],
        ),
    }


def build_toolkits(config: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
    """Resolve toolkits based on config + available dependencies."""
    toolsets = config.get("toolsets") or []
    if not toolsets or "auto" in toolsets:
        toolsets = _default_toolsets()
    specs = _tool_specs()
    toolkits: List[Any] = []
    info: Dict[str, Any] = {"enabled": [], "skipped": []}

    for name in toolsets:
        spec = specs.get(name)
        if spec is None:
            info["skipped"].append({"name": name, "reason": "unknown_toolset"})
            continue
        if not _has_env(spec.env_keys):
            info["skipped"].append(
                {"name": name, "reason": "missing_env", "env_keys": spec.env_keys}
            )
            continue
        cls = _safe_get_attr(spec.module, spec.attr)
        if cls is None:
            info["skipped"].append(
                {"name": name, "reason": "import_failed", "module": spec.module}
            )
            continue
        toolkits.append(cls)
        info["enabled"].append(name)

    return toolkits, info
