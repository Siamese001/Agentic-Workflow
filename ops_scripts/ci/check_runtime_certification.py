"""Phase E.1 W2 advisory runtime-certification gate.

Read-only consumer of the Phase D cert-decision ledgers. Loads a TOML
baseline, reads per-app ledgers via
``tools.runtime_cert.decisions.cert_decision_ledger.read_cert_decision_records``,
and returns a structured :class:`RuntimeCertGateResult`. Emits warnings in
advisory mode and build-pass/build-fail signals in strict mode.

This module does **no** promotion. Every record it reads carries
``runtime_certification_status = NOT_CERTIFIED`` (enforced at five layers
by Phase D). The gate's exit code is a build signal, never a
certification signal. See ``.windsurf/plans/runtime-cert-e1w2-gate-module-9a4b2e.md``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple, Union

try:  # Python >= 3.11
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - portability fallback
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

from tools.runtime_cert.decisions.cert_decision_ledger import (
    ledger_path_for_app,
    read_cert_decision_records,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    CertificationDecisionRecord,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "e1-baseline-v1"

DEFAULT_BASELINE_RELPATH = Path(
    "docs/reference/runtime_certification/cert_baseline.toml"
)

DISCLAIMER = (
    "no runtime certification performed - this is Phase E.1 advisory "
    "gate output only; runtime_certification_status remains NOT_CERTIFIED"
)

FAILURE_BASELINE_MISSING = "BASELINE_MISSING"
FAILURE_BASELINE_SCHEMA_INVALID = "BASELINE_SCHEMA_INVALID"
FAILURE_BASELINE_APP_INVALID = "BASELINE_APP_INVALID"
FAILURE_LEDGER_MISSING = "LEDGER_MISSING"
FAILURE_LEDGER_EMPTY = "LEDGER_EMPTY"
FAILURE_LATEST_DECISION_BELOW_BASELINE = "LATEST_DECISION_BELOW_BASELINE"
FAILURE_MANIFEST_HASH_MISMATCH = "MANIFEST_HASH_MISMATCH"
FAILURE_STATUS_NOT_NOT_CERTIFIED = "STATUS_NOT_NOT_CERTIFIED"
FAILURE_LEDGER_READ_ERROR = "LEDGER_READ_ERROR"
FAILURE_NO_BASELINE_APPS = "NO_BASELINE_APPS"

FAILURE_CODES = frozenset(
    {
        FAILURE_BASELINE_MISSING,
        FAILURE_BASELINE_SCHEMA_INVALID,
        FAILURE_BASELINE_APP_INVALID,
        FAILURE_LEDGER_MISSING,
        FAILURE_LEDGER_EMPTY,
        FAILURE_LATEST_DECISION_BELOW_BASELINE,
        FAILURE_MANIFEST_HASH_MISMATCH,
        FAILURE_STATUS_NOT_NOT_CERTIFIED,
        FAILURE_LEDGER_READ_ERROR,
        FAILURE_NO_BASELINE_APPS,
    }
)

WARNING_LEDGER_ABSENT_OPTIONAL = "LEDGER_ABSENT_OPTIONAL"
WARNING_LEDGER_EMPTY_OPTIONAL = "LEDGER_EMPTY_OPTIONAL"
WARNING_ADVISORY_FAILURES_SUPPRESSED = "ADVISORY_FAILURES_SUPPRESSED"
WARNING_STRICT_DOWNGRADED_BY_BASELINE = "STRICT_DOWNGRADED_BY_BASELINE"

WARNING_CODES = frozenset(
    {
        WARNING_LEDGER_ABSENT_OPTIONAL,
        WARNING_LEDGER_EMPTY_OPTIONAL,
        WARNING_ADVISORY_FAILURES_SUPPRESSED,
        WARNING_STRICT_DOWNGRADED_BY_BASELINE,
    }
)

VERDICT_ORDER: Mapping[str, int] = {
    VERDICT_REJECT: 0,
    VERDICT_HOLD: 1,
    VERDICT_CERTIFY: 2,
}

_ALLOWED_BASELINE_MODES = frozenset({"advisory", "strict_allowed"})
_ALLOWED_ROUTE_SHAPES = frozenset(
    {
        "R3_grounded_read",
        "build_time_compiler",
        "evaluator_only",
        "core_adjacent_utility",
    }
)
_ALLOWED_TOP_KEYS = frozenset({"schema_version", "mode", "apps"})
_ALLOWED_APP_KEYS = frozenset(
    {
        "app_name",
        "route_shape",
        "expected_runtime_certification_status",
        "min_verdict",
        "require_ledger",
        "manifest_hash",
        "notes",
    }
)


# ---------------------------------------------------------------------------
# Baseline loading
# ---------------------------------------------------------------------------


class BaselineError(Exception):
    """Base class for baseline load / validation failures."""

    code: str = FAILURE_BASELINE_SCHEMA_INVALID


class BaselineMissingError(BaselineError):
    code = FAILURE_BASELINE_MISSING


class BaselineSchemaInvalidError(BaselineError):
    code = FAILURE_BASELINE_SCHEMA_INVALID


class BaselineAppInvalidError(BaselineError):
    code = FAILURE_BASELINE_APP_INVALID


@dataclass(frozen=True)
class BaselineApp:
    app_name: str
    route_shape: str
    expected_runtime_certification_status: str
    min_verdict: str
    require_ledger: bool
    manifest_hash: str
    notes: str


@dataclass(frozen=True)
class RuntimeCertBaseline:
    schema_version: str
    mode: str
    apps: Tuple[BaselineApp, ...]
    source_path: str


def _require_str(obj: Mapping[str, object], key: str, ctx: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise BaselineAppInvalidError(
            f"{ctx}: field '{key}' must be a string, got {type(value).__name__}"
        )
    return value


def _require_bool(obj: Mapping[str, object], key: str, ctx: str) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise BaselineAppInvalidError(
            f"{ctx}: field '{key}' must be a bool, got {type(value).__name__}"
        )
    return value


def _validate_baseline_app(raw: Mapping[str, object], index: int) -> BaselineApp:
    ctx = f"apps[{index}]"
    extra = set(raw.keys()) - _ALLOWED_APP_KEYS
    if extra:
        raise BaselineAppInvalidError(
            f"{ctx}: unknown field(s) {sorted(extra)}"
        )
    missing = _ALLOWED_APP_KEYS - set(raw.keys())
    if missing:
        raise BaselineAppInvalidError(
            f"{ctx}: missing required field(s) {sorted(missing)}"
        )

    app_name = _require_str(raw, "app_name", ctx)
    if not app_name:
        raise BaselineAppInvalidError(f"{ctx}: app_name must be non-empty")

    route_shape = _require_str(raw, "route_shape", ctx)
    if route_shape not in _ALLOWED_ROUTE_SHAPES:
        raise BaselineAppInvalidError(
            f"{ctx}: route_shape '{route_shape}' not in {sorted(_ALLOWED_ROUTE_SHAPES)}"
        )

    expected_status = _require_str(
        raw, "expected_runtime_certification_status", ctx
    )
    if expected_status != NOT_CERTIFIED:
        raise BaselineAppInvalidError(
            f"{ctx}: expected_runtime_certification_status must be "
            f"'{NOT_CERTIFIED}', got '{expected_status}'"
        )

    min_verdict = _require_str(raw, "min_verdict", ctx)
    if min_verdict not in VERDICT_ORDER:
        raise BaselineAppInvalidError(
            f"{ctx}: min_verdict '{min_verdict}' not in {sorted(VERDICT_ORDER)}"
        )

    require_ledger = _require_bool(raw, "require_ledger", ctx)
    manifest_hash = _require_str(raw, "manifest_hash", ctx)
    if manifest_hash and (
        len(manifest_hash) != 64 or not all(c in "0123456789abcdef" for c in manifest_hash)
    ):
        raise BaselineAppInvalidError(
            f"{ctx}: manifest_hash must be empty or 64 lowercase hex chars"
        )
    notes = _require_str(raw, "notes", ctx)

    return BaselineApp(
        app_name=app_name,
        route_shape=route_shape,
        expected_runtime_certification_status=expected_status,
        min_verdict=min_verdict,
        require_ledger=require_ledger,
        manifest_hash=manifest_hash,
        notes=notes,
    )


def load_runtime_cert_baseline(path: Union[str, Path]) -> RuntimeCertBaseline:
    """Load and validate the TOML baseline. Raises :class:`BaselineError` subclasses."""
    resolved = Path(path)
    if not resolved.is_file():
        raise BaselineMissingError(f"baseline not found at {resolved}")

    try:
        with resolved.open("rb") as fh:
            raw = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise BaselineSchemaInvalidError(f"TOML parse error: {exc}") from exc

    if not isinstance(raw, dict):
        raise BaselineSchemaInvalidError("baseline root must be a table")

    extra = set(raw.keys()) - _ALLOWED_TOP_KEYS
    if extra:
        raise BaselineSchemaInvalidError(
            f"unknown top-level key(s) {sorted(extra)}"
        )

    schema_version = raw.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise BaselineSchemaInvalidError(
            f"schema_version must be '{SCHEMA_VERSION}', got {schema_version!r}"
        )

    mode = raw.get("mode")
    if mode not in _ALLOWED_BASELINE_MODES:
        raise BaselineSchemaInvalidError(
            f"mode must be in {sorted(_ALLOWED_BASELINE_MODES)}, got {mode!r}"
        )

    apps_raw = raw.get("apps", [])
    if not isinstance(apps_raw, list):
        raise BaselineSchemaInvalidError("'apps' must be an array")

    apps: list[BaselineApp] = []
    for i, entry in enumerate(apps_raw):
        if not isinstance(entry, dict):
            raise BaselineAppInvalidError(f"apps[{i}]: entry must be a table")
        apps.append(_validate_baseline_app(entry, i))

    return RuntimeCertBaseline(
        schema_version=schema_version,
        mode=mode,
        apps=tuple(apps),
        source_path=str(resolved),
    )


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RuntimeCertAppResult:
    app_name: str
    baseline_status: str  # "gated" | "baseline_invalid"
    latest_verdict: Optional[str]
    latest_decision_id: Optional[str]
    ledger_present: bool
    passed: bool
    failures: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for code in self.failures:
            if code not in FAILURE_CODES:
                raise ValueError(f"unknown failure code {code!r}")
        for code in self.warnings:
            if code not in WARNING_CODES:
                raise ValueError(f"unknown warning code {code!r}")
        # derived invariant
        if self.passed != (not self.failures):
            raise ValueError(
                "app_result.passed must equal (not failures); "
                f"passed={self.passed} failures={self.failures!r}"
            )

    def to_dict(self) -> dict:
        return {
            "app_name": self.app_name,
            "baseline_status": self.baseline_status,
            "latest_verdict": self.latest_verdict,
            "latest_decision_id": self.latest_decision_id,
            "ledger_present": self.ledger_present,
            "passed": self.passed,
            "failures": list(self.failures),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class RuntimeCertGateResult:
    mode: str  # "advisory" | "strict"
    baseline_path: str
    checked_apps: int
    passed: bool
    advisory: bool
    failure_count: int
    failures: Tuple[str, ...]
    warnings: Tuple[str, ...]
    app_results: Tuple[RuntimeCertAppResult, ...]
    runtime_certification_status: str = NOT_CERTIFIED
    disclaimer: str = DISCLAIMER

    def __post_init__(self) -> None:
        if self.mode not in {"advisory", "strict"}:
            raise ValueError(f"mode must be 'advisory' or 'strict', got {self.mode!r}")
        if self.advisory != (self.mode == "advisory"):
            raise ValueError("advisory must equal (mode == 'advisory')")
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                "runtime_certification_status MUST be NOT_CERTIFIED; "
                f"got {self.runtime_certification_status!r}"
            )
        if "no runtime certification performed" not in self.disclaimer:
            raise ValueError(
                "disclaimer must contain the non-promotion phrase"
            )
        for code in self.failures:
            if code not in FAILURE_CODES:
                raise ValueError(f"unknown gate-level failure code {code!r}")
        for code in self.warnings:
            if code not in WARNING_CODES:
                raise ValueError(f"unknown gate-level warning code {code!r}")

        app_failure_total = sum(len(r.failures) for r in self.app_results)
        expected_total = app_failure_total + len(self.failures)
        if self.failure_count != expected_total:
            raise ValueError(
                "failure_count must equal sum(app.failures) + gate.failures; "
                f"got {self.failure_count} expected {expected_total}"
            )
        if self.passed != (self.failure_count == 0):
            raise ValueError(
                "passed must equal (failure_count == 0); "
                f"passed={self.passed} failure_count={self.failure_count}"
            )
        if self.checked_apps != len(self.app_results):
            raise ValueError(
                "checked_apps must equal len(app_results); "
                f"got {self.checked_apps} vs {len(self.app_results)}"
            )

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "baseline_path": self.baseline_path,
            "checked_apps": self.checked_apps,
            "passed": self.passed,
            "advisory": self.advisory,
            "failure_count": self.failure_count,
            "failures": list(self.failures),
            "warnings": list(self.warnings),
            "app_results": [r.to_dict() for r in self.app_results],
            "runtime_certification_status": self.runtime_certification_status,
            "disclaimer": self.disclaimer,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Per-app evaluation
# ---------------------------------------------------------------------------


def _evaluate_app(
    app: BaselineApp, repo_root: Path
) -> RuntimeCertAppResult:
    failures: list[str] = []
    warnings: list[str] = []
    latest_verdict: Optional[str] = None
    latest_decision_id: Optional[str] = None
    ledger_present = False

    ledger_path = ledger_path_for_app(app.app_name, repo_root=repo_root)
    ledger_present = ledger_path.is_file()

    rows: Tuple[CertificationDecisionRecord, ...] = ()
    if ledger_present:
        try:
            rows = read_cert_decision_records(
                app.app_name, repo_root=repo_root
            )
        except (ValueError, sqlite3.Error, OSError) as exc:  # noqa: BLE001
            # D.3 tamper detection surfaces as ValueError; sqlite errors
            # bubble up as OSError subclasses.
            failures.append(FAILURE_LEDGER_READ_ERROR)
            del exc  # retained intentionally; reason code is surfaced instead

    # Ledger presence / emptiness bookkeeping
    if FAILURE_LEDGER_READ_ERROR not in failures:
        if not ledger_present:
            if app.require_ledger:
                failures.append(FAILURE_LEDGER_MISSING)
            else:
                warnings.append(WARNING_LEDGER_ABSENT_OPTIONAL)
        elif not rows:
            if app.require_ledger:
                failures.append(FAILURE_LEDGER_EMPTY)
            else:
                warnings.append(WARNING_LEDGER_EMPTY_OPTIONAL)
        else:
            latest = rows[-1]
            latest_verdict = latest.verdict
            latest_decision_id = latest.decision_id

            # Defense-in-depth status check
            if (
                latest.runtime_certification_status_before != NOT_CERTIFIED
                or latest.runtime_certification_status_after != NOT_CERTIFIED
            ):
                failures.append(FAILURE_STATUS_NOT_NOT_CERTIFIED)

            # Verdict ordering
            want = VERDICT_ORDER[app.min_verdict]
            got = VERDICT_ORDER.get(latest.verdict, -1)
            if got < want:
                failures.append(FAILURE_LATEST_DECISION_BELOW_BASELINE)

            # Manifest hash (only if baseline specified one)
            if app.manifest_hash and latest.manifest_hash != app.manifest_hash:
                failures.append(FAILURE_MANIFEST_HASH_MISMATCH)

    return RuntimeCertAppResult(
        app_name=app.app_name,
        baseline_status="gated",
        latest_verdict=latest_verdict,
        latest_decision_id=latest_decision_id,
        ledger_present=ledger_present,
        passed=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings),
    )


# ---------------------------------------------------------------------------
# Gate entrypoint
# ---------------------------------------------------------------------------


def check_runtime_certification(
    repo_root: Union[str, Path],
    baseline_path: Union[str, Path, None] = None,
    *,
    strict: bool = False,
) -> RuntimeCertGateResult:
    """Run the advisory gate. Never raises on evaluation failures."""
    repo_root_resolved = Path(repo_root).resolve()
    if baseline_path is None:
        baseline_resolved = repo_root_resolved / DEFAULT_BASELINE_RELPATH
    else:
        baseline_resolved = Path(baseline_path)

    gate_failures: list[str] = []
    gate_warnings: list[str] = []
    app_results: Tuple[RuntimeCertAppResult, ...] = ()
    effective_mode = "strict" if strict else "advisory"

    try:
        baseline = load_runtime_cert_baseline(baseline_resolved)
    except BaselineMissingError:
        gate_failures.append(FAILURE_BASELINE_MISSING)
        baseline = None
    except BaselineAppInvalidError:
        gate_failures.append(FAILURE_BASELINE_APP_INVALID)
        baseline = None
    except BaselineSchemaInvalidError:
        gate_failures.append(FAILURE_BASELINE_SCHEMA_INVALID)
        baseline = None

    if baseline is not None:
        # Baseline mode="advisory" overrides --strict per E-AG-5 defense in depth.
        if strict and baseline.mode == "advisory":
            effective_mode = "advisory"
            gate_warnings.append(WARNING_STRICT_DOWNGRADED_BY_BASELINE)

        if not baseline.apps:
            gate_failures.append(FAILURE_NO_BASELINE_APPS)
        else:
            results: list[RuntimeCertAppResult] = []
            for app in baseline.apps:
                results.append(_evaluate_app(app, repo_root_resolved))
            app_results = tuple(results)

    advisory = effective_mode == "advisory"
    app_failure_total = sum(len(r.failures) for r in app_results)
    failure_count = app_failure_total + len(gate_failures)
    passed = failure_count == 0

    if advisory and failure_count > 0:
        gate_warnings.append(WARNING_ADVISORY_FAILURES_SUPPRESSED)

    return RuntimeCertGateResult(
        mode=effective_mode,
        baseline_path=str(baseline_resolved),
        checked_apps=len(app_results),
        passed=passed,
        advisory=advisory,
        failure_count=failure_count,
        failures=tuple(gate_failures),
        warnings=tuple(gate_warnings),
        app_results=app_results,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _format_summary(result: RuntimeCertGateResult) -> str:
    lines = [
        "Runtime Certification Gate (advisory) - Phase E.1",
        f"  mode             : {result.mode}",
        f"  baseline_path    : {result.baseline_path}",
        f"  checked_apps     : {result.checked_apps}",
        f"  passed           : {result.passed}",
        f"  failure_count    : {result.failure_count}",
        f"  runtime_cert_status: {result.runtime_certification_status}",
        f"  disclaimer       : {result.disclaimer}",
    ]
    for r in result.app_results:
        lines.append(
            f"  - {r.app_name}: passed={r.passed} "
            f"latest_verdict={r.latest_verdict} "
            f"ledger_present={r.ledger_present} "
            f"failures={list(r.failures)}"
        )
    return "\n".join(lines)


def _format_failures(result: RuntimeCertGateResult) -> str:
    chunks: list[str] = []
    if result.failures:
        chunks.append("GATE failures: " + ", ".join(result.failures))
    if result.warnings:
        chunks.append("GATE warnings: " + ", ".join(result.warnings))
    for r in result.app_results:
        if r.failures:
            chunks.append(f"APP {r.app_name} failures: " + ", ".join(r.failures))
        if r.warnings:
            chunks.append(f"APP {r.app_name} warnings: " + ", ".join(r.warnings))
    return "\n".join(chunks)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_runtime_certification",
        description=(
            "Advisory runtime-certification gate (Phase E.1). "
            "Non-promoting; runtime_certification_status remains NOT_CERTIFIED."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root (defaults to current directory).",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Path to baseline TOML (defaults to "
        f"<repo_root>/{DEFAULT_BASELINE_RELPATH}).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict exit codes. Advisory baselines override this.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Optional path to write a JSON report.",
    )
    args = parser.parse_args(argv)

    result = check_runtime_certification(
        repo_root=args.repo_root,
        baseline_path=args.baseline,
        strict=args.strict,
    )

    sys.stdout.write(_format_summary(result))
    sys.stdout.write("\n")
    failure_text = _format_failures(result)
    if failure_text:
        sys.stderr.write(failure_text)
        sys.stderr.write("\n")

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(result.to_json(), encoding="utf-8")

    if result.advisory:
        return 0
    # strict mode
    gate_abstain = {
        FAILURE_BASELINE_MISSING,
        FAILURE_NO_BASELINE_APPS,
    }
    if any(code in gate_abstain for code in result.failures):
        return 2
    if result.passed:
        return 0
    return 1


__all__ = [
    "SCHEMA_VERSION",
    "DEFAULT_BASELINE_RELPATH",
    "DISCLAIMER",
    "FAILURE_CODES",
    "WARNING_CODES",
    "VERDICT_ORDER",
    "BaselineError",
    "BaselineMissingError",
    "BaselineSchemaInvalidError",
    "BaselineAppInvalidError",
    "BaselineApp",
    "RuntimeCertBaseline",
    "RuntimeCertAppResult",
    "RuntimeCertGateResult",
    "load_runtime_cert_baseline",
    "check_runtime_certification",
    "main",
]


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
