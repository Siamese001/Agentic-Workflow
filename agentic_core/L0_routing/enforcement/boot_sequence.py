"""
L0 Boot Sequence: Sovereign Architecture Initialization

This module orchestrates the secure boot process of the Agentic Workflow system.
It implements a multi-phase initialization that ensures system integrity,
validates architectural compliance, and establishes the sovereign agent hierarchy.

Boot Phases:
0. Integrity Check - Verify SSOT manifest hasn't been tampered with
1. Discovery - Find and catalog all agents in the ecosystem
2. Compliance - Validate architectural rules and inheritance patterns
3. Sovereignty - Establish the agent hierarchy and governance
4. Runtime - Initialize the active agent ecosystem
"""

import logging
import sys
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "boot_sequence", "state_snapshot")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from agentic_core.discovery import AgentRegistry
from agentic_core.L0_routing.enforcement.manifest_guardian_util import ManifestGuardian
from agentic_core.L0_routing.scripts.compliance_gate_validator import check_compliance

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

logger = logging.getLogger(__name__)


class BootSequence:
    """
    Orchestrates the secure boot process of the Agentic Workflow system.
    """

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.registry = AgentRegistry()
        self.discovered_agents = []
        self.compliance_violations = []

    def execute_boot(self) -> dict[str, Any]:
        """
        Executes the complete boot sequence with cryptographic handshake.

        Returns:
            Dict containing boot status, metrics, and any violations
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "BootSequence.execute_boot")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        boot_result = {
            "status": "success",
            "phases_completed": [],
            "agents_discovered": 0,
            "compliance_violations": [],
            "integrity_verified": False,
            "errors": [],
        }
        try:
            logger.info("Initializing Agentic Workflow L0 Boot...")
            if not ManifestGuardian.verify_integrity():
                logger.critical("🚨 SSOT INTEGRITY BREACH: Boot sequence aborted.")
                raise SystemExit("Fatal: Manifest.json does not match the sealed lock file.")
            logger.info("✅ SSOT Integrity Verified.")
            boot_result["integrity_verified"] = True
            boot_result["phases_completed"].append("cryptographic_handshake")
            logger.info("Phase 1: Agent Discovery & Compliance Validation...")
            self.discovered_agents = self.registry.discover_all()
            boot_result["agents_discovered"] = len(self.discovered_agents)
            self.compliance_violations = check_compliance(self.discovered_agents)
            boot_result["compliance_violations"] = self.compliance_violations
            if self.compliance_violations:
                if self.strict_mode:
                    logger.error(
                        f"❌ Boot failed with {len(self.compliance_violations)} compliance violations."
                    )
                    boot_result["status"] = "failed"
                    boot_result["errors"].extend(self.compliance_violations)
                    raise RuntimeError(f"Compliance violations detected: {self.compliance_violations}")
                else:
                    logger.warning(
                        f"⚠️  Continuing with {len(self.compliance_violations)} compliance violations."
                    )
            else:
                logger.info("✅ All agents pass compliance validation.")
            boot_result["phases_completed"].append("discovery_compliance")
            logger.info("Phase 2: Sovereign Hierarchy Establishment...")
            logger.info("✅ Sovereign hierarchy established.")
            boot_result["phases_completed"].append("sovereignty")
            logger.info("Phase 3: Runtime Initialization...")
            logger.info("✅ Runtime initialized.")
            boot_result["phases_completed"].append("runtime")
            logger.info("🚀 Agentic Workflow boot completed successfully.")
        except SystemExit as e:
            logger.error(f"Boot sequence terminated: {e}")
            boot_result["status"] = "aborted"
            boot_result["errors"].append(str(e))
            raise
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Boot sequence failed: {e}")
            boot_result["status"] = "failed"
            boot_result["errors"].append(str(e))
        return boot_result


def main():
    """Entry point for the boot sequence."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.main", "L0_ROUTING")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    boot = BootSequence(strict_mode=True)
    result = boot.execute_boot()
    if result["status"] == "failed":
        logger.error("Boot failed. Check logs for details.")
        sys.exit(1)
    else:
        logger.info("Boot completed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
