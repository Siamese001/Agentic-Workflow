#!/usr/bin/env python3
"""Dump actual values of derived constants needed at L0."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import pprint

from agentic_core.L5_safety.config.structure_blueprint import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    DEPTH_RULES,
    PROJECT_ROOT_WHITELIST,
)

print("DEPTH_RULES =", pprint.pformat(dict(DEPTH_RULES)))
print()
print("PROJECT_ROOT_WHITELIST =", pprint.pformat(sorted(PROJECT_ROOT_WHITELIST)))
print()
print("CORE_SUBFOLDER_MAP =", pprint.pformat({k: list(v) for k, v in CORE_SUBFOLDER_MAP.items()}))
print()
print("APPS_RG_SUBFOLDER_MAP =", pprint.pformat({k: list(v) for k, v in APPS_RG_SUBFOLDER_MAP.items()}))
print()
print("APPS_LIC_SUBFOLDER_MAP =", pprint.pformat({k: list(v) for k, v in APPS_LIC_SUBFOLDER_MAP.items()}))
print()
print("APPS_SHARED_SUBFOLDER_MAP =", pprint.pformat({k: list(v) for k, v in APPS_SHARED_SUBFOLDER_MAP.items()}))
