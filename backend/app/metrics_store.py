import json
from pathlib import Path


def save_metrics(path: str, metrics: dict[str, float]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)


def load_metrics(path: str) -> dict[str, float]:
    target = Path(path)
    if not target.exists():
        return {}
    with open(target, "r", encoding="utf-8") as handle:
        return json.load(handle)
