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
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, List, Any

logger = logging.getLogger(__name__)

# ==============================================================================
# OPTIONAL DEPENDENCY CHECKS
# ==============================================================================

# L5 Watchman: File System Monitoring
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    FileSystemEventHandler = object
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
    """Lazy import to avoid circular dependencies."""
    from agentic_core.domain.context import ValidationContext
    from agentic_core.L3_orchestration.canon_scheduler import CanonSwarmScheduler
    from agentic_core.L3_orchestration.intervention_server import (
        start_intervention_server,
        approval_event,
        FASTAPI_AVAILABLE,
    )
    from agentic_core.agents.governance import ArchitectureGovernor, DependencySentinel
    from agentic_core.agents.security import SafetyInspector, ConcurrencyGuardian
    from agentic_core.agents.quality import HygieneGuardian, CodeStyleGuardian
    from agentic_core.agents.repair import TestPilot
    from agentic_core.agents.infrastructure import Historian, GitAgent, WatchmanHandler
    from agentic_core.agents.planning import StrategicPlanner, ReflectionAgent
    
    return {
        'ValidationContext': ValidationContext,
        'CanonSwarmScheduler': CanonSwarmScheduler,
        'start_intervention_server': start_intervention_server,
        'approval_event': approval_event,
        'FASTAPI_AVAILABLE': FASTAPI_AVAILABLE,
        'ArchitectureGovernor': ArchitectureGovernor,
        'DependencySentinel': DependencySentinel,
        'SafetyInspector': SafetyInspector,
        'ConcurrencyGuardian': ConcurrencyGuardian,
        'HygieneGuardian': HygieneGuardian,
        'CodeStyleGuardian': CodeStyleGuardian,
        'TestPilot': TestPilot,
        'Historian': Historian,
        'GitAgent': GitAgent,
        'WatchmanHandler': WatchmanHandler,
        'StrategicPlanner': StrategicPlanner,
        'ReflectionAgent': ReflectionAgent,
    }


# ==============================================================================
# DAEMON MODE (L5 Watchman)
# ==============================================================================

def run_daemon_mode():
    """
    L5 Autonomous Mode: The Watchman - monitors repository for changes.
    
    Watches the repository for file modifications and automatically triggers
    surgical validation missions using blast radius analysis.
    """
    if not WATCHDOG_AVAILABLE:
        print("❌ WATCHDOG NOT AVAILABLE. Install with: pip install watchdog")
        sys.exit(1)
    
    imports = _get_imports()
    WatchmanHandler = imports['WatchmanHandler']
    
    print("=" * 60)
    print("🚀 THE WATCHMAN: L5 Autonomous Mode Active")
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
    observer.schedule(adapter, path='.', recursive=True)
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

def run_surgical_mode(target_file: str):
    """
    Surgical mode: Target a specific file for validation.
    
    Uses blast radius analysis to determine which files need to be validated
    based on the dependency graph.
    
    Args:
        target_file: Path to the file to validate
    """
    imports = _get_imports()
    CanonSwarmScheduler = imports['CanonSwarmScheduler']
    
    print(f"🎯 SURGICAL MODE: Targeting {target_file}")
    scheduler = CanonSwarmScheduler()
    scheduler.build_default_phases()
    asyncio.run(scheduler.run_mission(target_scope=target_file))


# ==============================================================================
# STANDARD MODE (L4)
# ==============================================================================

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
    
    ValidationContext = imports['ValidationContext']
    start_intervention_server = imports['start_intervention_server']
    approval_event = imports['approval_event']
    FASTAPI_AVAILABLE = imports['FASTAPI_AVAILABLE']
    ArchitectureGovernor = imports['ArchitectureGovernor']
    DependencySentinel = imports['DependencySentinel']
    SafetyInspector = imports['SafetyInspector']
    ConcurrencyGuardian = imports['ConcurrencyGuardian']
    HygieneGuardian = imports['HygieneGuardian']
    CodeStyleGuardian = imports['CodeStyleGuardian']
    TestPilot = imports['TestPilot']
    Historian = imports['Historian']
    GitAgent = imports['GitAgent']
    StrategicPlanner = imports['StrategicPlanner']
    ReflectionAgent = imports['ReflectionAgent']
    
    try:
        ctx = ValidationContext()
        
        # L5: Start live reasoning stream server in background
        if WEBSOCKETS_AVAILABLE:
            _start_websocket_server(ctx)
            
    except Exception as e:
        print(f"\n🛑 SYSTEM INITIALIZATION FAILED: {e}")
        sys.exit(1)
    
    # Build agent list
    agents = [
        Historian(ctx), ArchitectureGovernor(ctx), HygieneGuardian(ctx),
        CodeStyleGuardian(ctx), DependencySentinel(ctx), SafetyInspector(ctx),
        ConcurrencyGuardian(ctx), TestPilot(ctx)
    ]

    async def run_mission():
        MAX_CYCLES = 5
        cycle = 0
        
        # LEVEL 6: Create healing branch on start (GitOps)
        branch_name = f"healing/auto_{int(time.time())}"
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True, check=False)
            print(f"   🌱 GitOps: Created healing branch '{branch_name}'")
        except Exception:
            print("   ⚠️ GitOps: Could not create branch (may not be in git repo)")
        
        while cycle < MAX_CYCLES:
            cycle += 1
            ctx.signal_healing_cycle(cycle)
            print(f"\n=== 🧬 SELF-HEALING CYCLE {cycle}/{MAX_CYCLES} ===")
            
            # Reset tracking for this cycle
            ctx.modified_files.clear()
            
            # Build agenda based on cycle and signals
            agenda = _build_agenda(cycle, ctx, agents, GitAgent, StrategicPlanner, ReflectionAgent)
            
            # Deduplicate agenda
            final_agenda = _deduplicate_agenda(agenda)
            
            # L5 Human-in-the-Loop intervention check
            if await _check_intervention(cycle, ctx, FASTAPI_AVAILABLE, start_intervention_server, approval_event):
                break
            
            # Execute agents
            for agent in final_agenda:
                if agent.can_run():
                    await agent.execute()
            
            # Rollback on critical regression
            if "TEST_FAILURE" in ctx.signals and cycle > 1 and ctx.file_backups:
                print("   🚨 Critical Regression Detected. Initiating Rollback Protocol.")
                ctx.rollback_changes()
                ctx.signals.discard("TEST_FAILURE")
            
            # Convergence check
            if not ctx.modified_files and cycle > 1:
                ctx.signal_convergence()
                break
                
            if cycle < MAX_CYCLES:
                print(f"   🔄 Modifications detected. Rerunning validation to ensure stability...")
                await asyncio.sleep(1)
        else:
            _handle_max_cycles_reached(ctx)

        # L5: Remote Sync on Mission Completion
        _remote_sync(ctx, branch_name)

        print("\n💾 SAVING BLACKBOARD STATE...")
        ctx._save_memory()
        print("\nMISSION COMPLETE")

    asyncio.run(run_mission())


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


def _build_agenda(cycle: int, ctx, agents: List, GitAgent, StrategicPlanner, ReflectionAgent) -> List:
    """Build the agent execution agenda based on cycle and signals."""
    agenda = [GitAgent(ctx)]
    
    if cycle == 1:
        agenda.extend(agents)
        print("   📋 PLAN: Executing full system diagnostic.")
    else:
        print(f"   🤔 STRATEGY: Analyzing {len(ctx.signals)} signals to form agenda...")
        agenda.append(agents[0])  # Historian
        agenda.append(StrategicPlanner(ctx))
        
        if "TEST_FAILURE" in ctx.signals:
            agenda.extend([a for a in agents if a.name in ["Sherlock", "TestPilot"]])
            print("      -> Priority: Root Cause Analysis & Verification")
        
        if any(s for s in ctx.signals if "IMPORT" in s or "ModuleNotFound" in s):
            agenda.extend([a for a in agents if a.name == "DependencySentinel"])
            print("      -> Priority: Dependency Resolution")
        
        if ctx.modified_files:
            agenda.extend([a for a in agents if a.name in ["SafetyInspector", "CodeStyleGuardian"]])
            print("      -> Priority: Safety/Style check on modified files")
            
            impact_zone = set()
            for f in ctx.modified_files:
                deps = ctx.get_dependent_files(f)
                impact_zone.update(deps)
            
            if impact_zone:
                print(f"      ☢️ BLAST RADIUS: {len(impact_zone)} dependent files added to verification scope.")
                ctx.impact_zone = impact_zone
        
        if "SYNTAX_ERROR" in str(ctx.signals):
            agenda.extend([a for a in agents if a.name == "SafetyInspector"])
            print("      -> Priority: Syntax Repair")

        if len(agenda) == 2:
            agenda.append(agents[-1])  # TestPilot
            print("      -> Plan: General System Verification")
    
    agenda.append(ReflectionAgent(ctx))
    return agenda


def _deduplicate_agenda(agenda: List) -> List:
    """Deduplicate agenda while preserving order."""
    seen = set()
    final_agenda = []
    for a in agenda:
        if a.name not in seen:
            final_agenda.append(a)
            seen.add(a.name)
    return final_agenda


async def _check_intervention(cycle: int, ctx, FASTAPI_AVAILABLE: bool, 
                              start_intervention_server, approval_event) -> bool:
    """Check if human intervention is required and handle it."""
    high_risk = (
        cycle >= 3 and len(ctx.modified_files) > 8
        or "TEST_FAILURE" in ctx.signals and cycle > 2
        or len(ctx.signals) > 5
    )

    if high_risk and FASTAPI_AVAILABLE:
        print(f"\n   🚨 L5 INTERVENTION: High-risk state detected (cycle {cycle})")
        print(f"      Modified files: {len(ctx.modified_files)} | Signals: {len(ctx.signals)}")
        start_intervention_server(ctx)
        print(f"   ⏳ Awaiting human decision at http://127.0.0.1:8080")
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
            print("   ✅ HUMAN APPROVAL RECEIVED. Proceeding with execution.")
    
    return False


def _handle_max_cycles_reached(ctx):
    """Handle the case when max healing cycles are reached."""
    print(f"\n⚠️ MAX HEALING CYCLES REACHED. Escalating...")
    if ctx.modified_files or ctx.signals:
        esc_dir = Path("observability/human_review")
        esc_dir.mkdir(parents=True, exist_ok=True)
        report = f"# ESCALATION REPORT\nTimestamp: {time.ctime()}\nSignals: {ctx.signals}\nPending Files: {ctx.modified_files}"
        (esc_dir / f"escalation_{int(time.time())}.md").write_text(report)
        print(f"   🚨 Manual Review Required. Report saved to: {esc_dir}")


def _remote_sync(ctx, branch_name: str):
    """Sync to remote repository on mission completion."""
    if GITPYTHON_AVAILABLE and hasattr(ctx, 'signal_convergence') and getattr(ctx.signal_convergence, 'reached', False):
        remote_url = os.getenv("CANON_REMOTE_REPO")
        if remote_url:
            try:
                repo = Repo('.')
                try:
                    origin = repo.remote('origin')
                except ValueError:
                    origin = repo.create_remote('origin', remote_url)
                
                print(f"   ☁️ L5: Pushing healing branch to remote {remote_url}")
                push_info = origin.push(refspec=f'HEAD:refs/heads/{branch_name}')[0]
                if push_info.flags & push_info.ERROR:
                    print(f"   ❌ Push failed: {push_info.summary}")
                else:
                    print(f"   ✅ Successfully pushed {branch_name}")
            except Exception as e:
                print(f"   ⚠️ Remote push failed: {e}")
