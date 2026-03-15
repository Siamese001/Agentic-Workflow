"""Re-export symbols from the standalone determinism.py module.

The standalone agentic_core/L2_execution/determinism.py is shadowed by this
package directory. This __init__ loads it via importlib and re-exports its
public API so that existing `from agentic_core.L2_execution.determinism import ...`
calls continue to work.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L5_safety.enforcement.import_guard import get_import_guard
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

_STANDALONE = Path(__file__).resolve().parent.parent / "determinism.py"
if _STANDALONE.exists():
    get_import_guard().check(
        operation="spec_from_file_location", module_name="agentic_core.L2_execution._determinism_standalone"
    )
    _spec = importlib.util.spec_from_file_location(
        "agentic_core.L2_execution._determinism_standalone", _STANDALONE
    )
    _mod = importlib.util.module_from_spec(_spec)
    get_import_guard().check(operation="exec_module", module_name=_mod.__name__)
    _spec.loader.exec_module(_mod)
    build_agent_2x2_inventory = _mod.build_agent_2x2_inventory
    compute_p5_determinism_digest = _mod.compute_p5_determinism_digest
    compute_w6_determinism_digest = _mod.compute_w6_determinism_digest
    compute_lockdown_determinism_digest = _mod.compute_lockdown_determinism_digest
    generate_determinism_digest = _mod.generate_determinism_digest
    generate_lockdown_determinism_digest = _mod.generate_lockdown_determinism_digest
    write_agent_2x2_inventory = _mod.write_agent_2x2_inventory
    get_embedding_config_surface = _mod.get_embedding_config_surface
    get_meta_learning_config_surface = _mod.get_meta_learning_config_surface
    INVENTORY_ARTIFACT_PATH = _mod.INVENTORY_ARTIFACT_PATH
    REPO_ROOT = _mod.REPO_ROOT
