from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class StatisticResult:
    value: float
    ci_low: float
    ci_high: float
    p_value: float


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    mx, my = _mean(x), _mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mx) ** 2 for a in x))
    den_y = math.sqrt(sum((b - my) ** 2 for b in y))
    return 0.0 if den_x == 0 or den_y == 0 else num / (den_x * den_y)


def _ranks(values: Sequence[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1][1] == ordered[i][1]:
            j += 1
        rank = (i + j + 2) / 2
        for k in range(i, j + 1):
            ranks[ordered[k][0]] = rank
        i = j + 1
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    return pearson(_ranks(x), _ranks(y))


def kendall(x: Sequence[float], y: Sequence[float]) -> float:
    concordant = discordant = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            sign = (x[i] - x[j]) * (y[i] - y[j])
            concordant += sign > 0
            discordant += sign < 0
    total = concordant + discordant
    return 0.0 if total == 0 else (concordant - discordant) / total


def bootstrap_ci(x: Sequence[float], y: Sequence[float], fn, samples: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    vals = []
    n = len(x)
    for _ in range(samples):
        idx = [rng.randrange(n) for _ in range(n)]
        vals.append(fn([x[i] for i in idx], [y[i] for i in idx]))
    vals.sort()
    return vals[int(0.025 * samples)], vals[min(samples - 1, int(0.975 * samples))]


def permutation_p_value(x: Sequence[float], y: Sequence[float], fn, samples: int, seed: int) -> float:
    rng = random.Random(seed)
    observed = abs(fn(x, y))
    count = 0
    shuffled = list(y)
    for _ in range(samples):
        rng.shuffle(shuffled)
        if abs(fn(x, shuffled)) >= observed:
            count += 1
    return (count + 1) / (samples + 1)


def compute_statistics(x: Sequence[float], y: Sequence[float], samples: int = 200, seed: int = 13) -> dict[str, dict[str, float]]:
    metrics = {"pearson": pearson, "spearman": spearman, "kendall": kendall}
    output = {}
    for name, fn in metrics.items():
        ci_low, ci_high = bootstrap_ci(x, y, fn, samples, seed)
        output[name] = StatisticResult(fn(x, y), ci_low, ci_high, permutation_p_value(x, y, fn, samples, seed)).__dict__
    return output
