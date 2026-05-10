"""CI gate: apps_lic Exit / X1 / X3 hard-law enforcement.

Gate ID: APPS-LIC-EXIT-W7

Fails when:
  1. apps_lic_exit_binding module is not importable.
  2. exit_finalize_apps_lic is not callable.
  3. exit_finalize_apps_lic does not return X3Disposition.
  4. X3Disposition.eval_score is not None (scalar score must not be authoritative).
  5. A completed L2 does not produce exit_status='success'.
  6. A failed L2 produces outcome_authorized=True (fail-open).
  7. X3Disposition.l5_certification_ref is empty.
  8. gate_verdict_refs does not have exactly 10 entries (X1A-X1J).
  9. sealed_l2_digest does not match SealedL2Artifact.compilation_hash.
  10. Exit source contains forbidden patterns: chromadb, sentence_transformers,
      HopPipelineExecutor, pa_compose, l4_write, state_diff_authorized=True.
  11. proposed_state_diff is mutated by the Exit binding.
  12. X3Disposition.app_id != 'apps_lic'.

Exit codes:
  0 — all checks passed
  1 — one or more violations (fail-closed when APPS_LIC_EXIT_W7_FAIL_CLOSED=1)
  0 — advisory pass with warnings (default, no env var set)

Bypass: APPS_LIC_EXIT_W7_BYPASS=1
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import re
import sys
import textwrap
import uuid
from pathlib import Path
from typing import Any

_BYPASS = os.environ.get("APPS_LIC_EXIT_W7_BYPASS", "").strip() == "1"
_FAIL_CLOSED = os.environ.get("APPS_LIC_EXIT_W7_FAIL_CLOSED", "").strip() == "1"
_EXIT_MODULE = "agentic_core.runtime.exit.apps_lic_exit_binding"

_REPORT_PATH = Path("artifacts/ci/apps_lic_exit_w7_gate.json")


# ------------------------------------------------------------------ helpers --


def _make_sealed_l2(
    *,
    execution_status: str = "completed",
    generated_content: str = "Hi test,",
    compilation_hash: str = "abc123",
) -> Any:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.origin import Origin

    return SealedL2Artifact(
        request_id=uuid.uuid4().hex[:16],
        run_id=uuid.uuid4().hex[:16],
        app_id="apps_lic",
        trace_id=uuid.uuid4().hex[:16],
        execution_status=execution_status,
        generated_content=generated_content,
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff={},
        state_diff_authorized=False,
        compilation_hash=compilation_hash,
        prompt_artifact_digest="pa_digest_001",
        replay_key="rk-ci",
        tenant_id="apps_lic_tenant",
        l5_certification_ref="l2-apps-lic-outreach-message-ag8-w6-f3c2e1",
    )


def _code_only(src: str) -> str:
    lines = [ln for ln in src.splitlines() if not ln.strip().startswith("#")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r'""".*?"""', "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"'''.*?'''", "", cleaned, flags=re.DOTALL)
    return cleaned


# ----------------------------------------------------------------- checks ---


def _check_importable() -> list[str]:
    violations: list[str] = []
    try:
        mod = importlib.import_module(_EXIT_MODULE)
        if not hasattr(mod, "exit_finalize_apps_lic"):
            violations.append("exit_finalize_apps_lic not found in module")
        elif not callable(getattr(mod, "exit_finalize_apps_lic")):
            violations.append("exit_finalize_apps_lic is not callable")
    except ImportError as exc:
        violations.append(f"Module not importable: {exc}")
    return violations


def _check_returns_x3disposition() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.contracts.x3_disposition import X3Disposition
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        if not isinstance(result, X3Disposition):
            violations.append(
                f"exit_finalize_apps_lic returned {type(result).__name__}, expected X3Disposition"
            )
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during X3Disposition check: {exc}")
    return violations


def _check_eval_score_is_none() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        if result.eval_score is not None:
            violations.append(
                f"eval_score={result.eval_score!r} — must be None; scalar score is not authoritative"
            )
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during eval_score check: {exc}")
    return violations


def _check_completed_l2_succeeds() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="completed")
        result = exit_finalize_apps_lic(l2)
        if result.exit_status != "success":
            violations.append(
                f"Completed L2 produced exit_status={result.exit_status!r}, expected 'success'"
            )
        if not result.outcome_authorized:
            violations.append("Completed L2: outcome_authorized=False — should be True")
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during completed-L2 check: {exc}")
    return violations


def _check_failed_l2_denied() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="failed", generated_content="")
        result = exit_finalize_apps_lic(l2)
        if result.outcome_authorized:
            violations.append(
                "Failed L2 produced outcome_authorized=True — fail-open violation"
            )
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during failed-L2 check: {exc}")
    return violations


def _check_cert_ref() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        if not result.l5_certification_ref:
            violations.append("l5_certification_ref is empty")
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during cert-ref check: {exc}")
    return violations


def _check_gate_verdict_refs() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        n = len(result.gate_verdict_refs)
        if n != 10:
            violations.append(f"gate_verdict_refs has {n} entries, expected 10 (X1A-X1J)")
        gate_ids = {ref.split(":")[0] for ref in result.gate_verdict_refs}
        expected = {"X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1H", "X1I", "X1J"}
        missing = expected - gate_ids
        if missing:
            violations.append(f"gate_verdict_refs missing gates: {sorted(missing)}")
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during gate-verdict-refs check: {exc}")
    return violations


def _check_sealed_l2_digest() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(compilation_hash="deadbeef1234")
        result = exit_finalize_apps_lic(l2)
        if result.sealed_l2_digest != "deadbeef1234":
            violations.append(
                f"sealed_l2_digest={result.sealed_l2_digest!r} "
                "does not match SealedL2Artifact.compilation_hash='deadbeef1234'"
            )
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during sealed-l2-digest check: {exc}")
    return violations


def _check_source_forbidden_patterns() -> list[str]:
    violations: list[str] = []
    try:
        mod = importlib.import_module(_EXIT_MODULE)
        src = _code_only(inspect.getsource(mod))
        checks = [
            (r"chromadb", "ChromaDB import/call"),
            (r"sentence_transformers", "sentence_transformers import"),
            (r"SentenceTransformer", "SentenceTransformer usage"),
            (r"HopPipelineExecutor", "HopPipelineExecutor usage (tool/model execution)"),
            (r"pa_compose", "prompt assembly (pa_compose)"),
            (r"pa_compile", "prompt assembly (pa_compile)"),
            (r"state_diff_authorized\s*=\s*True", "state_diff_authorized=True (L4 write)"),
            (r"l4_write\s*\(", "direct l4_write() call"),
        ]
        for pat, label in checks:
            if re.search(pat, src):
                violations.append(f"Forbidden pattern found in Exit source: {label} ({pat!r})")
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during source-pattern check: {exc}")
    return violations


def _check_app_id() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        if result.app_id != "apps_lic":
            violations.append(
                f"X3Disposition.app_id={result.app_id!r}, expected 'apps_lic'"
            )
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during app_id check: {exc}")
    return violations


def _check_proposed_state_diff_inert() -> list[str]:
    violations: list[str] = []
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        exit_finalize_apps_lic(l2)
        if dict(l2.proposed_state_diff) != {}:
            violations.append(
                "Exit binding mutated proposed_state_diff — must remain empty (inert)"
            )
    except Exception as exc:  # noqa: BLE001
        violations.append(f"Exception during state-diff-inert check: {exc}")
    return violations


# ---------------------------------------------------------------- main run --


def main() -> int:
    if _BYPASS:
        print("APPS-LIC-EXIT-W7 BYPASS=1: skipping gate")
        _write_report([], bypassed=True)
        return 0

    print("APPS-LIC-EXIT-W7: running apps_lic Exit / X1 / X3 hard-law gate …")

    all_violations: list[str] = []

    checks = [
        ("importable", _check_importable),
        ("returns_x3disposition", _check_returns_x3disposition),
        ("eval_score_is_none", _check_eval_score_is_none),
        ("completed_l2_succeeds", _check_completed_l2_succeeds),
        ("failed_l2_denied", _check_failed_l2_denied),
        ("cert_ref", _check_cert_ref),
        ("gate_verdict_refs", _check_gate_verdict_refs),
        ("sealed_l2_digest", _check_sealed_l2_digest),
        ("source_forbidden_patterns", _check_source_forbidden_patterns),
        ("app_id", _check_app_id),
        ("proposed_state_diff_inert", _check_proposed_state_diff_inert),
    ]

    for check_name, check_fn in checks:
        v = check_fn()
        if v:
            for msg in v:
                print(f"  [FAIL] {check_name}: {msg}")
                all_violations.append(f"{check_name}: {msg}")
        else:
            print(f"  [OK]   {check_name}")

    _write_report(all_violations)

    if all_violations:
        print(
            f"\nAPPS-LIC-EXIT-W7: {len(all_violations)} violation(s) found."
        )
        if _FAIL_CLOSED:
            print("APPS_LIC_EXIT_W7_FAIL_CLOSED=1: failing CI")
            return 1
        print("Advisory mode: set APPS_LIC_EXIT_W7_FAIL_CLOSED=1 to make this blocking")
        return 0

    print("\nAPPS-LIC-EXIT-W7: all checks passed")
    return 0


def _write_report(violations: list[str], *, bypassed: bool = False) -> None:
    try:
        _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "gate": "APPS-LIC-EXIT-W7",
            "status": "bypassed" if bypassed else ("FAIL" if violations else "OK"),
            "violation_count": len(violations),
            "violations": violations,
        }
        _REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except OSError:
        pass


if __name__ == "__main__":
    sys.exit(main())
