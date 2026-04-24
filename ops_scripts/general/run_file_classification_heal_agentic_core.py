#!/usr/bin/env python3
"""Run ``FileClassificationAgent`` over ``agentic_core`` and persist a JSON report.

Healing is opt-in. The script tolerates mild agent API differences by trying a
small set of construction and invocation patterns before failing.
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

try:
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR as _AGENTIC_CORE_DIR,
        REPORTS_DIR as _REPORTS_DIR,
    )
except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
    _AGENTIC_CORE_DIR = "agentic_core"
    _REPORTS_DIR = "reports"


@dataclass(slots=True)
class ClassificationResult:
    file: str
    ok: bool
    mode: str
    payload: dict[str, Any] | None
    error: str | None


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / _AGENTIC_CORE_DIR).exists():
            return candidate

    return Path.cwd().resolve()


def _load_agent_class() -> type:
    module = importlib.import_module("agentic_core.L5_safety.reasoning.FileClassificationAgent")
    agent_class = getattr(module, "FileClassificationAgent", None)
    if agent_class is None:
        raise AttributeError("FileClassificationAgent class not found")
    return agent_class


def _build_agent(agent_class: type, enable_healing: bool) -> Any:
    constructor_attempts = [
        {"enable_healing": enable_healing},
        {"healing_enabled": enable_healing},
        {},
    ]
    last_error: Exception | None = None
    for kwargs in constructor_attempts:
        try:
            return agent_class(**kwargs)
        except TypeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return agent_class()


def _invoke_agent(agent: Any, file_path: Path, enable_healing: bool) -> tuple[str, dict[str, Any]]:
    call_attempts: list[tuple[str, str, dict[str, Any]]] = [
        ("classify_file", "classify_file", {"file_path": str(file_path), "enable_healing": enable_healing}),
        ("classify_file", "classify_file", {"path": str(file_path), "enable_healing": enable_healing}),
        ("classify", "classify", {"file_path": str(file_path), "enable_healing": enable_healing}),
        ("run", "run", {"file_path": str(file_path), "enable_healing": enable_healing}),
        ("__call__", "__call__", {"file_path": str(file_path), "enable_healing": enable_healing}),
    ]

    last_error: Exception | None = None
    for mode, attribute_name, kwargs in call_attempts:
        target = getattr(agent, attribute_name, None)
        if target is None or not callable(target):
            continue
        try:
            response = target(**kwargs)
            return mode, _normalize_payload(response)
        except TypeError as exc:
            last_error = exc
        except Exception as exc:  # guardian: allow-broad-exception -- offline tooling, reports failure
            raise RuntimeError(f"Agent call failed for {file_path}: {exc}") from exc

    if last_error is not None:
        raise last_error
    raise AttributeError("No supported agent invocation method found")


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return payload
    if hasattr(payload, "model_dump"):
        return payload.model_dump()  # type: ignore[no-any-return]
    if hasattr(payload, "dict"):
        return payload.dict()  # type: ignore[no-any-return]
    if hasattr(payload, "__dict__"):
        return dict(payload.__dict__)
    return {"value": repr(payload)}


def _iter_target_files(project_root: Path, file_paths: list[str] | None) -> list[Path]:
    if file_paths:
        return [Path(item).expanduser().resolve() for item in file_paths]

    root = project_root / _AGENTIC_CORE_DIR
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.py") if path.is_file() and "__pycache__" not in path.parts)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Optional explicit file list.")
    parser.add_argument("--enable-healing", action="store_true", help="Allow healing-capable agent behavior.")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of files to process.")
    parser.add_argument("--report-path", help="Optional JSON report path.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    project_root = _resolve_project_root()
    files = _iter_target_files(project_root, args.files)
    if args.limit > 0:
        files = files[: args.limit]

    if not files:
        LOGGER.error("No target files found under %s", project_root / _AGENTIC_CORE_DIR)
        return 2

    try:
        agent_class = _load_agent_class()
        agent = _build_agent(agent_class, enable_healing=args.enable_healing)
    except Exception as exc:  # guardian: allow-broad-exception -- offline tooling, reports failure
        LOGGER.error("Failed to initialize FileClassificationAgent: %s", exc)
        return 2

    results: list[ClassificationResult] = []
    for file_path in files:
        try:
            mode, payload = _invoke_agent(agent, file_path, enable_healing=args.enable_healing)
            results.append(ClassificationResult(str(file_path), True, mode, payload, None))
        except Exception as exc:  # guardian: allow-broad-exception -- offline tooling, reports failure
            results.append(ClassificationResult(str(file_path), False, "error", None, str(exc)))

    ok_count = sum(1 for item in results if item.ok)
    error_count = len(results) - ok_count
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "project_root": str(project_root),
        "target_root": str(project_root / _AGENTIC_CORE_DIR),
        "enable_healing": args.enable_healing,
        "processed": len(results),
        "ok": ok_count,
        "errors": error_count,
        "results": [asdict(item) for item in results],
    }

    report_path = (
        Path(args.report_path).expanduser().resolve()
        if args.report_path
        else project_root / _REPORTS_DIR / "file_classification" / "agentic_core_healing_report.json"
    )
    _atomic_write_json(report_path, report)
    LOGGER.info("Wrote report to %s", report_path)
    LOGGER.info("processed=%s ok=%s errors=%s", len(results), ok_count, error_count)
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
