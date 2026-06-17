"""Hook-independent decision-marker capture pipeline.

Bypasses legacy editor hooks entirely. Codex invokes ``append_marker.py`` via
``run_command`` at the end of every refactor-class response; a separate drain
process (``queue_to_ledger.py``) writes accumulated markers into the SQLite
decision ledger by reusing the existing capture-hook logic.

Components:
  - ``append_marker.py``: writes a single marker line into the JSONL queue
  - ``queue_to_ledger.py``: drains the queue into
    ``.claude/state/refactor_decisions/refactor_decision_ledger.sqlite`` (SSOT;
    see ``tools.refactor_decisions.ledger_paths``)

See `.claude/rules/author-gate-enforcement.md` Silent-Marker Invariant for
when Codex must emit markers.
"""
