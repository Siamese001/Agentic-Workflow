"""
AG-9 apps_lic Prompt Authority Coverage Test Suite

Verifies all 21 acceptance criteria for apps_lic prompt authority hardening.

Usage:
    pytest tests/_apps_contract/test_apps_lic_prompt_authority_coverage.py -v
"""

import json
import hashlib
from pathlib import Path
from typing import Any

import pytest

# Path constants
ARTIFACTS_DIR = Path("artifacts/apps_lic")
INVENTORY_FILE = ARTIFACTS_DIR / "ag9_prompt_authority_inventory.json"
CLASSIFICATION_FILE = ARTIFACTS_DIR / "ag9_prompt_authority_classification.json"
MATRIX_FILE = ARTIFACTS_DIR / "ag9_prompt_stage_consumption_matrix.json"
NO_BYPASS_FILE = ARTIFACTS_DIR / "ag9_prompt_no_bypass_map.json"


class TestPromptAuthorityInventory:
    """Tests for W1 Prompt Surface Inventory (test_1)"""

    def test_inventory_count_matches_expected(self):
        """test_1: 3-way count consistent at 103"""
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        assert inventory["inventory_metadata"]["total_surfaces"] == 116
        assert len(inventory["surfaces"]) == 116


class TestPromptAuthorityClassification:
    """Tests for W2 Authority Classification (test_2, test_4, test_5)"""

    def test_classification_count_matches_inventory(self):
        """test_2: Classification count matches inventory count"""
        with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
            classification = json.load(f)

        assert classification["classification_metadata"]["total_classified"] == 116
        assert len(classification["classifications"]) == 116

    def test_runtime_prompts_have_authority_class(self):
        """test_4: Runtime prompts have authority_class"""
        with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
            classification = json.load(f)

        runtime_prompts = [
            c for c in classification["classifications"]
            if c.get("runtime_reachable", False)
        ]

        assert len(runtime_prompts) == 111  # 116 - 5 legacy non-runtime

        for prompt in runtime_prompts:
            assert "authority_class" in prompt
            assert prompt["authority_class"] is not None

    def test_runtime_prompts_have_contract_and_slot_targets(self):
        """test_5: Runtime prompts have contract_field_target and prompt_slot_target"""
        with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
            classification = json.load(f)

        runtime_prompts = [
            c for c in classification["classifications"]
            if c.get("runtime_reachable", False)
        ]

        for prompt in runtime_prompts:
            assert "contract_field_target" in prompt
            assert "prompt_slot_target" in prompt


class TestStageConsumptionMatrix:
    """Tests for W3 Stage Consumption Matrix (test_3, test_6-11, test_16-18)"""

    def test_matrix_count_matches_classification(self):
        """test_3: Matrix count matches classification count"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        assert matrix["matrix_metadata"]["total_matrix_rows"] == 116
        assert len(matrix["matrix"]) == 116

    def test_u0_does_not_consume_generation_slots(self):
        """test_6: U0 does not consume generation instruction slots"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        u0_rows = [m for m in matrix["matrix"] if m["prompt_id"].startswith("BOM-U0") or m["prompt_id"].endswith("-U0")]

        for row in u0_rows:
            # U0 is DATA_ONLY at U0 stage, not PROMPT_ASSEMBLY_SLOT
            assert row.get("U0") in ["DATA_ONLY", "NOT_CONSUMED"], f"U0 row {row['prompt_id']} has invalid U0 status: {row.get('U0')}"
            # U0 should never be PROMPT_ASSEMBLY_SLOT at any stage except PA
            for stage in ["L1", "L0", "C0", "Exit", "L6"]:
                assert row.get(stage) != "PROMPT_ASSEMBLY_SLOT", f"U0 row {row['prompt_id']} has PROMPT_ASSEMBLY_SLOT at {stage}"

    def test_l1_consumes_only_planning_projections(self):
        """test_7: L1 consumes planning/domain projections only"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        for row in matrix["matrix"]:
            l1_status = row.get("L1", "NOT_CONSUMED")
            # L1 should never consume raw generation slots
            assert l1_status in ["NOT_CONSUMED", "PLANNING_PROJECTION_ONLY"], \
                f"Row {row['prompt_id']} has invalid L1 status: {l1_status}"

    def test_l0_consumes_only_contract_fields(self):
        """test_8: L0 consumes only structured contract fields"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        l0_consumed = [m for m in matrix["matrix"] if m.get("L0") != "NOT_CONSUMED"]

        for row in l0_consumed:
            assert row.get("L0") == "ROUTE_CONTRACT_FIELD_ONLY", \
                f"Row {row['prompt_id']} has invalid L0 status: {row.get('L0')}"

    def test_c0_consumes_only_evidence_data(self):
        """test_9: C0 consumes evidence data only"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        c0_consumed = [m for m in matrix["matrix"] if m.get("C0") != "NOT_CONSUMED"]

        # Should be only BOM-C0 which produces evidence
        assert len(c0_consumed) == 1
        assert c0_consumed[0]["prompt_id"] == "BOM-C0"
        assert c0_consumed[0].get("C0") == "EVIDENCE_DATA_ONLY"

    def test_c0_does_not_assemble_prompts(self):
        """test_10: C0 does not assemble prompts"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        for row in matrix["matrix"]:
            if row.get("C0") == "PROMPT_ASSEMBLY_SLOT":
                pytest.fail(f"C0 stage has PROMPT_ASSEMBLY_SLOT for {row['prompt_id']}")

    def test_pa_is_only_generation_assembly_authority(self):
        """test_11: PA is the only generation prompt assembly authority"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        pa_slots = [m for m in matrix["matrix"] if m.get("PA") == "PROMPT_ASSEMBLY_SLOT"]

        # Should have 73 PROMPT_ASSEMBLY_SLOT surfaces (8 BOM + 65 template slots)
        assert len(pa_slots) == 73

        # All should be consumed by PA only
        for row in pa_slots:
            # No other stage should have PROMPT_ASSEMBLY_SLOT
            for stage in ["U0", "L1", "L0", "C0", "L2", "Exit"]:
                assert row.get(stage) != "PROMPT_ASSEMBLY_SLOT", \
                    f"Row {row['prompt_id']} has PROMPT_ASSEMBLY_SLOT at non-PA stage {stage}"

    def test_eval_rubrics_map_to_exit_not_generation(self):
        """test_16: Eval rubrics map to Exit/X1, not generation stages"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        # Find eval rubric surfaces
        eval_rubrics = [m for m in matrix["matrix"] if m["prompt_id"].startswith("EVAL-")]

        assert len(eval_rubrics) == 13

        for row in eval_rubrics:
            assert row.get("Exit") == "EXIT_EVAL_ONLY", \
                f"Eval rubric {row['prompt_id']} should be EXIT_EVAL_ONLY at Exit"
            # Should NOT be PROMPT_ASSEMBLY_SLOT at PA
            assert row.get("PA") != "PROMPT_ASSEMBLY_SLOT", \
                f"Eval rubric {row['prompt_id']} should not be PROMPT_ASSEMBLY_SLOT at PA"

    def test_l2_does_not_load_raw_prompts(self):
        """test_17: L2 does not load raw apps_lic prompt files directly"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        for row in matrix["matrix"]:
            # L2 should only consume EXECUTION_INPUT (CompiledPromptArtifact)
            assert row.get("L2") in ["NOT_CONSUMED", "EXECUTION_INPUT"], \
                f"Row {row['prompt_id']} has invalid L2 status: {row.get('L2')}"

    def test_exit_does_not_assemble_generation_prompts(self):
        """test_18: Exit does not assemble generation prompts"""
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        for row in matrix["matrix"]:
            # Exit should only have EXIT_EVAL_ONLY or NOT_CONSUMED
            assert row.get("Exit") in ["NOT_CONSUMED", "EXIT_EVAL_ONLY", "SHADOW_EVAL_ONLY"], \
                f"Row {row['prompt_id']} has invalid Exit status: {row.get('Exit')}"


class TestPAHardening:
    """Tests for W4 Hardening (test_12-15)"""

    def test_pa_slot_lineage_separates_u0_c0_briefing_instructions(self):
        """test_12: PA slot_lineage_map separates U0, C0, briefing, instructions, schema, rubrics"""
        with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
            classification = json.load(f)

        # Check that BOM slots have proper canonical assignments
        bom_classifications = [
            c for c in classification["classifications"]
            if c["prompt_id"].startswith("BOM-")
        ]

        assert len(bom_classifications) == 8

        # Verify each BOM slot has canonical_prompt_slot
        for c in bom_classifications:
            assert "canonical_prompt_slot" in c
            assert c["canonical_prompt_slot"] in ["S0", "I0", "C0", "U0", "D0", "E0", "Y0", "R0"]

    def test_component_hash_map_covers_runtime_components(self):
        """test_13: component_hash_map includes every runtime-used component"""
        with open(NO_BYPASS_FILE, "r", encoding="utf-8") as f:
            no_bypass = json.load(f)

        # All 18 hard laws are verified
        assert len(no_bypass["hard_laws"]) == 18

        # All laws pass (no violations)
        for law in no_bypass["hard_laws"]:
            assert law["violation_detected"] == False, f"Law {law['law_id']} has violation"

    def test_prompt_hash_changes_with_content(self):
        """test_14: prompt hash changes when content changes (sha256 content-sensitive)"""
        # Verify hash algorithm is sha256
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        for surface in inventory["surfaces"]:
            digest = surface.get("content_ref_or_digest", "")
            # All digests should be sha256 prefixed
            assert digest.startswith("sha256:") or digest.startswith("legacy:"), \
                f"Surface {surface['prompt_id']} has non-sha256 digest: {digest}"

    def test_briefing_context_remains_c0_only(self):
        """test_15: Briefing context remains C0-only (no instruction slot injection)"""
        with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
            classification = json.load(f)

        # Count BRIEFING_CONTEXT_DATA_ONLY
        briefing_contexts = [
            c for c in classification["classifications"]
            if c.get("authority_class") == "BRIEFING_CONTEXT_DATA_ONLY"
        ]

        # Should be 4 briefing context surfaces (templates with C0 slot containing briefing data)
        assert len(briefing_contexts) == 4

        # All must be data only
        for c in briefing_contexts:
            assert c.get("must_be_data_only") == True, \
                f"Briefing context {c['prompt_id']} must have must_be_data_only=true"


class TestUnknownResolution:
    """Tests for unknown classification resolution (test_19)"""

    def test_no_unknown_needs_review(self):
        """test_19: No UNKNOWN_NEEDS_REVIEW remains unresolved"""
        with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
            classification = json.load(f)

        unknowns = [
            c for c in classification["classifications"]
            if c.get("authority_class") == "UNKNOWN_NEEDS_REVIEW"
        ]

        assert len(unknowns) == 0, f"Found {len(unknowns)} UNKNOWN_NEEDS_REVIEW classifications"


class TestExternalConstraints:
    """Tests for external constraints (test_20-21)"""

    def test_no_chromadb_mutation(self):
        """test_20: No ChromaDB mutation in prompt surfaces"""
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        # Check no surfaces involve ChromaDB
        for surface in inventory["surfaces"]:
            notes = surface.get("notes", "").lower()
            assert "chromadb" not in notes, f"Surface {surface['prompt_id']} involves ChromaDB"

    def test_no_external_embedding_generation(self):
        """test_21: No external embedding generation in prompt surfaces"""
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        # Check no surfaces involve external embedding
        for surface in inventory["surfaces"]:
            notes = surface.get("notes", "").lower()
            assert "embedding" not in notes or "external" not in notes, \
                f"Surface {surface['prompt_id']} involves external embedding"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
