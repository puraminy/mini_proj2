from __future__ import annotations

from pathlib import Path

from maskability_index.experiments import ExperimentRegistry


def build_registry() -> ExperimentRegistry:
    root = Path(__file__).resolve().parents[1]
    registry = ExperimentRegistry()
    registry.register("E01", root / "configs/experiments/reproduction.yaml")
    return registry


def main() -> None:
    registry = build_registry()
    for experiment_id in registry.list():
        registry.run(experiment_id, overrides={"results.root": "results/reproduction"})


if __name__ == "__main__":
    main()
