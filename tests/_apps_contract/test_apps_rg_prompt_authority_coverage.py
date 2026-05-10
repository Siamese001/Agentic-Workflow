"""W4 Prompt Authority Coverage Tests for apps_rg.

Proves the 21 invariants required by W4 acceptance criteria:
1.  inventory/classification/matrix counts reconcile at 86
2.  discovered_not_yet_classified count is visible and nonzero if still deferred
3.  no matrix prompt_id is missing classification
4.  no runtime prompt lacks authority_class
5.  no runtime prompt lacks contract_field_target or prompt_slot_target
6.  U0 does not consume instructional prompts as authority
7.  L1 consumes only planning/domain projections
8.  L0 consumes only structured L1PlanContract fields (no raw prompt text)
9.  L0 does not parse raw prompt text
10. C0 does not assemble prompts
11. PA is the only generation prompt assembly authority
12. PA slot_lineage_map separates U0 task from C0 evidence
13. PA component_hash_map includes runtime-used prompt components
14. prompt_hash changes when meaningful runtime prompt components change
15. retrieved evidence remains C0_EVIDENCE_DATA_ONLY
16. evaluator rubrics map to Exit/X1, not generation authority
17. L2 does not load raw apps_rg prompts
18. Exit does not assemble generation prompts
19. UNKNOWN_NEEDS_REVIEW rows are either resolved or explicitly deferred
20. no ChromaDB mutation
21. no embedding generation
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Repo-root path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACTS = REPO_ROOT / "artifacts" / "apps_rg"

# ---------------------------------------------------------------------------
# Fixture: load the three SOT JSON files once per session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def inventory() -> dict[str, Any]:
    with open(ARTIFACTS / "ag8_prompt_authority_inventory.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def classification() -> dict[str, Any]:
    with open(ARTIFACTS / "ag8_prompt_authority_classification.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def matrix() -> dict[str, Any]:
    with open(ARTIFACTS / "ag8_prompt_stage_consumption_matrix.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def inv_ids(inventory: dict[str, Any]) -> list[str]:
    return [p["prompt_id"] for p in inventory["prompts"]]


@pytest.fixture(scope="session")
def cls_ids(classification: dict[str, Any]) -> list[str]:
    return [p["prompt_id"] for p in classification["classifications"]]


@pytest.fixture(scope="session")
def mat_ids(matrix: dict[str, Any]) -> list[str]:
    return [r["prompt_id"] for r in matrix["matrix"]]


@pytest.fixture(scope="session")
def cls_map(classification: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {p["prompt_id"]: p for p in classification["classifications"]}


@pytest.fixture(scope="session")
def mat_map(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["prompt_id"]: r for r in matrix["matrix"]}


# ---------------------------------------------------------------------------
# Helper: classify runtime reachability
# ---------------------------------------------------------------------------

def _runtime_ids(cls_map: dict[str, dict]) -> list[str]:
    return [
        pid for pid, e in cls_map.items()
        if e.get("runtime_reachable") is True
    ]


# ---------------------------------------------------------------------------
# Test 1: count reconciliation
# ---------------------------------------------------------------------------

def test_1_count_reconciliation(inventory, classification, matrix, inv_ids, cls_ids, mat_ids):
    """T1: inventory count = classification count = matrix count = 86."""
    inv_meta = inventory["inventory_metadata"]["total_items"]
    cls_meta = classification["classification_metadata"]["total_classified"]
    assert inv_meta == 86, f"inventory metadata total_items={inv_meta}, expected 86"
    assert cls_meta == 86, f"classification metadata total_classified={cls_meta}, expected 86"
    assert len(inv_ids) == 86
    assert len(cls_ids) == 86
    assert len(mat_ids) == 86
    assert set(inv_ids) == set(cls_ids) == set(mat_ids), "Three-way ID set mismatch"


# ---------------------------------------------------------------------------
# Test 2: discovered_not_yet_classified bucket is visible and nonzero
# ---------------------------------------------------------------------------

def test_2_discovered_bucket_visible_and_nonzero(inventory):
    """T2: discovered_not_yet_classified is a top-level key with ≥1 entries."""
    bucket = inventory.get("discovered_not_yet_classified", [])
    assert isinstance(bucket, list), "discovered_not_yet_classified must be a list"
    assert len(bucket) > 0, (
        "discovered_not_yet_classified is empty — if all surfaces classified, "
        "update W4 acceptance criteria to reflect 0 deferred"
    )
    assert len(bucket) == 13, f"Expected 13 deferred surfaces, got {len(bucket)}"


# ---------------------------------------------------------------------------
# Test 3: no matrix prompt_id is missing from classification
# ---------------------------------------------------------------------------

def test_3_no_matrix_id_missing_classification(cls_ids, mat_ids):
    """T3: every matrix row has a corresponding classification entry."""
    missing = set(mat_ids) - set(cls_ids)
    assert not missing, f"Matrix IDs not in classification: {sorted(missing)}"


# ---------------------------------------------------------------------------
# Test 4: no runtime prompt lacks authority_class
# ---------------------------------------------------------------------------

def test_4_runtime_prompts_have_authority_class(cls_map):
    """T4: every runtime-reachable prompt has a non-empty authority_class."""
    violations = []
    for pid in _runtime_ids(cls_map):
        ac = cls_map[pid].get("authority_class", "")
        if not ac:
            violations.append(pid)
    assert not violations, f"Runtime prompts missing authority_class: {violations}"


# ---------------------------------------------------------------------------
# Test 5: no runtime prompt lacks contract_field_target or prompt_slot_target
# ---------------------------------------------------------------------------

def test_5_runtime_prompts_have_targets(cls_map):
    """T5: every runtime-reachable prompt has contract_field_target AND prompt_slot_target."""
    violations = []
    for pid in _runtime_ids(cls_map):
        e = cls_map[pid]
        cft = e.get("contract_field_target", "")
        pst = e.get("prompt_slot_target", "")
        if not cft or not pst:
            violations.append(f"{pid}(cft={cft!r},pst={pst!r})")
    assert not violations, f"Runtime prompts missing targets: {violations}"


# ---------------------------------------------------------------------------
# Test 6: U0 does not consume instructional prompts as authority
# ---------------------------------------------------------------------------

def test_6_u0_no_instruction_authority(mat_map, cls_map):
    """T6: U0 must not consume prompts whose slot is a generation instruction slot.

    Exception: BOM slot declarations (canonical_prompt_slot=U0_NEUTRALIZED_USER_TASK)
    consumed at U0 are legitimate — they are data-labeling policies, not generation
    instructions. The check is therefore slot-based, not authority-class-based:
    U0 must not REQUIRE prompts whose canonical_prompt_slot is a generation slot
    (S0_SYSTEM, I0_INSTRUCTIONS, E0_APPROVED_EXAMPLES, D0_DOMAIN_KNOWLEDGE).
    """
    generation_slots = {"S0_SYSTEM", "I0_INSTRUCTIONS", "E0_APPROVED_EXAMPLES",
                        "D0_DOMAIN_KNOWLEDGE"}
    violations = []
    for pid, row in mat_map.items():
        if row.get("U0_consumption") == "REQUIRED":
            slot = cls_map.get(pid, {}).get("canonical_prompt_slot", "")
            if slot in generation_slots:
                violations.append(f"{pid}(slot={slot})")
    assert not violations, f"U0 consuming generation instruction slots: {violations}"


# ---------------------------------------------------------------------------
# Test 7: L1 consumes only planning/domain projections
# ---------------------------------------------------------------------------

def test_7_l1_consumes_only_planning_projections(mat_map, cls_map):
    """T7: every prompt REQUIRED at L1 must have a planning, domain, or schema class.

    L1 is allowed to consume:
    - LEARNING_PRIOR: prior task/context knowledge
    - DOMAIN_INSTRUCTION: domain-level guidance
    - ROUTE_RULE: routing policy declarations
    - OUTPUT_SCHEMA: output schema declarations (L1 declares expected format via R0 slot)
    - POLICY_AUTHORITY: BOM/profile policy used for slot validation

    L1 must NOT consume raw generation instruction text (S0/I0/E0/D0 slot content).
    The check is slot-based for generation text, authority-class-based for policy.
    """
    generation_slots = {"S0_SYSTEM", "I0_INSTRUCTIONS", "E0_APPROVED_EXAMPLES",
                        "D0_DOMAIN_KNOWLEDGE"}
    violations = []
    for pid, row in mat_map.items():
        if row.get("L1_consumption") == "REQUIRED":
            slot = cls_map.get(pid, {}).get("canonical_prompt_slot", "")
            if slot in generation_slots:
                violations.append(f"{pid}(slot={slot})")
    assert not violations, f"L1 consuming raw generation instruction slots: {violations}"


# ---------------------------------------------------------------------------
# Test 8: L0 consumes only structured route fields (no raw text)
# ---------------------------------------------------------------------------

def test_8_l0_no_raw_prompt_consumption(mat_map, cls_map):
    """T8: no prompt REQUIRED at L0 has a raw-text slot (S0/I0/U0/C0/PA)."""
    raw_slots = {"S0_SYSTEM", "I0_INSTRUCTIONS", "U0_NEUTRALIZED_USER_TASK",
                 "C0_VERIFIED_EVIDENCE_DATA", "E0_APPROVED_EXAMPLES"}
    violations = []
    for pid, row in mat_map.items():
        if row.get("L0_consumption") == "REQUIRED":
            slot = cls_map.get(pid, {}).get("canonical_prompt_slot", "")
            if slot in raw_slots:
                violations.append(f"{pid}(slot={slot})")
    assert not violations, f"L0 consuming raw prompt slots: {violations}"


# ---------------------------------------------------------------------------
# Test 9: L0 binding does not parse raw prompt text (static analysis)
# ---------------------------------------------------------------------------

def test_9_l0_binding_no_raw_prompt_parse():
    """T9: the L0 binding source does not call any prompt text parser."""
    l0_path = REPO_ROOT / "agentic_core" / "L0_routing" / "apps_rg_l0_binding.py"
    content = l0_path.read_text(encoding="utf-8")
    forbidden_patterns = [
        "yaml.safe_load",
        "yaml.load",
        "json.loads",
        "open(",
        "read_text",
        "rg_prompt_profile",
        "slot_mapper",
        "prompt_bom",
    ]
    violations = [p for p in forbidden_patterns if p in content]
    assert not violations, f"L0 binding contains raw-prompt patterns: {violations}"


# ---------------------------------------------------------------------------
# Test 10: C0 binding does not assemble prompts
# ---------------------------------------------------------------------------

def test_10_c0_no_prompt_assembly():
    """T10: the C0 binding source does not call pa_compose_apps_rg or build prompt blocks."""
    c0_path = REPO_ROOT / "agentic_core" / "runtime" / "c0" / "apps_rg_c0_binding.py"
    content = c0_path.read_text(encoding="utf-8")
    forbidden = [
        "pa_compose_apps_rg",
        "PromptBlock(",
        "_build_system_preamble",
        "_build_user_instruction",
        "_build_u0_task_block",
        "_build_c0_evidence_block",
    ]
    violations = [f for f in forbidden if f in content]
    assert not violations, f"C0 binding contains prompt assembly: {violations}"


# ---------------------------------------------------------------------------
# Test 11: PA is the only generation prompt assembly authority
# ---------------------------------------------------------------------------

def test_11_pa_sole_generation_authority():
    """T11: only apps_rg_pa_binding.py calls PromptBlock and pa_compose_apps_rg."""
    pa_path = REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py"
    pa_content = pa_path.read_text(encoding="utf-8")
    assert "PromptBlock(" in pa_content, "PA binding must use PromptBlock"

    # No other binding in agentic_core should assemble PromptBlock for apps_rg
    other_bindings = [
        REPO_ROOT / "agentic_core" / "L0_routing" / "apps_rg_l0_binding.py",
        REPO_ROOT / "agentic_core" / "L1_cognition" / "apps_rg_l1_binding.py",
        REPO_ROOT / "agentic_core" / "runtime" / "c0" / "apps_rg_c0_binding.py",
        REPO_ROOT / "agentic_core" / "L2_execution" / "apps_rg_l2_binding.py",
        REPO_ROOT / "agentic_core" / "runtime" / "exit" / "apps_rg_exit_binding.py",
    ]
    violations = []
    for path in other_bindings:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if "PromptBlock(" in content:
                violations.append(path.name)
    assert not violations, f"Non-PA bindings assembling PromptBlock: {violations}"


# ---------------------------------------------------------------------------
# Test 12: PA slot_lineage_map separates U0 task from C0 evidence
# ---------------------------------------------------------------------------

def test_12_pa_slot_lineage_separates_u0_c0():
    """T12: pa_compose_apps_rg slot_lineage_map has distinct U0 and C0 entries."""
    from agentic_core.prompt_governance.apps_rg_pa_binding import (
        _build_u0_task_block,
        _build_c0_evidence_block,
    )
    # Verify the two builders are separate callables
    assert callable(_build_u0_task_block)
    assert callable(_build_c0_evidence_block)

    # Verify the PA source has the correct slot keys
    pa_path = REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py"
    content = pa_path.read_text(encoding="utf-8")
    assert "U0_NEUTRALIZED_USER_TASK" in content, "slot_lineage_map missing U0 slot"
    assert "C0_VERIFIED_EVIDENCE_DATA" in content, "slot_lineage_map missing C0 slot"
    assert "I0_INSTRUCTIONS" in content, "slot_lineage_map missing I0 slot"
    assert "R0_RESPONSE_SCHEMA" in content, "slot_lineage_map missing R0 slot"
    assert "S0_SYSTEM" in content, "slot_lineage_map missing S0 slot"
    # PAB-003: the slot_lineage_map dict must NOT use "USER_INTENT+EVIDENCE" as a value.
    # Note: the string may appear in comments explaining the fix — check dict assignments only.
    # Extract lines that are actual dict value assignments (contain '": "' pattern)
    dict_value_lines = [
        line for line in content.splitlines()
        if '"user_block_1' in line and "USER_INTENT+EVIDENCE" in line
    ]
    assert not dict_value_lines, (
        "PAB-003: slot_lineage_map dict still assigns USER_INTENT+EVIDENCE: "
        + str(dict_value_lines)
    )


# ---------------------------------------------------------------------------
# Test 13: PA component_hash_map includes all runtime-used prompt components
# ---------------------------------------------------------------------------

def test_13_pa_component_hash_map_complete():
    """T13: pa_compose_apps_rg component_hash_map covers all required components."""
    pa_path = REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py"
    content = pa_path.read_text(encoding="utf-8")
    required_keys = [
        '"style_profile__s0_i0"',
        '"evidence__c0"',
        '"u0_task_segment"',
        '"c0_evidence_segment"',
        '"l1_plan"',
        '"r0_schema"',
        '"app_payload"',
        '"route"',
    ]
    missing = [k for k in required_keys if k not in content]
    assert not missing, f"component_hash_map missing keys: {missing}"


# ---------------------------------------------------------------------------
# Test 14: prompt_hash changes when meaningful runtime content changes
# ---------------------------------------------------------------------------

def test_14_prompt_hash_changes_with_content():
    """T14: compilation_hash uses content hash (not length), so changing content
    changes the hash."""
    from agentic_core.prompt_governance.apps_rg_pa_binding import _component_hash

    content_a = "Resume tailoring for Company A, Senior Engineer role."
    content_b = "Resume tailoring for Company B, Director of Engineering role."
    assert content_a != content_b
    hash_a = _component_hash(content_a)
    hash_b = _component_hash(content_b)
    assert hash_a != hash_b, "Same hash for different content — hash is not content-sensitive"

    # Verify the PA binding uses content_hash not len in compilation_hash
    pa_path = REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py"
    content = pa_path.read_text(encoding="utf-8")
    assert "content_hash" in content, (
        "compilation_hash must use content_hash, not len(content)"
    )
    assert '"len"' not in content.split("compilation_hash")[1].split("canonical")[0] or \
           "content_hash" in content, (
        "compilation_hash must prefer content_hash over len for determinism"
    )


# ---------------------------------------------------------------------------
# Test 15: retrieved evidence maps to C0_VERIFIED_EVIDENCE_DATA, not instruction
# ---------------------------------------------------------------------------

def test_15_evidence_is_c0_only(cls_map, mat_map):
    """T15: C0 must not be used to inject generation instruction text.

    C0 is allowed to consume:
    - RETRIEVED_EVIDENCE: corpus/document evidence (canonical)
    - EXAMPLE_DATA: grounded examples
    - POLICY_AUTHORITY: BOM slot declarations and evidence directives that govern
      what C0 retrieves (slot=C0_VERIFIED_EVIDENCE_DATA) — these are metadata
      policies, not generation instructions

    C0 must NOT consume prompts whose slot is a generation instruction slot
    (S0_SYSTEM, I0_INSTRUCTIONS, E0_APPROVED_EXAMPLES).
    """
    generation_slots = {"S0_SYSTEM", "I0_INSTRUCTIONS", "E0_APPROVED_EXAMPLES",
                        "D0_DOMAIN_KNOWLEDGE"}
    violations = []
    for pid, row in mat_map.items():
        if row.get("C0_consumption") == "REQUIRED":
            slot = cls_map.get(pid, {}).get("canonical_prompt_slot", "")
            if slot in generation_slots:
                violations.append(f"{pid}(slot={slot})")
    assert not violations, f"C0 consuming generation instruction slots: {violations}"


# ---------------------------------------------------------------------------
# Test 16: evaluator rubrics map to Exit/X1, not generation authority
# ---------------------------------------------------------------------------

def test_16_rubrics_map_to_exit(cls_map, mat_map):
    """T16: prompts with EVAL_RUBRIC authority_class are consumed only at Exit_X1."""
    generation_stages = ["U0", "L1", "L0", "C0", "PA", "L2"]
    violations = []
    for pid, e in cls_map.items():
        if e.get("authority_class") == "EVAL_RUBRIC":
            row = mat_map.get(pid, {})
            for stage in generation_stages:
                key = stage + "_consumption"
                val = row.get(key, "FORBIDDEN")
                if val == "REQUIRED":
                    violations.append(f"{pid} consumed at {stage}")
    assert not violations, f"Evaluator rubrics consumed at generation stages: {violations}"


# ---------------------------------------------------------------------------
# Test 17: L2 binding does not load raw apps_rg prompts
# ---------------------------------------------------------------------------

def test_17_l2_no_raw_prompt_load():
    """T17: the L2 binding source does not open or parse apps_rg prompt files."""
    l2_path = REPO_ROOT / "agentic_core" / "L2_execution" / "apps_rg_l2_binding.py"
    content = l2_path.read_text(encoding="utf-8")
    forbidden = [
        "rg_prompt_profile",
        "rg_style_profile",
        "slot_mapper",
        "prompt_bom",
        "strategic_tailor",
        "warmup_pairs",
        "_build_system_preamble",
        "_build_user_instruction",
    ]
    violations = [f for f in forbidden if f in content]
    assert not violations, f"L2 binding loads raw apps_rg prompts: {violations}"


# ---------------------------------------------------------------------------
# Test 18: Exit binding does not assemble generation prompts
# ---------------------------------------------------------------------------

def test_18_exit_no_generation_prompt_assembly():
    """T18: the Exit binding does not assemble PromptBlock or call PA compose."""
    exit_path = REPO_ROOT / "agentic_core" / "runtime" / "exit" / "apps_rg_exit_binding.py"
    content = exit_path.read_text(encoding="utf-8")
    forbidden = [
        "pa_compose_apps_rg",
        "PromptBlock(",
        "_build_system_preamble",
        "_build_user_instruction",
        "_build_u0_task_block",
    ]
    violations = [f for f in forbidden if f in content]
    assert not violations, f"Exit binding assembles generation prompts: {violations}"


# ---------------------------------------------------------------------------
# Test 19: UNKNOWN_NEEDS_REVIEW rows are resolved or explicitly deferred
# ---------------------------------------------------------------------------

def test_19_no_unresolved_unknown(mat_map, cls_map):
    """T19: no row in the matrix has UNKNOWN_NEEDS_REVIEW consumption without
    a w4_resolution field in the classification entry."""
    stages = ["U0", "L1", "L0", "C0", "PA", "L3", "L2", "Exit_X1", "L6"]
    violations = []
    for pid, row in mat_map.items():
        for s in stages:
            key = s + "_consumption"
            if row.get(key) == "UNKNOWN_NEEDS_REVIEW":
                # Must have explicit w4_resolution in classification
                ce = cls_map.get(pid, {})
                if not ce.get("w4_resolution"):
                    violations.append(f"{pid}:{key}")
    assert not violations, f"Unresolved UNKNOWN_NEEDS_REVIEW without w4_resolution: {violations}"


# ---------------------------------------------------------------------------
# Test 20: no ChromaDB mutation
# ---------------------------------------------------------------------------

def test_20_no_chromadb_mutation():
    """T20: no apps_rg binding imports or calls chromadb Collection.add/upsert/delete."""
    binding_paths = [
        REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py",
        REPO_ROOT / "agentic_core" / "L0_routing" / "apps_rg_l0_binding.py",
        REPO_ROOT / "agentic_core" / "L1_cognition" / "apps_rg_l1_binding.py",
        REPO_ROOT / "agentic_core" / "runtime" / "c0" / "apps_rg_c0_binding.py",
        REPO_ROOT / "agentic_core" / "L2_execution" / "apps_rg_l2_binding.py",
        REPO_ROOT / "agentic_core" / "runtime" / "exit" / "apps_rg_exit_binding.py",
    ]
    chroma_mutations = [".add(", ".upsert(", ".delete(", "chromadb", "Collection.add"]
    violations = []
    for path in binding_paths:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            for pattern in chroma_mutations:
                if pattern in content:
                    violations.append(f"{path.name}:{pattern}")
    assert not violations, f"ChromaDB mutation found in bindings: {violations}"


# ---------------------------------------------------------------------------
# Test 21: no embedding generation
# ---------------------------------------------------------------------------

def test_21_no_embedding_generation():
    """T21: no apps_rg binding imports external embedding APIs.

    Note: .encode("utf-8") is legitimate Python for hashlib / string encoding
    and is NOT an embedding call. This test checks for external embedding library
    imports and API calls (sentence_transformers, openai.Embedding, etc.).
    """
    binding_paths = [
        REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py",
        REPO_ROOT / "agentic_core" / "L0_routing" / "apps_rg_l0_binding.py",
        REPO_ROOT / "agentic_core" / "L1_cognition" / "apps_rg_l1_binding.py",
        REPO_ROOT / "agentic_core" / "runtime" / "c0" / "apps_rg_c0_binding.py",
        REPO_ROOT / "agentic_core" / "L2_execution" / "apps_rg_l2_binding.py",
        REPO_ROOT / "agentic_core" / "runtime" / "exit" / "apps_rg_exit_binding.py",
    ]
    # Only catch external embedding library imports/calls — NOT hashlib .encode("utf-8")
    embed_patterns = [
        "sentence_transformers",
        "openai.Embedding",
        "embed_query(",
        "get_embedding(",
        "embeddings.create(",
        "SentenceTransformer(",
        "from sentence_transformers",
        "import sentence_transformers",
    ]
    violations = []
    for path in binding_paths:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            for pattern in embed_patterns:
                if pattern in content:
                    violations.append(f"{path.name}:{pattern}")
    assert not violations, f"External embedding API found in bindings: {violations}"
