"""G15 — Filesystem / Shell / Data Access Gate.

Spec: bound runtime fs/shell/data access.
Stop: shell/fs access outside sandbox envelope MUST NOT execute.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

DESTRUCTIVE_TOKENS = (
    "rm -rf",
    "del /q",
    "shutdown",
    "mkfs",
    "dd if=",
    "format c:",
    "drop table",
    "drop database",
)
CREDENTIAL_PATHS = ("/etc/shadow", "/etc/passwd", "~/.ssh", "~/.aws", "/.aws/credentials")


def _normalize(path: str) -> str:
    try:
        return str(PurePosixPath(path)).lower()
    except (ValueError, OSError):
        return path.lower()


@register_gate
class FilesystemShellGate:
    GATE_ID = "G15"
    PRIMARY_LAYER = "L2"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        call = ctx.tool_call
        op = call.get("op", "read")  # read | write | delete | shell
        path = str(call.get("path", "") or "")
        cmd = str(call.get("cmd", "") or "").lower()
        sandbox_root = call.get("sandbox_root", "")
        # Stop: missing sandbox.
        if not sandbox_root:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["missing_sandbox"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Path traversal.
        norm = _normalize(path)
        sandbox_norm = _normalize(sandbox_root)
        if path and ".." in path:
            signals.append(
                RegressionSignal(name="out_of_scope_path_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["path_traversal"],
                signals=signals,
                stop_condition_violated=True,
            )
        if path and not norm.startswith(sandbox_norm):
            signals.append(
                RegressionSignal(name="out_of_scope_path_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["path_outside_sandbox"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Credential exploration.
        if any(c in norm for c in CREDENTIAL_PATHS):
            signals.append(
                RegressionSignal(name="credential_access_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["credential_path"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Shell command screening.
        if op == "shell":
            if any(t in cmd for t in DESTRUCTIVE_TOKENS):
                if not call.get("destructive_authorized"):
                    signals.append(
                        RegressionSignal(
                            name="destructive_command_attempt_count", value=1.0, severity="alert"
                        )
                    )
                    return GateDecision(
                        gate_id=self.GATE_ID,
                        disposition=Disposition.DENY,
                        reason_codes=["destructive_command_blocked"],
                        signals=signals,
                        stop_condition_violated=True,
                    )
                signals.append(
                    RegressionSignal(name="blocked_shell_command_rate", value=1.0, severity="warn")
                )
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.ESCALATE_HITL,
                    reason_codes=["destructive_command_authorized_pending_hitl"],
                    signals=signals,
                )
        # Default: sandboxed allow.
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.SANDBOX.value,
            reason_codes=[f"{op}_allowed"],
            signals=signals,
        )


__all__ = ["FilesystemShellGate"]
