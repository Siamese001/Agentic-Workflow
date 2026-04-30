"""Negative fixture for ``check_config_references`` (W4 P4.5 audit).

Contains an env-flag read that is deliberately NOT declared in
``.env.example`` and NOT in ``config/config_references_allowlist.yaml``.
The config-references gate MUST detect this — it is the canonical
"undeclared reads" failure mode the gate exists to prevent.

Do NOT import this file from production code. It is exercised only by the
in-process audit harness at
``tests/unit/ops_scripts/ci/test_gate_precision_audit.py``.
"""

from __future__ import annotations

import os


def _read_fake_flag_getenv() -> str:
    """Should be flagged: os.getenv("P45_FAKE_FLAG_DO_NOT_DECLARE")."""
    return os.getenv("P45_FAKE_FLAG_DO_NOT_DECLARE", "default-value")


def _read_fake_flag_environ_get() -> str:
    """Should be flagged: os.environ.get("P45_FAKE_FLAG_ENVIRON_GET")."""
    return os.environ.get("P45_FAKE_FLAG_ENVIRON_GET", "default-value")


def _read_fake_flag_subscript() -> str:
    """Should be flagged: os.environ["P45_FAKE_FLAG_SUBSCRIPT"]."""
    return os.environ["P45_FAKE_FLAG_SUBSCRIPT"]
