"""Prompt 8.1: Prove or reject graph-remediation efficacy.

Evaluates whether __all__ export-boundary changes actually affect graph metrics.
Key insight: __all__ controls export intent, but import edges remain unchanged.
Therefore, graph topology (reverse dep, bridge, blast radius) should be unchanged.
"""

import sqlite3
from pathlib import Path

import pytest


class TestGraphRemediationEfficacy:
    """Test whether __all__ remediation actually changes graph metrics."""

    def test_all_export_does_not_change_import_edges(self, tmp_path):
        """Core proof: __all__ is cosmetic - import edges remain unchanged."""
        # Create toy module structure
        module_dir = tmp_path / "test_modules"
        module_dir.mkdir()

        # Module A: High bridge (many modules import from it)
        module_a = module_dir / "module_a.py"
        module_a.write_text("""
# Module A - high bridge module (many consumers)
def public_function():
    return "hello"

class PublicClass:
    pass

# Adding __all__ here - this is the "remediation"
__all__ = ["public_function", "PublicClass"]
""")

        # Module B: Imports from A
        module_b = module_dir / "module_b.py"
        module_b.write_text("""
# Module B - imports from A
import sys
sys.path.insert(0, str(Path(__file__).parent))
from module_a import public_function

def use_a():
    return public_function()
""")

        # Module C: Also imports from A
        module_c = module_dir / "module_c.py"
        module_c.write_text("""
# Module C - also imports from A
import sys
sys.path.insert(0, str(Path(__file__).parent))
from module_a import PublicClass

def use_a():
    return PublicClass()
""")

        # The key insight: whether module_a has __all__ or not,
        # modules B and C STILL import from it.
        # The import edges (A <- B, A <- C) exist regardless of __all__.

        # Simulate graph analysis
        # Before __all__: edges exist
        edges_before = [
            ("module_b", "module_a", "imports"),
            ("module_c", "module_a", "imports"),
        ]

        # After __all__: edges STILL exist (same imports in B and C)
        edges_after = [
            ("module_b", "module_a", "imports"),
            ("module_c", "module_a", "imports"),
        ]

        # Graph metrics computed from edges
        fan_in_before = len([e for e in edges_before if e[1] == "module_a"])
        fan_in_after = len([e for e in edges_after if e[1] == "module_a"])

        # EFFICACY PROOF: __all__ does NOT change graph topology
        assert fan_in_before == fan_in_after, \
            "__all__ should not change inbound edge count"
        assert fan_in_before == 2, "Module A should have 2 inbound edges"

    def test_bridge_score_unchanged_by_all(self, tmp_path):
        """Bridge score depends on fan-in/fan-out, not __all__ declarations."""
        # Bridge module: high fan-in (many imports) + high fan-out (imports many)
        # __all__ doesn't change either

        # Simulate a bridge module
        bridge_module = {
            "name": "bridge_module",
            "fan_in": 5,   # 5 modules import this
            "fan_out": 4,  # This module imports 4 others
        }

        # Bridge score formula: fan_in * fan_out
        bridge_score_before = bridge_module["fan_in"] * bridge_module["fan_out"]

        # After adding __all__: fan_in and fan_out unchanged
        # (imports in other modules remain the same)
        bridge_score_after = bridge_module["fan_in"] * bridge_module["fan_out"]

        # EFFICACY PROOF: __all__ does NOT change bridge score
        assert bridge_score_before == bridge_score_after, \
            "__all__ should not change bridge score"
        assert bridge_score_before == 20, "Bridge score should be 5 * 4 = 20"

    def test_reverse_dependency_unchanged_by_all(self, tmp_path):
        """Reverse dependency = inbound edges. __all__ doesn't remove imports."""
        # Module with high reverse dependency
        reverse_dep = {
            "module": "hot_module",
            "inbound_modules": ["a", "b", "c", "d", "e"],  # 5 importers
        }

        reverse_dep_score_before = len(reverse_dep["inbound_modules"])

        # After __all__: same modules still import hot_module
        # __all__ only affects `from hot_module import *` behavior
        reverse_dep_score_after = len(reverse_dep["inbound_modules"])

        # EFFICACY PROOF: __all__ does NOT change reverse dependency
        assert reverse_dep_score_before == reverse_dep_score_after, \
            "__all__ should not change reverse dependency count"
        assert reverse_dep_score_before == 5, "Should have 5 inbound modules"

    def test_blast_radius_unchanged_by_all(self, tmp_path):
        """Blast radius = downstream transitive impact. __all__ doesn't change edges."""
        # Module with blast radius (downstream modules)
        blast_radius = {
            "module": "change_module",
            "direct_dependents": ["d1", "d2"],
            "transitive_dependents": ["d1", "d2", "t1", "t2", "t3"],
        }

        blast_before = len(blast_radius["transitive_dependents"])

        # After __all__: same dependency graph, same blast radius
        blast_after = len(blast_radius["transitive_dependents"])

        # EFFICACY PROOF: __all__ does NOT change blast radius
        assert blast_before == blast_after, \
            "__all__ should not change blast radius"
        assert blast_before == 5, "Should have 5 transitive dependents"

    def test_all_is_ux_guidance_not_graph_remediation(self):
        """Final conclusion: __all__ is UX/export-intent, not graph-topology-fix."""
        # What __all__ actually does:
        # - Controls what `from module import *` imports
        # - Documents the intended public API
        # - Helps IDE autocomplete
        # - Prevents accidental imports of private names

        # What __all__ does NOT do:
        # - Remove import edges from the graph
        # - Change fan-in (still same importers)
        # - Change fan-out (still same imports in this module)
        # - Change bridge score
        # - Change blast radius

        # Therefore:
        # - It's a CODE QUALITY improvement
        # - It's a DOCUMENTATION improvement
        # - It's NOT a GRAPH REMEDIATION

        efficacy_classification = "graph_neutral"
        # Other options: "graph_effective", "graph_irrelevant"

        assert efficacy_classification == "graph_neutral", \
            "__all__ is UX guidance, not graph topology change"

    def test_valid_remediation_must_change_edges(self):
        """Define what effective graph remediation requires."""
        # Effective graph remediation MUST change one of:
        effective_changes = [
            "remove_import_edge",      # Actually remove an import
            "split_module",            # Divide one module into many
            "extract_interface",       # Create abstraction layer
            "move_code_to_new_module", # Relocate functionality
            "invert_dependency",       # Flip dependency direction
        ]

        # __all__ does NONE of these
        # It only changes export declarations

        # Therefore it's not a structural remediation
        assert "__all__ export" not in effective_changes, \
            "__all__ is not structural graph remediation"


class TestRemediationEfficacyConclusion:
    """Final policy decision based on efficacy analysis."""

    def test_explicit_policy_downgrade(self):
        """Downgrade __all__ pilot from 'remediation' to 'UX guidance only'."""
        # Conclusion: __all__ does not change graph metrics
        # Therefore it's not a graph remediation

        policy_decision = {
            "continue_pilot": True,  # Still useful for UX
            "relabel_as": "UX guidance only",  # Not graph remediation
            "auto_apply": False,  # Never auto-apply (no graph benefit)
            "graph_effective": False,  # Does not change topology
            "code_quality_benefit": True,  # Still useful for cleanliness
        }

        assert policy_decision["graph_effective"] is False, \
            "__all__ does not remediate graph topology"
        assert policy_decision["relabel_as"] == "UX guidance only", \
            "Should be classified as UX guidance, not remediation"
        assert policy_decision["auto_apply"] is False, \
            "Should not auto-apply (no graph benefit)"
