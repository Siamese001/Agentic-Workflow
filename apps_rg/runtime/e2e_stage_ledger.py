"""Hash-chained stage authority for apps_rg full E2E runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import yaml

E2E_STAGE_LEDGER_FILENAME = "e2e_stage_ledger.json"
E2E_LAUNCH_RECEIPT_FILENAME = "e2e_launch_receipt.json"
E2E_STAGE_LEDGER_SCHEMA_VERSION = "apps_rg.e2e_stage_ledger.v1"
E2E_LAUNCH_RECEIPT_SCHEMA_VERSION = "apps_rg.e2e_launch_receipt.v1"
DEFAULT_STAGE_GRAPH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "domain_contract"
    / "e2e_stage_graph.resume_generation.v1.yaml"
)

_ALLOWED_STATUSES = frozenset(
    {"PASS", "FAIL", "BLOCKED", "RETRYABLE", "SKIPPED"}
)
_DEPENDENCY_SUCCESS_STATUSES = frozenset({"PASS", "SKIPPED"})
_TERMINAL_FAILURE_STATUSES = frozenset({"FAIL", "BLOCKED"})


class StageTransitionError(RuntimeError):
    """Raised when a stage attempts an invalid state transition."""


@dataclass(frozen=True, slots=True)
class StageDefinition:
    stage_id: str
    depends_on: tuple[str, ...]
    skip_allowed: bool = False
    terminal_closeout: bool = False


@dataclass(frozen=True, slots=True)
class StageReceipt:
    stage_id: str
    status: str
    attempt: int
    e2e_run_id: str
    child_run_id: str
    reason_code: str
    started_at_utc: str
    finished_at_utc: str
    input_refs: dict[str, Any]
    output_refs: dict[str, Any]
    input_digest: str
    output_digest: str
    previous_receipt_digest: str
    receipt_digest: str


@dataclass(frozen=True, slots=True)
class LedgerVerificationReport:
    valid: bool
    complete: bool
    errors: tuple[str, ...]
    entry_count: int
    terminal_stage: str


@dataclass(frozen=True, slots=True)
class CacheCompletionReport:
    valid: bool
    errors: tuple[str, ...]
    artifact_dir: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _read_graph(path: Path) -> tuple[dict[str, StageDefinition], tuple[str, ...], str]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError(f"unable to load E2E stage graph: {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise RuntimeError("E2E stage graph must be a mapping")
    rows = raw.get("stages")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("E2E stage graph must declare non-empty stages")
    definitions: dict[str, StageDefinition] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("E2E stage graph stage rows must be mappings")
        stage_id = str(row.get("id") or "").strip().upper()
        if not stage_id or stage_id in definitions:
            raise RuntimeError(f"invalid or duplicate E2E stage id: {stage_id!r}")
        definitions[stage_id] = StageDefinition(
            stage_id=stage_id,
            depends_on=tuple(str(item).strip().upper() for item in row.get("depends_on") or ()),
            skip_allowed=bool(row.get("skip_allowed")),
            terminal_closeout=bool(row.get("terminal_closeout")),
        )
    for definition in definitions.values():
        missing = [dep for dep in definition.depends_on if dep not in definitions]
        if missing:
            raise RuntimeError(
                f"E2E stage {definition.stage_id} has unknown dependencies: {missing}"
            )
    success_required = tuple(
        str(item).strip().upper() for item in raw.get("success_required") or ()
    )
    if not success_required or any(item not in definitions for item in success_required):
        raise RuntimeError("E2E stage graph success_required is missing or invalid")
    return definitions, success_required, _digest(raw)


def _entry_digest(entry: Mapping[str, Any]) -> str:
    body = {key: value for key, value in entry.items() if key != "receipt_digest"}
    return _digest(body)


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _latest_by_stage(entries: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    latest: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        latest[str(entry.get("stage_id") or "").upper()] = entry
    return latest


class E2EStageLedger:
    """Append-only logical ledger persisted as one canonical JSON artifact."""

    def __init__(
        self,
        *,
        path: Path,
        graph_path: Path,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        self.path = path
        self.graph_path = graph_path
        self._clock = clock
        self._definitions, self._success_required, self._graph_digest = _read_graph(
            graph_path
        )

    @classmethod
    def create(
        cls,
        *,
        artifact_dir: Path,
        e2e_run_id: str,
        stage_graph_path: Path | None = None,
        clock: Callable[[], str] = _utc_now,
    ) -> E2EStageLedger:
        run_id = str(e2e_run_id or "").strip()
        if not run_id:
            raise ValueError("e2e_run_id is required")
        graph_path = (stage_graph_path or DEFAULT_STAGE_GRAPH).resolve()
        ledger = cls(
            path=Path(artifact_dir) / E2E_STAGE_LEDGER_FILENAME,
            graph_path=graph_path,
            clock=clock,
        )
        if ledger.path.exists():
            raise FileExistsError(f"E2E stage ledger already exists: {ledger.path}")
        created_at = clock()
        payload = {
            "schema_version": E2E_STAGE_LEDGER_SCHEMA_VERSION,
            "e2e_run_id": run_id,
            "created_at_utc": created_at,
            "stage_graph_ref": str(graph_path),
            "stage_graph_digest": ledger._graph_digest,
            "entries": [],
            "ledger_digest": _digest(
                {
                    "e2e_run_id": run_id,
                    "stage_graph_digest": ledger._graph_digest,
                    "receipt_digests": [],
                }
            ),
        }
        ledger.path.parent.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(ledger.path, payload)
        return ledger

    def _load(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StageTransitionError(f"unreadable E2E stage ledger: {exc}") from exc
        if not isinstance(payload, dict):
            raise StageTransitionError("E2E stage ledger is not a JSON object")
        report = verify_e2e_stage_ledger(self.path)
        if not report.valid:
            raise StageTransitionError(
                "cannot append to invalid E2E stage ledger: " + "; ".join(report.errors)
            )
        return payload

    @classmethod
    def open(
        cls,
        *,
        artifact_dir: Path,
        stage_graph_path: Path | None = None,
        clock: Callable[[], str] = _utc_now,
    ) -> E2EStageLedger:
        graph_path = (stage_graph_path or DEFAULT_STAGE_GRAPH).resolve()
        ledger = cls(
            path=Path(artifact_dir) / E2E_STAGE_LEDGER_FILENAME,
            graph_path=graph_path,
            clock=clock,
        )
        if not ledger.path.is_file():
            raise FileNotFoundError(f"E2E stage ledger does not exist: {ledger.path}")
        ledger._load()
        return ledger

    def record(
        self,
        *,
        stage_id: str,
        status: str,
        attempt: int = 1,
        input_refs: Mapping[str, Any] | None = None,
        output_refs: Mapping[str, Any] | None = None,
        reason_code: str = "",
        child_run_id: str = "",
        started_at_utc: str | None = None,
        finished_at_utc: str | None = None,
    ) -> StageReceipt:
        sid = str(stage_id or "").strip().upper()
        stat = str(status or "").strip().upper()
        if sid not in self._definitions:
            raise StageTransitionError(f"unknown E2E stage: {sid!r}")
        if stat not in _ALLOWED_STATUSES:
            raise StageTransitionError(f"invalid E2E stage status: {stat!r}")
        if attempt < 1:
            raise StageTransitionError("attempt must be >= 1")
        definition = self._definitions[sid]
        if stat == "SKIPPED" and not definition.skip_allowed:
            raise StageTransitionError(f"stage {sid} does not allow SKIPPED")

        payload = self._load()
        entries = list(payload.get("entries") or ())
        latest = _latest_by_stage(entries)
        if not definition.terminal_closeout:
            failed = [
                key
                for key, entry in latest.items()
                if str(entry.get("status") or "").upper() in _TERMINAL_FAILURE_STATUSES
            ]
            if failed:
                raise StageTransitionError(
                    f"stage {sid} cannot run after terminal failure in {failed[-1]}"
                )
            missing = [
                dep
                for dep in definition.depends_on
                if dep not in latest
                or str(latest[dep].get("status") or "").upper()
                not in _DEPENDENCY_SUCCESS_STATUSES
            ]
            if missing:
                raise StageTransitionError(
                    f"stage {sid} requires successful dependencies: {', '.join(missing)}"
                )

        previous_stage_entries = [
            entry for entry in entries if str(entry.get("stage_id") or "").upper() == sid
        ]
        expected_attempt = len(previous_stage_entries) + 1
        if attempt != expected_attempt:
            raise StageTransitionError(
                f"stage {sid} requires attempt {expected_attempt}, got {attempt}"
            )
        if previous_stage_entries and str(
            previous_stage_entries[-1].get("status") or ""
        ).upper() != "RETRYABLE":
            raise StageTransitionError(
                f"stage {sid} cannot retry after terminal status "
                f"{previous_stage_entries[-1].get('status')!r}"
            )

        start = started_at_utc or self._clock()
        finish = finished_at_utc or self._clock()
        inputs = dict(input_refs or {})
        outputs = dict(output_refs or {})
        previous_digest = str(entries[-1].get("receipt_digest") or "") if entries else ""
        body = {
            "stage_id": sid,
            "status": stat,
            "attempt": attempt,
            "e2e_run_id": str(payload.get("e2e_run_id") or ""),
            "child_run_id": str(child_run_id or ""),
            "reason_code": str(reason_code or ""),
            "started_at_utc": start,
            "finished_at_utc": finish,
            "input_refs": inputs,
            "output_refs": outputs,
            "input_digest": _digest(inputs),
            "output_digest": _digest(outputs),
            "previous_receipt_digest": previous_digest,
        }
        receipt_payload = {**body, "receipt_digest": _entry_digest(body)}
        entries.append(receipt_payload)
        payload["entries"] = entries
        payload["ledger_digest"] = _digest(
            {
                "e2e_run_id": payload["e2e_run_id"],
                "stage_graph_digest": payload["stage_graph_digest"],
                "receipt_digests": [entry["receipt_digest"] for entry in entries],
            }
        )
        _write_json_atomic(self.path, payload)
        return StageReceipt(**receipt_payload)


def verify_e2e_stage_ledger(path: Path) -> LedgerVerificationReport:
    errors: list[str] = []
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return LedgerVerificationReport(False, False, (f"unreadable:{exc}",), 0, "")
    if not isinstance(payload, dict):
        return LedgerVerificationReport(False, False, ("ledger_not_object",), 0, "")
    graph_ref = Path(str(payload.get("stage_graph_ref") or ""))
    try:
        definitions, success_required, graph_digest = _read_graph(graph_ref)
    except RuntimeError as exc:
        return LedgerVerificationReport(False, False, (f"stage_graph:{exc}",), 0, "")
    if str(payload.get("schema_version") or "") != E2E_STAGE_LEDGER_SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    if str(payload.get("stage_graph_digest") or "") != graph_digest:
        errors.append("stage_graph_digest_mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        errors.append("entries_not_list")
        entries = []
    previous_digest = ""
    latest: dict[str, Mapping[str, Any]] = {}
    attempts: dict[str, int] = {}
    terminal_failure = ""
    for raw in entries:
        if not isinstance(raw, dict):
            errors.append("entry_not_object")
            continue
        sid = str(raw.get("stage_id") or "").upper()
        try:
            attempt = int(raw.get("attempt") or 0)
        except (TypeError, ValueError):
            attempt = 0
            errors.append(f"attempt_invalid:{sid}")
        if sid not in definitions:
            errors.append(f"unknown_stage:{sid}")
            continue
        status = str(raw.get("status") or "").upper()
        if status not in _ALLOWED_STATUSES:
            errors.append(f"status_invalid:{sid}:{status}")
        if str(raw.get("e2e_run_id") or "") != str(payload.get("e2e_run_id") or ""):
            errors.append(f"run_id_mismatch:{sid}:{attempt}")
        expected_attempt = attempts.get(sid, 0) + 1
        if attempt != expected_attempt:
            errors.append(f"attempt_sequence:{sid}:{attempt}:{expected_attempt}")
        attempts[sid] = attempt
        if str(raw.get("previous_receipt_digest") or "") != previous_digest:
            errors.append(f"previous_digest_mismatch:{sid}:{attempt}")
        expected_digest = _entry_digest(raw)
        if str(raw.get("receipt_digest") or "") != expected_digest:
            errors.append(f"receipt_digest_mismatch:{sid}:{attempt}")
        definition = definitions[sid]
        if not definition.terminal_closeout:
            if terminal_failure:
                errors.append(f"stage_after_terminal_failure:{sid}:{terminal_failure}")
            for dep in definition.depends_on:
                dep_status = str(latest.get(dep, {}).get("status") or "").upper()
                if dep_status not in _DEPENDENCY_SUCCESS_STATUSES:
                    errors.append(f"dependency_not_satisfied:{sid}:{dep}")
        if status == "SKIPPED" and not definition.skip_allowed:
            errors.append(f"skip_not_allowed:{sid}")
        if sid in latest and str(latest[sid].get("status") or "").upper() != "RETRYABLE":
            errors.append(f"retry_after_terminal:{sid}:{attempt}")
        if status in _TERMINAL_FAILURE_STATUSES:
            terminal_failure = sid
        latest[sid] = raw
        previous_digest = str(raw.get("receipt_digest") or "")
    expected_ledger_digest = _digest(
        {
            "e2e_run_id": payload.get("e2e_run_id"),
            "stage_graph_digest": payload.get("stage_graph_digest"),
            "receipt_digests": [
                entry.get("receipt_digest") for entry in entries if isinstance(entry, dict)
            ],
        }
    )
    if str(payload.get("ledger_digest") or "") != expected_ledger_digest:
        errors.append("ledger_digest_mismatch")
    complete = not errors and all(
        stage in latest
        and str(latest[stage].get("status") or "").upper()
        in _DEPENDENCY_SUCCESS_STATUSES
        for stage in success_required
    )
    terminal_stage = str(entries[-1].get("stage_id") or "") if entries else ""
    return LedgerVerificationReport(
        valid=not errors,
        complete=complete,
        errors=tuple(errors),
        entry_count=len(entries),
        terminal_stage=terminal_stage,
    )


def emit_e2e_launch_receipt(
    *,
    output_root: Path,
    run_dir: Path,
    e2e_run_id: str,
    command: Sequence[str],
    route_signing_key_id: str,
    baseline_ref: str,
    created_at_utc: str | None = None,
) -> Path:
    root = Path(output_root).resolve()
    target = Path(run_dir).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("run_dir must be contained by output_root") from exc
    if not target.is_dir():
        raise ValueError(f"run_dir does not exist: {target}")
    run_id = str(e2e_run_id or "").strip()
    key_id = str(route_signing_key_id or "").strip()
    if not run_id:
        raise ValueError("e2e_run_id is required")
    payload = {
        "schema_version": E2E_LAUNCH_RECEIPT_SCHEMA_VERSION,
        "e2e_run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "output_root": str(root),
        "run_dir": str(target),
        "command": [str(part) for part in command],
        "route_signing_key_id": key_id,
        "route_signing_key_id_present": bool(key_id),
        "baseline_ref": str(baseline_ref or ""),
        "stage_graph_ref": str(DEFAULT_STAGE_GRAPH.resolve()),
        "stage_graph_digest": _read_graph(DEFAULT_STAGE_GRAPH.resolve())[2],
    }
    payload["launch_digest"] = _digest(payload)
    path = target / E2E_LAUNCH_RECEIPT_FILENAME
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return path


def validate_cached_e2e_completion(
    artifact_dir: Path,
    *,
    require_research_execution: bool = False,
) -> CacheCompletionReport:
    """Require a cache candidate to carry the same terminal proof as a fresh run."""
    root = Path(artifact_dir)
    errors: list[str] = []
    ledger_path = root / E2E_STAGE_LEDGER_FILENAME
    if not ledger_path.is_file():
        errors.append("stage_ledger_missing")
    else:
        ledger_report = verify_e2e_stage_ledger(ledger_path)
        if not ledger_report.valid:
            errors.extend(f"stage_ledger_invalid:{item}" for item in ledger_report.errors)
        if not ledger_report.complete:
            errors.append("stage_ledger_incomplete")
        if require_research_execution:
            try:
                ledger_payload = json.loads(ledger_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                ledger_payload = {}
            entries = ledger_payload.get("entries") if isinstance(ledger_payload, dict) else []
            preflight_entries = [
                entry
                for entry in entries or []
                if isinstance(entry, dict)
                and str(entry.get("stage_id") or "").upper() == "PREFLIGHT"
            ]
            preflight = preflight_entries[-1] if preflight_entries else {}
            if str(preflight.get("status") or "").upper() != "PASS":
                errors.append("preflight_stage_not_passed")
            research_entries = [
                entry
                for entry in entries or []
                if isinstance(entry, dict)
                and str(entry.get("stage_id") or "").upper() == "RESEARCH"
            ]
            research = research_entries[-1] if research_entries else {}
            if str(research.get("status") or "").upper() != "PASS":
                errors.append("research_stage_not_executed")
            research_outputs = research.get("output_refs")
            research_outputs = research_outputs if isinstance(research_outputs, dict) else {}
            if not (
                str(research_outputs.get("research_bridge_response") or "").strip()
                and str(research_outputs.get("delegated_briefing") or "").strip()
            ):
                errors.append("research_stage_evidence_missing")
            research_ref_path = root / "research" / "research_artifact_ref.json"
            try:
                research_ref = json.loads(research_ref_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                research_ref = {}
            required_research_paths = (
                "research_artifact_dir",
                "research_briefing_path",
                "research_company_brief_path",
                "research_envelope_path",
            )
            if not isinstance(research_ref, dict) or not str(
                research_ref.get("research_run_id") or ""
            ).strip():
                errors.append("research_artifact_ref_invalid")
            for field in required_research_paths:
                raw_path = str(research_ref.get(field) or "").strip()
                path = Path(raw_path) if raw_path else Path()
                path_exists = path.is_dir() if field == "research_artifact_dir" else path.is_file()
                if not raw_path or not path_exists:
                    errors.append(f"research_producer_path_missing:{field}")

    post_x3_path = root / "apps_rg_post_x3_completion_receipt.json"
    try:
        post_x3 = json.loads(post_x3_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        post_x3 = {}
    if not isinstance(post_x3, dict) or not (
        post_x3.get("completed") is True
        and post_x3.get("x3_to_uwg_to_eval_to_l6_completed") is True
        and post_x3.get("durable_promotion_committed") is True
    ):
        errors.append("post_x3_incomplete")

    from apps_rg.runtime.run_output_contract import MANDATORY_OUTPUT_FILENAMES

    for filename in MANDATORY_OUTPUT_FILENAMES:
        path = root / filename
        try:
            present = path.is_file() and path.stat().st_size > 0
        except OSError:
            present = False
        if not present:
            errors.append(f"mandatory_output_missing:{filename}")
    return CacheCompletionReport(
        valid=not errors,
        errors=tuple(errors),
        artifact_dir=str(root.resolve()),
    )


__all__ = [
    "DEFAULT_STAGE_GRAPH",
    "E2E_LAUNCH_RECEIPT_FILENAME",
    "E2E_STAGE_LEDGER_FILENAME",
    "E2EStageLedger",
    "CacheCompletionReport",
    "LedgerVerificationReport",
    "StageReceipt",
    "StageTransitionError",
    "emit_e2e_launch_receipt",
    "validate_cached_e2e_completion",
    "verify_e2e_stage_ledger",
]
