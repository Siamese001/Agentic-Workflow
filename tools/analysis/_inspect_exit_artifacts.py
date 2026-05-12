"""One-shot script: inspect exit proof artifacts for a given run directory."""
import json
import pathlib
import sys

run_dir = pathlib.Path(
    "artifacts/apps_rg/runs/20260512_005523390168_0000_rg-run-cce45466fa4d"
)

receipt_path = run_dir / "07_gate_receipt.json"
if receipt_path.exists():
    r = json.loads(receipt_path.read_text(encoding="utf-8"))
    print("=== 07_gate_receipt.json ===")
    print(f"  x3_code:              {r.get('x3_code')}")
    print(f"  decisive_reason:      {r.get('decisive_reason')}")
    print(f"  decisive_blockers:    {r.get('decisive_blocker_gate_ids')}")
    print(f"  hard_fail_count:      {r.get('hard_fail_count')}")
    print(f"  unknown_count:        {r.get('unknown_count')}")
    print(f"  gate_mesh_result_ref: {r.get('gate_mesh_result_ref', '')[:32]}...")
    print()
else:
    print("  MISSING: 07_gate_receipt.json")

mesh_path = run_dir / "07_gate_mesh_result.json"
if mesh_path.exists():
    m = json.loads(mesh_path.read_text(encoding="utf-8"))
    print("=== 07_gate_mesh_result.json ===")
    for v in m.get("verdicts", []):
        print(f"  {v['gate_id']}: {v['result']:<15s} reason_codes={v.get('reason_codes', [])}")
    print(f"  blocks_allow_finish:  {m.get('blocks_allow_finish')}")
    print(f"  digest:               {m.get('deterministic_digest', '')[:32]}...")
    print()
else:
    print("  MISSING: 07_gate_mesh_result.json")

g28_path = run_dir / "07_g28_post_mesh_verdict.json"
if g28_path.exists():
    g = json.loads(g28_path.read_text(encoding="utf-8"))
    print("=== 07_g28_post_mesh_verdict.json ===")
    print(f"  G28 post-mesh result: {g.get('result')}")
    print(f"  reason_codes:         {g.get('reason_codes')}")
    print()
else:
    print("  (07_g28_post_mesh_verdict.json not written)")

disp_path = run_dir / "07_Exit_disposition.json"
if disp_path.exists():
    d = json.loads(disp_path.read_text(encoding="utf-8"))
    print("=== 07_Exit_disposition.json ===")
    print(f"  exit_status:          {d.get('exit_status')}")
    print(f"  outcome_authorized:   {d.get('outcome_authorized')}")
    print(f"  hitl_required:        {d.get('hitl_required')}")
    refs = d.get("gate_verdict_refs", [])
    print(f"  gate_verdict_refs ({len(refs)} entries):")
    for ref in refs:
        print(f"    {ref}")
else:
    print("  MISSING: 07_Exit_disposition.json")
