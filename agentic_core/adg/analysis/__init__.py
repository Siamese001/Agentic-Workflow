"""ADG Analysis package — enhancements 6-10.

Modules:
  snapshot    - Enhancement 6: Deterministic canonical graph snapshotting
  diff        - Enhancement 7: Historical graph diff engine
  ownership   - Enhancement 8: Ownership / blast-radius overlay
  confidence  - Enhancement 9: Edge confidence and provenance scoring
  repair      - Enhancement 10: Repair recommendation / routing layer
"""

from agentic_core.adg.analysis.CanonicalSnapshot import CanonicalSnapshot, build_snapshot
from agentic_core.adg.analysis.EdgeConfidence import EdgeConfidence, score_edges
from agentic_core.adg.analysis.GraphDiff import GraphDiff, diff_snapshots
from agentic_core.adg.analysis.healer_validator_graph_validator import (
    HealerValidatorEdge,
    HealerValidatorReport,
    detect_healer_validator_relationships,
)
from agentic_core.adg.analysis.ImpactReport import ImpactReport, predict_impact
from agentic_core.adg.analysis.ModuleOwnership import ModuleOwnership, OwnershipRegistry
from agentic_core.adg.analysis.RepairRoute import RepairRoute, route_violations

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
    # G1 (gap): Healer/validator graph
    "HealerValidatorEdge",
    "HealerValidatorReport",
    "detect_healer_validator_relationships",
]
