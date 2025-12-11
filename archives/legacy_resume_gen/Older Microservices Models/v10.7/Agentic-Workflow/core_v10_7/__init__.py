"""Public API surface for the modularised v10.7 core."""
from __future__ import annotations

import os
<<<<<<< HEAD
import site
=======
>>>>>>> main
import sys
from asyncio import TimeoutError as AsyncTimeoutError

# --- Vendor path bootstrap for Codex offline environment ---
VENDOR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "vendor"))
if os.path.isdir(VENDOR_PATH) and VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

<<<<<<< HEAD
# Ensure site-packages directories remain discoverable even in notebook or
# sandboxed launchers that manipulate sys.path.
try:
    candidate_paths = site.getsitepackages()
except AttributeError:  # pragma: no cover - PyPy/embedded
    candidate_paths = []

for candidate in candidate_paths + [getattr(site, "getusersitepackages", lambda: None)()]:
    if candidate and os.path.isdir(candidate) and candidate not in sys.path:
        sys.path.append(candidate)

=======
>>>>>>> main
from canon_validator import agents as _agents
from canon_validator import clients as _clients
from canon_validator import config as _config
from canon_validator import constants as _constants
from canon_validator import context as _context
from canon_validator import exceptions as _exceptions
from canon_validator import mcp as _mcp
from canon_validator import models as _models
from canon_validator import resilience as _resilience
from canon_validator import services as _services

from archives.legacy_resume_gen.Older Microservices Models.v10.7.Agentic-Workflow.core_v10_7.agents import *  # noqa: F401,F403
from tests.unit.runtime.test_multi_provider_clients import *  # noqa: F401,F403
from shared.reasoning_config import *  # noqa: F401,F403
from archives.legacy_resume_gen.Older Microservices Models.v10.7.Agentic-Workflow.core_v10_7.constants import *  # noqa: F401,F403
from scripts.utilities.format_scripts_context import *  # noqa: F401,F403
from archives.legacy_resume_gen.Older Microservices Models.v10.7.Agentic-Workflow.core_v10_7.exceptions import *  # noqa: F401,F403
from archives.legacy_resume_gen.Older Microservices Models.v10.7.Agentic-Workflow.core_v10_7.mcp import *  # noqa: F401,F403
from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.dag.test_dag_models import *  # noqa: F401,F403
from archives.legacy_resume_gen.Older Microservices Models.v10.7.Agentic-Workflow.core_v10_7.resilience import *  # noqa: F401,F403
from apps_shared.pipeline.synthesis.use_tools.invoke_pipeline_services import *  # noqa: F401,F403

__all__ = sorted(
    set(
        _agents.__all__
        + _clients.__all__
        + _config.__all__
        + _constants.__all__
        + _context.__all__
        + _exceptions.__all__
        + _mcp.__all__
        + _models.__all__
        + _resilience.__all__
        + _services.__all__
        + ["AsyncTimeoutError"]
    )
)
