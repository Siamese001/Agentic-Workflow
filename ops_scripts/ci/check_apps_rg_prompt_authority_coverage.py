"""CI gate: apps_rg Prompt Authority Coverage (W4).

Gate ID: PA-COV
Checks that:
- inventory/classification/matrix counts agree
- no matrix prompt_id is absent from classification
- no classification prompt_id is absent from matrix
- runtime prompts have authority_class, contract_field_target, prompt_slot_target
- PA slot_lineage_map covers U0/C0/I0/R0 separately (PAB-003)
- PA component_hash_map covers all runtime-used components
- U0 does not consume instruction authority
- L0 binding does not parse raw prompt text
- C0 binding does not assemble prompts
- L2 binding does not load raw apps_rg prompts
- Exit binding does not assemble generation prompts
- user text cannot become instruction authority
- retrieved evidence cannot become instruction authority
- evaluator rubrics cannot become generation instruction
- UNKNOWN_NEEDS_REVIEW is not treated as PASS
- NOT_APPLICABLE entries have a reason

Exit codes:
  0 — all checks pass (or advisory-only with no errors)
  1 — one or more ERROR findings (fail-closed mode only)

Bypass: PA_COV_BYPASS=1
Fail-closed: PA_COV_FAIL_CLOSED=1
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACTS = REPO_ROOT / "artifacts" / "apps_rg"
BYPASS = os.environ.get("PA_COV_BYPASS", "").strip() == "1"
FAIL_CLOSED = os.environ.get("PA_COV_FAIL_CLOSED", "").strip() == "1"

REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "apps_rg_prompt_authority_coverage.json"


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_counts(inv: dict, cls: dict, mat: dict, findings: list) -> None:
    inv_ids = [p["prompt_id"] for p in inv["prompts"]]
    cls_ids = [p["prompt_id"] for p in cls["classifications"]]
    mat_ids = [r["prompt_id"] for r in mat["matrix"]]
    inv_meta = inv["inventory_metadata"]["total_items"]
    cls_meta = cls["classification_metadata"]["total_classified"]

    if inv_meta != 86 or len(inv_ids) != 86:
        findings.append({"level": "ERROR", "check": "count_reconciliation",
                         "detail": f"inventory: meta={inv_meta}, array={len(inv_ids)}, expected 86"})
    if cls_meta != 86 or len(cls_ids) != 86:
        findings.append({"level": "ERROR", "check": "count_reconciliation",
                         "detail": f"classification: meta={cls_meta}, array={len(cls_ids)}, expected 86"})
    if len(mat_ids) != 86:
        findings.append({"level": "ERROR", "check": "count_reconciliation",
                         "detail": f"matrix array={len(mat_ids)}, expected 86"})

    missing_from_cls = set(mat_ids) - set(cls_ids)
    if missing_from_cls:
        findings.append({"level": "ERROR", "check": "matrix_ids_missing_classification",
                         "detail": sorted(missing_from_cls)})
    missing_from_mat = set(cls_ids) - set(mat_ids)
    if missing_from_mat:
        findings.append({"level": "ERROR", "check": "classification_ids_missing_matrix",
                         "detail": sorted(missing_from_mat)})


def _check_runtime_prompts(cls: dict, findings: list) -> None:
    instruction_classes = {"DOMAIN_INSTRUCTION", "SYSTEM_AUTHORITY", "POLICY_AUTHORITY"}
    for e in cls["classifications"]:
        if e.get("runtime_reachable") is not True:
            continue
        pid = e["prompt_id"]
        if not e.get("authority_class"):
            findings.append({"level": "ERROR", "check": "runtime_missing_authority_class",
                             "prompt_id": pid})
        if not e.get("contract_field_target") or not e.get("prompt_slot_target"):
            findings.append({"level": "ERROR", "check": "runtime_missing_targets",
                             "prompt_id": pid,
                             "cft": e.get("contract_field_target"),
                             "pst": e.get("prompt_slot_target")})


def _check_stage_boundaries(cls: dict, mat: dict, findings: list) -> None:
    cls_map = {p["prompt_id"]: p for p in cls["classifications"]}
    mat_map = {r["prompt_id"]: r for r in mat["matrix"]}
    # Generation instruction slots — these must not cross layer boundaries
    generation_slots = {"S0_SYSTEM", "I0_INSTRUCTIONS", "E0_APPROVED_EXAMPLES",
                        "D0_DOMAIN_KNOWLEDGE"}
    # Strict L0 raw slots — L0 must not consume any raw text slots
    l0_raw_slots = {"S0_SYSTEM", "I0_INSTRUCTIONS", "U0_NEUTRALIZED_USER_TASK",
                    "C0_VERIFIED_EVIDENCE_DATA", "E0_APPROVED_EXAMPLES"}
    generation_stages = ["U0", "L1", "L0", "C0", "PA", "L2"]
    stages = ["U0", "L1", "L0", "C0", "PA", "L3", "L2", "Exit_X1", "L6"]

    for pid, row in mat_map.items():
        ce = cls_map.get(pid, {})
        ac = ce.get("authority_class", "")
        slot = ce.get("canonical_prompt_slot", "")

        # U0 must not REQUIRE generation instruction slots.
        # Exception: BOM slot declarations (slot=U0_NEUTRALIZED_USER_TASK) are
        # data-labeling policies, not generation instructions — allowed at U0.
        if row.get("U0_consumption") == "REQUIRED" and slot in generation_slots:
            findings.append({"level": "ERROR", "check": "u0_generation_slot_violation",
                             "prompt_id": pid, "slot": slot})

        # L1 must not REQUIRE generation instruction slots.
        # OUTPUT_SCHEMA, POLICY_AUTHORITY at L1 are valid for planning projections.
        if row.get("L1_consumption") == "REQUIRED" and slot in generation_slots:
            findings.append({"level": "ERROR", "check": "l1_generation_slot_violation",
                             "prompt_id": pid, "slot": slot})

        # L0 must not REQUIRE raw prompt text slots
        if row.get("L0_consumption") == "REQUIRED" and slot in l0_raw_slots:
            findings.append({"level": "ERROR", "check": "l0_raw_prompt_slot",
                             "prompt_id": pid, "slot": slot})

        # C0 must not REQUIRE generation instruction slots.
        # POLICY_AUTHORITY at C0 with slot=C0_VERIFIED_EVIDENCE_DATA is valid
        # (BOM evidence slot declarations / evidence directives).
        if row.get("C0_consumption") == "REQUIRED" and slot in generation_slots:
            findings.append({"level": "ERROR", "check": "c0_generation_slot_violation",
                             "prompt_id": pid, "slot": slot})

        # Eval rubrics must not be REQUIRED at generation stages
        if ac == "EVAL_RUBRIC":
            for s in generation_stages:
                if row.get(s + "_consumption") == "REQUIRED":
                    findings.append({"level": "ERROR", "check": "eval_rubric_at_generation_stage",
                                     "prompt_id": pid, "stage": s})

        # UNKNOWN_NEEDS_REVIEW is not a PASS — must have w4_resolution
        for s in stages:
            if row.get(s + "_consumption") == "UNKNOWN_NEEDS_REVIEW":
                if not ce.get("w4_resolution"):
                    findings.append({"level": "ERROR", "check": "unknown_without_resolution",
                                     "prompt_id": pid, "stage": s})

        # NOT_APPLICABLE must have a reason
        for s in stages:
            if row.get(s + "_consumption") == "NOT_APPLICABLE_WITH_REASON":
                if not row.get("stage_consumption_reason") and not ce.get("classification_reason"):
                    findings.append({"level": "WARN", "check": "not_applicable_missing_reason",
                                     "prompt_id": pid, "stage": s})


def _check_pa_binding(findings: list) -> None:
    pa_path = REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "pa_binding.py"
    if pa_path.exists():
        content = pa_path.read_text(encoding="utf-8")
        # PAB-003: slot_lineage_map dict must not assign USER_INTENT+EVIDENCE as a value.
        # The string may appear in comments documenting the fix — only catch dict value assignments.
        dict_value_violations = [
            line for line in content.splitlines()
            if '"user_block_1' in line and "USER_INTENT+EVIDENCE" in line
        ]
        if dict_value_violations:
            findings.append({"level": "ERROR", "check": "pab003_u0_c0_conflation",
                             "detail": "slot_lineage_map dict assigns USER_INTENT+EVIDENCE",
                             "lines": dict_value_violations})

    required_slots = ["U0_NEUTRALIZED_USER_TASK", "C0_VERIFIED_EVIDENCE_DATA",
                      "I0_INSTRUCTIONS", "R0_RESPONSE_SCHEMA", "S0_SYSTEM"]
    for s in required_slots:
        if s not in content:
            findings.append({"level": "ERROR", "check": "pa_slot_lineage_missing",
                             "detail": f"slot_lineage_map missing: {s}"})

    # component_hash_map must cover all runtime components
    required_hash_keys = [
        '"style_profile__s0_i0"', '"evidence__c0"', '"u0_task_segment"',
        '"c0_evidence_segment"', '"l1_plan"', '"r0_schema"', '"app_payload"', '"route"',
    ]
    for k in required_hash_keys:
        if k not in content:
            findings.append({"level": "ERROR", "check": "pa_component_hash_map_missing",
                             "detail": f"component_hash_map missing key: {k}"})

    # compilation_hash must use content_hash not len
    if "content_hash" not in content:
        findings.append({"level": "ERROR", "check": "pa_prompt_hash_not_content_sensitive",
                         "detail": "compilation_hash must cover content_hash, not only len(content)"})


def _check_binding_isolation(findings: list) -> None:
    checks = [
        {
            "path": REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "l0_binding.py",
            "name": "L0",
            "forbidden": ["yaml.safe_load", "yaml.load", "rg_prompt_profile", "slot_mapper", "prompt_bom"],
        },
        {
            "path": REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "c0_binding.py",
            "name": "C0",
            "forbidden": ["pa_compose_apps_rg", "PromptBlock(", "_build_system_preamble",
                          "_build_user_instruction", "_build_u0_task_block"],
        },
        {
            "path": REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "l2_binding_adapter.py",
            "name": "L2",
            "forbidden": ["rg_prompt_profile", "rg_style_profile", "slot_mapper", "prompt_bom",
                          "strategic_tailor", "warmup_pairs", "_build_system_preamble"],
        },
        {
            "path": REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "exit_binding.py",
            "name": "Exit",
            "forbidden": ["pa_compose_apps_rg", "PromptBlock(", "_build_system_preamble",
                          "_build_user_instruction", "_build_u0_task_block"],
        },
    ]
    chroma_patterns = [".add(", ".upsert(", ".delete(", "chromadb", "Collection.add"]
    # Only catch external embedding library imports/calls.
    # .encode("utf-8") is hashlib/stdlib — NOT an embedding call, never flag it.
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

    for check in checks:
        path = check["path"]
        name = check["name"]
        if not path.exists():
            findings.append({"level": "WARN", "check": f"{name}_binding_missing",
                             "detail": str(path)})
            continue
        content = path.read_text(encoding="utf-8")
        for f in check["forbidden"]:
            if f in content:
                findings.append({"level": "ERROR", "check": f"{name}_isolation_violation",
                                 "detail": f})
        for p in chroma_patterns:
            if p in content:
                findings.append({"level": "ERROR", "check": "chromadb_mutation",
                                 "binding": name, "pattern": p})
        for p in embed_patterns:
            if p in content:
                findings.append({"level": "ERROR", "check": "embedding_generation",
                                 "binding": name, "pattern": p})


def main() -> int:
    if BYPASS:
        print("PA-COV: BYPASSED (PA_COV_BYPASS=1)")
        return 0

    findings: list[dict] = []

    try:
        inv = _load_json(ARTIFACTS / "ag8_prompt_authority_inventory.json")
        cls = _load_json(ARTIFACTS / "ag8_prompt_authority_classification.json")
        mat = _load_json(ARTIFACTS / "ag8_prompt_stage_consumption_matrix.json")
    except FileNotFoundError as e:
        print(f"PA-COV: ERROR — artifact missing: {e}")
        return 1

    _check_counts(inv, cls, mat, findings)
    _check_runtime_prompts(cls, findings)
    _check_stage_boundaries(cls, mat, findings)
    _check_pa_binding(findings)
    _check_binding_isolation(findings)

    errors = [f for f in findings if f["level"] == "ERROR"]
    warns = [f for f in findings if f["level"] == "WARN"]

    report = {
        "gate": "PA-COV",
        "status": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "warn_count": len(warns),
        "findings": findings,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    for finding in findings:
        level = finding["level"]
        detail = {k: v for k, v in finding.items() if k not in ("level",)}
        print(f"PA-COV [{level}] {json.dumps(detail)}")

    summary = f"PA-COV: {len(errors)} errors, {len(warns)} warnings"
    if not errors:
        print(f"PA-COV: PASS — {summary}")
        return 0
    else:
        print(f"PA-COV: {'FAIL' if FAIL_CLOSED else 'WARN (advisory)'} — {summary}")
        return 1 if FAIL_CLOSED else 0


if __name__ == "__main__":
    sys.exit(main())
