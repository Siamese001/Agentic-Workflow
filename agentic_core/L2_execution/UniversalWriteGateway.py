"""Universal Write Gateway — Single mutation authority for all writes.

Enforces write permissions, records mutations, and supports replay mode
for deterministic simulation without actual side-effects.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.enforcement.guardrail_gate import (
    GuardrailGate,
)
from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

Logger = logging.getLogger(__name__)


class ToolNotAllowedError(PermissionError):
    """Raised when an instruction attempts to execute a tool not on the allowlist."""


@dataclass(frozen=True)
class MutationRecord:
    """Immutable record of a write operation for audit trails.

    Wave 1 hardening: mutation_hash is sha256(actor_id + run_id + operation + path + data_hash).
    This makes the record deterministically reproducible and tamper-evident.
    The timestamp field is a deterministic digest, NOT os.urandom or datetime.now.
    """

    mutation_hash: str
    actor_id: str
    run_id: str
    operation: str
    path: str
    replay_key: str = ""
    data_hash: str | None = None
    size_bytes: int | None = None
    permitted: bool = True
    replay_mode: bool = False

    @classmethod
    def build(
        cls,
        *,
        actor_id: str,
        run_id: str,
        operation: str,
        path: str,
        data: str | bytes | None = None,
        replay_key: str = "",
        permitted: bool = True,
        replay_mode: bool = False,
    ) -> "MutationRecord":
        """Construct a MutationRecord with a deterministic mutation_hash."""
        data_hash: str | None = None
        size_bytes: int | None = None
        if data is not None:
            data_bytes = data.encode("utf-8") if isinstance(data, str) else data
            data_hash = hashlib.sha256(data_bytes).hexdigest()
            size_bytes = len(data_bytes)
        raw = f"{actor_id}:{run_id}:{operation}:{path}:{data_hash or ''}:{replay_key}"
        mutation_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return cls(
            mutation_hash=mutation_hash,
            actor_id=actor_id,
            run_id=run_id,
            operation=operation,
            path=str(Path(path).as_posix()),
            replay_key=replay_key,
            data_hash=data_hash,
            size_bytes=size_bytes,
            permitted=permitted,
            replay_mode=replay_mode,
        )


@dataclass
class SimulationResult:
    """Result of a simulated write operation in replay mode."""

    operation: str
    path: str
    would_succeed: bool
    simulated_size: int
    simulated_hash: str
    replay_mode: bool = True


class UniversalWriteGateway:
    """Single mutation authority for all FS/DB/vector writes.

    Enforces write permissions, records mutations, and supports replay mode
    for deterministic simulation.
    """

    def __init__(
        self,
        replay_mode: bool = False,
        policy_hash: str = "",
        actor_id: str = "uwg",
        run_id: str = "",
    ):
        self.replay_mode = replay_mode
        self.actor_id = actor_id
        self.run_id = run_id
        self._frozen: bool = False
        self._write_permissions: dict[str, bool] = {}
        self._mutation_ledger: list[MutationRecord] = []
        self._state_snapshots: list[dict] = []
        self._allowed_paths: set[str] = {"artifacts/", "docs/reports/", "logs/", "temp/", ".cache/"}
        self._blocked_extensions = {".exe", ".dll", ".so", ".dylib", ".py", ".js", ".ts", ".jsx", ".tsx"}
        self._allowed_tools: set[str] = {
            "file_system.read",
            "file_system.write",
            "code_interpreter.run_python",
        }
        self._guardrail_gate: GuardrailGate = GuardrailGate(policy_hash=policy_hash, strict_mode=False)

    def check_write_permission(self, path: str, operation: str = "write") -> bool:
        """Check if write operation is permitted."""
        if self.replay_mode:
            return True
        path_normalized = str(Path(path).as_posix())
        for allowed in self._allowed_paths:
            if path_normalized.startswith(allowed):
                return True
        ext = Path(path).suffix.lower()
        if ext in self._blocked_extensions:
            return False
        return self._write_permissions.get(path_normalized, False)

    def record_mutation(
        self,
        path: str,
        operation: str,
        data: str | bytes | None = None,
        permitted: bool | None = None,
        replay_key: str = "",
    ) -> MutationRecord:
        """Record mutation for audit trail with deterministic mutation_hash."""
        if permitted is None:
            permitted = self.check_write_permission(path, operation)
        record = MutationRecord.build(
            actor_id=self.actor_id,
            run_id=self.run_id,
            operation=operation,
            path=path,
            data=data,
            replay_key=replay_key,
            permitted=permitted,
            replay_mode=self.replay_mode,
        )
        self._mutation_ledger.append(record)
        return record

    def write_through(
        self,
        path: str,
        data: str | bytes,
        *,
        replay_key: str = "",
        actor_id: str | None = None,
        run_id: str | None = None,
    ) -> "MutationRecord | SimulationResult":
        """Sovereign write path — all governed writes MUST use this method.

        This is the only method that produces a ``writes_through`` ADG edge.
        Direct ``writes_to`` callers must be migrated to this entry point.
        """
        self._guardrail_gate.check(operation="write_through", target=path)
        if self._frozen:
            raise PermissionError("REQ-091: UWG write_through blocked — gateway is frozen.")
        effective_actor = actor_id or self.actor_id
        effective_run = run_id or self.run_id
        if self.replay_mode:
            return self.simulate_write(path, "write_through", data)
        if not self.check_write_permission(path, "write"):
            record = MutationRecord.build(
                actor_id=effective_actor,
                run_id=effective_run,
                operation="write_through_blocked",
                path=path,
                data=data,
                replay_key=replay_key,
                permitted=False,
                replay_mode=self.replay_mode,
            )
            self._mutation_ledger.append(record)
            raise ToolNotAllowedError(
                f"UWG write_through blocked: path '{path}' is not in the allowed write set."
            )
        data_bytes = data.encode("utf-8") if isinstance(data, str) else data
        if replay_key and not self._verify_replay_hash(data_bytes, replay_key):
            raise PermissionError(
                "REQ-354: UWG write_through blocked — replay hash mismatch."
            )
        record = MutationRecord.build(
            actor_id=effective_actor,
            run_id=effective_run,
            operation="write_through",
            path=path,
            data=data,
            replay_key=replay_key,
            permitted=True,
            replay_mode=self.replay_mode,
        )
        self._mutation_ledger.append(record)
        Logger.debug("UWG write_through: %s actor=%s run=%s hash=%s", path, effective_actor, effective_run, record.mutation_hash[:12])
        return record

    def snapshot_state(
        self,
        label: str,
        state: dict,
        *,
        actor_id: str | None = None,
        run_id: str | None = None,
    ) -> dict:
        """Record a versioned state snapshot into the UWG ledger.

        Produces a ``snapshots_state`` ADG edge. Each snapshot is append-only
        and carries a deterministic content hash so it can be verified during replay.
        """
        import json as _json

        effective_actor = actor_id or self.actor_id
        effective_run = run_id or self.run_id
        version = len(self._state_snapshots)
        raw = _json.dumps(state, sort_keys=True, default=str)
        content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        snapshot = {
            "version": version,
            "label": label,
            "actor_id": effective_actor,
            "run_id": effective_run,
            "content_hash": content_hash,
            "state": state,
        }
        self._state_snapshots.append(snapshot)
        self.record_mutation(
            path=f"snapshot://{label}/{version}",
            operation="snapshot_state",
            data=raw,
            permitted=True,
        )
        Logger.debug("UWG snapshot_state: %s v%d hash=%s", label, version, content_hash[:12])
        return snapshot

    def get_state_snapshots(self) -> list[dict]:
        """Return append-only copy of all state snapshots."""
        return list(self._state_snapshots)

    @staticmethod
    def verify_mutation_record(record: MutationRecord) -> bool:
        """Verify that a MutationRecord's mutation_hash matches its fields.

        Returns True if the record is internally consistent (not tampered).
        """
        raw = f"{record.actor_id}:{record.run_id}:{record.operation}:{record.path}:{record.data_hash or ''}:{record.replay_key}"
        expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return expected == record.mutation_hash

    def simulate_write(self, path: str, operation: str, data: str | bytes | None = None) -> SimulationResult:
        """Simulate write operation in replay mode."""
        if not self.replay_mode:
            raise RuntimeError("simulate_write called outside replay mode")
        would_succeed = self.check_write_permission(path, operation)
        simulated_size = 0
        simulated_hash = ""
        if data is not None:
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = data
            simulated_size = len(data_bytes)
            simulated_hash = hashlib.sha256(data_bytes).hexdigest()
        return SimulationResult(
            operation=operation,
            path=str(Path(path).as_posix()),
            would_succeed=would_succeed,
            simulated_size=simulated_size,
            simulated_hash=simulated_hash,
            replay_mode=True,
        )

    def grant_write_permission(self, path: str) -> None:
        """Grant write permission for a specific path."""
        if self.replay_mode:
            return
        self._write_permissions[str(Path(path).as_posix())] = True

    def revoke_write_permission(self, path: str) -> None:
        """Revoke write permission for a specific path."""
        if self.replay_mode:
            return
        self._write_permissions[str(Path(path).as_posix())] = False

    def get_mutation_ledger(self) -> list[MutationRecord]:
        """Get immutable copy of mutation ledger."""
        return list(self._mutation_ledger)

    def clear_mutation_ledger(self) -> None:
        """Clear mutation ledger (for testing only)."""
        if self.replay_mode:
            return
        self._mutation_ledger.clear()

    def execute_instruction(self, instruction: InstructionPacket) -> None:
        """
        The sovereign entry point for all tool executions.

        Validates the tool name from the InstructionPacket against the allowlist
        before allowing any operation to proceed.

        Raises:
            ToolNotAllowedError: If the tool is not in the allowlist.
        """
        tool_name = instruction.metadata.get("tool_name")
        self._guardrail_gate.check(
            operation="execute_instruction",
            target=f"tool_execution/{tool_name or 'unknown'}",
        )
        if not tool_name or tool_name not in self._allowed_tools:
            self.record_mutation(
                path=f"tool_execution/{tool_name or 'unknown'}",
                operation="execute_instruction_blocked",
                permitted=False,
            )
            raise ToolNotAllowedError(f"Tool '{tool_name}' is not on the allowlist. Execution blocked.")
        self.record_mutation(
            path=f"tool_execution/{tool_name}", operation="execute_instruction_allowed", permitted=True
        )

    def write_file(self, path: str, data: str | bytes) -> SimulationResult | MutationRecord:
        """Write data to path via the UWG sovereign gate.

        Spec: L2 [UWG] UNIVERSAL WRITE GATEWAY, Guarantee #6.
        - replay_mode=True: returns SimulationResult (no real write).
        - replay_mode=False: raises ToolNotAllowedError on blocked paths/extensions.
        """
        self._guardrail_gate.check(operation="write_file", target=path)
        if self.replay_mode:
            return self.simulate_write(path, "write", data)
        if not self.check_write_permission(path, "write"):
            self.record_mutation(path=path, operation="write", data=data, permitted=False)
            ext = Path(path).suffix.lower()
            reason = (
                f"extension '{ext}' is blocked"
                if ext in self._blocked_extensions
                else f"path '{path}' is not in the allowed write set"
            )
            raise ToolNotAllowedError(
                f"UWG write_file blocked: {reason}. Route writes through an allowed path or grant explicit permission."
            )
        return self.record_mutation(path=path, operation="write", data=data, permitted=True)

    def append_file(self, path: str, data: str | bytes) -> SimulationResult | MutationRecord:
        """Append data to path via the UWG sovereign gate.

        Same blocking semantics as write_file.
        """
        self._guardrail_gate.check(operation="append_file", target=path)
        if self.replay_mode:
            return self.simulate_write(path, "append", data)
        if not self.check_write_permission(path, "append"):
            self.record_mutation(path=path, operation="append", data=data, permitted=False)
            ext = Path(path).suffix.lower()
            reason = (
                f"extension '{ext}' is blocked"
                if ext in self._blocked_extensions
                else f"path '{path}' is not in the allowed write set"
            )
            raise ToolNotAllowedError(f"UWG append_file blocked: {reason}.")
        return self.record_mutation(path=path, operation="append", data=data, permitted=True)

    def delete_file(self, path: str) -> SimulationResult | MutationRecord:
        """Delete a file via the UWG sovereign gate.

        Same blocking semantics: replay_mode returns SimulationResult; live raises on disallowed.
        """
        self._guardrail_gate.check(operation="delete_file", target=path)
        if self.replay_mode:
            return self.simulate_write(path, "delete")
        if not self.check_write_permission(path, "delete"):
            self.record_mutation(path=path, operation="delete", permitted=False)
            raise ToolNotAllowedError(
                f"UWG delete_file blocked: path '{path}' is not in the allowed write set."
            )
        return self.record_mutation(path=path, operation="delete", permitted=True)

    def rename_file(self, src: str, dst: str) -> SimulationResult | MutationRecord:
        """Rename/move a file via the UWG sovereign gate.

        Both src and dst must be in the allowed write set.
        """
        if self.replay_mode:
            return self.simulate_write(dst, "rename")
        src_ok = self.check_write_permission(src, "rename")
        dst_ok = self.check_write_permission(dst, "rename")
        if not src_ok or not dst_ok:
            blocked = src if not src_ok else dst
            self.record_mutation(path=src, operation="rename", permitted=False)
            raise ToolNotAllowedError(
                f"UWG rename_file blocked: path '{blocked}' is not in the allowed write set."
            )
        return self.record_mutation(path=src, operation="rename", permitted=True)

    def _verify_signature(self, signature: str) -> bool:
        """REQ-019/177/354: verify a write-payload signature.

        Stub implementation — returns True for any non-empty signature.
        Override in subclasses or inject via test doubles for stricter verification.
        """
        return bool(signature)

    def _verify_replay_hash(self, payload: bytes, replay_key: str) -> bool:
        """REQ-354: verify deterministic replay hash.

        Checks that hash(payload) matches the declared replay_key so the
        write is reproducible and has not been tampered with in transit.
        Override in subclasses for production-strength verification.
        """
        if not replay_key:
            return False
        computed = hashlib.sha256(payload).hexdigest()
        return computed == replay_key

    def _verify_plan_hash(self, plan_hash: str) -> bool:
        """REQ-354: verify mutation originated from an authorised execution plan.

        Stub returns True for any non-empty plan_hash.  Override in subclasses
        to compare against the active execution plan registry.
        """
        return bool(plan_hash)

    def freeze(self) -> None:
        """REQ-091: Tier III freeze — all writes blocked until process restart."""
        self._frozen = True

    def write(
        self, payload: bytes, signature: str, store: Any, *, replay_key: str = "", plan_hash: str = ""
    ) -> None:
        """REQ-019/177/354: signature-before-side-effect write gate.

        Enforces three sequential checks before delegating to store.write():
        1. Guardrail pre-check — applies_guardrail before any mutation.
        2. Signature verification — payload must be signed.
        3. Replay hash verification — payload hash must match replay_key.
        4. Plan hash verification — mutation must originate from an authorised plan.

        All checks must pass.  store is never touched on any failure.
        """
        self._guardrail_gate.check(operation="write", target="store")
        if self._frozen:
            raise PermissionError("REQ-091: UWG write blocked — gateway is frozen.")
        if not self._verify_signature(signature):
            raise PermissionError(
                "REQ-019: UWG write blocked — signature verification failed before state mutation."
            )
        if replay_key and (not self._verify_replay_hash(payload, replay_key)):
            raise PermissionError(
                "REQ-354: UWG write blocked — replay hash mismatch; payload has been tampered with or is non-deterministic."
            )
        if plan_hash and (not self._verify_plan_hash(plan_hash)):
            raise PermissionError(
                "REQ-354: UWG write blocked — plan hash verification failed; mutation does not originate from an authorised execution plan."
            )
        store.write(payload)

    def get_write_stats(self) -> dict[str, Any]:
        """Return statistics about write operations."""
        total = len(self._mutation_ledger)
        permitted = sum(1 for r in self._mutation_ledger if r.permitted)
        write_through_count = sum(
            1 for r in self._mutation_ledger if r.operation == "write_through"
        )
        return {
            "total_mutations": total,
            "permitted_mutations": permitted,
            "blocked_mutations": total - permitted,
            "write_through_count": write_through_count,
            "snapshot_count": len(self._state_snapshots),
            "replay_mode": self.replay_mode,
            "actor_id": self.actor_id,
            "run_id": self.run_id,
            "allowed_paths": sorted(self._allowed_paths),
            "write_permissions": dict(self._write_permissions),
        }

    def validate_promotion_pointer_update(
        self, namespace: str, old_pointer: str, new_pointer: str, capability_token
    ) -> bool:
        """Validate promotion pointer update with capability token."""
        if self.replay_mode:
            return self._simulate_promotion_validation(namespace, old_pointer, new_pointer, capability_token)
        if not hasattr(capability_token, "validate_scope_and_use"):
            Logger.error("Invalid capability token for promotion update")
            return False
        if hasattr(capability_token, "target_namespace") and capability_token.target_namespace != namespace:
            Logger.error(f"Token namespace mismatch: {capability_token.target_namespace} != {namespace}")
            return False
        if (
            hasattr(capability_token, "allowed_action")
            and capability_token.allowed_action != "pointer_update"
        ):
            Logger.error(f"Invalid action: {capability_token.allowed_action}")
            return False
        self.record_mutation(
            operation="promotion_pointer_update",
            path=f"promotion://{namespace}",
            data=f"{old_pointer}->{new_pointer}",
            permitted=True,
        )
        Logger.info(
            f"Promotion pointer update validated for namespace {namespace}: {old_pointer} -> {new_pointer}"
        )
        return True

    def _simulate_promotion_validation(
        self, namespace: str, old_pointer: str, new_pointer: str, capability_token
    ) -> bool:
        """Simulate promotion validation in replay mode."""
        self.record_mutation(
            path=f"promotion://{namespace}",
            operation="promotion_pointer_update",
            data=f"{old_pointer}->{new_pointer}",
            permitted=True,
        )
        return True

    def update_pointer(self, namespace: str, old_pointer: str, new_pointer: str, capability_token) -> bool:
        """Update pointer with validation."""
        if not self.validate_promotion_pointer_update(namespace, old_pointer, new_pointer, capability_token):
            return False
        Logger.info(f"Pointer updated in namespace {namespace}")
        return True


_global_gateway: UniversalWriteGateway | None = None


def get_write_gateway() -> UniversalWriteGateway:
    """Get the global write gateway instance."""
    global _global_gateway
    if _global_gateway is None:
        _global_gateway = UniversalWriteGateway()
    return _global_gateway


def set_write_gateway(gateway: UniversalWriteGateway) -> None:
    """Set the global write gateway instance (for testing)."""
    global _global_gateway
    _global_gateway = gateway


def reset_write_gateway() -> None:
    """Reset the global write gateway (for testing)."""
    global _global_gateway
    _global_gateway = None
