"""Unified Author-Gate post-cascade hook suite.

Consolidates 8 Author-Gate related hooks into single process spawn:
- author_gate_capture
- author_gate_miss_detector
- author_gate_ui_audit
- author_gate_schema_audit
- ask_user_question_packet_audit
- author_gate_pipeline_audit
- ag_queue_drain_audit
- ag_queue_seed_capture

Reduces post_cascade hook chain overhead while preserving all audit behaviors.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import individual audit modules
from . import (
    post_cascade_author_gate_capture,
    post_cascade_author_gate_miss_detector,
    post_cascade_author_gate_ui_audit,
    post_cascade_author_gate_schema_audit,
    post_cascade_ask_user_question_packet_audit,
    post_cascade_author_gate_pipeline_audit,
    post_cascade_ag_queue_drain_audit,
    post_cascade_ag_queue_seed_capture,
)


def main() -> int:
    """Run all Author-Gate audits in sequence."""
    if os.environ.get("AG_SUITE_BYPASS") == "1":
        print("[author_gate_suite] BYPASS via AG_SUITE_BYPASS=1", file=sys.stderr)
        return 0

    results = []
    
    # Run each audit with fail-soft semantics (don't short-circuit on failure)
    audits = [
        ("capture", post_cascade_author_gate_capture.main),
        ("miss_detector", post_cascade_author_gate_miss_detector.main),
        ("ui_audit", post_cascade_author_gate_ui_audit.main),
        ("schema_audit", post_cascade_author_gate_schema_audit.main),
        ("ask_packet_audit", post_cascade_ask_user_question_packet_audit.main),
        ("pipeline_audit", post_cascade_author_gate_pipeline_audit.main),
        ("queue_drain", post_cascade_ag_queue_drain_audit.main),
        ("queue_seed", post_cascade_ag_queue_seed_capture.main),
    ]
    
    for name, audit_func in audits:
        try:
            result = audit_func()
            results.append((name, result))
        except Exception as e:
            print(f"[author_gate_suite] {name} error: {e}", file=sys.stderr)
            results.append((name, 1))
    
    # Summary output (visible when show_output=true)
    failed = [name for name, rc in results if rc != 0]
    if failed:
        print(f"[author_gate_suite] {len(failed)}/{len(results)} audits flagged: {', '.join(failed)}")
    else:
        print(f"[author_gate_suite] {len(results)}/{len(results)} audits clean")
    
    return 0  # Suite always returns 0; individual failures logged


if __name__ == "__main__":
    sys.exit(main())
