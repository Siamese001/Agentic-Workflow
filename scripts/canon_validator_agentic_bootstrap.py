#!/usr/bin/env python3
"""
Canon Validator v2.0 - Bootstrap Entry Point

This file is a minimal bootstrap that re-exports the modularized Canon Validator
from the `canon_validator` package. The original monolithic implementation has been
split into subatomic modules for maintainability and governance compliance.

Usage:
    python canon_validator_agentic_bootstrap.py

Or import directly:
    from canon_validator import SwarmScheduler
    scheduler = SwarmScheduler()
    await scheduler.run_mission()
"""

import asyncio
import sys

# Fix Windows console encoding FIRST (before any print with unicode)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Re-export everything from the modularized package
from canon_validator import (  # Config; Types; Base; Prompts; Core Agents; Safety and Testing Agents; Security and Performance Agents; Strategic and Operational Agents; Refinement and Optimization Agents; Orchestrator
    ALLOWED_ROOT_FILES, ALLOWED_ROOT_FOLDERS, EXCLUDED_DIRS, EXCLUDED_FILES,
    FEW_SHOT_GLOBAL_REFACTOR, FEW_SHOT_PROMPTS, MAX_DEPTH, MAX_LINES,
    MIN_DEPTH, POSITIVE_INSTRUCTIONAL_CONTEXT, ArchitectureGovernor,
    BenchmarkingAgent, BudgetManager, CodeStyleGuardian, ConcurrencyGuardian,
    DeadlockDetector, DependencyGraph, DependencySentinel, DocEnforcer,
    GitAgent, Historian, HygieneGuardian, ImportPatcher,
    IntelligentOrchestrator, MemoryLeakDetector, NamingEnforcer,
    PatternEnforcer, PerformanceEnforcer, ReflectionAgent, SafetyInspector,
    SecurityEnforcer, Sherlock, StrategicPlanner, StructuralEngineer,
    SubAtomicAgent, SwarmScheduler, TestPilot, TheCartographer, TheOmniContext,
    TheStrategist, ToolsmithAgent, TypeEnforcer, ValidationContext,
    get_python_files, is_excluded)

# Legacy alias for backward compatibility
IntelligentOrchestrator = SwarmScheduler


async def main():
    """Main entry point for the Canon Validator."""
    print("=" * 60)
    print("CANON VALIDATOR v2.0 - SUBATOMIC ARCHITECTURE")
    print("=" * 60)
    print()
    print("This bootstrap re-exports from the modularized canon_validator package.")
    print("All 50 keys are covered by subatomic agent classes.")
    print()

    scheduler = SwarmScheduler()
    await scheduler.run_mission()


if __name__ == "__main__":
    asyncio.run(main())
