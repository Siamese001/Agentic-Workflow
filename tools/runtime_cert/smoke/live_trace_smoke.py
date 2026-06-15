"""Non-promoting live-trace smoke harness — Phase C.6.

First end-to-end wiring of the Phase C.1→C.2→C.3 pipeline on a real
runtime-ADG snapshot, scoped to a single app (``apps_research``) per the
Phase C.6 Author-Gate.

Design references
-----------------
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md``
- C.1 adapter:  ``tools/runtime_cert/runtime_adg_query_adapter.py``
- C.2 normalizer: ``tools/runtime_cert/trace_row_normalizer.py``
- C.3 extractor: ``tools/runtime_cert/extractors/r3_evidence.py``
- B.2 schema:   ``system_learning/runtime_adg/app_route_contracts.py``
  (``build_r3_grounded_read_contract``)
- B.3 hash:     ``system_learning/runtime_adg/manifest_hash.py``
  (``compute_manifest_hash_for_app``)
- Snapshot:     ``system_learning/runtime_adg/snapshot.py``

What this module does
---------------------
- Loads a runtime-ADG snapshot JSON file from disk.
- Computes the ``apps_research`` manifest hash via B.3 helper.
- Builds a canonical R3 contract via B.2 factory.
- Runs C.1 row iteration, filters to ``apps_research`` rows only.
- Normalizes rows via C.2 with the contract's bindings.
- Runs C.3 ``extract_r3_evidence`` to produce an evidence report.
- Packages the result in a ``LiveTraceSmokeReport`` (also frozen-dataclass).
- Optionally writes the report as JSON with explicit NOT_CERTIFIED
  disclaimer.

What this module does NOT do
----------------------------
- Does NOT certify any app.
- Does NOT write to any production store.
- Does NOT modify emitters, scanners, CI gates, or app behavior.
- Does NOT rename spans or alter classification.
- Does NOT run on any app other than ``apps_research`` (first smoke app
  per C.6 Author-Gate decision).
- Does NOT promote ``runtime_certification_status`` — always NOT_CERTIFIED.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration (required for all runtime-cert tools).
__adg_consumer_mode__ = "runtime_cert_read"

import json
import logging
import os
from importlib import import_module
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from tools.runtime_cert.extractors.r3_evidence import (
    R3EvidenceReport,
    extract_r3_evidence,
)
from tools.runtime_cert.runtime_adg_query_adapter import (
    NOT_CERTIFIED,
    build_test_snapshot,
    iter_rows_from_snapshot,
)
from tools.runtime_cert.trace_row_normalizer import normalize_trace_rows

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Only app supported by Phase C.6 smoke harness per Author-Gate decision.
SMOKE_APP_NAME: Final[str] = "apps_research"

#: Env var that must equal this value during smoke runs (CC-SHARED-05
#: full-stack assertion — matrix v2 §6.3 option b).
REQUIRED_ENV_VAR: Final[str] = "AGENTIC_CORE_STACK"
REQUIRED_ENV_VALUE: Final[str] = "full"

#: Default subpath for each app's manifest (matches B.3 helper default).
_MANIFEST_SUBPATH: Final[str] = "spine_manifest.yaml"

#: Phase C.6 static runtime mode — reflects snapshot-based evidence,
#: NOT runtime certification. Used only in the report for provenance.
_STATIC_RUNTIME_MODE_C6: Final[str] = "APP_OVERLAY_STATIC_EVIDENCE"

#: Non-promoting disclaimer embedded in every emitted report.
REPORT_DISCLAIMER: Final[str] = (
    "no runtime certification performed — this is Phase C.6 non-promoting "
    "evidence only"
)


def _compute_manifest_hash_for_app(app_name: str, repo_root: str | Path | None) -> str:
    helper = import_module(
        "agentic_core.L6_system_learning.manifest_hash"
    ).compute_manifest_hash_for_app
    return helper(app_name, repo_root=repo_root)


def _build_r3_grounded_read_contract(**kwargs: Any) -> Any:
    helper = import_module(
        "agentic_core.L6_system_learning.app_route_contracts"
    ).build_r3_grounded_read_contract
    return helper(**kwargs)


# ---------------------------------------------------------------------------
# LiveTraceSmokeReport
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LiveTraceSmokeReport:
    """Snapshot-level smoke report for one app (Phase C.6).

    ``runtime_certification_status`` is always ``NOT_CERTIFIED`` —
    ``__post_init__`` raises ``ValueError`` on any other value.

    ``passed_trace_observed`` signals Phase D readiness only — it does NOT
    promote the certification status.
    """

    app_name: str
    route_shape: str
    snapshot_path: str
    manifest_hash: str
    static_runtime_mode: str
    runtime_certification_status: str
    c1_row_count: int
    c2_normalized_row_count: int
    observed_contracts: tuple[str, ...]
    missing_contracts: tuple[str, ...]
    attribute_hardening_required: tuple[str, ...]
    unknown_needs_runtime_run: tuple[str, ...]
    forbidden_violations_count: int
    passed_trace_observed: bool
    evidence_report: R3EvidenceReport
    failure_reasons: tuple[str, ...]
    notes: str

    # Back-compat accessor for task spec field name `forbidden_violations`.
    forbidden_violations: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"LiveTraceSmokeReport.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C.6 never writes a certification verdict."
            )

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable representation.

        Always includes a top-level ``disclaimer`` string so operators who
        read the file outside this codebase see the NOT_CERTIFIED constraint
        without reading the code.
        """
        return {
            "disclaimer": REPORT_DISCLAIMER,
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "snapshot_path": self.snapshot_path,
            "manifest_hash": self.manifest_hash,
            "static_runtime_mode": self.static_runtime_mode,
            "runtime_certification_status": self.runtime_certification_status,
            "c1_row_count": self.c1_row_count,
            "c2_normalized_row_count": self.c2_normalized_row_count,
            "observed_contracts": list(self.observed_contracts),
            "missing_contracts": list(self.missing_contracts),
            "attribute_hardening_required": list(self.attribute_hardening_required),
            "unknown_needs_runtime_run": list(self.unknown_needs_runtime_run),
            "forbidden_violations_count": self.forbidden_violations_count,
            "passed_trace_observed": self.passed_trace_observed,
            "evidence_report": self.evidence_report.to_dict(),
            "failure_reasons": list(self.failure_reasons),
            "notes": self.notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Public harness
# ---------------------------------------------------------------------------


def run_apps_research_live_trace_smoke(
    snapshot_path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> LiveTraceSmokeReport:
    """Run the Phase C.6 non-promoting live-trace smoke for ``apps_research``.

    Parameters
    ----------
    snapshot_path:
        Path to a JSON file containing a ``RuntimeADGSnapshot.to_dict()``
        serialization. Must exist and be readable.
    repo_root:
        Optional override for manifest-hash resolution; forwarded to
        :func:`compute_manifest_hash_for_app`. Defaults to the inferred
        repo root.

    Returns
    -------
    LiveTraceSmokeReport
        Structured report. ``runtime_certification_status`` is always
        ``NOT_CERTIFIED``.

    Raises
    ------
    RuntimeError
        If ``AGENTIC_CORE_STACK`` is not set to ``"full"`` in the
        environment (CC-SHARED-05 full-stack assertion failure).
    FileNotFoundError
        If ``snapshot_path`` does not exist.
    ValueError
        If the snapshot file is unreadable or does not contain a valid
        snapshot shape.
    """
    # ---- Env-var assertion (CC-SHARED-05 full-stack mode) ----------------
    actual = os.environ.get(REQUIRED_ENV_VAR)
    if actual != REQUIRED_ENV_VALUE:
        raise RuntimeError(
            f"{REQUIRED_ENV_VAR}={actual!r} — Phase C.6 smoke requires "
            f"{REQUIRED_ENV_VAR}={REQUIRED_ENV_VALUE!r} to assert full-stack "
            "mode (CC-SHARED-05 design-matrix §6.3 option b). Set it in the "
            "environment and re-run."
        )

    # ---- Path validation -------------------------------------------------
    snap_path = Path(snapshot_path)
    if not snap_path.exists():
        raise FileNotFoundError(
            f"Phase C.6 smoke: snapshot path {str(snap_path)!r} does not exist."
        )
    if not snap_path.is_file():
        raise FileNotFoundError(
            f"Phase C.6 smoke: snapshot path {str(snap_path)!r} is not a file."
        )

    # ---- Manifest hash (real file on disk) -------------------------------
    manifest_hash = _compute_manifest_hash_for_app(
        SMOKE_APP_NAME, repo_root=repo_root
    )

    # ---- Canonical R3 contract ------------------------------------------
    contract = _build_r3_grounded_read_contract(
        app_name=SMOKE_APP_NAME,
        manifest_path=f"{SMOKE_APP_NAME}/{_MANIFEST_SUBPATH}",
        manifest_hash=manifest_hash,
        static_runtime_mode=_STATIC_RUNTIME_MODE_C6,
    )

    # ---- Load snapshot ---------------------------------------------------
    snapshot = _load_snapshot_from_path(snap_path)

    # ---- C.1: iterate rows (no app_name override — rely on attrs) -------
    # Passing app_name="" means the row's app_name is pulled from
    # attributes["app_name"] per the C.1 adapter contract.
    all_c1_rows = list(iter_rows_from_snapshot(snapshot))
    c1_apps_research_rows = [
        r for r in all_c1_rows if r.app_name == SMOKE_APP_NAME
    ]

    notes_parts: list[str] = []
    if len(all_c1_rows) > len(c1_apps_research_rows):
        skipped = len(all_c1_rows) - len(c1_apps_research_rows)
        other_apps = sorted(
            {r.app_name for r in all_c1_rows if r.app_name != SMOKE_APP_NAME}
        )
        notes_parts.append(
            f"{skipped} row(s) from other app(s) ({', '.join(other_apps)}) "
            "ignored by smoke filter."
        )
    if not c1_apps_research_rows:
        notes_parts.append(
            f"Snapshot contains no rows with app_name={SMOKE_APP_NAME!r}; "
            "all required R3 contracts will be reported as missing."
        )

    # ---- C.2: normalize ---------------------------------------------------
    normalized = normalize_trace_rows(c1_apps_research_rows, contract.bindings)

    # ---- C.3: evidence ---------------------------------------------------
    evidence = extract_r3_evidence(normalized, contract)

    # ---- Package smoke report --------------------------------------------
    forbidden_violation_dicts: tuple[dict[str, Any], ...] = tuple(
        {
            "span_id": row.span_id,
            "span_name": row.span_name,
            "contract_name": row.contract_name,
            "trace_id": row.trace_id,
            "phase_c_status": row.phase_c_status,
        }
        for row in evidence.forbidden_violations
    )

    # Merge evidence.notes into smoke-level notes for operator convenience.
    if evidence.notes:
        notes_parts.append(f"evidence: {evidence.notes}")

    return LiveTraceSmokeReport(
        app_name=SMOKE_APP_NAME,
        route_shape=contract.route_shape.value,
        snapshot_path=str(snap_path),
        manifest_hash=manifest_hash,
        static_runtime_mode=_STATIC_RUNTIME_MODE_C6,
        runtime_certification_status=NOT_CERTIFIED,
        c1_row_count=len(all_c1_rows),
        c2_normalized_row_count=len(normalized),
        observed_contracts=evidence.observed_contracts,
        missing_contracts=evidence.missing_contracts,
        attribute_hardening_required=evidence.attribute_hardening_required,
        unknown_needs_runtime_run=evidence.unknown_needs_runtime_run,
        forbidden_violations_count=len(evidence.forbidden_violations),
        forbidden_violations=forbidden_violation_dicts,
        passed_trace_observed=evidence.passed_trace_observed,
        evidence_report=evidence,
        failure_reasons=evidence.failure_reasons,
        notes="  ".join(notes_parts) if notes_parts else "",
    )


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------


def write_live_trace_smoke_report(
    report: LiveTraceSmokeReport,
    output_path: str | Path,
) -> Path:
    """Write the smoke report as a JSON file with explicit disclaimer.

    The emitted JSON object is ``report.to_dict()``, which includes a
    top-level ``disclaimer`` field and explicit ``runtime_certification_status``
    field, so a human or downstream tool reading the file sees the
    NOT_CERTIFIED constraint without needing to run any code.

    Parameters
    ----------
    report:
        A ``LiveTraceSmokeReport`` from :func:`run_apps_research_live_trace_smoke`.
    output_path:
        Target path for the JSON file. Parent directories are created.

    Returns
    -------
    Path
        The absolute path of the written file.
    """
    # Enforce the constraint a second time at serialization time — belt and
    # braces. If a caller constructed a report object by hand with an
    # invalid status, __post_init__ would have rejected it; this line just
    # guards against bit-rot.
    if report.runtime_certification_status != NOT_CERTIFIED:
        raise ValueError(
            f"write_live_trace_smoke_report: refusing to write report with "
            f"runtime_certification_status={report.runtime_certification_status!r} "
            f"— only {NOT_CERTIFIED!r} is allowed."
        )

    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.to_json(), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Snapshot loader (local — no production storage-subsystem coupling)
# ---------------------------------------------------------------------------


def _load_snapshot_from_path(path: Path) -> Any:
    """Load a ``RuntimeADGSnapshot`` from a JSON file.

    The file is expected to be the output of ``snapshot.to_dict()`` or an
    equivalent dict with ``trace_id``, ``mission``, ``started_at_utc``,
    ``ended_at_utc``, and ``nodes``. Reconstructs via
    :func:`build_test_snapshot`, which recomputes the content-addressed
    ``snapshot_id`` from the rebuilt structure. This avoids coupling the
    smoke harness to any live storage subsystem.

    Raises
    ------
    ValueError
        If the file is not valid JSON, not a dict, or missing required
        top-level keys.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"Phase C.6 smoke: could not read snapshot at {str(path)!r}: {exc}"
        ) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Phase C.6 smoke: snapshot at {str(path)!r} is not valid JSON: "
            f"{exc.msg} (line {exc.lineno}, col {exc.colno})"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Phase C.6 smoke: snapshot at {str(path)!r} must be a JSON "
            f"object; got {type(data).__name__}."
        )

    required_keys = ("trace_id", "mission", "started_at_utc", "ended_at_utc", "nodes")
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(
            f"Phase C.6 smoke: snapshot at {str(path)!r} missing required "
            f"key(s): {missing}."
        )

    nodes_raw = data.get("nodes") or []
    if not isinstance(nodes_raw, list):
        raise ValueError(
            f"Phase C.6 smoke: snapshot 'nodes' field must be a list; "
            f"got {type(nodes_raw).__name__}."
        )

    return build_test_snapshot(
        trace_id=str(data["trace_id"]),
        nodes=nodes_raw,
        mission=str(data.get("mission", "test")),
        started_at_utc=int(data.get("started_at_utc", 0)),
        ended_at_utc=int(data.get("ended_at_utc", 1)),
    )


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

__all__ = [
    "LiveTraceSmokeReport",
    "REPORT_DISCLAIMER",
    "REQUIRED_ENV_VALUE",
    "REQUIRED_ENV_VAR",
    "SMOKE_APP_NAME",
    "run_apps_research_live_trace_smoke",
    "write_live_trace_smoke_report",
]
