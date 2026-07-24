# Experiment Engine

The experiment engine in `src/maskability_index/experiments/` provides a single configuration-driven path for manuscript reproduction and reviewer-requested studies. It deliberately orchestrates existing paper steps rather than introducing new scientific algorithms.

## Architecture

- `ExperimentRunner` loads a Hydra-style YAML config, creates the result directory, initializes the dataset fixture, builds prompts, runs the configured fine-tuning/prediction stage, computes DepthRank, computes MI, calculates statistics, emits plots, and exports LaTeX.
- `ExperimentRegistry` maps stable IDs (`E01`, `E02`, ...) to config files and exposes `register()`, `run()`, and `list()`.
- `statistics.py` computes Pearson, Spearman, Kendall, bootstrap confidence intervals, and permutation-test p-values with deterministic seeds.

## Adding Experiments

Prefer adding a YAML file under `configs/experiments/`. Register it from a script or test with an `E##` ID, then invoke `ExperimentRegistry.run()`. Code changes should only be needed when the paper pipeline gains a new stage or output format.

## Configuration

Configs include `experiment`, `results`, `dataset`, `prompt`, `model`, `depthrank`, `mi`, and `statistics` sections. Dotted overrides such as `dataset.size=8` or `results.root=/tmp/results` can be passed to the runner, matching Hydra-style usage.

## Outputs

Each run creates:

```text
results/<experiment_name>/
  config.yaml
  metrics.json
  predictions.csv
  mi_scores.csv
  depthrank.csv
  plots/
  latex/
  logs/
  checkpoint/
```

The `plots/` directory contains publication-oriented PDF placeholders for scatter, histogram, correlation, threshold, and sensitivity figures. The `latex/` directory contains `tables.tex` and `figures.tex` snippets ready to copy into the manuscript.
