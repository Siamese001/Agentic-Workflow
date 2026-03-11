"""ADG Analysis package — enhancements 6-10.

Modules:
  snapshot    - Enhancement 6: Deterministic canonical graph snapshotting
  diff        - Enhancement 7: Historical graph diff engine
  ownership   - Enhancement 8: Ownership / blast-radius overlay
  confidence  - Enhancement 9: Edge confidence and provenance scoring
  repair      - Enhancement 10: Repair recommendation / routing layer
"""

from agentic_core.adg.analysis.confidence import EdgeConfidence, score_edges
from agentic_core.adg.analysis.diff import GraphDiff, diff_snapshots
from agentic_core.adg.analysis.impact import ImpactReport, predict_impact
from agentic_core.adg.analysis.ownership import ModuleOwnership, OwnershipRegistry
from agentic_core.adg.analysis.repair import RepairRoute, route_violations
from agentic_core.adg.analysis.snapshot import CanonicalSnapshot, build_snapshot

__all__ = [
    "CanonicalSnapshot",
    "build_snapshot",
    "GraphDiff",
    "diff_snapshots",
    "ImpactReport",
    "predict_impact",
    "ModuleOwnership",
    "OwnershipRegistry",
    "EdgeConfidence",
    "score_edges",
    "RepairRoute",
    "route_violations",
]
