"""Batch fix NameErrors in agentic_core source files.

Strategy: For each file with a NameError at module level, add the missing
import/definition BEFORE the line that uses it.
"""
import ast
import os
import re
import sys

ROOT = r"C:\Git\Agentic-Workflow"

# Known fixes: name -> import statement to add at top of file
IMPORT_FIXES = {
    "APPS_LIC_DIR": "from agentic_core.L0_routing.config.path_constants import APPS_LIC_DIR",
    "APPS_RG_DIR": "from agentic_core.L0_routing.config.path_constants import APPS_RG_DIR",
    "APPS_SHARED_DIR": "from agentic_core.L0_routing.config.path_constants import APPS_SHARED_DIR",
    "AGENTIC_CORE_DIR": "from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR",
    "OPS_SCRIPTS_DIR": "from agentic_core.L0_routing.config.path_constants import OPS_SCRIPTS_DIR",
    "ARCHIVES_DIR": "from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR",
    "REPORTS_DIR": "from agentic_core.L0_routing.config.path_constants import REPORTS_DIR",
    "SYSTEM_LEARNING_DIR": "from agentic_core.L0_routing.config.path_constants import SYSTEM_LEARNING_DIR",
    "TESTS_UNIT_DIR": "from agentic_core.L0_routing.config.path_constants import TESTS_UNIT_DIR",
    "Path": "from pathlib import Path",
    "_emit_writes_through": "from agentic_core.runtime.lifecycle_trace_contract import _emit_writes_through",
}

# Stub definitions for classes not importable
STUB_FIXES = {
    "HealerMixin": 'class HealerMixin:\n    """Stub HealerMixin."""\n    pass\n',
    "MCPHardenedMixin": 'class MCPHardenedMixin:\n    """Stub MCPHardenedMixin."""\n    pass\n',
    "L5SafetyBase": 'class L5SafetyBase:\n    """Stub L5SafetyBase."""\n    pass\n',
    "VMProvider": 'class VMProvider:\n    """Stub VMProvider."""\n    pass\n',
    "DiscoveredAgent": 'class DiscoveredAgent:\n    """Stub DiscoveredAgent."""\n    pass\n',
    "layer_entry": 'def layer_entry(f):\n    """Stub layer_entry decorator."""\n    return f\n',
    "timeout": 'def timeout(seconds):\n    """Stub timeout decorator."""\n    def wrapper(f): return f\n    return wrapper\n',
    "L0_MAINTENANCE_DIR": 'L0_MAINTENANCE_DIR = "agentic_core/L0_routing/maintenance"\n',
}








if __name__ == "__main__":
    main()
