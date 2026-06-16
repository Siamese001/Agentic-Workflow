"""Strict model catalog loader for shared provider model identifiers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
MODEL_CATALOG_PATH: Final[Path] = REPO_ROOT / "config" / "model_catalog.json"


class ModelCatalogError(RuntimeError):
    """Raised when the model catalog is missing, malformed, or incomplete."""


@lru_cache(maxsize=1)
def _catalog() -> dict[str, Any]:
    try:
        data = json.loads(MODEL_CATALOG_PATH.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ModelCatalogError(f"Model catalog is unreadable: {MODEL_CATALOG_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise ModelCatalogError(f"Model catalog is malformed JSON: {MODEL_CATALOG_PATH}") from exc
    if not isinstance(data, dict):
        raise ModelCatalogError(f"Model catalog root must be an object: {MODEL_CATALOG_PATH}")
    return data


def model_id(path: str) -> str:
    node: Any = _catalog()
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ModelCatalogError(f"Missing model catalog key: {path}")
        node = node[part]
    if not isinstance(node, str) or not node.strip():
        raise ModelCatalogError(f"Model catalog key must be a non-empty string: {path}")
    return node.strip()


def model_id_list(path: str) -> tuple[str, ...]:
    node: Any = _catalog()
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ModelCatalogError(f"Missing model catalog key: {path}")
        node = node[part]
    if not isinstance(node, list) or not all(isinstance(item, str) and item.strip() for item in node):
        raise ModelCatalogError(f"Model catalog key must be a list of non-empty strings: {path}")
    return tuple(item.strip() for item in node)


OPENAI_DEFAULT_MODEL_ID: Final[str] = model_id("openai.default")
OPENAI_CHAT_JUDGE_MODEL_ID: Final[str] = model_id("openai.chat_judge")
OPENAI_OMIT_TEMPERATURE_MODELS: Final[frozenset[str]] = frozenset(
    model_id_list("openai.omit_temperature")
)
OPENAI_NON_CHAT_COMPLETIONS_MODELS: Final[frozenset[str]] = frozenset(
    model_id_list("openai.non_chat_completions")
)

__all__ = [
    "MODEL_CATALOG_PATH",
    "ModelCatalogError",
    "OPENAI_CHAT_JUDGE_MODEL_ID",
    "OPENAI_DEFAULT_MODEL_ID",
    "OPENAI_OMIT_TEMPERATURE_MODELS",
    "OPENAI_NON_CHAT_COMPLETIONS_MODELS",
    "model_id",
    "model_id_list",
]
