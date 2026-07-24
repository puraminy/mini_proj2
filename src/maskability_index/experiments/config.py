from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "None", "~"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value.strip('"\'')


def load_config(path: str | Path) -> dict[str, Any]:
    """Load the simple YAML subset used by repository experiment configs."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, sep, value = raw.strip().partition(":")
        if not sep:
            continue
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value.strip() == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value)
    return root


def apply_overrides(config: dict[str, Any], overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply Hydra-style dotted key overrides to a copied config dictionary."""
    merged = dict(config)
    for dotted, value in (overrides or {}).items():
        cursor = merged
        parts = dotted.split(".")
        for part in parts[:-1]:
            next_value = cursor.get(part, {})
            if not isinstance(next_value, dict):
                next_value = {}
            cursor[part] = next_value
            cursor = next_value
        cursor[parts[-1]] = value
    return merged


def dump_yaml(data: dict[str, Any], path: str | Path, indent: int = 0) -> None:
    """Write deterministic, human-readable YAML for result archival."""
    lines: list[str] = []

    def emit(mapping: dict[str, Any], level: int) -> None:
        pad = " " * level
        for key in sorted(mapping):
            value = mapping[key]
            if isinstance(value, dict):
                lines.append(f"{pad}{key}:")
                emit(value, level + 2)
            else:
                lines.append(f"{pad}{key}: {repr(value) if isinstance(value, str) else value}")

    emit(data, indent)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
