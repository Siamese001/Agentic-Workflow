from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

"\nCanon Validator Mission Runner\n\nContains all mission execution modes:\n- Standard Mode (L4): Full validation mission with self-healing cycles\n- Daemon Mode (L5): The Watchman - file system monitoring\n- Surgical Mode: Target specific files for validation\n\nThis module consolidates all mission execution logic from the canon validator.\n"
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP, DEFAULT_TIMEOUT
from agentic_core.L0_routing.enforcement.runtime_guard import runtime_guard
from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced
from agentic_core.utils.security_util import safe_git_execute

Logger = logging.getLogger(__name__)
try:
    from watchdog.events import FileSystemEventHandler  # noqa: F401
    from watchdog.observers import Observer  # noqa: F401

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None
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
    from agentic_core.InterventionServer import FASTAPI_AVAILABLE, approval_event, start_intervention_server

    from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent as ArchitectureGovernor

    return {
        "ValidationContext": None,
        "CanonSwarmScheduler": CanonSwarmScheduler,
        "start_intervention_server": start_intervention_server,
        "approval_event": approval_event,
        "FASTAPI_AVAILABLE": FASTAPI_AVAILABLE,
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


def _v15_build_mission_manifest(mode_name: str, target_layer: str = "L3"):
    """§8.1c — Construct SurgicalManifest for mission runner mode entry.

    Returns None when V15 enforcement is off (zero overhead).
    Lazy imports to avoid pulling heavy dependency chains at module level.
    """
    if not is_v15_enforced():
        return None
    import hashlib as _hl

    from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
    from agentic_core.L0_routing.types.determinism_contracts_types import require_manifest_hash_ok
    from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest

    _hex8 = _hl.sha256(f"mission_runner.{mode_name}".encode()).hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    ast_snippet = f"mission_runner.{mode_name}()"
    manifest = SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="MissionRunner",
        target_layer=target_layer,
        ast_snippet=ast_snippet,
        serialization_canon="mission_runner",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=_hl.sha256(ast_snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )
    require_manifest_hash_ok(manifest)
    return manifest


def _v15_gateway_audit(manifest, trace_id: str) -> None:
    """§8.1c — Invoke gateway.execute in LOG_ONLY mode for audit trail."""
    if manifest is None:
        return
    try:
        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        gw.execute(
            manifest,
            lambda m: {"status": "audit", "errors": 0},
            lambda: (
                _hl.sha256(b"fs_mission").hexdigest(),
                _hl.sha256(b"git_mission").hexdigest(),
                _hl.sha256(b"mem_mission").hexdigest(),
            ),
            trace_id=trace_id,
            agent_id="mission_runner",
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        raise
        Logger.warning("[V15] Gateway audit failed (LOG_ONLY): %s", exc)


@runtime_guard("C.run_daemon_mode.mission_runner")
def run_daemon_mode():
    """
    L5 Autonomous Mode: The Watchman - monitors repository for changes.

    Watches the repository for file modifications and automatically triggers
    surgical validation missions using blast radius analysis.
    """
    manifest = _v15_build_mission_manifest("run_daemon_mode", target_layer="L5")
    if manifest is not None:
        _v15_gateway_audit(manifest, trace_id=manifest.correlation_id)
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    handler = WatchmanHandler(loop)

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


@runtime_guard("E.run_surgical_mode.mission_runner")
def run_surgical_mode(target_file: str):
    """
    Surgical mode: Target a specific file for validation.

    Uses blast radius analysis to determine which files need to be validated
    based on the dependency graph.

    Args:
        target_file: Path to the file to validate
    """
    manifest = _v15_build_mission_manifest("run_surgical_mode", target_layer="L3")
    if manifest is not None:
        _v15_gateway_audit(manifest, trace_id=manifest.correlation_id)
    imports = _get_imports()
    CanonSwarmScheduler = imports["CanonSwarmScheduler"]
    print(f"🎯 SURGICAL MODE: Targeting {target_file}")
    scheduler = CanonSwarmScheduler()
    scheduler.build_default_phases()
    asyncio.run(scheduler.run_mission(target_scope=target_file))


@runtime_guard("C.run_standard_mode.mission_runner")
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
    manifest = _v15_build_mission_manifest("run_standard_mode", target_layer="L4")
    if manifest is not None:
        _v15_gateway_audit(manifest, trace_id=manifest.correlation_id)
    imports = _get_imports()
    ValidationContext = imports["ValidationContext"]
    start_intervention_server = imports["start_intervention_server"]
    approval_event = imports["approval_event"]
    FASTAPI_AVAILABLE = imports["FASTAPI_AVAILABLE"]
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
        if WEBSOCKETS_AVAILABLE:
            _start_websocket_server(ctx)
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"\n🛑 SYSTEM INITIALIZATION FAILED: {e}")
        sys.exit(1)
    agents = [
        ArchitectureGovernor(ctx),
        HygieneGuardian(ctx),
        CodeStyleGuardian(ctx),
        DependencySentinelAgent(ctx),
        SafetyInspectorAgent(ctx),
        PatternEnforcerAgent(ctx),
        NamingEnforcer(ctx),
        TypeEnforcer(ctx),
        ConcurrencyGuardianAgent(ctx),
        StructuralEngineer(ctx),
        Historian(ctx),
        TestPilot(ctx),
    ]
    ctx.instructions.append("[SYSTEM] MUTATION MODE: Agents should fix violations, not just report them.")

    async def run_mission():
        MAX_CYCLES = 5
        cycle = 0
        branch_name = f"healing/auto_{int(time.time())}"
        try:
            safe_git_execute(
                ["checkout", "-b", branch_name], repo_root=Path.cwd(), timeout=DEFAULT_TIMEOUT, check=False
            )
            print(f"   [GIT] GitOps: Created healing branch '{branch_name}'")
        # guardian: allow-silent-swallow
        except Exception:
            print("   [!] GitOps: Could not create branch (may not be in git repo)")
        while cycle < MAX_CYCLES:
            cycle += 1
            ctx.signal_healing_cycle(cycle)
            print(f"\n=== [CYCLE] SELF-HEALING CYCLE {cycle}/{MAX_CYCLES} ===")
            ctx.modified_files.clear()
            agenda = _build_agenda(cycle, ctx, agents, GitAgent, StrategicPlannerAgent, ReflectionAgent)
            final_agenda = _deduplicate_agenda(agenda)
            if await _check_intervention(
                cycle, ctx, FASTAPI_AVAILABLE, start_intervention_server, approval_event
            ):
                break
            for agent in final_agenda:
                if agent.can_run():
                    await agent.execute()
            if "TEST_FAILURE" in ctx.signals and cycle > 1 and ctx.file_backups:
                print("   [ALERT] Critical Regression Detected. Initiating Rollback Protocol.")
                ctx.rollback_changes()
                ctx.signals.discard("TEST_FAILURE")
            if not ctx.modified_files and cycle > 1:
                ctx.signal_convergence()
                break
            if cycle < MAX_CYCLES:
                print("   [~] Modifications detected. Rerunning validation to ensure stability...")
                await asyncio.sleep(DEFAULT_SLEEP)
        else:
            _handle_max_cycles_reached(ctx)
        _remote_sync(ctx, branch_name)
        print("\n[SAVE] SAVING BLACKBOARD STATE...")
        ctx._save_memory()
        print("\nMISSION COMPLETE")

    return run_mission


@runtime_guard("C._start_websocket_server.mission_runner")
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
        agenda.append(agents[0])
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
                    f"      ☢️ BLAST RADIUS: {len(impact_zone)} dependent files added to verification scope."
                )
                ctx.impact_zone = impact_zone
        if "SYNTAX_ERROR" in str(ctx.signals):
            agenda.extend([a for a in agents if a.name == "SafetyInspectorAgent"])
            print("      -> Priority: Syntax Repair")
        if len(agenda) == 2:
            agenda.append(agents[-1])
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
    cycle: int, ctx, FASTAPI_AVAILABLE: bool, start_intervention_server, approval_event
) -> bool:
    """Check if human intervention is required and handle it."""
    high_risk = (
        cycle >= 3
        and len(ctx.modified_files) > 8
        or ("TEST_FAILURE" in ctx.signals and cycle > 2)
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
        _wg.ensure_dir(esc_dir)
        report = f"# ESCALATION REPORT\nTimestamp: {time.ctime()}\nSignals: {ctx.signals}\nPending Files: {ctx.modified_files}"
        _wg.write_text(esc_dir / f"escalation_{int(time.time())}.md", report)
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
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"   [!] Remote push failed: {e}")
