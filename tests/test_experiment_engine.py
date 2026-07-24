from pathlib import Path

from maskability_index.experiments import ExperimentRegistry, ExperimentRunner


def test_reproduction_pipeline_creates_outputs(tmp_path: Path) -> None:
    result = ExperimentRunner(
        "configs/experiments/reproduction.yaml",
        overrides={"results.root": str(tmp_path), "dataset.size": 6, "statistics.bootstrap_samples": 10},
    ).run()

    output = Path(result["output_dir"])
    assert (output / "config.yaml").exists()
    assert (output / "metrics.json").exists()
    assert (output / "predictions.csv").exists()
    assert (output / "mi_scores.csv").exists()
    assert (output / "depthrank.csv").exists()
    assert (output / "plots" / "scatter.pdf").exists()
    assert (output / "plots" / "histogram.pdf").exists()
    assert (output / "plots" / "correlation.pdf").exists()
    assert (output / "plots" / "threshold.pdf").exists()
    assert (output / "plots" / "sensitivity.pdf").exists()
    assert (output / "latex" / "tables.tex").exists()
    assert (output / "latex" / "figures.tex").exists()
    assert (output / "logs").is_dir()
    assert (output / "checkpoint").is_dir()


def test_registry_lists_and_runs_experiments(tmp_path: Path) -> None:
    registry = ExperimentRegistry()
    registry.register("E01", "configs/experiments/reproduction.yaml")

    assert registry.list() == ["E01"]
    result = registry.run("E01", overrides={"results.root": str(tmp_path), "dataset.size": 5, "statistics.bootstrap_samples": 10})

    assert Path(result["output_dir"]).name == "reproduction"


def test_configuration_overrides_are_written(tmp_path: Path) -> None:
    ExperimentRunner("configs/experiments/reproduction.yaml", overrides={"results.root": str(tmp_path), "dataset.size": 3}).run()

    archived = (tmp_path / "reproduction" / "config.yaml").read_text(encoding="utf-8")
    assert "size: 3" in archived
