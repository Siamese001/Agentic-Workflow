"""Verification harness for the parent-thinning refactor.

Runs 8 tests against docs/reference/. Exits 0 only if every test passes.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
REF = REPO / "docs" / "reference"
SKIP_DIRS = {"_archive", "__pycache__", "Transformer Templates"}

# Parents that were thinned (R1/R2/R3) and the children they MUST reference
THINNED_PARENTS = {
    REF / "03A_C0_Context_Engine" / "C0_Context_Engine.md": [
        "C0.0_Preflight_Grounding_Eligibility.md",
        "C0.1_Retrieval_Plan.md",
        "C0.2_Evidence_Fetch.md",
        "C0.3_Graph_RAG.md",
        "C0.4_Shape_Rerank_Stratify.md",
        "C0.5_Final_Evidence_Contract.md",
        "C0.6_Weak_Support_Refinement.md",
        "C0.7_C0_Observability_Tests_Anti_Bypass.md",
    ],
    REF / "04_L2_Execute" / "04_L2_Execute.md": [
        "04.1_L2_Execution_Entry_Authority_and_Packet_Intake.md",
        "04.2_L2_E1_Prep_Frozen_Execution_Room.md",
        "04.3_L2_E2_Valid_Work_Order_and_Gate_Check.md",
        "04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run.md",
        "04.5_L2_E4_Heal_Same_Authority_Repair_Governor.md",
        "04.6_L2_E5_Seal_Artifact_and_Dispatch.md",
        "04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md",
        "04.8_L2_Observability_Replay_Anti_Bypass_Tests.md",
    ],
    REF / "05_Exit_Evaluation_and_Control" / "05_Live_Runtime_Exit_Control_&_Evaluation.md": [
        "05.1_Exit_Input_Normalization_and_Review_Packet.md",
        "05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md",
        "05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md",
        "05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md",
        "05.5_Exit_Aggregation_and_X3_Disposition.md",
        "05.6_Exit_HITL_Freeze_Review_and_Reclearance.md",
        "05.7_Exit_Return_Response_and_Runtime_Exhaust.md",
        "05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md",
    ],
}

CLEAN_PARENTS = [
    REF / "00A_L5_Governance_Safety" / "00A_L5_Governance_Safety.md",
    REF / "00B_L4_State_Archive_and_UWG" / "00B_L4_State_Archive_and_UWG.md",
    REF / "00C_Runtime_Gates_Current_Run_Mesh" / "00C_Runtime_Gates_Current_Run_Mesh.md",
    REF / "01_Request_Intake" / "01_request_intake.md",
    REF / "02_L1_Reasoning_Plan" / "02_L1_Reasoning_Plan_Generation.md",
    REF / "03_L0_Route_Decision_and_L3_Orchestration" / "03_L0_Route_Decision_Switching_L3.md",
    REF / "03B_PA_Prompt_Assembly" / "PA_Prompt_Assembly.md",
    REF / "06_L6_Observability_and_System_Learning" / "06_Shadow_Evaluation_System_Learning.md",
    REF / "99_End_to_End_Runtime_Proof_and_Acceptance" / "99_End_to_End_Runtime_Proof_and_Acceptance.md",
]

# Key phrases that MUST be discoverable somewhere under the parent's folder
KEY_PHRASES = {
    REF / "03A_C0_Context_Engine": [
        "FinalEvidenceContract",
        "Retrieved text is data, not instruction",
        "RetrievalPlan",
        "GraphExpandedEvidencePool",
        "ShapedEvidenceSet",
        "WeakSupportRefinementInput",
    ],
    REF / "04_L2_Execute": [
        "sealed_l2_artifact",
        "proposed_state_diff",
        "same-authority",
        "PTC",
        "frozen_execution_context",
    ],
    REF / "05_Exit_Evaluation_and_Control": [
        "X1A",
        "X1J",
        "X3C",
        "ExitReviewPacket",
        "exactly one X3",
        "HITL",
    ],
}

MECE_MARKER = "MECE ALIGNMENT FULL OVERWRITE HEADER"
GLOBAL_NO_OVERLAP_MARKER = "GLOBAL NO-OVERLAP LAW"

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


# --- Test 1: thinned parents reference all required children ---
def test_thinned_child_maps():
    fails = []
    for parent, children in THINNED_PARENTS.items():
        if not parent.is_file():
            fails.append(f"MISSING PARENT: {parent.relative_to(REF)}")
            continue
        text = read(parent)
        for c in children:
            if c not in text:
                fails.append(f"{parent.relative_to(REF)} missing ref to {c}")
    record("T1 thinned parents reference all required children", not fails, "; ".join(fails))


# --- Test 2: every referenced child file exists on disk ---
def test_referenced_children_exist():
    fails = []
    for parent, children in THINNED_PARENTS.items():
        for c in children:
            child_path = parent.parent / c
            if not child_path.is_file():
                fails.append(f"MISSING CHILD: {child_path.relative_to(REF)}")
    record("T2 every referenced child exists on disk", not fails, "; ".join(fails))


# --- Test 3: thinned parents are within size envelope (<=50KB) ---
def test_thinned_sizes():
    fails = []
    for parent in THINNED_PARENTS:
        size = parent.stat().st_size
        if size > 50_000:
            fails.append(f"{parent.relative_to(REF)} = {size} bytes (>50KB)")
    record("T3 thinned parents <=50KB", not fails, "; ".join(fails))


# --- Test 4: clean parents stayed within size envelope (<=20KB) ---
def test_clean_sizes():
    fails = []
    for parent in CLEAN_PARENTS:
        if not parent.is_file():
            fails.append(f"MISSING: {parent.relative_to(REF)}")
            continue
        size = parent.stat().st_size
        if size > 20_000:
            fails.append(f"{parent.relative_to(REF)} = {size} bytes (>20KB)")
    record("T4 clean parents <=20KB", not fails, "; ".join(fails))


# --- Test 5: every parent has MECE header + global no-overlap law ---
def test_parent_headers():
    fails = []
    for parent in list(THINNED_PARENTS) + CLEAN_PARENTS:
        text = read(parent)
        if MECE_MARKER not in text:
            fails.append(f"{parent.relative_to(REF)} missing MECE header")
        if GLOBAL_NO_OVERLAP_MARKER not in text:
            fails.append(f"{parent.relative_to(REF)} missing GLOBAL NO-OVERLAP LAW")
    record("T5 every parent has MECE + no-overlap headers", not fails, "; ".join(fails))


# --- Test 6: key phrases preserved under each thinned parent's folder ---
def test_key_phrase_preservation():
    fails = []
    for folder, phrases in KEY_PHRASES.items():
        # Collect text from all .md files in this folder
        corpus = ""
        for p in folder.rglob("*.md"):
            corpus += read(p)
        for phrase in phrases:
            if phrase not in corpus:
                fails.append(f"{folder.name}: missing key phrase '{phrase}'")
    record("T6 every key phrase preserved under parent folder", not fails, "; ".join(fails))


# --- Test 7: no lowercase _detailed.md cross-file path refs remain ---
def test_no_stale_detailed_refs():
    fails = []
    pattern = re.compile(r"_detailed\.md")
    self_docs = {"PARENT_THINNING_ZERO_LOSS_REPORT.md", "00X_Requirements_Traceability_and_No_Loss_Map.md"}
    for p in REF.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(REF).parts):
            continue
        if p.suffix.lower() not in (".md", ".json"):
            continue
        if p.name in self_docs:
            continue
        text = read(p)
        if pattern.search(text):
            count = len(pattern.findall(text))
            fails.append(f"{p.relative_to(REF)}: {count} hits")
    record("T7 no lowercase _detailed.md refs remain (excluding Transformer Templates)", not fails, "; ".join(fails[:5]))


# --- Test 8: manifest integrity ---
def test_manifest_integrity():
    manifest_path = REF / "UPDATED_MANIFEST.json"
    if not manifest_path.is_file():
        record("T8 manifest exists and integrity holds", False, "UPDATED_MANIFEST.json not found")
        return
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    fails = []
    sample = data["files"][:: max(1, len(data["files"]) // 20)]  # spot-check ~20 files
    for entry in sample:
        p = REF / entry["path"]
        if not p.is_file():
            fails.append(f"missing: {entry['path']}")
            continue
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        if h.hexdigest() != entry["sha256"]:
            fails.append(f"sha mismatch: {entry['path']}")
    record(
        f"T8 manifest integrity (spot-checked {len(sample)}/{len(data['files'])} files)",
        not fails,
        "; ".join(fails),
    )


def main() -> int:
    test_thinned_child_maps()
    test_referenced_children_exist()
    test_thinned_sizes()
    test_clean_sizes()
    test_parent_headers()
    test_key_phrase_preservation()
    test_no_stale_detailed_refs()
    test_manifest_integrity()

    print("=" * 80)
    print("PARENT-THINNING VERIFICATION HARNESS")
    print("=" * 80)
    passed = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}")
        if not ok and detail:
            print(f"       -> {detail}")
        if ok:
            passed += 1
    print("=" * 80)
    print(f"RESULT: {passed}/{len(results)} tests passed")
    print("=" * 80)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
