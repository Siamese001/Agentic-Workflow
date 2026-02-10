from __future__ import annotations

"""
Canon Validator Mission Runner

Contains all mission execution modes:
- Standard Mode (L4): Full validation mission with self-healing cycles
- Daemon Mode (L5): The Watchman - file system monitoring
- Surgical Mode: Target specific files for validation

This module consolidates all mission execution logic from the canon validator.
"""
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

from agentic_core.utils.security import safe_git_execute

from agentic_core.L0_maintenance.enforcement.v15_runtime_guard import (
    v15_runtime_guard,
)

# [SSOT IMPORT] Structure blueprint is the single source of truth


Logger = logging.getLogger(__name__)

# ==============================================================================
# OPTIONAL DEPENDENCY CHECKS
# ==============================================================================

# L5 Watchman: File System Monitoring
try:
    from watchdog.events import FileSystemEventhandler  # noqa: F401
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None

# L5 Live Reasoning Stream: WebSockets
try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None

# L5 Multi-Repository: GitPython
try:
    from git import Repo

    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False
    Repo = None


def _get_imports():
    """Lazy import to avoid circular dependencies.

    NOTE: We import from scripts/CanonValidatorAgent/agents/ which has the FULL
    self-healing agents with mutation logic. The agentic_core/agents/ versions
    are detection-only stubs without healing capabilities.
    """
    # Import ALL self-healing agents from CanonValidatorAgent (ZERO CAPABILITY LOSS)
    # WatchmanHandler is in agentic_core (not in scripts/CanonValidatorAgent)
    # DEPRECATED: CanonSwarmScheduler removed - scheduling handled differently now
    # from agentic_core.canon_scheduler import CanonSwarmScheduler
    from agentic_core.InterventionServer import (
        FASTAPI_AVAILABLE,
        approval_event,
        start_intervention_server,
    )

    # GRAVITY FIX: Removed all scripts.CanonValidatorAgent imports
    # These agents need to be moved to agentic_core or refactored
    from agentic_core.L5_safety.validators.GovernanceAgent import (
        GovernanceAgent as ArchitectureGovernor,  # Keys 40, 41, 50 + syntax fix
    )

    # Use the FULL ValidationContext from scripts/CanonValidatorAgent which has all methods
    # GRAVITY FIX: Removed all scripts.CanonValidatorAgent imports
    # These agents need to be moved to agentic_core or refactored

    return {
        "ValidationContext": None,
        "CanonSwarmScheduler": CanonSwarmScheduler,
        "start_intervention_server": start_intervention_server,
        "approval_event": approval_event,
        "FASTAPI_AVAILABLE": FASTAPI_AVAILABLE,
        # All agents for zero capability loss
        "ArchitectureGovernor": ArchitectureGovernor,
        "CodeStyleGuardian": None,
        "ConcurrencyGuardianAgent": None,
        "DependencySentinelAgent": None,
        "GitAgent": None,
        "Historian": None,
        "HygieneGuardian": None,
        "NamingEnforcer": None,
        "TypeEnforcer": None,
        "PatternEnforcerAgent": None,
        "StructuralEngineer": None,
        "SafetyInspectorAgent": None,
        "TestPilot": None,
        "ReflectionAgent": None,
        "StrategicPlannerAgent": None,
        "WatchmanHandler": WatchmanHandler,
    }


# ==============================================================================
# DAEMON MODE (L5 Watchman)
# ==============================================================================


@v15_runtime_guard("C.run_daemon_mode.mission_runner")
def run_daemon_mode():
    """
    L5 Autonomous Mode: The Watchman - monitors repository for changes.

    Watches the repository for file modifications and automatically triggers
    surgical validation missions using blast radius analysis.
    """
    if not WATCHDOG_AVAILABLE:
        print("[X] WATCHDOG NOT AVAILABLE. Install with: pip install watchdog")
        sys.exit(1)

    imports = _get_imports()
    WatchmanHandler = imports["WatchmanHandler"]

    print("=" * 60)
    print("[START] THE WATCHMAN: L5 Autonomous Mode Active")
    print("=" * 60)
    print("   Monitoring repository for changes...")
    print("   Press Ctrl+C to stop.")
    print("=" * 60)

    # Create event loop for async operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Create handler and observer
    handler = WatchmanHandler(loop)

    # Wrap handler to work with watchdog's FileSystemEventHandler
    class WatchdogAdapter(FileSystemEventHandler):
        def __init__(self, watchman_handler):
            self.watchman = watchman_handler

        def on_modified(self, event):
            self.watchman.on_modified(event)

    adapter = WatchdogAdapter(handler)
    observer = Observer()
    observer.schedule(adapter, path=".", recursive=True)
    observer.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n[WATCHMAN] 🛑 Shutting down gracefully...")
        observer.stop()
    finally:
        observer.join()
        loop.close()
        print("[WATCHMAN] 👋 The Watchman has left the building.")


# ==============================================================================
# SURGICAL MODE
# ==============================================================================


@v15_runtime_guard("E.run_surgical_mode.mission_runner")
def run_surgical_mode(target_file: str):
    """
    Surgical mode: Target a specific file for validation.

    Uses blast radius analysis to determine which files need to be validated
    based on the dependency graph.

    Args:
        target_file: Path to the file to validate
    """
    imports = _get_imports()
    CanonSwarmScheduler = imports["CanonSwarmScheduler"]

    print(f"🎯 SURGICAL MODE: Targeting {target_file}")
    scheduler = CanonSwarmScheduler()
    scheduler.build_default_phases()
    asyncio.run(scheduler.run_mission(target_scope=target_file))


# ==============================================================================
# STANDARD MODE (L4)
# ==============================================================================


@v15_runtime_guard("C.run_standard_mode.mission_runner")
def run_standard_mode():
    """
    Standard L4 Mode: Full validation mission with self-healing cycles.

    Executes a complete validation mission with:
    - GitOps branch creation
    - Multi-cycle self-healing
    - Signal-based agent scheduling
    - Human-in-the-loop intervention
    - Rollback on critical regression
    - Remote sync on completion
    """
    imports = _get_imports()

    ValidationContext = imports["ValidationContext"]
    start_intervention_server = imports["start_intervention_server"]
    approval_event = imports["approval_event"]
    FASTAPI_AVAILABLE = imports["FASTAPI_AVAILABLE"]
    # ALL agents for zero capability loss
    ArchitectureGovernor = imports["ArchitectureGovernor"]
    CodeStyleGuardian = imports["CodeStyleGuardian"]
    ConcurrencyGuardianAgent = imports["ConcurrencyGuardianAgent"]
    DependencySentinelAgent = imports["DependencySentinelAgent"]
    GitAgent = imports["GitAgent"]
    Historian = imports["Historian"]
    HygieneGuardian = imports["HygieneGuardian"]
    NamingEnforcer = imports["NamingEnforcer"]
    TypeEnforcer = imports["TypeEnforcer"]
    PatternEnforcerAgent = imports["PatternEnforcerAgent"]
    StructuralEngineer = imports["StructuralEngineer"]
    SafetyInspectorAgent = imports["SafetyInspectorAgent"]
    TestPilot = imports["TestPilot"]
    imports["ReflectionAgent"]
    imports["StrategicPlannerAgent"]

    try:
        ctx = ValidationContext()

        # L5: Start live reasoning stream server in background
        if WEBSOCKETS_AVAILABLE:
            _start_websocket_server(ctx)

    except Exception as e:
        print(f"\n🛑 SYSTEM INITIALIZATION FAILED: {e}")
        sys.exit(1)

    # Build COMPLETE agent list - Full sovereign validation coverage
    # Order matches original IntelligentOrchestratorAgent swarm order
    agents = [
        # 1. Structure (Blocker) - Architecture validation + syntax fix
        ArchitectureGovernor(ctx),
        # 2. Generative Policy - Hygiene + auto-delete
        HygieneGuardian(ctx),
        # 3. Syntax/Style (Signal: AST_VALID) - Code style + auto-fix
        CodeStyleGuardian(ctx),
        # 4. Import Hygiene (Signal: DEPS_VALID) - Dependencies + autoflake/isort
        DependencySentinelAgent(ctx),
        # 5. Security (Signal: SECURE) - Safety validation
        SafetyInspectorAgent(ctx),
        # 6. Patterns - Pattern enforcement
        PatternEnforcerAgent(ctx),
        # 7. Naming - Naming conventions + auto-fix
        NamingEnforcer(ctx),
        # 8. Types - Type hints + auto-inject typing
        TypeEnforcer(ctx),
        # 9. Concurrency - Async/threading safety
        ConcurrencyGuardianAgent(ctx),
        # 10. Structure - Structural validation
        StructuralEngineer(ctx),
        # 11. History
        Historian(ctx),
        # 12. Tests - Test validation
        TestPilot(ctx),
    ]

    # Enable MUTATION MODE for self-healing - agents will fix issues, not just report
    ctx.instructions.append("[SYSTEM] MUTATION MODE: Agents should fix violations, not just report them.")

    async def run_mission():
        MAX_CYCLES = 5
        cycle = 0

        # LEVEL 6: Create healing branch on start (GitOps)
        branch_name = f"healing/auto_{int(time.time())}"
        try:
            safe_git_execute(["checkout", "-b", branch_name], repo_root=Path.cwd(), timeout=10, check=False)
            print(f"   [GIT] GitOps: Created healing branch '{branch_name}'")
        except Exception:
            print("   [!] GitOps: Could not create branch (may not be in git repo)")

        while cycle < MAX_CYCLES:
            cycle += 1
            ctx.signal_healing_cycle(cycle)
            print(f"\n=== [CYCLE] SELF-HEALING CYCLE {cycle}/{MAX_CYCLES} ===")
            # Reset tracking for this cycle
            ctx.modified_files.clear()

            # Build agenda based on cycle and signals
            agenda = _build_agenda(cycle, ctx, agents, GitAgent, StrategicPlannerAgent, ReflectionAgent)

            # Deduplicate agenda
            final_agenda = _deduplicate_agenda(agenda)

            # L5 Human-in-the-Loop intervention check
            if await _check_intervention(
                cycle,
                ctx,
                FASTAPI_AVAILABLE,
                start_intervention_server,
                approval_event,
            ):
                break

            # Execute agents
            for agent in final_agenda:
                if agent.can_run():
                    await agent.execute()

            # Rollback on critical regression
            if "TEST_FAILURE" in ctx.signals and cycle > 1 and ctx.file_backups:
                print("   [ALERT] Critical Regression Detected. Initiating Rollback Protocol.")
                ctx.rollback_changes()
                ctx.signals.discard("TEST_FAILURE")

            # Convergence check
            if not ctx.modified_files and cycle > 1:
                ctx.signal_convergence()
                break

            if cycle < MAX_CYCLES:
                print("   [~] Modifications detected. Rerunning validation to ensure stability...")
                await asyncio.sleep(1)
        else:
            _handle_max_cycles_reached(ctx)

        # L5: Remote Sync on Mission Completion
        _remote_sync(ctx, branch_name)

        print("\n[SAVE] SAVING BLACKBOARD STATE...")
        ctx._save_memory()
        print("\nMISSION COMPLETE")

    # Return the coroutine for the caller to run
    return run_mission


@v15_runtime_guard("C._start_websocket_server.mission_runner")
def _start_websocket_server(ctx):
    """Start WebSocket server for live reasoning stream."""
    import threading

    async def ws_handler(websocket):
        ctx.websocket_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            ctx.websocket_clients.discard(websocket)

    async def start_ws_server():
        async with websockets.serve(ws_handler, "127.0.0.1", 8765):
            print("   📡 L5: Live reasoning stream at ws://127.0.0.1:8765")
            await asyncio.Future()

    def run_ws_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_ws_server())

    ws_thread = threading.Thread(target=run_ws_server, daemon=True)
    ws_thread.start()


def _build_agenda(cycle: int, ctx, agents: list, GitAgent, StrategicPlannerAgent, ReflectionAgent) -> list:
    """Build the agent execution agenda based on cycle and signals."""
    agenda = [GitAgent(ctx)]

    if cycle == 1:
        agenda.extend(agents)
        print("   [PLAN] PLAN: Executing full system diagnostic.")
    else:
        print(f"   🤔 STRATEGY: Analyzing {len(ctx.signals)} signals to form agenda...")
        agenda.append(agents[0])  # Historian
        agenda.append(RgStrategicPlannerAgent(ctx))

        if "TEST_FAILURE" in ctx.signals:
            agenda.extend([a for a in agents if a.name in ["Sherlock", "TestPilot"]])
            print("      -> Priority: Root Cause Analysis & Verification")

        if any(s for s in ctx.signals if "IMPORT" in s or "ModuleNotFound" in s):
            agenda.extend([a for a in agents if a.name == "DependencySentinelAgent"])
            print("      -> Priority: Dependency Resolution")

        if ctx.modified_files:
            agenda.extend([a for a in agents if a.name in ["SafetyInspectorAgent", "CodeStyleGuardian"]])
            print("      -> Priority: Safety/Style check on modified files")

            impact_zone = set()
            for f in ctx.modified_files:
                deps = ctx.get_dependent_files(f)
                impact_zone.update(deps)

            if impact_zone:
                print(
                    f"      ☢️ BLAST RADIUS: {len(impact_zone)} dependent files added to verification scope.",
                )
                ctx.impact_zone = impact_zone

        if "SYNTAX_ERROR" in str(ctx.signals):
            agenda.extend([a for a in agents if a.name == "SafetyInspectorAgent"])
            print("      -> Priority: Syntax Repair")

        if len(agenda) == 2:
            agenda.append(agents[-1])  # TestPilot
            print("      -> Plan: General System Verification")

    agenda.append(RgReflectionAgent(ctx))
    return agenda


def _deduplicate_agenda(agenda: list) -> list:
    """Deduplicate agenda while preserving order."""
    seen = set()
    final_agenda = []
    for a in agenda:
        if a.name not in seen:
            final_agenda.append(a)
            seen.add(a.name)
    return final_agenda


async def _check_intervention(
    cycle: int,
    ctx,
    FASTAPI_AVAILABLE: bool,
    start_intervention_server,
    approval_event,
) -> bool:
    """Check if human intervention is required and handle it."""
    high_risk = (
        cycle >= 3
        and len(ctx.modified_files) > 8
        or "TEST_FAILURE" in ctx.signals
        and cycle > 2
        or len(ctx.signals) > 5
    )

    if high_risk and FASTAPI_AVAILABLE:
        print(f"\n   [ALERT] L5 INTERVENTION: High-risk state detected (cycle {cycle})")
        print(f"      Modified files: {len(ctx.modified_files)} | Signals: {len(ctx.signals)}")
        start_intervention_server(ctx)
        print("   ⏳ Awaiting human decision at http://127.0.0.1:8080")
        approval_event.clear()
        try:
            await asyncio.wait_for(approval_event.wait(), timeout=None)
        except asyncio.CancelledError:
            pass

        if "VETOED" in ctx.signals:
            print("   🛑 HUMAN VETO RECEIVED. Aborting mission.")
            ctx.signals.add("HUMAN_VETO")
            return True
        else:
            print("   [OK] HUMAN APPROVAL RECEIVED. Proceeding with execution.")

    return False


def _handle_max_cycles_reached(ctx):
    """Handle the case when max healing cycles are reached."""
    print("\n[!] MAX HEALING CYCLES REACHED. Escalating...")
    if ctx.modified_files or ctx.signals:
        esc_dir = Path("observability/human_review")
        esc_dir.mkdir(parents=True, exist_ok=True)
        report = f"# ESCALATION REPORT\nTimestamp: {time.ctime()}\nSignals: {ctx.signals}\nPending Files: {ctx.modified_files}"
        (esc_dir / f"escalation_{int(time.time())}.md").write_text(report)
        print(f"   [ALERT] Manual Review Required. Report saved to: {esc_dir}")


def _remote_sync(ctx, branch_name: str):
    """Sync to remote repository on mission completion."""
    if (
        GITPYTHON_AVAILABLE
        and hasattr(ctx, "signal_convergence")
        and getattr(ctx.signal_convergence, "reached", False)
    ):
        remote_url = os.getenv("CANON_REMOTE_REPO")
        if remote_url:
            try:
                repo = Repo(".")
                try:
                    origin = repo.remote("origin")
                except ValueError:
                    origin = repo.create_remote("origin", remote_url)

                print(f"   ☁️ L5: Pushing healing branch to remote {remote_url}")
                push_info = origin.push(refspec=f"HEAD:refs/heads/{branch_name}")[0]
                if push_info.flags & push_info.ERROR:
                    print(f"   [X] Push failed: {push_info.summary}")
                else:
                    print(f"   [OK] Successfully pushed {branch_name}")
            except Exception as e:
                print(f"   [!] Remote push failed: {e}")
