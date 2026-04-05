"""Apply Wave G: batch post-scan edge merges into a single sorted() + compute_digest().

Currently 3 separate sorted(set(result.edges) | set(new_edges)) + compute_digest()
calls run after the main scan loop — each is O(N log N) on 728k edges.
Fix: accumulate all post-scan additions into a running set, sort ONCE at the end.
"""

import pathlib

TARGET = pathlib.Path(r"c:\Git\Agentic-Workflow\agentic_core\adg\extraction\static_scanner.py")
content = TARGET.read_text(encoding="utf-8")

old_postscan = (
    "        # GV: Layer violation post-scan pass\n"
    "        violation_edges = _emit_layer_violation_edges(result)\n"
    "        if violation_edges:\n"
    "            violation_edges, violation_stamp_stats = _stamp_semantic_types_with_stats(violation_edges)\n"
    "            _merge_surface_evidence(surface_evidence_totals, violation_stamp_stats)\n"
    "            result.edges = sorted(set(result.edges) | set(violation_edges))\n"
    "            result.compute_digest()\n"
    "\n"
    "        propagation_evidence = _violation_propagation_eligibility(result)\n"
    "        manifest.violation_propagation_eligible_count = propagation_evidence[\n"
    '            "violation_propagation_eligible_count"\n'
    "        ]\n"
    "        manifest.violation_propagation_target_count = propagation_evidence[\n"
    '            "violation_propagation_target_count"\n'
    "        ]\n"
    "\n"
    "        # Phase 3d: Violation trace depth — propagate violations through lineage\n"
    "        propagation_edges = _propagate_violations(result)\n"
    "        if propagation_edges:\n"
    "            propagation_edges, propagation_stamp_stats = _stamp_semantic_types_with_stats(propagation_edges)\n"
    "            _merge_surface_evidence(surface_evidence_totals, propagation_stamp_stats)\n"
    "            result.edges = sorted(set(result.edges) | set(propagation_edges))\n"
    "            result.compute_digest()\n"
    "\n"
    "        # E5: Cyclic dependency detection post-scan pass\n"
    "        cycle_edges = _detect_cycles(result)\n"
    "        if cycle_edges:\n"
    "            cycle_edges, cycle_stamp_stats = _stamp_semantic_types_with_stats(cycle_edges)\n"
    "            _merge_surface_evidence(surface_evidence_totals, cycle_stamp_stats)\n"
    "            result.edges = sorted(set(result.edges) | set(cycle_edges))\n"
    "            result.compute_digest()"
)

new_postscan = (
    "        # GV / Phase 3d / E5: batch all post-scan edge additions — sort ONCE at the end\n"
    "        _post_scan_edge_set: set = set(result.edges)\n"
    "\n"
    "        # GV: Layer violation post-scan pass\n"
    "        violation_edges = _emit_layer_violation_edges(result)\n"
    "        if violation_edges:\n"
    "            violation_edges, violation_stamp_stats = _stamp_semantic_types_with_stats(violation_edges)\n"
    "            _merge_surface_evidence(surface_evidence_totals, violation_stamp_stats)\n"
    "            _post_scan_edge_set |= set(violation_edges)\n"
    "\n"
    "        # Propagation eligibility needs the violation edges present\n"
    "        result.edges = sorted(_post_scan_edge_set)  # temp sort for eligibility check\n"
    "        propagation_evidence = _violation_propagation_eligibility(result)\n"
    "        manifest.violation_propagation_eligible_count = propagation_evidence[\n"
    '            "violation_propagation_eligible_count"\n'
    "        ]\n"
    "        manifest.violation_propagation_target_count = propagation_evidence[\n"
    '            "violation_propagation_target_count"\n'
    "        ]\n"
    "\n"
    "        # Phase 3d: Violation trace depth — propagate violations through lineage\n"
    "        propagation_edges = _propagate_violations(result)\n"
    "        if propagation_edges:\n"
    "            propagation_edges, propagation_stamp_stats = _stamp_semantic_types_with_stats(propagation_edges)\n"
    "            _merge_surface_evidence(surface_evidence_totals, propagation_stamp_stats)\n"
    "            _post_scan_edge_set |= set(propagation_edges)\n"
    "\n"
    "        # E5: Cyclic dependency detection post-scan pass\n"
    "        cycle_edges = _detect_cycles(result)\n"
    "        if cycle_edges:\n"
    "            cycle_edges, cycle_stamp_stats = _stamp_semantic_types_with_stats(cycle_edges)\n"
    "            _merge_surface_evidence(surface_evidence_totals, cycle_stamp_stats)\n"
    "            _post_scan_edge_set |= set(cycle_edges)\n"
    "\n"
    "        # Single sort + digest for all post-scan additions\n"
    "        result.edges = sorted(_post_scan_edge_set)\n"
    "        result.compute_digest()"
)

assert old_postscan in content, "post-scan block not found!"
content = content.replace(old_postscan, new_postscan, 1)
print("[OK] Wave G: batched post-scan merges into single sorted() + compute_digest()")

TARGET.write_text(content, encoding="utf-8")
print(f"[DONE] {TARGET}")
