"""W4d-4 proof-evidence fixtures.

These are deterministic, narrow validators used by the 5 pilot tests
(10C-REQ-049, 167, 086, 089, 122). They prove the *machinery* — runtime
artifact shape, OTEL span receipts, replay-digest stability, and
boundary-violating negative controls — without depending on the runtime
implementation being complete.

When the real runtime artifacts/spans land, the same tests can be
re-pointed at the runtime emitters; only the fixture imports change.
"""
