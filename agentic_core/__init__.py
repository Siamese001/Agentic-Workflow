"""
AGENTIC CORE: THE BRAIN (Key 40)
================================
The sovereign domain for domain-agnostic agentic reasoning.
This package contains the 5 Atomic Layers of the architecture.

STRUCTURE:
- L1_cognition/       : Strategy, Planning, Reflection
- L2_execution/       : Tools, Engines, IO
- L3_orchestration/   : Workflows, Fission, Delegation
- L4_state/           : Context, Memory, Persistence
- L5_safety/          : Guardrails, Security, PII

COMPLIANCE:
- This package is SOVEREIGN. It must NOT import from 'apps_*'.
- Domain-specific logic (e.g., 'BulletNarrative') belongs in 'apps_rg'.
"""
from typing import Any, Optional, Protocol, Dict, List
import re
import time


import logging
import sys

# Optional dashboard dependencies
try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    _PANDAS_AVAILABLE = False
    pd = None

try:
    import streamlit as st
    _STREAMLIT_AVAILABLE = True
except ImportError:
    _STREAMLIT_AVAILABLE = False
    st = None

# ==============================================================================
# 1. SOVEREIGN CONFIGURATION
# ==============================================================================

__version__ = "2.8.0"
__author__ = "Architecture Governor"

# Configure centralized logger for The Brain
_logger = logging.getLogger("agentic_core")
_logger.setLevel(logging.INFO) # Can be overridden by Key 0 (Global Config)

# ==============================================================================
# 2. LAYER EXPOSURE
# ==============================================================================

# We explicitly do NOT import all agents here to prevent:
# 1. Circular Dependencies (The "Mega-Init" anti-pattern)
# 2. Premature loading of heavy ML libraries
# 3. Violation of Fission (Agents should be imported only when needed)

# Agents should be discovered via 'canon_validator' or imported specifically:
# from agentic_core.L5_safety import PIISanitizerAgent

# ==============================================================================
# 3. RUNTIME BRIDGE (The Janitor)
# ==============================================================================

# Expose compliance tools for external validators (Key 46/47)
try:
    from .runtime import compliance
except ImportError:
    # Allow partial initialization during bootstrapping/migration
    _logger.warning("agentic_core.runtime.compliance not found. Skipping bridge.")
    compliance = None

# ==============================================================================
# 4. FLIGHT RECORDER DASHBOARD (Architectural Violation for Debugging)
# ==============================================================================
# WARNING: This section introduces UI/DB dependencies into agentic_core,
# violating its sovereign principles. It is intended for debugging purposes only
# and should ideally reside in a separate 'apps_debug' package.

try:
    _DASHBOARD_DEPS_AVAILABLE = True
except ImportError:
    _DASHBOARD_DEPS_AVAILABLE = False

_DASHBOARD_DB_PATH = "flight_recorder.duckdb"

# Dashboard functions only defined if streamlit is available
if st:
    def run_flight_recorder_dashboard():
        """
        Launches the Subatomic Flight Recorder Dashboard.
        This function encapsulates the Streamlit UI logic.
        To run: `streamlit run path/to/agentic_core/__init__.py`
        """
        if not _DASHBOARD_DEPS_AVAILABLE:
            st.error("Missing dashboard dependencies. Install with: pip install streamlit plotly pandas duckdb")
            st.stop()
        
        st.title("✈️ Subatomic Flight Recorder")
        st.info("Dashboard functionality temporarily simplified for validator stability.")
        st.stop()
else:
    run_flight_recorder_dashboard = None

__all__ = [
    "__version__",
    "compliance",
    "run_flight_recorder_dashboard", # Expose the dashboard launcher
]

# This block allows the __init__.py to be run directly by Streamlit for the dashboard
if __name__ == "__main__":
    # Check if Streamlit is running this script
    if 'streamlit' in sys.modules and st._is_running_with_streamlit:
        run_flight_recorder_dashboard()
    else:
        # If imported or run as a regular Python script, do not launch UI
        _logger.info("agentic_core package imported. Flight Recorder Dashboard not launched automatically.")
        _logger.info("To run the dashboard, use: streamlit run path/to/agentic_core/__init__.py")