"""Phase E.1 W2 — advisory runtime-certification gate tests.

All tests use ``tmp_path`` as ``repo_root`` / baseline location. No real
repo ``artifacts/ledgers/`` is ever written. Fixtures construct synthetic
ledger rows via D.3's public writer (tmp_path-scoped).
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest

from tools.runtime_cert.decisions.cert_decision_ledger import (
    ledger_path_for_app,
    write_cert_decision_record,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    make_certification_decision_record,
)

from ops_scripts.ci import check_runtime_certification as gate


# ---------------------------------------------------------------------------
# Baseline fixture helpers
# ---------------------------------------------------------------------------


def _baseline_text(
    *,
    schema_version: str = gate.SCHEMA_VERSION,
    mode: str = "advisory",
    apps_block: str = "",
) -> str:
    return (
        f'schema_version = "{schema_version}"\n'
        f'mode = "{mode}"\n'
        f"{apps_block}\n"
    )


def _app_block(
    *,
    app_name: str = "apps_research",
    route_shape: str = "R3_grounded_read",
    min_verdict: str = "hold",
    require_ledger: bool = True,
    manifest_hash: str = "",
    notes: str = "test",
) -> str:
    return (
        "[[apps]]\n"
        f'app_name = "{app_name}"\n'
        f'route_shape = "{route_shape}"\n'
        f'expected_runtime_certification_status = "NOT_CERTIFIED"\n'
        f'min_verdict = "{min_verdict}"\n'
        f"require_ledger = {'true' if require_ledger else 'false'}\n"
        f'manifest_hash = "{manifest_hash}"\n'
        f'notes = "{notes}"\n'
    )


def _write_baseline(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "cert_baseline.toml"
    path.write_text(body, encoding="utf-8")
    return path


def _write_decision(
    tmp_path: Path,
    *,
    app_name: str = "apps_research",
    verdict: str = VERDICT_HOLD,
    manifest_hash: str = "a" * 64,
    generated_at: str = "2026-05-01T12:00:00+00:00",
) -> None:
    record = make_certification_decision_record(
        generated_at_utc=generated_at,
        app_name=app_name,
        route_shape="R3_grounded_read",
        manifest_hash=manifest_hash,
        evidence_kind="r3",
        closeout_report_id="co-1",
        closeout_report_hash="b" * 64,
        trace_observed_n=40,
        trace_observed_success_n=35,
        evidence_rate=0.875,
        wilson_lower=0.75,
        z_score=2.0,
        uplift=0.1,
        verdict=verdict,
        failure_reasons=(),
        next_review_utc="2026-06-01T00:00:00+00:00",
    )
    result = write_cert_decision_record(record, repo_root=tmp_path)
    assert result.written or result.already_exists


# ---------------------------------------------------------------------------
# 1-5: baseline-level failures
# ---------------------------------------------------------------------------


def test_baseline_missing_produces_failure(tmp_path: Path) -> None:
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=tmp_path / "nope.toml"
    )
    assert result.failures == (gate.FAILURE_BASELINE_MISSING,)
    assert not result.passed
    assert result.runtime_certification_status == NOT_CERTIFIED


def test_baseline_invalid_schema_version(tmp_path: Path) -> None:
    path = _write_baseline(
        tmp_path,
        _baseline_text(schema_version="wrong-v0", apps_block=_app_block()),
    )
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.failures == (gate.FAILURE_BASELINE_SCHEMA_INVALID,)


def test_baseline_unknown_top_level_key(tmp_path: Path) -> None:
    # Unknown key must be in the root table (before any [[apps]] array-of-table),
    # otherwise TOML binds it to the last-opened table.
    body = (
        f'schema_version = "{gate.SCHEMA_VERSION}"\n'
        f'mode = "advisory"\n'
        f'extra = "nope"\n'
        f"{_app_block()}\n"
    )
    path = _write_baseline(tmp_path, body)
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.failures == (gate.FAILURE_BASELINE_SCHEMA_INVALID,)


def test_baseline_unknown_app_key(tmp_path: Path) -> None:
    body = _baseline_text(apps_block=_app_block() + 'garbage = "x"\n')
    path = _write_baseline(tmp_path, body)
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.failures == (gate.FAILURE_BASELINE_APP_INVALID,)


def test_no_baseline_apps(tmp_path: Path) -> None:
    path = _write_baseline(tmp_path, _baseline_text(apps_block="apps = []\n"))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.failures == (gate.FAILURE_NO_BASELINE_APPS,)
    assert result.checked_apps == 0


# ---------------------------------------------------------------------------
# 6-12: app-level behavior
# ---------------------------------------------------------------------------


def test_app_missing_ledger_when_required(tmp_path: Path) -> None:
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.failure_count == 1
    (app_result,) = result.app_results
    assert app_result.failures == (gate.FAILURE_LEDGER_MISSING,)
    assert not app_result.ledger_present


def test_app_missing_ledger_with_require_ledger_false(tmp_path: Path) -> None:
    path = _write_baseline(
        tmp_path,
        _baseline_text(apps_block=_app_block(require_ledger=False)),
    )
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.passed
    (app_result,) = result.app_results
    assert app_result.warnings == (gate.WARNING_LEDGER_ABSENT_OPTIONAL,)
    assert not app_result.ledger_present


def test_app_empty_ledger(tmp_path: Path) -> None:
    # Create the empty ledger file manually (schema only, no rows).
    from tools.runtime_cert.decisions.cert_decision_ledger import (
        ensure_cert_decision_ledger,
    )

    ensure_cert_decision_ledger(
        ledger_path_for_app("apps_research", repo_root=tmp_path)
    )
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    (app_result,) = result.app_results
    assert app_result.failures == (gate.FAILURE_LEDGER_EMPTY,)
    assert app_result.ledger_present


def test_latest_reject_below_hold_fails(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_REJECT)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    (app_result,) = result.app_results
    assert app_result.failures == (gate.FAILURE_LATEST_DECISION_BELOW_BASELINE,)
    assert app_result.latest_verdict == VERDICT_REJECT


def test_latest_hold_meets_hold_passes(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_HOLD)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.passed
    (app_result,) = result.app_results
    assert app_result.latest_verdict == VERDICT_HOLD


def test_latest_certify_passes_but_status_remains_not_certified(
    tmp_path: Path,
) -> None:
    _write_decision(tmp_path, verdict=VERDICT_CERTIFY)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.passed
    (app_result,) = result.app_results
    assert app_result.latest_verdict == VERDICT_CERTIFY
    assert result.runtime_certification_status == NOT_CERTIFIED


def test_manifest_hash_mismatch_fails(tmp_path: Path) -> None:
    _write_decision(tmp_path, manifest_hash="a" * 64)
    path = _write_baseline(
        tmp_path,
        _baseline_text(apps_block=_app_block(manifest_hash="c" * 64)),
    )
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    (app_result,) = result.app_results
    assert app_result.failures == (gate.FAILURE_MANIFEST_HASH_MISMATCH,)


def test_manifest_hash_empty_skips_check(tmp_path: Path) -> None:
    _write_decision(tmp_path, manifest_hash="a" * 64)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    # manifest_hash in baseline is "" (default) -> skipped; hold>=hold passes
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.passed


# ---------------------------------------------------------------------------
# 13-15: CLI modes
# ---------------------------------------------------------------------------


def test_advisory_cli_returns_zero_on_failures(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_REJECT)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    rc = gate.main(
        ["--repo-root", str(tmp_path), "--baseline", str(path)]
    )
    assert rc == 0


def test_strict_cli_returns_one_on_failures(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_REJECT)
    path = _write_baseline(
        tmp_path,
        _baseline_text(mode="strict_allowed", apps_block=_app_block()),
    )
    rc = gate.main(
        ["--repo-root", str(tmp_path), "--baseline", str(path), "--strict"]
    )
    assert rc == 1


def test_strict_overridden_by_advisory_baseline(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_REJECT)
    path = _write_baseline(
        tmp_path, _baseline_text(mode="advisory", apps_block=_app_block())
    )
    rc = gate.main(
        ["--repo-root", str(tmp_path), "--baseline", str(path), "--strict"]
    )
    assert rc == 0


def test_strict_cli_returns_two_on_gate_abstain(tmp_path: Path) -> None:
    # BASELINE_MISSING in strict mode = abstain, exit 2.
    rc = gate.main(
        [
            "--repo-root",
            str(tmp_path),
            "--baseline",
            str(tmp_path / "nope.toml"),
            "--strict",
        ]
    )
    assert rc == 2


# ---------------------------------------------------------------------------
# 16-17: --report + disclaimer
# ---------------------------------------------------------------------------


def test_report_writes_json_with_disclaimer(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_HOLD)
    baseline_path = _write_baseline(
        tmp_path, _baseline_text(apps_block=_app_block())
    )
    report_path = tmp_path / "report" / "gate.json"
    rc = gate.main(
        [
            "--repo-root",
            str(tmp_path),
            "--baseline",
            str(baseline_path),
            "--report",
            str(report_path),
        ]
    )
    assert rc == 0
    assert report_path.is_file()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["runtime_certification_status"] == NOT_CERTIFIED
    assert "no runtime certification performed" in data["disclaimer"]


def test_report_not_written_without_flag(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_HOLD)
    baseline_path = _write_baseline(
        tmp_path, _baseline_text(apps_block=_app_block())
    )
    gate.main(
        ["--repo-root", str(tmp_path), "--baseline", str(baseline_path)]
    )
    assert not any(tmp_path.rglob("*.json"))


# ---------------------------------------------------------------------------
# 18-20: no-forbidden-imports audit
# ---------------------------------------------------------------------------


_MODULE_SRC = Path(gate.__file__).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "pattern",
    [
        r"\bfrom\s+tools\.spine\.scanner",
        r"\bimport\s+tools\.spine\.scanner",
        r"\bfrom\s+agentic_core\.L\d_",
        r"\bimport\s+agentic_core\.L\d_",
    ],
)
def test_gate_has_no_scanner_or_layer_imports(pattern: str) -> None:
    assert re.search(pattern, _MODULE_SRC) is None


def test_gate_has_no_emitter_imports() -> None:
    # runtime_adg emitter paths are forbidden. Importing read-only ledger / record
    # from tools.runtime_cert is allowed and does not match this pattern.
    assert re.search(r"\btools\.runtime_adg", _MODULE_SRC) is None


@pytest.mark.parametrize(
    "app_pkg",
    [
        "apps_research",
        "apps_knowledge_capture",
        "apps_eval",
        "apps_underwriting_ai",
        "apps_shared",
    ],
)
def test_gate_has_no_app_package_imports(app_pkg: str) -> None:
    # app packages must not appear as real import statements; fixture strings are OK
    assert re.search(rf"\b(?:from|import)\s+{app_pkg}\b", _MODULE_SRC) is None


def test_gate_does_not_import_write_cert_decision_record() -> None:
    assert "write_cert_decision_record" not in _MODULE_SRC


# ---------------------------------------------------------------------------
# 21-24: disclaimer / no real writes / determinism / tomllib
# ---------------------------------------------------------------------------


def test_gate_result_has_non_certification_disclaimer(tmp_path: Path) -> None:
    _write_decision(tmp_path, verdict=VERDICT_HOLD)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert "no runtime certification performed" in result.disclaimer
    assert result.runtime_certification_status == NOT_CERTIFIED
    assert result.runtime_certification_status == NOT_CERTIFIED
    assert NOT_CERTIFIED in result.to_json()


def test_gate_does_not_write_real_repo_ledgers(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    before = sorted((repo_root / "artifacts" / "ledgers").glob(
        "cert_decision_*.sqlite"
    )) if (repo_root / "artifacts" / "ledgers").exists() else []
    _write_decision(tmp_path, verdict=VERDICT_HOLD)
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    after = sorted((repo_root / "artifacts" / "ledgers").glob(
        "cert_decision_*.sqlite"
    )) if (repo_root / "artifacts" / "ledgers").exists() else []
    assert before == after


def test_first_failure_does_not_short_circuit(tmp_path: Path) -> None:
    # Two baseline apps, both failing with LEDGER_MISSING (require_ledger).
    body = _baseline_text(
        apps_block=_app_block(app_name="apps_research")
        + _app_block(app_name="apps_knowledge_capture"),
    )
    path = _write_baseline(tmp_path, body)
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    assert result.checked_apps == 2
    assert result.failure_count == 2
    assert all(
        r.failures == (gate.FAILURE_LEDGER_MISSING,) for r in result.app_results
    )


def test_ledger_read_error_is_caught(tmp_path: Path) -> None:
    # Corrupt the ledger file by writing garbage bytes; D.3 read-back raises.
    ledger_path = ledger_path_for_app("apps_research", repo_root=tmp_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_bytes(b"not a sqlite database")
    path = _write_baseline(tmp_path, _baseline_text(apps_block=_app_block()))
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    (app_result,) = result.app_results
    assert gate.FAILURE_LEDGER_READ_ERROR in app_result.failures
    assert app_result.ledger_present


def test_toml_parsing_uses_stdlib_tomllib() -> None:
    # The module should use stdlib tomllib when available (Python 3.11+).
    import sys as _sys

    if _sys.version_info >= (3, 11):
        assert "tomllib" in _MODULE_SRC
    else:  # pragma: no cover
        assert "tomli" in _MODULE_SRC


def test_deterministic_failure_ordering(tmp_path: Path) -> None:
    # An app failing multiple checks should list failures in the source order
    # defined by _evaluate_app: STATUS_NOT_NOT_CERTIFIED -> BELOW_BASELINE ->
    # MANIFEST_HASH_MISMATCH. Trigger verdict+manifest failures simultaneously.
    _write_decision(tmp_path, verdict=VERDICT_REJECT, manifest_hash="a" * 64)
    body = _baseline_text(
        apps_block=_app_block(min_verdict="hold", manifest_hash="c" * 64)
    )
    path = _write_baseline(tmp_path, body)
    result = gate.check_runtime_certification(
        repo_root=tmp_path, baseline_path=path
    )
    (app_result,) = result.app_results
    assert app_result.failures == (
        gate.FAILURE_LATEST_DECISION_BELOW_BASELINE,
        gate.FAILURE_MANIFEST_HASH_MISMATCH,
    )
