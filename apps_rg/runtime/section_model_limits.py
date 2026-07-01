"""Provider-neutral section model limits and identity for apps_rg generation.

The generator model identity and runtime context budget are read from
``apps_rg/config/provider_profiles.yaml``. Environment variables may provide
credentials and endpoints, but they do not select apps_rg generator models or
runtime LLM budgets.
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

# Provider-profile SSOT path (apps_rg/config/provider_profiles.yaml). This module
# lives at apps_rg/runtime/, so parents[1] == apps_rg.
_PROVIDER_PROFILES_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1] / "config" / "provider_profiles.yaml"
)


class SectionModelSSOTError(RuntimeError):
    """Raised when apps_rg generation model SSOT cannot be loaded."""


def _strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    for idx, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def _yaml_scalar(value: str) -> Any:
    raw = value.strip()
    if raw in {"", "null", "Null", "NULL", "~"}:
        return None
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    try:
        if "." not in raw:
            return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def _next_yaml_content(lines: list[tuple[int, str]], start_idx: int, parent_indent: int) -> str:
    for indent, content in lines[start_idx:]:
        if indent <= parent_indent:
            return ""
        return content
    return ""


def _parse_provider_profiles_without_yaml(text: str) -> dict[str, Any]:
    """Tiny parser for this repo-owned YAML shape when PyYAML is unavailable."""
    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        stripped_comment = _strip_yaml_comment(raw_line).rstrip()
        if not stripped_comment.strip():
            continue
        indent = len(stripped_comment) - len(stripped_comment.lstrip(" "))
        lines.append((indent, stripped_comment.strip()))

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    for idx, (indent, content) in enumerate(lines):
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise SectionModelSSOTError(f"Invalid indentation in {_PROVIDER_PROFILES_PATH}")
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                raise SectionModelSSOTError(f"Invalid list entry in {_PROVIDER_PROFILES_PATH}: {content}")
            parent.append(_yaml_scalar(content[2:]))
            continue
        key, sep, value = content.partition(":")
        if not sep or not key.strip():
            raise SectionModelSSOTError(f"Invalid mapping entry in {_PROVIDER_PROFILES_PATH}: {content}")
        if not isinstance(parent, dict):
            raise SectionModelSSOTError(f"Invalid nested mapping in {_PROVIDER_PROFILES_PATH}: {content}")
        key = key.strip()
        value = value.strip()
        if value:
            parent[key] = _yaml_scalar(value)
            continue
        next_content = _next_yaml_content(lines, idx + 1, indent)
        child: Any = [] if next_content.startswith("- ") else {}
        parent[key] = child
        stack.append((indent, child))
    return root


def _provider_config() -> dict[str, Any]:
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(_PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
    except ImportError:
        data = _parse_provider_profiles_without_yaml(
            _PROVIDER_PROFILES_PATH.read_text(encoding="utf-8")
        )
    except (AttributeError, OSError, TypeError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        raise SectionModelSSOTError(f"Cannot load apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}") from exc
    if not isinstance(data, dict):
        raise SectionModelSSOTError(f"Invalid apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}")
    return data


def _provider_profiles() -> dict:
    data = _provider_config()
    profiles = (data or {}).get("profiles") or {}
    if not isinstance(profiles, dict):
        raise SectionModelSSOTError(f"Missing profiles block in apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}")
    return profiles


def _runtime_limits() -> dict[str, Any]:
    data = _provider_config()
    limits = data.get("runtime_limits") or {}
    if not isinstance(limits, dict):
        raise SectionModelSSOTError(f"Missing runtime_limits block in apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}")
    return limits


def _runtime_limit_value(path: str) -> Any:
    current: Any = _runtime_limits()
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise SectionModelSSOTError(f"Missing runtime_limits.{path} in {_PROVIDER_PROFILES_PATH}")
        current = current[part]
    return current


def runtime_limit_int(path: str) -> int:
    value = _runtime_limit_value(path)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SectionModelSSOTError(f"runtime_limits.{path} must be an int in {_PROVIDER_PROFILES_PATH}") from exc


def runtime_limit_float(path: str) -> float:
    value = _runtime_limit_value(path)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise SectionModelSSOTError(f"runtime_limits.{path} must be a float in {_PROVIDER_PROFILES_PATH}") from exc


def runtime_limit_str(path: str) -> str:
    value = _runtime_limit_value(path)
    if not isinstance(value, str) or not value.strip():
        raise SectionModelSSOTError(f"runtime_limits.{path} must be a non-empty string in {_PROVIDER_PROFILES_PATH}")
    return value.strip()


def runtime_limit_mapping(path: str) -> dict[str, Any]:
    value = _runtime_limit_value(path)
    if not isinstance(value, dict):
        raise SectionModelSSOTError(f"runtime_limits.{path} must be a mapping in {_PROVIDER_PROFILES_PATH}")
    return dict(value)


SECTION_MODEL_MAX_MODEL_LEN: Final[int] = runtime_limit_int("section_context_window")


def _required_section_model(profile_key: str, section_id: str | None) -> str:
    sid = str(section_id or "").strip().lower()
    if not sid:
        raise SectionModelSSOTError(
            f"Missing section_id for profiles.{profile_key}.model_by_section lookup in {_PROVIDER_PROFILES_PATH}"
        )
    by_section = _ssot_model_by_section(profile_key)
    model = by_section.get(sid)
    if not model:
        raise SectionModelSSOTError(
            f"Missing profiles.{profile_key}.model_by_section.{sid} in {_PROVIDER_PROFILES_PATH}"
        )
    return model


def _selector_models() -> dict[str, dict[str, str]]:
    raw = _provider_config().get("selector_models") or {}
    if not isinstance(raw, dict):
        raise SectionModelSSOTError(f"selector_models must be a mapping in {_PROVIDER_PROFILES_PATH}")
    out: dict[str, dict[str, str]] = {}
    for selector_role, value in raw.items():
        if not isinstance(value, dict):
            raise SectionModelSSOTError(
                f"selector_models.{selector_role} must be a mapping in {_PROVIDER_PROFILES_PATH}"
            )
        provider_key = str(value.get("provider_key") or "").strip()
        model = str(value.get("model") or "").strip()
        if not provider_key or not model:
            raise SectionModelSSOTError(
                f"selector_models.{selector_role} requires provider_key and model in {_PROVIDER_PROFILES_PATH}"
            )
        out[str(selector_role).strip().lower()] = {
            "provider_key": provider_key,
            "model": model,
        }
    return out


def resolve_selector_provider_model(selector_role: str) -> tuple[str, str, str]:
    """Return ``(provider_key, model, model_source)`` for an advisory pool selector."""
    role = str(selector_role or "").strip().lower()
    if not role:
        raise SectionModelSSOTError(f"Missing selector role for selector_models lookup in {_PROVIDER_PROFILES_PATH}")
    selectors = _selector_models()
    row = selectors.get(role)
    if row is None:
        raise SectionModelSSOTError(f"Missing selector_models.{role} in {_PROVIDER_PROFILES_PATH}")
    return (
        row["provider_key"],
        row["model"],
        f"apps_rg/config/provider_profiles.yaml:selector_models.{role}.model",
    )


def selector_role_for_section(section_id: str, *, slot_kind: str | None = None) -> str:
    """Map a section/slot to the selector-model role in provider_profiles.yaml."""
    sid = str(section_id or "").strip().lower()
    kind = str(slot_kind or "").strip().lower()
    if sid == "competencies" and kind == "competencies":
        return "competencies_graph_pool_selector"
    if sid in {"unify_bullets", "ibm_bullets", "insurtech_bullets", "ey_bullets"}:
        return "employment_bullet_pool_selector"
    raise SectionModelSSOTError(f"No selector model configured for section={sid!r} slot_kind={kind!r}")


def _ssot_model_by_section(profile_key: str = "external_claude_generator") -> dict[str, str]:
    """Per-section model pins from the provider-profiles SSOT."""
    profiles = _provider_profiles()
    raw = (profiles.get(profile_key) or {}).get("model_by_section") or {}
    if not isinstance(raw, dict):
        return {}
    return {
        str(k).strip().lower(): str(v).strip()
        for k, v in raw.items()
        if str(k).strip() and str(v).strip()
    }


def resolve_section_generation_model(
    section_id: str | None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """THE single resolver for the apps_rg per-section generator model (SSOT-backed).

    Every apps_rg generation dispatch MUST route the model through this function so the
    provider request carries the per-section model and no other source can win.

    Missing/unknown section ids fail closed. Provider-level default models are intentionally not
    supported for proof-bearing apps_rg lanes.
    """
    _ = environ
    sid = str(section_id or "").strip().lower()
    if not sid:
        raise SectionModelSSOTError(f"Missing section_id for generation model resolution in {_PROVIDER_PROFILES_PATH}")

    matches = [
        (profile_key, models[sid])
        for profile_key in ("external_claude_generator", "external_openai_generator")
        for models in (_ssot_model_by_section(profile_key),)
        if sid in models
    ]
    if len(matches) == 1:
        return matches[0][1]
    if len(matches) > 1:
        profiles = ", ".join(profile_key for profile_key, _model in matches)
        raise SectionModelSSOTError(
            f"Ambiguous generation model pin for section={sid!r}; found in profiles {profiles}"
        )
    raise SectionModelSSOTError(
        f"Missing generation model pin for section={sid!r} in {_PROVIDER_PROFILES_PATH}"
    )


def external_claude_generation_model(
    environ: Mapping[str, str] | None = None,
    *,
    section_id: str | None = None,
) -> str:
    """Claude generator model for one explicit section."""
    return resolve_section_generation_model(section_id, environ)


def external_openai_generation_model(
    environ: Mapping[str, str] | None = None,
    *,
    section_id: str | None = None,
) -> str:
    """OpenAI generator model from apps_rg provider_profiles.yaml.

    OpenAI generator model for one explicit section. Missing/unknown section ids fail closed.
    """
    _ = environ
    return _required_section_model("external_openai_generator", section_id)


def external_openai_generation_model_source(section_id: str | None = None) -> str:
    """YAML path that resolved the OpenAI generation model for runtime receipts."""
    sid = str(section_id or "").strip().lower()
    if sid and sid in _ssot_model_by_section("external_openai_generator"):
        return (
            "apps_rg/config/provider_profiles.yaml:"
            f"profiles.external_openai_generator.model_by_section.{sid}"
        )
    raise SectionModelSSOTError(
        f"Missing profiles.external_openai_generator.model_by_section.{sid or '<empty>'} in {_PROVIDER_PROFILES_PATH}"
    )


# Compatibility labels for legacy PA metadata. These are explicit lane pins, not resolver
# fallbacks; runtime dispatch must call the section-aware resolvers above.
SECTION_MODEL_ID: Final[str] = resolve_section_generation_model("competencies")
DEFAULT_EXTERNAL_CLAUDE_MODEL: Final[str] = resolve_section_generation_model("competencies")
DEFAULT_EXTERNAL_OPENAI_MODEL: Final[str] = external_openai_generation_model(section_id="unify_narrative")

__all__ = [
    "DEFAULT_EXTERNAL_CLAUDE_MODEL",
    "DEFAULT_EXTERNAL_OPENAI_MODEL",
    "SECTION_MODEL_ID",
    "SECTION_MODEL_MAX_MODEL_LEN",
    "SectionModelSSOTError",
    "external_claude_generation_model",
    "external_openai_generation_model",
    "external_openai_generation_model_source",
    "resolve_section_generation_model",
    "resolve_selector_provider_model",
    "runtime_limit_float",
    "runtime_limit_mapping",
    "runtime_limit_int",
    "runtime_limit_str",
    "selector_role_for_section",
]
