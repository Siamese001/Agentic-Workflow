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
E2E_STAGE_LEDGER_SEAL_FILENAME = "e2e_stage_ledger_seal_receipt.json"
E2E_LAUNCH_RECEIPT_FILENAME = "e2e_launch_receipt.json"
E2E_STAGE_LEDGER_SCHEMA_VERSION = "apps_rg.e2e_stage_ledger.v1"
E2E_STAGE_LEDGER_V2_SCHEMA_VERSION = "apps_rg.e2e_stage_ledger.v2"
E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION = "apps_rg.e2e_stage_ledger_seal.v1"
E2E_LAUNCH_RECEIPT_SCHEMA_VERSION = "apps_rg.e2e_launch_receipt.v1"
AUTHORITY_CONTRACT_ID = "apps_research_rg_e2e_authority"
AUTHORITY_CONTRACT_REF = (
    "config/certification/apps_research_rg_e2e_authority_contract.v1.json"
)
DEFAULT_AUTHORITY_CONTRACT = Path(__file__).resolve().parents[2] / AUTHORITY_CONTRACT_REF
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
    status_derivation: str = "CALLER_ASSERTED_NON_PRODUCT_COMPATIBILITY"
    authoritative_receipt_ref: str = ""
    authoritative_receipt_sha256: str = ""
    authoritative_receipt_schema_version: str = ""
    authoritative_receipt_byte_length: int = 0
    artifact_bindings: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class LedgerVerificationReport:
    valid: bool
    complete: bool
    errors: tuple[str, ...]
    entry_count: int
    terminal_stage: str
    sealed: bool = False
    ledger_sha256: str = ""


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


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _resolve_contained_artifact(root: Path, artifact_ref: str | Path) -> Path:
    base = Path(root).resolve()
    raw = Path(artifact_ref)
    target = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise StageTransitionError(
            f"authoritative artifact escapes ledger directory: {artifact_ref}"
        ) from exc
    if not target.is_file():
        raise StageTransitionError(f"authoritative artifact is missing: {artifact_ref}")
    return target


def _artifact_binding(root: Path, artifact_ref: str | Path) -> dict[str, Any]:
    target = _resolve_contained_artifact(root, artifact_ref)
    raw = target.read_bytes()
    return {
        "artifact_ref": target.relative_to(Path(root).resolve()).as_posix(),
        "sha256": _sha256_bytes(raw),
        "byte_length": len(raw),
    }


def _receipt_schema_version(payload: Mapping[str, Any]) -> str:
    return str(payload.get("schema_version") or "").strip()


def _derive_receipt_status(payload: Mapping[str, Any], *, status_field: str) -> str:
    if status_field != "status":
        raise StageTransitionError(
            "authoritative ledger receipts must use the canonical 'status' field"
        )
    raw = payload.get(status_field)
    status = str(raw or "").strip().upper()
    aliases = {
        "PASSED": "PASS",
        "SUCCESS": "PASS",
        "FAILED": "FAIL",
        "SKIPPED_NON_PRODUCT": "SKIPPED",
    }
    status = aliases.get(status, status)
    if status not in _ALLOWED_STATUSES:
        raise StageTransitionError(
            f"authoritative receipt field {status_field!r} has no known status: {raw!r}"
        )
    return status


def _derive_product_receipt_status(
    stage_id: str,
    payload: Mapping[str, Any],
) -> str:
    """Derive product-stage state from that stage's frozen receipt semantics."""

    sid = str(stage_id or "").upper()
    if sid == "APPS_RESEARCH_RUNTIME":
        passed = bool(
            payload.get("created_after_exit") is True
            and str(payload.get("exit_disposition_ref") or "").strip()
            and str(payload.get("gate_mesh_result_ref") or "").strip()
            and str(payload.get("sealed_result_ref") or "").strip()
        )
        return "PASS" if passed else "BLOCKED"
    if sid == "APPS_RESEARCH_EXIT":
        try:
            counts_zero = all(
                int(payload.get(field) or 0) == 0
                for field in ("hard_fail_count", "unknown_count", "missing_gate_count")
            )
        except (TypeError, ValueError):
            counts_zero = False
        passed = bool(
            payload.get("x3_code") == "X3D_ALLOW_FINISH"
            and payload.get("required_gates_passed") is True
            and counts_zero
        )
        return "PASS" if passed else "BLOCKED"
    if sid == "HANDOFF_BUNDLE_COMMIT":
        commit = payload.get("commit_protocol")
        passed = bool(
            payload.get("schema_version") == "apps_research.apps_rg_handoff.v2"
            and isinstance(payload.get("identity"), dict)
            and isinstance(commit, dict)
            and str(commit.get("commit_marker_ref") or "").strip()
            and str(commit.get("commit_marker_sha256") or "").strip()
        )
        return "PASS" if passed else "BLOCKED"
    if sid == "UWG_COMMIT":
        return "PASS" if payload.get("commit_status") == "COMMITTED" else "BLOCKED"
    if sid == "PRODUCT_AUTHORIZATION_CLOSE":
        return (
            "PASS"
            if payload.get("authorized") is True
            and payload.get("immutable") is True
            and payload.get("status") == "AUTHORIZED"
            else "BLOCKED"
        )
    return _derive_receipt_status(payload, status_field="status")


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


def _verify_external_seal(
    ledger_path: Path,
    *,
    payload: Mapping[str, Any],
    entry_count: int,
    terminal_stage: str,
) -> tuple[bool, tuple[str, ...], str]:
    seal_path = ledger_path.parent / E2E_STAGE_LEDGER_SEAL_FILENAME
    if not seal_path.exists():
        return False, (), ""
    errors: list[str] = []
    try:
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return True, (f"ledger_seal_unreadable:{type(exc).__name__}",), ""
    if not isinstance(seal, dict):
        return True, ("ledger_seal_not_object",), ""
    ledger_bytes = ledger_path.read_bytes()
    ledger_sha256 = _sha256_bytes(ledger_bytes)
    if str(seal.get("ledger_ref") or "") != ledger_path.name:
        errors.append("ledger_seal_ref_mismatch")
    if str(seal.get("ledger_schema_version") or "") != str(
        payload.get("schema_version") or ""
    ):
        errors.append("ledger_seal_schema_mismatch")
    if str(seal.get("ledger_sha256") or "") != ledger_sha256:
        errors.append("ledger_seal_digest_mismatch")
    try:
        byte_length = int(seal.get("ledger_byte_length"))
    except (TypeError, ValueError):
        byte_length = -1
    if byte_length != len(ledger_bytes):
        errors.append("ledger_seal_byte_length_mismatch")
    try:
        sealed_entry_count = int(seal.get("entry_count"))
    except (TypeError, ValueError):
        sealed_entry_count = -1
    if sealed_entry_count != entry_count:
        errors.append("ledger_seal_entry_count_mismatch")
    if str(seal.get("terminal_stage_id") or "") != terminal_stage:
        errors.append("ledger_seal_terminal_stage_mismatch")
    if str(payload.get("schema_version") or "") == E2E_STAGE_LEDGER_V2_SCHEMA_VERSION:
        if seal.get("schema_version") != E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION:
            errors.append("ledger_seal_schema_version_mismatch")
        if seal.get("authority_contract_id") != AUTHORITY_CONTRACT_ID:
            errors.append("ledger_seal_authority_contract_mismatch")
        if seal.get("terminal_state") != payload.get("terminal_state"):
            errors.append("ledger_seal_terminal_state_mismatch")
    identity = payload.get("identity")
    identity_basis = (
        identity
        if isinstance(identity, dict)
        else {"e2e_run_id": str(payload.get("e2e_run_id") or "")}
    )
    if str(seal.get("identity_sha256") or "") != _digest(identity_basis):
        errors.append("ledger_seal_identity_mismatch")
    return True, tuple(errors), ledger_sha256


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
        _receipt_binding: Mapping[str, Any] | None = None,
        _artifact_bindings: Sequence[Mapping[str, Any]] = (),
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
        if (self.path.parent / E2E_STAGE_LEDGER_SEAL_FILENAME).exists():
            raise StageTransitionError("cannot append to a sealed E2E stage ledger")

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
        receipt_binding = dict(_receipt_binding or {})
        artifact_bindings = tuple(dict(item) for item in _artifact_bindings)
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
            "output_digest": (
                _digest(
                    {
                        "authoritative_receipt_sha256": receipt_binding.get("sha256"),
                        "artifact_bindings": artifact_bindings,
                    }
                )
                if receipt_binding
                else _digest(outputs)
            ),
            "previous_receipt_digest": previous_digest,
            "status_derivation": (
                "AUTHORITATIVE_RECEIPT_BYTES"
                if receipt_binding
                else "CALLER_ASSERTED_NON_PRODUCT_COMPATIBILITY"
            ),
            "authoritative_receipt_ref": str(receipt_binding.get("artifact_ref") or ""),
            "authoritative_receipt_sha256": str(receipt_binding.get("sha256") or ""),
            "authoritative_receipt_schema_version": str(
                receipt_binding.get("schema_version") or ""
            ),
            "authoritative_receipt_byte_length": int(
                receipt_binding.get("byte_length") or 0
            ),
            "artifact_bindings": artifact_bindings,
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

    def record_from_receipt(
        self,
        *,
        stage_id: str,
        receipt_ref: str | Path,
        status_field: str = "status",
        expected_schema_version: str = "",
        artifact_refs: Mapping[str, str | Path] | None = None,
        attempt: int = 1,
        input_refs: Mapping[str, Any] | None = None,
        output_refs: Mapping[str, Any] | None = None,
        reason_code: str = "",
        child_run_id: str = "",
        started_at_utc: str | None = None,
        finished_at_utc: str | None = None,
    ) -> StageReceipt:
        """Record a stage status derived from immutable receipt bytes.

        ``status`` is intentionally absent from this API.  The value is parsed
        from the authoritative receipt, whose exact bytes are bound into the
        entry and re-resolved by ledger verification.
        """

        binding = _artifact_binding(self.path.parent, receipt_ref)
        receipt_path = self.path.parent / binding["artifact_ref"]
        try:
            receipt_payload = json.loads(receipt_path.read_bytes())
        except json.JSONDecodeError as exc:
            raise StageTransitionError(
                f"authoritative receipt is not valid JSON: {receipt_ref}"
            ) from exc
        if not isinstance(receipt_payload, dict):
            raise StageTransitionError("authoritative receipt must be a JSON object")
        schema_version = _receipt_schema_version(receipt_payload)
        if expected_schema_version and schema_version != expected_schema_version:
            raise StageTransitionError(
                "authoritative receipt schema mismatch: "
                f"expected {expected_schema_version!r}, got {schema_version!r}"
            )
        binding["schema_version"] = schema_version
        status = _derive_receipt_status(receipt_payload, status_field=status_field)
        artifacts: list[dict[str, Any]] = []
        for artifact_id, artifact_ref in sorted((artifact_refs or {}).items()):
            artifact = _artifact_binding(self.path.parent, artifact_ref)
            artifact["artifact_id"] = str(artifact_id)
            artifacts.append(artifact)
        outputs = dict(output_refs or {})
        outputs.setdefault("authoritative_receipt", binding["artifact_ref"])
        return self.record(
            stage_id=stage_id,
            status=status,
            attempt=attempt,
            input_refs=input_refs,
            output_refs=outputs,
            reason_code=reason_code,
            child_run_id=child_run_id,
            started_at_utc=started_at_utc,
            finished_at_utc=finished_at_utc,
            _receipt_binding=binding,
            _artifact_bindings=artifacts,
        )

    def seal(
        self,
        *,
        terminal_state: Mapping[str, bool] | None = None,
        require_complete: bool = True,
        sealed_at_utc: str | None = None,
    ) -> Path:
        """Close the ledger with a separate receipt over its exact bytes."""

        seal_path = self.path.parent / E2E_STAGE_LEDGER_SEAL_FILENAME
        if seal_path.exists():
            raise StageTransitionError(f"E2E stage ledger is already sealed: {seal_path}")
        report = verify_e2e_stage_ledger(self.path)
        if not report.valid:
            raise StageTransitionError(
                "cannot seal invalid E2E stage ledger: " + "; ".join(report.errors)
            )
        if require_complete and not report.complete:
            raise StageTransitionError("cannot seal incomplete E2E stage ledger")
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        ledger_bytes = self.path.read_bytes()
        state = {
            "product_authorized": False,
            "pipeline_complete": False,
            "observability_repair_required": False,
            **dict(terminal_state or {}),
        }
        product_v2 = (
            str(payload.get("schema_version") or "") == E2E_STAGE_LEDGER_V2_SCHEMA_VERSION
        )
        identity = payload.get("identity")
        identity_basis = (
            identity
            if isinstance(identity, dict)
            else {"e2e_run_id": str(payload.get("e2e_run_id") or "")}
        )
        seal = {
            "schema_version": (
                E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION
                if product_v2
                else "apps_rg.e2e_stage_ledger_legacy_seal.v1"
            ),
            "authority_contract_id": (
                AUTHORITY_CONTRACT_ID if product_v2 else "NON_PRODUCT_COMPATIBILITY"
            ),
            "identity_sha256": _digest(identity_basis),
            "ledger_ref": self.path.name,
            "ledger_schema_version": str(payload.get("schema_version") or ""),
            "ledger_sha256": _sha256_bytes(ledger_bytes),
            "ledger_byte_length": len(ledger_bytes),
            "entry_count": report.entry_count,
            "terminal_stage_id": report.terminal_stage,
            "terminal_state": state,
            "sealed_at_utc": sealed_at_utc or self._clock(),
        }
        if not product_v2:
            seal["compatibility_classification"] = "NON_PRODUCT_ONLY"
        _write_json_atomic(seal_path, seal)
        return seal_path


def _load_authority_contract(
    path: Path,
) -> tuple[dict[str, dict[str, Any]], tuple[str, ...], str]:
    contract_path = Path(path).resolve()
    try:
        contract_bytes = contract_path.read_bytes()
        payload = json.loads(contract_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"unable to load E2E authority contract: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("contract_id") != AUTHORITY_CONTRACT_ID:
        raise RuntimeError("E2E authority contract id is invalid")
    rows = payload.get("stages")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("E2E authority contract has no stages")
    stages: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("E2E authority contract contains a non-object stage")
        stage_id = str(row.get("stage_id") or "").strip().upper()
        if not stage_id or stage_id in stages:
            raise RuntimeError(f"invalid or duplicate authority stage: {stage_id!r}")
        stages[stage_id] = row
        order.append(stage_id)
    return stages, tuple(order), _sha256_bytes(contract_bytes)


def _validate_product_identity(identity: Mapping[str, Any]) -> None:
    required = {
        "producer_app_id",
        "consumer_app_id",
        "parent_run_id",
        "child_run_id",
        "request_id",
        "trace_root",
        "tenant_id",
        "target_company",
        "target_role",
        "jd_sha256",
        "brief_sha256",
        "policy_hash",
        "blueprint_hash",
        "schema_version",
    }
    missing = sorted(
        field for field in required if not str(identity.get(field) or "").strip()
    )
    if missing:
        raise ValueError("canonical run identity is incomplete: " + ", ".join(missing))
    if str(identity.get("schema_version")) != "apps_research_rg_run_identity.v1":
        raise ValueError("canonical run identity schema_version is invalid")
    for field in ("jd_sha256", "brief_sha256", "policy_hash", "blueprint_hash"):
        value = str(identity.get(field) or "")
        if len(value) != 71 or not value.startswith("sha256:"):
            raise ValueError(f"canonical run identity {field} is not sha256-bound")
        try:
            int(value[7:], 16)
        except ValueError as exc:
            raise ValueError(
                f"canonical run identity {field} is not sha256-bound"
            ) from exc


def _receipt_identity_matches(
    receipt: Mapping[str, Any],
    identity: Mapping[str, Any],
    *,
    stage_id: str = "",
) -> bool:
    embedded = receipt.get("identity")
    if not isinstance(embedded, dict):
        embedded = receipt.get("run_identity")
    if isinstance(embedded, dict):
        return embedded == dict(identity)
    if str(receipt.get("identity_sha256") or "") == _digest(dict(identity)):
        return True
    sid = str(stage_id or "").upper()
    expected = dict(identity)
    if sid == "APPS_RESEARCH_U0":
        return all(
            str(receipt.get(receipt_field) or "")
            == str(expected.get(identity_field) or "")
            for receipt_field, identity_field in (
                ("parent_run_id", "parent_run_id"),
                ("child_run_id", "child_run_id"),
                ("request_id", "request_id"),
                ("trace_root", "trace_root"),
                ("tenant_id", "tenant_id"),
            )
        )
    if sid in {"APPS_RESEARCH_RUNTIME", "APPS_RESEARCH_EXIT"}:
        return all(
            str(receipt.get(receipt_field) or "")
            == str(expected.get(identity_field) or "")
            for receipt_field, identity_field in (
                ("run_id", "child_run_id"),
                ("trace_root", "trace_root"),
            )
        ) and (
            sid != "APPS_RESEARCH_EXIT"
            or str(receipt.get("request_id") or "")
            == str(expected.get("request_id") or "")
        )
    if sid == "UWG_COMMIT":
        return all(
            str(receipt.get(field) or "") == str(expected.get(identity_field) or "")
            for field, identity_field in (
                ("run_id", "parent_run_id"),
                ("request_id", "request_id"),
                ("trace_root", "trace_root"),
            )
        )
    return False


class ReceiptDerivedE2EStageLedger:
    """Product-v2 ledger whose entries can only be created from receipt bytes."""

    def __init__(
        self,
        *,
        path: Path,
        authority_contract_path: Path,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        self.path = Path(path)
        self.authority_contract_path = Path(authority_contract_path).resolve()
        self._clock = clock
        self._stages, self._stage_order, self._contract_sha256 = (
            _load_authority_contract(self.authority_contract_path)
        )

    @classmethod
    def create(
        cls,
        *,
        artifact_dir: Path,
        identity: Mapping[str, Any],
        authority_contract_path: Path = DEFAULT_AUTHORITY_CONTRACT,
        clock: Callable[[], str] = _utc_now,
    ) -> ReceiptDerivedE2EStageLedger:
        canonical_identity = dict(identity)
        _validate_product_identity(canonical_identity)
        ledger = cls(
            path=Path(artifact_dir) / E2E_STAGE_LEDGER_FILENAME,
            authority_contract_path=authority_contract_path,
            clock=clock,
        )
        if ledger.path.exists():
            raise FileExistsError(f"E2E stage ledger already exists: {ledger.path}")
        contract_ref = (
            AUTHORITY_CONTRACT_REF
            if ledger.authority_contract_path == DEFAULT_AUTHORITY_CONTRACT.resolve()
            else str(ledger.authority_contract_path)
        )
        payload = {
            "schema_version": E2E_STAGE_LEDGER_V2_SCHEMA_VERSION,
            "authority_contract_id": AUTHORITY_CONTRACT_ID,
            "identity": canonical_identity,
            "stage_graph": {
                "contract_ref": contract_ref,
                "contract_sha256": ledger._contract_sha256,
                "stage_ids": list(ledger._stage_order),
            },
            "entries": [],
            "terminal_state": {
                "product_authorized": False,
                "pipeline_complete": False,
                "observability_repair_required": False,
            },
        }
        ledger.path.parent.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(ledger.path, payload)
        return ledger

    @classmethod
    def open(
        cls,
        *,
        artifact_dir: Path,
        authority_contract_path: Path = DEFAULT_AUTHORITY_CONTRACT,
        clock: Callable[[], str] = _utc_now,
    ) -> ReceiptDerivedE2EStageLedger:
        ledger = cls(
            path=Path(artifact_dir) / E2E_STAGE_LEDGER_FILENAME,
            authority_contract_path=authority_contract_path,
            clock=clock,
        )
        report = verify_e2e_stage_ledger(ledger.path)
        if not report.valid:
            raise StageTransitionError(
                "cannot open invalid receipt-derived ledger: " + "; ".join(report.errors)
            )
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
                "cannot append to invalid receipt-derived ledger: "
                + "; ".join(report.errors)
            )
        return payload

    def record_from_receipt(
        self,
        *,
        stage_id: str,
        receipt_ref: str | Path,
        status_field: str = "status",
        expected_schema_version: str = "",
        artifact_refs: Sequence[str | Path] = (),
        next_stage_id: str | None = None,
        started_at_utc: str | None = None,
        completed_at_utc: str | None = None,
    ) -> dict[str, Any]:
        if (self.path.parent / E2E_STAGE_LEDGER_SEAL_FILENAME).exists():
            raise StageTransitionError("cannot append to a sealed E2E stage ledger")
        sid = str(stage_id or "").strip().upper()
        if sid not in self._stages:
            raise StageTransitionError(f"unknown authority stage: {sid!r}")
        if sid in {
            "STAGE_LEDGER_SEAL",
            "TERMINAL_MANIFEST_SEAL",
            "PIPELINE_COMPLETION_CLOSE",
        }:
            raise StageTransitionError(
                f"authority stage {sid} is external to the sealed stage ledger"
            )
        payload = self._load()
        identity = payload.get("identity")
        if not isinstance(identity, dict):
            raise StageTransitionError("receipt-derived ledger identity is missing")
        entries = list(payload.get("entries") or ())
        if not entries and sid != "FRESH_PREFLIGHT":
            raise StageTransitionError("first receipt-derived stage must be FRESH_PREFLIGHT")
        if entries:
            expected_stage = entries[-1].get("next_stage_id")
            if sid != expected_stage:
                raise StageTransitionError(
                    f"stage {sid} does not match prior next stage {expected_stage!r}"
                )
        stage_contract = self._stages[sid]
        allowed_next = tuple(
            str(item).upper() for item in stage_contract.get("allowed_next") or ()
        )
        selected_next = str(next_stage_id).upper() if next_stage_id else None
        if selected_next is None and len(allowed_next) == 1:
            selected_next = allowed_next[0]
        if selected_next is not None and selected_next not in allowed_next:
            raise StageTransitionError(
                f"stage {sid} cannot transition to {selected_next}; allowed={allowed_next}"
            )
        if selected_next is None and allowed_next:
            raise StageTransitionError(
                f"stage {sid} has multiple continuations; next_stage_id is required"
            )
        receipt_binding = _artifact_binding(self.path.parent, receipt_ref)
        receipt_path = self.path.parent / receipt_binding["artifact_ref"]
        try:
            receipt = json.loads(receipt_path.read_bytes())
        except json.JSONDecodeError as exc:
            raise StageTransitionError("authoritative receipt is not valid JSON") from exc
        if not isinstance(receipt, dict):
            raise StageTransitionError("authoritative receipt must be a JSON object")
        schema_version = _receipt_schema_version(receipt)
        if not schema_version:
            raise StageTransitionError("authoritative receipt schema_version is missing")
        if expected_schema_version and schema_version != expected_schema_version:
            raise StageTransitionError(
                f"authoritative receipt schema mismatch: {schema_version!r}"
            )
        if not _receipt_identity_matches(receipt, identity, stage_id=sid):
            raise StageTransitionError("authoritative receipt identity does not match ledger")
        if status_field != "status":
            raise StageTransitionError(
                "product ledger receipts must use frozen stage status semantics"
            )
        status = _derive_product_receipt_status(sid, receipt)
        if status in {"FAIL", "BLOCKED"}:
            selected_next = None
        bindings = [
            _artifact_binding(self.path.parent, artifact_ref)
            for artifact_ref in artifact_refs
        ]
        now = self._clock()
        entry = {
            "sequence": len(entries),
            "stage_id": sid,
            "authority_plane": str(stage_contract.get("authority_plane") or ""),
            "status": "SKIPPED_NON_PRODUCT" if status == "SKIPPED" else status,
            "status_derivation": "AUTHORITATIVE_RECEIPT_BYTES",
            "authoritative_receipt_ref": receipt_binding["artifact_ref"],
            "authoritative_receipt_sha256": receipt_binding["sha256"],
            "authoritative_receipt_schema_version": schema_version,
            "identity_sha256": _digest(identity),
            "artifact_bindings": bindings,
            "started_at_utc": started_at_utc or str(
                receipt.get("started_at_utc") or receipt.get("created_at_utc") or now
            ),
            "completed_at_utc": completed_at_utc or str(
                receipt.get("completed_at_utc")
                or receipt.get("finished_at_utc")
                or receipt.get("created_at_utc")
                or now
            ),
            "next_stage_id": selected_next,
        }
        entries.append(entry)
        payload["entries"] = entries
        _write_json_atomic(self.path, payload)
        return entry

    def seal(
        self,
        *,
        terminal_state: Mapping[str, bool],
        sealed_at_utc: str | None = None,
    ) -> Path:
        seal_path = self.path.parent / E2E_STAGE_LEDGER_SEAL_FILENAME
        if seal_path.exists():
            raise StageTransitionError(f"E2E stage ledger is already sealed: {seal_path}")
        payload = self._load()
        entries = payload.get("entries")
        entries = entries if isinstance(entries, list) else []
        if not entries:
            raise StageTransitionError("cannot seal an empty receipt-derived ledger")
        non_success = [
            str(entry.get("stage_id") or "")
            for entry in entries
            if str(entry.get("status") or "") not in {"PASS", "SKIPPED_NON_PRODUCT"}
        ]
        if non_success:
            raise StageTransitionError(
                "cannot seal a ledger containing unsuccessful stages: "
                + ", ".join(non_success)
            )
        state = {
            "product_authorized": bool(terminal_state.get("product_authorized")),
            "pipeline_complete": bool(terminal_state.get("pipeline_complete")),
            "observability_repair_required": bool(
                terminal_state.get("observability_repair_required")
            ),
        }
        if state["pipeline_complete"] and not state["product_authorized"]:
            raise StageTransitionError("pipeline completion requires product authorization")
        if state["observability_repair_required"] != (
            state["product_authorized"] and not state["pipeline_complete"]
        ):
            raise StageTransitionError(
                "repair state must equal product_authorized and not pipeline_complete"
            )
        terminal_stage = str(entries[-1].get("stage_id") or "")
        expected_terminal = (
            "MANDATORY_OUTPUTS"
            if state["product_authorized"]
            else "TERMINAL_NON_PRODUCT"
        )
        if terminal_stage != expected_terminal:
            raise StageTransitionError(
                f"cannot seal product state at {terminal_stage}; expected {expected_terminal}"
            )
        closed_at = sealed_at_utc or self._clock()
        payload["terminal_state"] = state
        payload["closed_at_utc"] = closed_at
        _write_json_atomic(self.path, payload)
        report = verify_e2e_stage_ledger(self.path)
        if not report.valid:
            raise StageTransitionError(
                "cannot seal invalid receipt-derived ledger: " + "; ".join(report.errors)
            )
        ledger_bytes = self.path.read_bytes()
        seal = {
            "schema_version": E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION,
            "authority_contract_id": AUTHORITY_CONTRACT_ID,
            "identity_sha256": _digest(payload["identity"]),
            "ledger_ref": self.path.name,
            "ledger_schema_version": E2E_STAGE_LEDGER_V2_SCHEMA_VERSION,
            "ledger_sha256": _sha256_bytes(ledger_bytes),
            "ledger_byte_length": len(ledger_bytes),
            "entry_count": len(entries),
            "terminal_stage_id": terminal_stage,
            "terminal_state": state,
            "sealed_at_utc": closed_at,
        }
        _write_json_atomic(seal_path, seal)
        return seal_path


def _verify_receipt_derived_v2(
    path: Path,
    payload: Mapping[str, Any],
) -> LedgerVerificationReport:
    errors: list[str] = []
    if payload.get("authority_contract_id") != AUTHORITY_CONTRACT_ID:
        errors.append("authority_contract_id_mismatch")
    identity = payload.get("identity")
    if not isinstance(identity, dict):
        errors.append("identity_missing")
        identity = {}
    else:
        try:
            _validate_product_identity(identity)
        except ValueError as exc:
            errors.append(f"identity_invalid:{exc}")
    stage_graph = payload.get("stage_graph")
    if not isinstance(stage_graph, dict):
        errors.append("stage_graph_missing")
        stage_graph = {}
    contract_ref = str(stage_graph.get("contract_ref") or "")
    contract_path = (
        DEFAULT_AUTHORITY_CONTRACT
        if contract_ref == AUTHORITY_CONTRACT_REF
        else Path(contract_ref)
    )
    try:
        stages, stage_order, contract_sha256 = _load_authority_contract(contract_path)
    except RuntimeError as exc:
        return LedgerVerificationReport(
            False,
            False,
            (f"authority_contract:{exc}",),
            0,
            "",
        )
    if stage_graph.get("contract_sha256") != contract_sha256:
        errors.append("authority_contract_digest_mismatch")
    if stage_graph.get("stage_ids") != list(stage_order):
        errors.append("authority_stage_ids_mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        errors.append("entries_not_list")
        entries = []
    prior_next: str | None = "FRESH_PREFLIGHT"
    for sequence, raw in enumerate(entries):
        if not isinstance(raw, dict):
            errors.append(f"entry_not_object:{sequence}")
            continue
        sid = str(raw.get("stage_id") or "").upper()
        status = str(raw.get("status") or "").upper()
        if raw.get("sequence") != sequence:
            errors.append(f"sequence_mismatch:{sid}:{sequence}")
        if sid != prior_next:
            errors.append(f"stage_order_mismatch:{sid}:{prior_next}")
        if sid not in stages:
            errors.append(f"unknown_stage:{sid}")
            continue
        if sid in {
            "STAGE_LEDGER_SEAL",
            "TERMINAL_MANIFEST_SEAL",
            "PIPELINE_COMPLETION_CLOSE",
        }:
            errors.append(f"external_stage_embedded_in_ledger:{sid}")
        if raw.get("authority_plane") != stages[sid].get("authority_plane"):
            errors.append(f"authority_plane_mismatch:{sid}")
        if raw.get("status_derivation") != "AUTHORITATIVE_RECEIPT_BYTES":
            errors.append(f"status_not_receipt_derived:{sid}")
        receipt_ref = str(raw.get("authoritative_receipt_ref") or "")
        try:
            receipt_path = _resolve_contained_artifact(path.parent, receipt_ref)
            receipt_bytes = receipt_path.read_bytes()
            receipt = json.loads(receipt_bytes)
            if not isinstance(receipt, dict):
                raise ValueError("receipt_not_object")
        except (StageTransitionError, OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"authoritative_receipt_unreadable:{sid}:{type(exc).__name__}")
            receipt = {}
            receipt_bytes = b""
        if raw.get("authoritative_receipt_sha256") != _sha256_bytes(receipt_bytes):
            errors.append(f"authoritative_receipt_digest_mismatch:{sid}")
        if raw.get("authoritative_receipt_schema_version") != _receipt_schema_version(
            receipt
        ):
            errors.append(f"authoritative_receipt_schema_mismatch:{sid}")
        if raw.get("identity_sha256") != _digest(identity):
            errors.append(f"entry_identity_digest_mismatch:{sid}")
        if not _receipt_identity_matches(receipt, identity, stage_id=sid):
            errors.append(f"authoritative_receipt_identity_mismatch:{sid}")
        try:
            derived_status = _derive_product_receipt_status(sid, receipt)
            if derived_status == "SKIPPED":
                derived_status = "SKIPPED_NON_PRODUCT"
        except StageTransitionError:
            derived_status = ""
            errors.append(f"authoritative_receipt_status_unknown:{sid}")
        if derived_status != status:
            errors.append(f"authoritative_receipt_status_mismatch:{sid}")
        bindings = raw.get("artifact_bindings")
        if not isinstance(bindings, list):
            errors.append(f"artifact_bindings_invalid:{sid}")
            bindings = []
        for binding in bindings:
            if not isinstance(binding, dict):
                errors.append(f"artifact_binding_invalid:{sid}")
                continue
            ref = str(binding.get("artifact_ref") or "")
            try:
                artifact_path = _resolve_contained_artifact(path.parent, ref)
                artifact_bytes = artifact_path.read_bytes()
            except (StageTransitionError, OSError):
                errors.append(f"artifact_binding_unreadable:{sid}:{ref}")
                continue
            if binding.get("sha256") != _sha256_bytes(artifact_bytes):
                errors.append(f"artifact_binding_digest_mismatch:{sid}:{ref}")
            if binding.get("byte_length") != len(artifact_bytes):
                errors.append(f"artifact_binding_length_mismatch:{sid}:{ref}")
        selected_next = raw.get("next_stage_id")
        allowed_next = tuple(
            str(item).upper() for item in stages[sid].get("allowed_next") or ()
        )
        if selected_next is not None and selected_next not in allowed_next:
            errors.append(f"next_stage_invalid:{sid}:{selected_next}")
        if status in {"FAIL", "BLOCKED"} and selected_next is not None:
            errors.append(f"failed_stage_has_continuation:{sid}:{selected_next}")
        if selected_next is None and allowed_next and status not in {"FAIL", "BLOCKED"}:
            errors.append(f"next_stage_missing:{sid}")
        prior_next = selected_next
    terminal_stage = str(entries[-1].get("stage_id") or "") if entries else ""
    sealed, seal_errors, ledger_sha256 = _verify_external_seal(
        path,
        payload=payload,
        entry_count=len(entries),
        terminal_stage=terminal_stage,
    )
    errors.extend(seal_errors)
    if sealed and "closed_at_utc" not in payload:
        errors.append("closed_at_utc_missing")
    terminal_state = payload.get("terminal_state")
    if not isinstance(terminal_state, dict):
        errors.append("terminal_state_missing")
    complete = (
        not errors
        and sealed
        and terminal_stage in {"MANDATORY_OUTPUTS", "TERMINAL_NON_PRODUCT"}
        and all(
            isinstance(entry, dict)
            and str(entry.get("status") or "") in {"PASS", "SKIPPED_NON_PRODUCT"}
            for entry in entries
        )
    )
    return LedgerVerificationReport(
        valid=not errors,
        complete=complete,
        errors=tuple(errors),
        entry_count=len(entries),
        terminal_stage=terminal_stage,
        sealed=sealed and not seal_errors,
        ledger_sha256=ledger_sha256,
    )


def verify_e2e_stage_ledger(path: Path) -> LedgerVerificationReport:
    errors: list[str] = []
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return LedgerVerificationReport(False, False, (f"unreadable:{exc}",), 0, "")
    if not isinstance(payload, dict):
        return LedgerVerificationReport(False, False, ("ledger_not_object",), 0, "")
    if str(payload.get("schema_version") or "") == E2E_STAGE_LEDGER_V2_SCHEMA_VERSION:
        return _verify_receipt_derived_v2(Path(path), payload)
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
        if str(raw.get("status_derivation") or "") == "AUTHORITATIVE_RECEIPT_BYTES":
            receipt_ref = str(raw.get("authoritative_receipt_ref") or "")
            try:
                receipt_path = _resolve_contained_artifact(Path(path).parent, receipt_ref)
                receipt_bytes = receipt_path.read_bytes()
                receipt_payload = json.loads(receipt_bytes)
                if not isinstance(receipt_payload, dict):
                    raise ValueError("receipt_not_object")
            except (StageTransitionError, OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(
                    f"authoritative_receipt_unreadable:{sid}:{attempt}:{type(exc).__name__}"
                )
                receipt_payload = {}
                receipt_bytes = b""
            if str(raw.get("authoritative_receipt_sha256") or "") != _sha256_bytes(
                receipt_bytes
            ):
                errors.append(f"authoritative_receipt_digest_mismatch:{sid}:{attempt}")
            try:
                authoritative_length = int(
                    raw.get("authoritative_receipt_byte_length") or 0
                )
            except (TypeError, ValueError):
                authoritative_length = -1
            if authoritative_length != len(receipt_bytes):
                errors.append(f"authoritative_receipt_length_mismatch:{sid}:{attempt}")
            if str(raw.get("authoritative_receipt_schema_version") or "") != (
                _receipt_schema_version(receipt_payload)
            ):
                errors.append(f"authoritative_receipt_schema_mismatch:{sid}:{attempt}")
            try:
                receipt_status = _derive_receipt_status(
                    receipt_payload,
                    status_field="status",
                )
            except StageTransitionError:
                receipt_status = ""
                errors.append(f"authoritative_receipt_status_unknown:{sid}:{attempt}")
            if receipt_status != status:
                errors.append(f"authoritative_receipt_status_mismatch:{sid}:{attempt}")
            artifact_bindings = raw.get("artifact_bindings")
            artifact_bindings = (
                artifact_bindings if isinstance(artifact_bindings, list) else []
            )
            for binding in artifact_bindings:
                if not isinstance(binding, dict):
                    errors.append(f"artifact_binding_invalid:{sid}:{attempt}")
                    continue
                artifact_ref = str(binding.get("artifact_ref") or "")
                try:
                    artifact_path = _resolve_contained_artifact(
                        Path(path).parent,
                        artifact_ref,
                    )
                    artifact_bytes = artifact_path.read_bytes()
                except (StageTransitionError, OSError):
                    errors.append(
                        f"artifact_binding_unreadable:{sid}:{attempt}:{artifact_ref}"
                    )
                    continue
                if str(binding.get("sha256") or "") != _sha256_bytes(artifact_bytes):
                    errors.append(
                        f"artifact_binding_digest_mismatch:{sid}:{attempt}:{artifact_ref}"
                    )
                try:
                    artifact_length = int(binding.get("byte_length"))
                except (TypeError, ValueError):
                    artifact_length = -1
                if artifact_length != len(artifact_bytes):
                    errors.append(
                        f"artifact_binding_length_mismatch:{sid}:{attempt}:{artifact_ref}"
                    )
            expected_output_digest = _digest(
                {
                    "authoritative_receipt_sha256": raw.get(
                        "authoritative_receipt_sha256"
                    ),
                    "artifact_bindings": artifact_bindings,
                }
            )
            if str(raw.get("output_digest") or "") != expected_output_digest:
                errors.append(f"receipt_output_digest_mismatch:{sid}:{attempt}")
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
    sealed, seal_errors, ledger_sha256 = _verify_external_seal(
        Path(path),
        payload=payload,
        entry_count=len(entries),
        terminal_stage=terminal_stage,
    )
    errors.extend(seal_errors)
    return LedgerVerificationReport(
        valid=not errors,
        complete=complete and not seal_errors,
        errors=tuple(errors),
        entry_count=len(entries),
        terminal_stage=terminal_stage,
        sealed=sealed and not seal_errors,
        ledger_sha256=ledger_sha256,
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
                "research_handoff_v2_path",
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
    "AUTHORITY_CONTRACT_ID",
    "AUTHORITY_CONTRACT_REF",
    "DEFAULT_STAGE_GRAPH",
    "DEFAULT_AUTHORITY_CONTRACT",
    "E2E_LAUNCH_RECEIPT_FILENAME",
    "E2E_STAGE_LEDGER_FILENAME",
    "E2E_STAGE_LEDGER_SEAL_FILENAME",
    "E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION",
    "E2E_STAGE_LEDGER_V2_SCHEMA_VERSION",
    "E2EStageLedger",
    "ReceiptDerivedE2EStageLedger",
    "CacheCompletionReport",
    "LedgerVerificationReport",
    "StageReceipt",
    "StageTransitionError",
    "emit_e2e_launch_receipt",
    "validate_cached_e2e_completion",
    "verify_e2e_stage_ledger",
]
