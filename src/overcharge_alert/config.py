from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

APP_NAME = "Overcharge-Alert"

_resolved_config_path: Path | None = None


@dataclass
class Config:
    threshold_percent: int = 80
    poll_interval_seconds: float = 30.0

    def clamp(self) -> None:
        self.threshold_percent = max(1, min(100, int(self.threshold_percent)))
        self.poll_interval_seconds = max(0.5, float(self.poll_interval_seconds))


def config_path() -> Path:
    base = Path(user_config_dir(APP_NAME, appauthor=False))
    return base / "config.json"


def _config_candidates() -> list[Path]:
    """
    Search order (first existing file wins):
    - Packaged exe: directory of the .exe, then default user path.
    - Development: package dir config.json (e.g. src/overcharge_alert/config.json), then
      src/config.json when in a repo layout, then default user path.
    """
    default = config_path()
    if getattr(sys, "frozen", False):
        return [
            Path(sys.executable).resolve().parent / "config.json",
            default,
        ]
    paths: list[Path] = []
    package_dir = Path(__file__).resolve().parent
    paths.append(package_dir / "config.json")
    dev_root = package_dir.parent
    if dev_root.name == "src":
        paths.append(dev_root / "config.json")
    paths.append(default)
    return paths


def _first_existing_config_path() -> Path | None:
    for path in _config_candidates():
        if path.is_file():
            return path
    return None


def get_active_config_path() -> Path:
    """Config file in use after load_config(); defaults to config_path() if not loaded yet."""
    return _resolved_config_path if _resolved_config_path is not None else config_path()


def default_config() -> Config:
    return Config()


def _merge_dict(cfg: Config, data: dict[str, Any]) -> None:
    if "threshold_percent" in data:
        cfg.threshold_percent = int(data["threshold_percent"])
    if "poll_interval_seconds" in data:
        cfg.poll_interval_seconds = float(data["poll_interval_seconds"])


def load_config() -> Config:
    global _resolved_config_path

    path = _first_existing_config_path()
    cfg = default_config()
    if path is None:
        cfg.clamp()
        save_config(cfg)
        _resolved_config_path = config_path()
        return cfg
    _resolved_config_path = path
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        cfg.clamp()
        return cfg
    _merge_dict(cfg, data)
    cfg.clamp()
    return cfg


def save_config(cfg: Config) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=2)
        f.write("\n")
