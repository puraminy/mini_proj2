from __future__ import annotations

from pathlib import Path
from typing import Any

from .runner import ExperimentRunner


class ExperimentRegistry:
    """Registry that maps stable experiment IDs such as E01 to YAML configs."""

    def __init__(self) -> None:
        self._experiments: dict[str, Path] = {}

    def register(self, experiment_id: str, config_path: str | Path) -> None:
        if not experiment_id.startswith("E") or not experiment_id[1:].isdigit():
            raise ValueError("experiment IDs must use the E01, E02, ... format")
        self._experiments[experiment_id] = Path(config_path)

    def list(self) -> list[str]:
        return sorted(self._experiments)

    def run(self, experiment_id: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        return ExperimentRunner(self._experiments[experiment_id], overrides).run()
