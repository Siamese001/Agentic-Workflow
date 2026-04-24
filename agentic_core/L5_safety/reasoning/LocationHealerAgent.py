"""LocationHealerAgent - Backward compatibility re-export shim.

DEPRECATED: The LocationHealerAgent class body was relocated to
agentic_core.L5_safety.utils.location_healer_util (MW-9, 2026-04-24) so
that this reasoning/ module can be archived at the agent-deprecation W6
sweep without breaking consumers. New code MUST import from the util
module directly.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W5 of agent-deprecation-migration-d7a3f2)
Archive-eligible date: 2026-07-23
Category: facade-reexport-shim
Canonical replacement: agentic_core.L5_safety.utils.location_healer_util

This shim re-exports every public symbol the class body previously exposed
so that any lingering import path still resolves during the 90-day cooling
window. Consumers migrated in MW-9 commit are listed below for W6 verification:

  - agentic_core/L5_safety/reasoning/hierarchy_healer.py
  - agentic_core/L5_safety/utils/location_path_util.py
  - agentic_core/L5_safety/utils/runners/agent_roster_runner.py
  - agentic_core/L5_safety/utils/runners/orchestrator_runner.py
  - ops_scripts/general/sovereign_healing_mission.py
  - tests/integration/agentic_core/test_depth_violation_no_archive_invariant.py
  - tools/generate/territory_healer_adapters.py

Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__LocationHealerAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_LocationHealerAgent.json
"""

from __future__ import annotations

import warnings as _warnings

from agentic_core.L5_safety.utils.location_healer_util import (  # noqa: F401
    LocationHealerAgent,
)

_warnings.warn(
    "agentic_core.L5_safety.reasoning.LocationHealerAgent is a deprecation "
    "re-export shim. Import LocationHealerAgent from "
    "agentic_core.L5_safety.utils.location_healer_util instead. "
    "This shim will be archived on or after 2026-07-23.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["LocationHealerAgent"]
