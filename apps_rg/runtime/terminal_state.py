"""Apps RG terminal state machines at and after the UWG product boundary."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PRODUCT_AUTHORIZATION_RECEIPT_FILENAME = (
    "apps_rg_product_authorization_receipt.json"
)
PRODUCT_AUTHORIZATION_SCHEMA_VERSION = "apps_rg.product_authorization_receipt.v1"


class TerminalStateError(RuntimeError):
    """Raised for an invalid or contradictory terminal-state transition."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _require_sha256(value: str, field: str) -> str:
    text = str(value or "")
    if len(text) != 71 or not text.startswith("sha256:"):
        raise TerminalStateError(f"{field} must be a sha256:<64-lowercase-hex> digest")
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise TerminalStateError(
            f"{field} must be a sha256:<64-lowercase-hex> digest"
        ) from exc
    if text[7:] != text[7:].lower():
        raise TerminalStateError(f"{field} must use lowercase hex")
    return text


def _resolve_contained_file(root: Path, ref: str | Path) -> Path:
    base = Path(root).resolve()
    raw = Path(ref)
    target = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise TerminalStateError(f"artifact escapes run directory: {ref}") from exc
    if not target.is_file():
        raise TerminalStateError(f"artifact is missing: {ref}")
    return target


def _binding(root: Path, ref: str | Path) -> dict[str, Any]:
    target = _resolve_contained_file(root, ref)
    raw = target.read_bytes()
    return {
        "artifact_ref": target.relative_to(Path(root).resolve()).as_posix(),
        "sha256": _sha256_bytes(raw),
        "byte_length": len(raw),
    }


@dataclass(frozen=True, slots=True)
class ProductAuthorizationState:
    authorized: bool
    status: str
    boundary: str
    immutable: bool
    decision_receipt_ref: str
    decision_receipt_sha256: str
    output_artifact_sha256: str | None
    closed_at_utc: str


@dataclass(frozen=True, slots=True)
class PipelineCompletionState:
    complete: bool
    status: str
    observability_repair_required: bool
    decisive_stage_id: str


class TerminalStateMachine:
    """Keep current-run authorization separate from post-boundary completion."""

    def __init__(self) -> None:
        self._product: ProductAuthorizationState | None = None
        self._pipeline = PipelineCompletionState(
            complete=False,
            status="INCOMPLETE",
            observability_repair_required=False,
            decisive_stage_id="PRODUCT_AUTHORIZATION_CLOSE",
        )
        self._sealed = False

    @property
    def product_authorized(self) -> bool:
        return bool(self._product and self._product.authorized)

    @property
    def pipeline_complete(self) -> bool:
        return self._pipeline.complete

    @property
    def observability_repair_required(self) -> bool:
        return self._pipeline.observability_repair_required

    @property
    def product_authorization(self) -> ProductAuthorizationState:
        if self._product is None:
            raise TerminalStateError("product authorization boundary has not closed")
        return self._product

    @property
    def pipeline_completion(self) -> PipelineCompletionState:
        return self._pipeline

    def close_product_authorization(
        self,
        *,
        authorized: bool,
        decision_receipt_ref: str,
        decision_receipt_sha256: str,
        output_artifact_sha256: str | None,
        non_product: bool = False,
        closed_at_utc: str | None = None,
    ) -> ProductAuthorizationState:
        if self._sealed:
            raise TerminalStateError("terminal state is sealed")
        if self._product is not None:
            raise TerminalStateError("product authorization is immutable after close")
        decision_digest = _require_sha256(
            decision_receipt_sha256,
            "decision_receipt_sha256",
        )
        output_digest = (
            _require_sha256(output_artifact_sha256, "output_artifact_sha256")
            if output_artifact_sha256 is not None
            else None
        )
        if authorized and non_product:
            raise TerminalStateError("an authorized product cannot be NON_PRODUCT")
        if authorized and output_digest is None:
            raise TerminalStateError(
                "authorized product state requires exact output artifact bytes"
            )
        if not authorized and output_digest is not None:
            raise TerminalStateError(
                "blocked/non-product state cannot claim an authorized output digest"
            )
        self._product = ProductAuthorizationState(
            authorized=bool(authorized),
            status=("AUTHORIZED" if authorized else "NON_PRODUCT" if non_product else "BLOCKED"),
            boundary="UWG_COMMIT_CLOSED" if authorized else "NOT_CLOSED",
            immutable=True,
            decision_receipt_ref=str(decision_receipt_ref or ""),
            decision_receipt_sha256=decision_digest,
            output_artifact_sha256=output_digest,
            closed_at_utc=closed_at_utc or _utc_now(),
        )
        if not self._product.decision_receipt_ref:
            self._product = None
            raise TerminalStateError("decision_receipt_ref is required")
        return self._product

    def record_pipeline_completion(
        self,
        *,
        complete: bool,
        decisive_stage_id: str,
        failed: bool = False,
    ) -> PipelineCompletionState:
        if self._sealed:
            raise TerminalStateError("terminal state is sealed")
        if self._product is None:
            raise TerminalStateError(
                "pipeline state cannot close before product authorization state"
            )
        if complete and not self._product.authorized:
            raise TerminalStateError("pipeline completion requires product authorization")
        if complete and failed:
            raise TerminalStateError("complete pipeline state cannot also be failed")
        decisive = str(decisive_stage_id or "").strip()
        if not decisive:
            raise TerminalStateError("decisive_stage_id is required")
        self._pipeline = PipelineCompletionState(
            complete=bool(complete),
            status="COMPLETE" if complete else "FAILED" if failed else "INCOMPLETE",
            observability_repair_required=bool(
                self._product.authorized and not complete
            ),
            decisive_stage_id=decisive,
        )
        return self._pipeline

    def seal(self) -> None:
        if self._product is None:
            raise TerminalStateError("cannot seal before product authorization closes")
        self._sealed = True

    def snapshot(self) -> dict[str, bool]:
        return {
            "product_authorized": self.product_authorized,
            "pipeline_complete": self.pipeline_complete,
            "observability_repair_required": self.observability_repair_required,
        }

    def manifest_blocks(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return asdict(self.product_authorization), asdict(self.pipeline_completion)


def persist_product_authorization_receipt(
    *,
    artifact_dir: Path,
    identity: Mapping[str, Any],
    state: ProductAuthorizationState,
    decision_receipt_ref: str | Path,
    output_artifact_ref: str | Path | None = None,
) -> Path:
    """Persist the immutable UWG-bound decision using exclusive creation."""

    root = Path(artifact_dir).resolve()
    decision = _binding(root, decision_receipt_ref)
    if decision["sha256"] != state.decision_receipt_sha256:
        raise TerminalStateError("decision receipt bytes do not match terminal state")
    output = _binding(root, output_artifact_ref) if output_artifact_ref is not None else None
    if state.authorized:
        if output is None or output["sha256"] != state.output_artifact_sha256:
            raise TerminalStateError("authorized output bytes do not match terminal state")
    elif output is not None:
        raise TerminalStateError("non-authorized state cannot persist an output binding")
    payload = {
        "schema_version": PRODUCT_AUTHORIZATION_SCHEMA_VERSION,
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "identity": dict(identity),
        "identity_sha256": _digest(dict(identity)),
        "authorized": state.authorized,
        "status": state.status,
        "boundary": state.boundary,
        "immutable": True,
        "decision_receipt": decision,
        "output_artifact": output,
        "closed_at_utc": state.closed_at_utc,
    }
    target = root / PRODUCT_AUTHORIZATION_RECEIPT_FILENAME
    try:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    except FileExistsError as exc:
        raise TerminalStateError("product authorization receipt is already closed") from exc
    return target


__all__ = [
    "PRODUCT_AUTHORIZATION_RECEIPT_FILENAME",
    "PRODUCT_AUTHORIZATION_SCHEMA_VERSION",
    "PipelineCompletionState",
    "ProductAuthorizationState",
    "TerminalStateError",
    "TerminalStateMachine",
    "persist_product_authorization_receipt",
]
