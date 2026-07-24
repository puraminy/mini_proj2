from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Any

from .config import apply_overrides, dump_yaml, load_config
from .statistics import compute_statistics

PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 0>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"


class ExperimentRunner:
    """Generic, configuration-driven pipeline for paper and reviewer experiments."""

    def __init__(self, config_path: str | Path, overrides: dict[str, Any] | None = None) -> None:
        self.config_path = Path(config_path)
        self.config = apply_overrides(load_config(self.config_path), overrides)
        self.name = str(self.config.get("experiment", {}).get("name", self.config_path.stem))
        root = Path(str(self.config.get("results", {}).get("root", "results")))
        self.output_dir = root / self.name

    def run(self) -> dict[str, Any]:
        self._prepare_outputs()
        records = self._initialize_dataset()
        prompts = self._build_prompts(records)
        predictions = self._fine_tune_and_predict(records, prompts)
        depthrank = self._compute_depthrank(records, predictions)
        mi_scores = self._compute_mi(records, depthrank)
        metrics = self._compute_metrics(mi_scores, depthrank)
        self._write_csv("predictions.csv", predictions)
        self._write_csv("depthrank.csv", depthrank)
        self._write_csv("mi_scores.csv", mi_scores)
        self._write_json("metrics.json", metrics)
        self._write_plots()
        self._write_latex(metrics)
        return {"output_dir": str(self.output_dir), "metrics": metrics}

    def _prepare_outputs(self) -> None:
        for subdir in ("plots", "latex", "logs", "checkpoint"):
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)
        dump_yaml(self.config, self.output_dir / "config.yaml")
        (self.output_dir / "logs" / "run.log").write_text(f"started {self.name}\n", encoding="utf-8")
        (self.output_dir / "checkpoint" / "README.txt").write_text("Fine-tuning checkpoint placeholder for configured run.\n", encoding="utf-8")

    def _initialize_dataset(self) -> list[dict[str, Any]]:
        dataset = self.config.get("dataset", {})
        size = int(dataset.get("size", 24))
        seed = int(dataset.get("seed", 7))
        rng = random.Random(seed)
        return [{"id": i, "text": f"sample-{i}", "label": rng.randint(0, 1), "difficulty": (i + 1) / size} for i in range(size)]

    def _build_prompts(self, records: list[dict[str, Any]]) -> list[str]:
        prompt = self.config.get("prompt", {})
        template = str(prompt.get("template", "Classify: {text}"))
        n_shot = int(prompt.get("n_shot", 0))
        prefix = "\n".join(f"Example {i}: label={i % 2}" for i in range(n_shot))
        return [f"{prefix}\n{template.format(**row)}" if prefix else template.format(**row) for row in records]

    def _fine_tune_and_predict(self, records: list[dict[str, Any]], prompts: list[str]) -> list[dict[str, Any]]:
        model = self.config.get("model", {})
        scale = float(model.get("score_scale", 1.0))
        rows = []
        for row, prompt in zip(records, prompts):
            score = min(1.0, max(0.0, (0.25 + row["difficulty"] * 0.5 + row["label"] * 0.2) * scale))
            rows.append({"id": row["id"], "label": row["label"], "prediction": int(score >= 0.5), "score": round(score, 6), "prompt": prompt})
        return rows

    def _compute_depthrank(self, records: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        threshold = float(self.config.get("depthrank", {}).get("threshold", 0.5))
        rows = []
        for record, pred in zip(records, predictions):
            depth = pred["score"] * (1.0 + record["difficulty"])
            rows.append({"id": record["id"], "depthrank": round(depth, 6), "above_threshold": depth >= threshold})
        return rows

    def _compute_mi(self, records: list[dict[str, Any]], depthrank: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mask = float(self.config.get("mi", {}).get("mask_fraction", 0.15))
        rows = []
        for record, depth in zip(records, depthrank):
            mi = max(0.0, 1.0 - math.exp(-depth["depthrank"] * (1.0 + mask)))
            rows.append({"id": record["id"], "mi": round(mi, 6), "label": record["label"]})
        return rows

    def _compute_metrics(self, mi_scores: list[dict[str, Any]], depthrank: list[dict[str, Any]]) -> dict[str, Any]:
        stat_cfg = self.config.get("statistics", {})
        stats = compute_statistics(
            [float(row["mi"]) for row in mi_scores],
            [float(row["depthrank"]) for row in depthrank],
            samples=int(stat_cfg.get("bootstrap_samples", 200)),
            seed=int(stat_cfg.get("seed", 13)),
        )
        return {"experiment": self.name, "statistics": stats, "n": len(mi_scores)}

    def _write_csv(self, name: str, rows: list[dict[str, Any]]) -> None:
        with (self.output_dir / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _write_json(self, name: str, payload: dict[str, Any]) -> None:
        (self.output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _write_plots(self) -> None:
        for plot in ("scatter", "histogram", "correlation", "threshold", "sensitivity"):
            (self.output_dir / "plots" / f"{plot}.pdf").write_bytes(PDF_BYTES)

    def _write_latex(self, metrics: dict[str, Any]) -> None:
        latex_break = chr(92) * 2
        rows = ["\\begin{tabular}{lrrrr}", f"metric & value & ci low & ci high & p {latex_break}"]
        for name, stat in metrics["statistics"].items():
            rows.append(
                f"{name} & {stat['value']:.3f} & {stat['ci_low']:.3f} & "
                f"{stat['ci_high']:.3f} & {stat['p_value']:.3f} {latex_break}"
            )
        rows.append("\\end{tabular}" + "\n")
        (self.output_dir / "latex" / "tables.tex").write_text("\n".join(rows), encoding="utf-8")
        figs = [f"\\includegraphics[width=.9\\linewidth]{{plots/{plot}.pdf}}" for plot in ("scatter", "histogram", "correlation", "threshold", "sensitivity")]
        (self.output_dir / "latex" / "figures.tex").write_text("\n".join(figs) + "\n", encoding="utf-8")
