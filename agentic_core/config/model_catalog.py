"""Strict model catalog loader for shared provider model identifiers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
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


def catalog_value(path: str) -> Any:
    node: Any = _catalog()
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ModelCatalogError(f"Missing model catalog key: {path}")
        node = node[part]
    return node


def model_id(path: str) -> str:
    node = catalog_value(path)
    if not isinstance(node, str) or not node.strip():
        raise ModelCatalogError(f"Model catalog key must be a non-empty string: {path}")
    return node.strip()


def model_id_list(path: str) -> tuple[str, ...]:
    node = catalog_value(path)
    if not isinstance(node, list) or not all(isinstance(item, str) and item.strip() for item in node):
        raise ModelCatalogError(f"Model catalog key must be a list of non-empty strings: {path}")
    return tuple(item.strip() for item in node)


OPENAI_DEFAULT_MODEL_ID: Final[str] = model_id("openai.default")
OPENAI_CHAT_JUDGE_MODEL_ID: Final[str] = model_id("openai.chat_judge")
OPENAI_SMALL_CLASSIFIER_MODEL_ID: Final[str] = model_id("openai.small_classifier")
OPENAI_OMIT_TEMPERATURE_MODELS: Final[frozenset[str]] = frozenset(
    model_id_list("openai.omit_temperature")
)
OPENAI_NON_CHAT_COMPLETIONS_MODELS: Final[frozenset[str]] = frozenset(
    model_id_list("openai.non_chat_completions")
)
OPENAI_GPT5_FAMILY_PREFIX: Final[str] = model_id("openai.families.gpt5_prefix")
OPENAI_GPT4_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4")
OPENAI_GPT4_0613_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4_0613")
OPENAI_GPT4_32K_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4_32k")
OPENAI_GPT4_32K_0613_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4_32k_0613")
OPENAI_GPT4_TURBO_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4_turbo")
OPENAI_GPT4O_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4o")
OPENAI_GPT4O_VERSIONED_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4o_2024_08_06")
OPENAI_GPT4O_MINI_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4o_mini")
OPENAI_GPT4O_MINI_VERSIONED_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_4o_mini_2024_07_18")
OPENAI_GPT3_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_3")
OPENAI_GPT35_TURBO_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_35_turbo")
OPENAI_GPT35_TURBO_0613_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_35_turbo_0613")
OPENAI_GPT35_TURBO_16K_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_35_turbo_16k")
OPENAI_GPT35_TURBO_16K_0613_MODEL_ID: Final[str] = model_id("openai.legacy.gpt_35_turbo_16k_0613")

ANTHROPIC_DEFAULT_MODEL_ID: Final[str] = model_id("anthropic.default")
ANTHROPIC_HAIKU_MODEL_ID: Final[str] = model_id("anthropic.haiku")
ANTHROPIC_HAIKU_DATED_MODEL_ID: Final[str] = model_id("anthropic.haiku_dated")
ANTHROPIC_HAIKU_4_5_DOT_MODEL_ID: Final[str] = model_id("anthropic.haiku_4_5_dot")
ANTHROPIC_HAIKU_4_5_20251001_MODEL_ID: Final[str] = model_id("anthropic.haiku_4_5_20251001")
ANTHROPIC_SONNET_MODEL_ID: Final[str] = model_id("anthropic.sonnet")
ANTHROPIC_SONNET_4_20250514_MODEL_ID: Final[str] = model_id("anthropic.sonnet_4_20250514")
ANTHROPIC_SONNET_4_5_MODEL_ID: Final[str] = model_id("anthropic.sonnet_4_5")
ANTHROPIC_SONNET_4_5_20250929_MODEL_ID: Final[str] = model_id("anthropic.sonnet_4_5_20250929")
ANTHROPIC_SONNET_4_5_DOT_MODEL_ID: Final[str] = model_id("anthropic.sonnet_4_5_dot")
ANTHROPIC_OPUS_MODEL_ID: Final[str] = model_id("anthropic.opus")
ANTHROPIC_OPUS_4_5_MODEL_ID: Final[str] = model_id("anthropic.opus_4_5")
ANTHROPIC_OPUS_4_7_DOT_MODEL_ID: Final[str] = model_id("anthropic.opus_4_7_dot")
ANTHROPIC_GENERIC_CLAUDE3_MODEL_ID: Final[str] = model_id("anthropic.generic.claude_3")
ANTHROPIC_GENERIC_INSTANT_MODEL_ID: Final[str] = model_id("anthropic.generic.instant")
ANTHROPIC_GENERIC_OPUS_MODEL_ID: Final[str] = model_id("anthropic.generic.opus")
ANTHROPIC_GENERIC_FABLE_MODEL_ID: Final[str] = model_id("anthropic.generic.fable")
ANTHROPIC_GENERIC_HAIKU_MODEL_ID: Final[str] = model_id("anthropic.generic.haiku")
ANTHROPIC_GENERIC_SONNET_MODEL_ID: Final[str] = model_id("anthropic.generic.sonnet")
ANTHROPIC_LEGACY_HAIKU_3_MODEL_ID: Final[str] = model_id("anthropic.legacy.haiku_3")
ANTHROPIC_LEGACY_HAIKU_3_20240307_MODEL_ID: Final[str] = model_id(
    "anthropic.legacy.haiku_3_20240307"
)
ANTHROPIC_LEGACY_SONNET_35_MODEL_ID: Final[str] = model_id("anthropic.legacy.sonnet_35_latest")
ANTHROPIC_LEGACY_SONNET_35_20241022_MODEL_ID: Final[str] = model_id(
    "anthropic.legacy.sonnet_35_20241022"
)

GEMINI_FLASH_MODEL_ID: Final[str] = model_id("gemini.flash")
GEMINI_PRO_MODEL_ID: Final[str] = model_id("gemini.pro")
GEMINI_PRO_LEGACY_MODEL_ID: Final[str] = model_id("gemini.legacy.gemini_pro")
GEMINI_15_FLASH_MODEL_ID: Final[str] = model_id("gemini.legacy.flash_15")
GEMINI_15_PRO_MODEL_ID: Final[str] = model_id("gemini.legacy.pro_15")
GEMINI_20_FLASH_MODEL_ID: Final[str] = model_id("gemini.legacy.flash_20")
GEMINI_20_FLASH_EXP_MODEL_ID: Final[str] = model_id("gemini.legacy.flash_20_exp")
GEMINI_25_FLASH_MODEL_ID: Final[str] = model_id("gemini.legacy.flash_25")
GEMINI_25_PRO_MODEL_ID: Final[str] = model_id("gemini.legacy.pro_25")
GEMINI_3_PRO_PREVIEW_MODEL_ID: Final[str] = model_id("gemini.legacy.pro_3_preview")
GEMINI_2_FAMILY_PREFIX: Final[str] = model_id("gemini.families.v2_prefix")
GEMINI_3_FAMILY_PREFIX: Final[str] = model_id("gemini.families.v3_prefix")

QWEN_LOCAL_MODEL_ID: Final[str] = model_id("qwen.local_32b_awq")
QWEN_32B_INSTRUCT_MODEL_ID: Final[str] = model_id("qwen.local_32b_instruct")
QWEN_14B_AWQ_MODEL_ID: Final[str] = model_id("qwen.local_14b_awq")
QWEN_14B_INSTRUCT_MODEL_ID: Final[str] = model_id("qwen.local_14b_instruct")
QWEN_7B_INSTRUCT_MODEL_ID: Final[str] = model_id("qwen.local_7b_instruct")
QWEN_VLLM_LABEL: Final[str] = model_id("qwen.vllm_label")

BGE_M3_MODEL_ID: Final[str] = model_id("embedding.bge_m3")
BGE_M3_VERSION_ID: Final[str] = model_id("embedding.bge_m3_v1")
BGE_LARGE_EN_MODEL_ID: Final[str] = model_id("embedding.bge_large_en_v1_5")
BGE_RERANKER_MODEL_ID: Final[str] = model_id("embedding.bge_reranker_v2_m3")
BGE_RERANKER_BASE_MODEL_ID: Final[str] = model_id("embedding.bge_reranker_base")

__all__ = [
    "ANTHROPIC_DEFAULT_MODEL_ID",
    "ANTHROPIC_GENERIC_CLAUDE3_MODEL_ID",
    "ANTHROPIC_GENERIC_FABLE_MODEL_ID",
    "ANTHROPIC_GENERIC_HAIKU_MODEL_ID",
    "ANTHROPIC_GENERIC_INSTANT_MODEL_ID",
    "ANTHROPIC_GENERIC_OPUS_MODEL_ID",
    "ANTHROPIC_GENERIC_SONNET_MODEL_ID",
    "ANTHROPIC_HAIKU_4_5_20251001_MODEL_ID",
    "ANTHROPIC_HAIKU_4_5_DOT_MODEL_ID",
    "ANTHROPIC_HAIKU_DATED_MODEL_ID",
    "ANTHROPIC_HAIKU_MODEL_ID",
    "ANTHROPIC_LEGACY_HAIKU_3_20240307_MODEL_ID",
    "ANTHROPIC_LEGACY_HAIKU_3_MODEL_ID",
    "ANTHROPIC_LEGACY_SONNET_35_20241022_MODEL_ID",
    "ANTHROPIC_LEGACY_SONNET_35_MODEL_ID",
    "ANTHROPIC_OPUS_MODEL_ID",
    "ANTHROPIC_OPUS_4_5_MODEL_ID",
    "ANTHROPIC_OPUS_4_7_DOT_MODEL_ID",
    "ANTHROPIC_SONNET_4_20250514_MODEL_ID",
    "ANTHROPIC_SONNET_4_5_20250929_MODEL_ID",
    "ANTHROPIC_SONNET_4_5_DOT_MODEL_ID",
    "ANTHROPIC_SONNET_4_5_MODEL_ID",
    "ANTHROPIC_SONNET_MODEL_ID",
    "BGE_LARGE_EN_MODEL_ID",
    "BGE_M3_MODEL_ID",
    "BGE_M3_VERSION_ID",
    "BGE_RERANKER_BASE_MODEL_ID",
    "BGE_RERANKER_MODEL_ID",
    "GEMINI_15_FLASH_MODEL_ID",
    "GEMINI_15_PRO_MODEL_ID",
    "GEMINI_2_FAMILY_PREFIX",
    "GEMINI_20_FLASH_MODEL_ID",
    "GEMINI_20_FLASH_EXP_MODEL_ID",
    "GEMINI_25_FLASH_MODEL_ID",
    "GEMINI_25_PRO_MODEL_ID",
    "GEMINI_3_FAMILY_PREFIX",
    "GEMINI_3_PRO_PREVIEW_MODEL_ID",
    "GEMINI_FLASH_MODEL_ID",
    "GEMINI_PRO_LEGACY_MODEL_ID",
    "GEMINI_PRO_MODEL_ID",
    "MODEL_CATALOG_PATH",
    "ModelCatalogError",
    "OPENAI_CHAT_JUDGE_MODEL_ID",
    "OPENAI_DEFAULT_MODEL_ID",
    "OPENAI_GPT35_TURBO_0613_MODEL_ID",
    "OPENAI_GPT35_TURBO_16K_0613_MODEL_ID",
    "OPENAI_GPT35_TURBO_16K_MODEL_ID",
    "OPENAI_GPT35_TURBO_MODEL_ID",
    "OPENAI_GPT3_MODEL_ID",
    "OPENAI_GPT4_0613_MODEL_ID",
    "OPENAI_GPT4_32K_0613_MODEL_ID",
    "OPENAI_GPT4_32K_MODEL_ID",
    "OPENAI_GPT4O_MINI_MODEL_ID",
    "OPENAI_GPT4O_MINI_VERSIONED_MODEL_ID",
    "OPENAI_GPT4O_MODEL_ID",
    "OPENAI_GPT4O_VERSIONED_MODEL_ID",
    "OPENAI_GPT4_MODEL_ID",
    "OPENAI_GPT4_TURBO_MODEL_ID",
    "OPENAI_GPT5_FAMILY_PREFIX",
    "OPENAI_NON_CHAT_COMPLETIONS_MODELS",
    "OPENAI_OMIT_TEMPERATURE_MODELS",
    "OPENAI_SMALL_CLASSIFIER_MODEL_ID",
    "QWEN_14B_AWQ_MODEL_ID",
    "QWEN_14B_INSTRUCT_MODEL_ID",
    "QWEN_32B_INSTRUCT_MODEL_ID",
    "QWEN_7B_INSTRUCT_MODEL_ID",
    "QWEN_LOCAL_MODEL_ID",
    "QWEN_VLLM_LABEL",
    "catalog_value",
    "model_id",
    "model_id_list",
]
