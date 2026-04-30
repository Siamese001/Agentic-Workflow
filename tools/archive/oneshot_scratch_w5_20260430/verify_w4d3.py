"""Final W4d-3 verification: sample each hardened matrix."""
import csv
csv.field_size_limit(2_000_000)

def show(label, path, n=3, key=None):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    print(f"\n=== {label} ===  rows={len(rows)}  cols={len(rows[0])}")
    print(f"  columns: {list(rows[0].keys())}")
    for r in rows[:n]:
        kid = r[key] if key else (r.get("req_id") or r.get("metric_id") or r.get("binding_id") or r.get("10c_req_id"))
        print(f"  --- {kid} ---")
        for k, v in r.items():
            if k == key:
                continue
            short = (v[:90] + "...") if len(v) > 90 else v
            print(f"    {k:<32} = {short}")

show("requirements_vs_10a", "docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv", 2, "10c_req_id")
show("metric_obligation", "docs/reports/design/10c_reconciliation/10c_metric_obligation_matrix.csv", 2, "metric_id")
show("model_binding (true models)", "docs/reports/design/10c_reconciliation/10c_model_binding_matrix.csv", 2, "binding_id")
show("nonmodel_control_binding", "docs/reports/design/10c_reconciliation/10c_nonmodel_control_binding_matrix.csv", 2, "binding_id")

# Coverage breakdown for requirements_vs_10a
from collections import Counter
rows = list(csv.DictReader(open("docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv", encoding="utf-8")))
print("\n=== requirements_vs_10a coverage breakdown ===")
print(f"  coverage_status_normalized: {dict(Counter(r['coverage_status_normalized'] for r in rows))}")
print(f"  baseline_gap_class:         {dict(Counter(r['baseline_gap_class'] for r in rows))}")
print(f"  requires_10a_backport:      {dict(Counter(r['requires_10a_backport'] for r in rows))}")
print(f"  new_best_practice_wave:     {dict(Counter(r['new_best_practice_wave'] for r in rows if r['new_best_practice_wave']))}")
