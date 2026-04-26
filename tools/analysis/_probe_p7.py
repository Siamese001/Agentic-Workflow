import json
d = json.load(open(r"artifacts/audit_phase7_final_report.json"))

print("=== TOP 25 RANKED FINDINGS ===")
for r in d["top_50_ranked"][:25]:
    print(f'{r["rank"]:3d}. {r["resolved_path"][:70]:<70s} L={r["layer"]:8s} fi={r["fan_in"]:>6d} fo={r["fan_out"]:>4d} imp={r["impact_score"]:8.2f} sev={r["severity_final"]} surf={r["surfaces"]:20s} phases={r["phases"]}')

print()
print("=== WAVE PLAN SUMMARY ===")
for w in d["wave_plan"]:
    print(f'{w["wave"]} ({w["label"]}): {w["item_count"]} items, total_impact={w["total_impact"]:.1f}')
    for item in w["items"][:5]:
        print(f'    {item["resolved_path"][:70]:<70s} L={item["layer"]:8s} imp={item["impact_score"]:8.2f} fi={item["fan_in"]:>6d} fo={item["fan_out"]:>4d} surf={item["surfaces"]}')
    if w["item_count"] > 5:
        print(f'    ... and {w["item_count"] - 5} more')

print()
print("=== OVERALL STATS ===")
print(json.dumps(d["overall_stats"], indent=2))
