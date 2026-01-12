#!/usr/bin/env python3
"""Wrapper to run full_agent_discovery.py with proper path setup."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run
from scripts.full_agent_discovery import main
main()
