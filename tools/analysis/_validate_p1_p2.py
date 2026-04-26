import json
p = json.load(open('artifacts/audit_phase1_ssot_dup_symbols.json', encoding='utf-8'))
findings = p['findings']
true_cross = sum(1 for f in findings if f['layer_count'] >= 2)
print(f'Phase 1 total: {len(findings)}')
print(f'  layer_count >= 2 (true cross-layer): {true_cross}')
print(f'  layer_count == 1 (single-layer dup): {len(findings) - true_cross}')
print()
print('Top 15 by layer_count x file_count:')
ranked = sorted(findings, key=lambda f: (f['layer_count'], f['file_count']), reverse=True)[:15]
for f in ranked:
    print(f"  L={f['layer_count']} files={f['file_count']:>3d} sev={f['_severity']:<3s} {f['short_name']:<25s} layers={f['layers']}")

print()
p2 = json.load(open('artifacts/audit_phase2_cross_layer_types.json', encoding='utf-8'))
print(f'Phase 2 total: {len(p2["findings"])}')
print(f'Top 15:')
for f in sorted(p2['findings'], key=lambda x: (x.get('layer_count', 0), x.get('file_count', 0)), reverse=True)[:15]:
    print(f"  L={f.get('layer_count','?')} files={f.get('file_count','?'):>3} sev={f.get('_severity','?'):<3s} {f.get('short_name','?'):<30s} layers={f.get('layers','?')}")
