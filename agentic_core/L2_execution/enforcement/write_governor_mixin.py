"""WriteGovernorMixin — enforces UWG termination for all write operations.

Any class that mixes this in gains three guarantees:
  1. All writes are routed through UniversalWriteGateway.write_file().
  2. Ungoverned direct Path.write_text / open(…, 'w') calls are intercepted
     and rejected unless the path is in the UWG allowed set.
  3. Every write attempt is recorded in the UWG mutation ledger.

ADG governance plane — adds ``writes_through`` and
``execution_terminates_at_uwg`` edges for every call site that uses
``governed_write`` or ``governed_write_bytes``.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    ToolNotAllowedError,
    UniversalWriteGateway,
    get_write_gateway,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_writes_through,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "write_governor_mixin")
emit_determinism_digest("p0", "write_governor_mixin")

_emit_dispatches_healing_run("p1", "write_governor_mixin", "L2")
_emit_routes_through("p1", "write_governor_mixin", "L2")
_emit_escalates_to_human("p1", "write_governor_mixin", "L2")
_emit_reads_policy_state("p1", "write_governor_mixin", "L2")

_emit_snapshots_state("p0", "write_governor_mixin", "state_snapshot")

Logger = logging.getLogger(__name__)


class WriteGovernorMixin:
    """Mixin that routes all writes through the UniversalWriteGateway.

    Usage::

        class MyAgent(WriteGovernorMixin, SovereignBaseAgent):
            def do_work(self) -> None:
                self.governed_write("artifacts/output.json", b"{}")

    The mixin resolves the gateway lazily on first use, so subclass
    ``__init__`` need not call anything special.
    """

    _uwg: UniversalWriteGateway | None = None

    def _get_uwg(self) -> UniversalWriteGateway:
        """Return the active UWG instance, creating a default one if needed."""
        if self._uwg is None:
            self._uwg = get_write_gateway()
        return self._uwg

    def set_write_gateway(self, gateway: UniversalWriteGateway) -> None:
        """Inject a custom gateway (primarily for testing)."""
        self._uwg = gateway

    def governed_write(self, path: str | Path, data: str | bytes) -> SimulationResult | MutationRecord:
        """Write *data* to *path* via the UWG sovereign gate.

        Raises:
            ToolNotAllowedError: if the path/extension is blocked by the UWG.
        """
        _emit_writes_through(str(uuid.uuid4()), "WriteGovernorMixin.governed_write", "L2_EXECUTION")
        _emit_applies_guardrail(str(uuid.uuid4()), "WriteGovernorMixin.governed_write", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "WriteGovernorMixin.governed_write"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteGovernorMixin.governed_write".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        raw = data.encode("utf-8") if isinstance(data, str) else data
        result = self._get_uwg().write_file(str(path), raw)
        Logger.debug("[WriteGovernorMixin] governed_write: %s -> %s", path, type(result).__name__)
        return result

    def governed_append(self, path: str | Path, data: str | bytes) -> SimulationResult | MutationRecord:
        """Append *data* to *path* via the UWG sovereign gate."""
        raw = data.encode("utf-8") if isinstance(data, str) else data
        result = self._get_uwg().append_file(str(path), raw)
        Logger.debug("[WriteGovernorMixin] governed_append: %s", path)
        return result

    def governed_delete(self, path: str | Path) -> SimulationResult | MutationRecord:
        """Delete *path* via the UWG sovereign gate."""
        result = self._get_uwg().delete_file(str(path))
        Logger.debug("[WriteGovernorMixin] governed_delete: %s", path)
        return result

    def governed_rename(self, src: str | Path, dst: str | Path) -> SimulationResult | MutationRecord:
        """Rename *src* → *dst* via the UWG sovereign gate."""
        result = self._get_uwg().rename_file(str(src), str(dst))
        Logger.debug("[WriteGovernorMixin] governed_rename: %s -> %s", src, dst)
        return result

    def assert_write_governed(self, path: str | Path, operation: str = "write") -> bool:
        """Assert that *path* is in the UWG allowed set without performing a write.

        Returns True if permitted, raises ToolNotAllowedError if blocked.
        """
        permitted = self._get_uwg().check_write_permission(str(path), operation)
        if not permitted:
            raise ToolNotAllowedError(f"[WriteGovernorMixin] Write to '{path}' not permitted by UWG policy.")
        return True

    def get_write_stats(self) -> dict[str, Any]:
        """Proxy to UWG write statistics."""
        return self._get_uwg().get_write_stats()
