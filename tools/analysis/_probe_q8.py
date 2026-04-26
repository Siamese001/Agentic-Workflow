import json
d = json.load(open(r"artifacts/audit_phase5_ssot.json"))
q = d["queries"]

print("=== Q9 PVIEW DETAILS ===")
for r in q["q9_pview_ssot_matches"]:
    print(json.dumps({k: v for k, v in r.items() if k.startswith("_") or k in ("node_id", "adg_name", "layer", "resolved_path", "file_path")}, default=str))

print()
print("=== Q8 NON-EXCEPTION EVIDENCE (hardcoding/SSOT signals) ===")
skip = {"Exception", "OSError", "AttributeError", "ValueError", "KeyError", "TypeError", "RuntimeError", "ImportError"}
evs = {}
for r in q["q8_violation_ssot_conflicts"]:
    e = r.get("evidence", "")
    if e and e not in skip:
        evs[e] = evs.get(e, 0) + 1
for e, cnt in sorted(evs.items(), key=lambda x: -x[1]):
    print(f"  {e}: {cnt}")

print()
print("=== Q8 SAMPLE ROWS (hardcoding evidence) ===")
hardcode_rows = [r for r in q["q8_violation_ssot_conflicts"] if r.get("evidence") in ("REPO_ROOT", "NOTION_API_VERSION", "DB_PATH", "MAX_RESPONSE_BYTES", "HOOK_PATH")]
for r in hardcode_rows[:10]:
    print(json.dumps({"file_path": r["file_path"], "evidence": r["evidence"], "severity": r["severity"]}, default=str))
