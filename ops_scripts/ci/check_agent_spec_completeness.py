#!/usr/bin/env python3
"""CI gate: AgentSpec completeness across all apps_* domains.

Plan: apps-core-contract-rectification-a8f3c2 Phase 2.3

Checks:
  1. Every apps_* domain has agent_spec_config.py.
  2. Every agent_spec_config.py exports a root AgentSpec class inheriting
     PromptReceptionSpec (adapter_version + exemplar_task_class fields).
  3. Root class has a `version` field.

Exit codes:
  0 — all checks pass
  1 — one or more ERRORs found
  2 — internal error (import failure, etc.)

Environment:
  AGENT_SPEC_COMPLETENESS_FAIL_CLOSED=1  raise exit 1 even on WARNs (default: ERRORs only)
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


ROOT = _bootstrap_repo_root()

APPS = [
    "apps_qna",
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_exec",
    "apps_eval",
    "apps_underwriting_ai",
]

REQUIRED_RECEPTION_FIELDS = ("adapter_version", "exemplar_task_class")


def _check_app(app_id: str, errors: list[str], warnings: list[str]) -> None:
    spec_path = ROOT / app_id / "config" / "agent_spec_config.py"
    if not spec_path.is_file():
        errors.append(f"MISSING_AGENT_SPEC: {app_id} — {spec_path} not found")
        return

    module_name = f"{app_id}.config.agent_spec_config"
    try:
        mod = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"IMPORT_ERROR: {app_id}.config.agent_spec_config — {exc}")
        return

    exported = getattr(mod, "__all__", None)
    if not exported:
        warnings.append(f"NO_ALL: {app_id}.config.agent_spec_config has no __all__")

    # Find root AgentSpec class — prefer *AgentSpecs (multi-agent roots) first,
    # then fall back to *AgentSpec singular only if no plural form is found.
    root_cls = None
    for name in dir(mod):
        obj = getattr(mod, name, None)
        if obj is None or not isinstance(obj, type):
            continue
        if name.endswith("AgentSpecs"):
            root_cls = obj
            break
    if root_cls is None:
        # Fallback: singular *AgentSpec that directly inherits PromptReceptionSpec
        # (avoids matching inner per-agent spec classes that share the suffix)
        for name in dir(mod):
            obj = getattr(mod, name, None)
            if obj is None or not isinstance(obj, type):
                continue
            if name.endswith("AgentSpec"):
                bases = [b.__name__ for b in getattr(obj, "__mro__", ())]
                if "PromptReceptionSpec" in bases:
                    root_cls = obj
                    break

    if root_cls is None:
        errors.append(
            f"NO_ROOT_CLASS: {app_id}.config.agent_spec_config has no *AgentSpecs class"
        )
        return

    # Check PromptReceptionSpec inheritance via field presence
    try:
        import pydantic

        if hasattr(root_cls, "model_fields"):
            field_names = set(root_cls.model_fields.keys())
        else:
            field_names = set(root_cls.__fields__.keys())
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"FIELD_INTROSPECT_WARN: {app_id} — {exc}")
        field_names = set()

    for field in REQUIRED_RECEPTION_FIELDS:
        if field not in field_names:
            errors.append(
                f"MISSING_RECEPTION_FIELD: {app_id}.{root_cls.__name__} "
                f"is missing PromptReceptionSpec field {field!r}"
            )

    if "version" not in field_names:
        warnings.append(
            f"NO_VERSION_FIELD: {app_id}.{root_cls.__name__} has no version field"
        )


def main() -> int:
    fail_closed = os.environ.get("AGENT_SPEC_COMPLETENESS_FAIL_CLOSED", "0") == "1"

    errors: list[str] = []
    warnings: list[str] = []

    print(f"[check_agent_spec_completeness] checking {len(APPS)} apps")
    for idx, app_id in enumerate(APPS, 1):
        print(f"  [{idx}/{len(APPS)}] {app_id}")
        _check_app(app_id, errors, warnings)

    print()
    if warnings:
        for w in warnings:
            print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"ERROR {e}")

    n_err = len(errors)
    n_warn = len(warnings)
    print(f"\nSummary: {n_err} ERROR(s), {n_warn} WARN(s) across {len(APPS)} apps")

    if n_err > 0:
        print("RESULT: FAIL (errors found)")
        return 1
    if fail_closed and n_warn > 0:
        print("RESULT: FAIL (warnings, AGENT_SPEC_COMPLETENESS_FAIL_CLOSED=1)")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
