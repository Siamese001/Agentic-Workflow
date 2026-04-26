import json
from pathlib import Path

ART = Path(r"artifacts")

print("=" * 90)
print("PHASE 16 — UNCOVERED CATEGORIES (gap vs 94 CI gates)")
print("=" * 90)
p16 = json.loads((ART / "audit_phase16_uncovered_by_ci.json").read_text(encoding="utf-8"))
for u in p16["uncovered_summary"]:
    print(f"\n  [{u['source_phase']}] {u['category']} — {u['finding_count']} findings")
    print(f"     {u['description']}")
    print(f"     Rationale: {u['rationale_for_uncovered']}")
    print(f"     Closest CI gates: {u['ci_gates_closest']}")

print()
print("=" * 90)
print("PHASE 9 — OBSERVABILITY BLIND SPOTS (top 17, high fan_in, no L6 edges)")
print("=" * 90)
p9 = json.loads((ART / "audit_phase9_observability_blind_spots.json").read_text(encoding="utf-8"))
for r in p9["findings"]:
    print(f"  fi={r['fan_in']:>5d} fo={r['fan_out']:>4d} L={r['layer']:5s} {r['resolved_path']}")

print()
print("=" * 90)
print("PHASE 10 — HARDCODED EXTERNAL LITERALS (top 21)")
print("=" * 90)
p10 = json.loads((ART / "audit_phase10_hardcoded_external.json").read_text(encoding="utf-8"))
for r in p10["findings"][:21]:
    print(f"  {r['matched_pattern']:<28s} {r['file_path']}:{r['line_no']}  evidence={r['evidence']}")

print()
print("=" * 90)
print("PHASE 11 — PROVIDER EGRESS CONCENTRATION (top 15)")
print("=" * 90)
p11 = json.loads((ART / "audit_phase11_provider_egress.json").read_text(encoding="utf-8"))
for r in p11["findings"][:15]:
    print(f"  egress={r['egress_count']:>3d} targets={r['distinct_targets']:>3d} L={r['layer']:5s} {r['resolved_path']}")

print()
print("=" * 90)
print("PHASE 12 — MIXED-CALLEE-LAYER DISPATCHERS (top 15)")
print("=" * 90)
p12 = json.loads((ART / "audit_phase12_mixed_callee_layers.json").read_text(encoding="utf-8"))
for r in p12["findings"][:15]:
    print(f"  layers={r['distinct_callee_layers']} edges={r['total_edges']:>4d} L={r['layer']:5s} callees={r['callee_layers'][:40]:<40s} {r['resolved_path']}")

print()
print("=" * 90)
print("PHASE 14 — ENV VAR OUTSIDE CONFIG (top 15)")
print("=" * 90)
p14 = json.loads((ART / "audit_phase14_env_var.json").read_text(encoding="utf-8"))
for r in p14["findings"][:15]:
    print(f"  L={r['layer']:5s} {r['resolved_path']}  symbol={r['adg_name'][:60]}")

print()
print("=" * 90)
print("PHASE 15 — ORPHAN CONFIG WITH BLAST RADIUS (top 15)")
print("=" * 90)
p15 = json.loads((ART / "audit_phase15_orphan_config.json").read_text(encoding="utf-8"))
for r in p15["findings"][:15]:
    print(f"  fi={r['fan_in']} fo={r['fan_out']:>3d} L={r['layer']:5s} {r['resolved_path']}")

print()
print("=" * 90)
print("PHASE 8 — UNTRIAGED VIOLATIONS BY SEVERITY")
print("=" * 90)
p8 = json.loads((ART / "audit_phase8_untriaged_aging.json").read_text(encoding="utf-8"))
for r in p8["by_severity"]:
    print(f"  {r['category']:>12s}/{r['severity']:>8s}: {r['cnt']:>5d} ({r['files']} files, {r['evidence_kinds']} evidence kinds)")
print("  Top files:")
for r in p8["top_files"][:10]:
    print(f"    {r['cnt']:>4d}  {r['file_path']}")
