from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_CONFIG: Dict[str, Any] = {
    "profile_name": "Research Radar",
    "keywords": [],
    "exclude_keywords": [],
    "sources": {"crossref": True, "openalex": True, "arxiv": True, "semantic_scholar": True},
    "max_results_per_keyword": 10,
    "lookback_days": 30,
    "min_relevance_score": 35,
}


def load_config(path: str | Path = "config/interests.yaml") -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config file must contain a YAML mapping: {path}")

    config = {**DEFAULT_CONFIG, **loaded}
    config["sources"] = {**DEFAULT_CONFIG["sources"], **(loaded.get("sources") or {})}
    config["keywords"] = [str(x).strip() for x in config.get("keywords", []) if str(x).strip()]
    config["exclude_keywords"] = [str(x).strip() for x in config.get("exclude_keywords", []) if str(x).strip()]
    return config
