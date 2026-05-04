"""Shared helpers for app-runtime drivers.

All Phase 2 drivers (apps_rfp, apps_research, apps_exec, apps_lic, apps_rg,
apps_eval, apps_shared) follow the same shape:

  1. Lazy-import the app's primary engine module (this triggers real
     lifecycle-trace ``_emit_*`` events via the imported module body).
  2. Pull fixture data from ``ctx.spec.extra_payload``.
  3. Build app-specific user-spec artifacts deterministically.
  4. Wrap each artifact with the canonical ``_proof_trace`` envelope so
     the verifier's artifact-trace-link check passes.
  5. Return ``{kind: relative_path}`` for every file written.

The shared helpers below own the envelope, JSON write, and "import an
engine module to prove the import path is real" idiom.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any


def trace_meta(ctx) -> dict[str, Any]:
    """Stable trace-link envelope — must match the verifier's link check."""
    return {
        "kind": "AppDriverArtifact",
        "app_id": ctx.spec.app_id,
        "request_id": ctx.request_id_hint,
        "run_id": ctx.run_id,
        "trace_id": ctx.trace_id,
        "trace_root": ctx.trace_root,
        "session_id": ctx.session_id,
        "policy_hash": f"ph-{ctx.spec.app_id}",
        "blueprint_hash": f"bp-{ctx.spec.app_id}",
        "replay_key": f"rrk-{ctx.run_id}",
    }


def write_artifact(
    ctx,
    *,
    rel_filename: str,
    payload: Any,
    kind: str | None = None,
) -> tuple[str, str]:
    """Write a JSON artifact under ``ctx.scenario_dir`` and return (kind, rel_path).

    Wraps the payload exactly once with the trace-link envelope. The wrapper
    is byte-identical between two runs with the same seed (no timestamps).
    """
    scenario_dir: Path = ctx.scenario_dir
    scenario_dir.mkdir(parents=True, exist_ok=True)
    full = scenario_dir / rel_filename
    body = {
        "kind": kind or rel_filename.rsplit(".", 1)[0].replace("_", " ").title().replace(" ", ""),
        "payload": payload,
        "_proof_trace": trace_meta(ctx),
    }
    full.write_text(
        json.dumps(body, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return body["kind"], rel_filename


def write_markdown(ctx, *, rel_filename: str, body: str) -> str:
    """Write a markdown artifact under ctx.scenario_dir; returns rel_path.

    Markdown bodies do not carry the JSON envelope but the trace-link is
    embedded as a YAML-style front-matter header for the verifier.
    """
    scenario_dir: Path = ctx.scenario_dir
    scenario_dir.mkdir(parents=True, exist_ok=True)
    full = scenario_dir / rel_filename
    meta = trace_meta(ctx)
    header_lines = [
        "<!--",
        f"run_id: {meta['run_id']}",
        f"trace_id: {meta['trace_id']}",
        f"request_id: {meta['request_id']}",
        f"app_id: {meta['app_id']}",
        f"replay_key: {meta['replay_key']}",
        "-->",
        "",
    ]
    full.write_text("\n".join(header_lines) + body, encoding="utf-8")
    return rel_filename


def import_real_engine(module_path: str) -> tuple[bool, str]:
    """Import an engine module to trigger its lifecycle-trace _emit_* calls.

    Returns (success, detail). Failure is non-fatal — the driver can still
    produce artifacts; the import-failure detail is preserved in the proof.
    """
    try:
        importlib.import_module(module_path)
    except ImportError as exc:
        return False, f"ImportError: {exc!r}"
    except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
        return False, f"InitError: {exc!r}"
    return True, "ok"
