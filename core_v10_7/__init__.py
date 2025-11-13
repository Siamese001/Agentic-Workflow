"""Public API surface for the modularised v10.7 core."""
from __future__ import annotations

import os
import sys
from asyncio import TimeoutError as AsyncTimeoutError

# --- Vendor path bootstrap for Codex offline environment ---
VENDOR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "vendor"))
if os.path.isdir(VENDOR_PATH) and VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

from . import agents as _agents
from . import clients as _clients
from . import config as _config
from . import constants as _constants
from . import context as _context
from . import exceptions as _exceptions
from . import mcp as _mcp
from . import models as _models
from . import resilience as _resilience
from . import services as _services

from .agents import *  # noqa: F401,F403
from .clients import *  # noqa: F401,F403
from .config import *  # noqa: F401,F403
from .constants import *  # noqa: F401,F403
from .context import *  # noqa: F401,F403
from .exceptions import *  # noqa: F401,F403
from .mcp import *  # noqa: F401,F403
from .models import *  # noqa: F401,F403
from .resilience import *  # noqa: F401,F403
from .services import *  # noqa: F401,F403

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
