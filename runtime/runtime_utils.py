from __future__ import annotations

"""Snapshot-local runtime.runtime_utils shim for v10_10 tests.

This module allows imports of the form::

    from runtime.runtime_utils import invoke_model, SandboxConfig

when tests are run with rootdir=Agentic-Workflow-10_10. It delegates to the
existing runtime_utils module at the snapshot root.
"""

from runtime_utils import *  # noqa: F401,F403
