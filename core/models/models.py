from __future__ import annotations

"""Snapshot-local core.models.models shim for v10_10 tests.

When tests are run with rootdir=Agentic-Workflow-10_10, ``core`` resolves to
this package. This module re-exports the snapshot-local ``models`` module so
imports like ``from core.models.models import JobInput`` work as expected.
"""

from models import *  # noqa: F401,F403
