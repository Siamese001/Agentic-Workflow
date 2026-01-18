#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discovery Roster Builder - Layer-Based Tagging System

Replaces hard-coded agent rosters with dynamic discovery-based filtering and sorting.

Features:
1. Loads agents from agent_discovery_full.json
2. Filters for agents implementing HealerMixin
3. Sorts by Layer Tier (L0 → L6, then Apps, Utils)
4. Instantiates agents with proper error handling

Usage:
    from agentic_core.L3_orchestration.discovery_roster_builder import build_healing_roster
    roster = build_healing_roster(project_root)
"""
import json
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

Logger = logging.getLogger(__name__)

# Color-coded terminal output
try:
    from agentic_core.utils.terminal_colors import (
        discovery_status, progress_bar, log_status, Colors, print_success, print_warning, print_error
    )
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    def discovery_status(*args, **kwargs): return ""
    def progress_bar(*args, **kwargs): return ""
    def log_status(level, msg, **kwargs): print(f"[{level.upper()}] {msg}")
    def print_success(msg): print(f"[OK] {msg}")
    def print_warning(msg): print(f"[WARN] {msg}")
    def print_error(msg): print(f"[ERR] {msg}")
    class Colors:
        RESET = BRIGHT_GREEN = BRIGHT_RED = BRIGHT_YELLOW = BRIGHT_CYAN = BRIGHT_MAGENTA = DIM = ""

# Layer priority for sorting (lower = higher priority, runs first)
LAYER_PRIORITY = {
    'L0': 0,   # Maintenance - runs first (infrastructure)
    'L1': 1,   # Cognition
    'L2': 2,   # Execution
    'L3': 3,   # Orchestration
    'L4': 4,   # State
    'L5': 5,   # Safety - runs after structure is stable
    'L6': 6,   # Observability - runs last for core
    'Apps': 7, # Application-specific agents
    'Utils': 8, # Utility agents
}

# Agents to skip (known problematic or abstract)
SKIP_AGENTS = {
    # Abstract base classes
    'SovereignBaseAgent',      # Abstract base
    'L0MaintenanceBaseAgent',  # Abstract base
    'L1CognitionBaseAgent',    # Abstract base
    'L2ExecutionBaseAgent',    # Abstract base
    'L3OrchestrationBaseAgent', # Abstract base
    'L4StateBaseAgent',        # Abstract base
    'L5SafetyBaseAgent',       # Abstract base
    'L6ObservabilityBaseAgent', # Abstract base
    # Mixins (not agents)
    'HealerMixin',             # Mixin, not agent
    'MCPHardenedMixin',        # Mixin, not agent
    'SubatomicTestingMixin',   # Mixin, not agent
    # Tier 0 & Tier 1 Core Agents (handled in mandatory tiers, not discovery)
    'SyntaxValidatorAgent',    # Tier 0: Pre-Flight
    'HygieneGuardianAgent',    # Tier 0: Pre-Flight
    'TwoPhaseDeduplicationAgent',  # Tier 1: Structural Stabilization
    'LocationAgent',           # Tier 1: Structural Stabilization
    'HierarchyAgent',          # Tier 1: Structural Stabilization
    'NamingAgent',             # Tier 1: Structural Stabilization
    # Tier 2 Core Agents
    'ImportAgent',             # Tier 2: Architectural Alignment
    # Tier 4 Final Safety Gate
    'AutonomyGuardianAgent',   # Tier 4: Final Safety Gate
}


def load_discovery_data(project_root: Path) -> List[Dict[str, Any]]:
    """Load agent discovery data from JSON file."""
    discovery_file = project_root / "agent_discovery_full.json"
    
    if not discovery_file.exists():
        Logger.warning(f"Discovery file not found: {discovery_file}")
        return []
    
    try:
        with open(discovery_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return list(data.values())
        else:
            Logger.warning(f"Unexpected discovery data type: {type(data)}")
            return []
            
    except Exception as e:
        Logger.error(f"Failed to load discovery data: {e}")
        return []


def filter_healer_agents(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter agents that implement HealerMixin.
    
    Criteria:
    1. Has 'HealerMixin' in inheritance chain
    2. Has 'heal_repository' in key_methods
    3. Is not in SKIP_AGENTS list
    4. Is not an abstract base class
    """
    healers = []
    
    for agent in agents:
        class_name = agent.get('class_name', '')
        
        # Skip known problematic agents
        if class_name in SKIP_AGENTS:
            continue
        
        # Skip abstract base classes
        if class_name.endswith('BaseAgent') or class_name.startswith('Abstract'):
            continue
        
        # Check for HealerMixin in inheritance
        inheritance = agent.get('inheritance', [])
        # [HARDENING] Check for string literal 'HealerMixin' or robust inheritance check
        has_healer_mixin = any(base in ['HealerMixin', 'Healer', 'SovereignHealer'] for base in inheritance)
        
        # Check for heal_repository method
        # [HARDENING] Some agents might not list methods in JSON if parsing failed slightly,
        # so we also check the 'has_healing' boolean flag from discovery if available.
        key_methods = agent.get('key_methods', [])
        has_heal_method = 'heal_repository' in key_methods
        has_healing_flag = agent.get('has_healing', False)
        
        # Must have HealerMixin OR heal_repository method
        if has_healer_mixin or has_heal_method or has_healing_flag:
            healers.append(agent)
        else:
            # Trace log for excluded agents (useful for debugging missing agents)
            # Logger.debug(f"Skipping non-healer: {class_name}")
            pass
    
    return healers


def get_layer_priority(agent: Dict[str, Any]) -> int:
    """Get sorting priority for an agent based on its layer."""
    layer = agent.get('layer', 'Utils')
    return LAYER_PRIORITY.get(layer, 99)


def sort_by_layer(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort agents by Layer Tier (L0 → L6, then Apps, Utils).
    
    Within each layer, sort alphabetically by class name for consistency.
    """
    return sorted(agents, key=lambda a: (get_layer_priority(a), a.get('class_name', '')))


def path_to_module(file_path: str) -> str:
    """Convert file path to Python module path."""
    # Remove .py extension
    module_path = file_path.replace('.py', '')
    
    # Convert path separators to dots
    module_path = module_path.replace('\\', '.').replace('/', '.')
    
    # Remove leading dots if any
    module_path = module_path.lstrip('.')
    
    return module_path


def instantiate_agent(
    agent_data: Dict[str, Any],
    project_root: Path
) -> Optional[Tuple[str, Any]]:
    """
    Dynamically instantiate an agent from discovery data.
    
    Args:
        agent_data: Agent metadata from discovery JSON
        project_root: Project root path for initialization
        
    Returns:
        Tuple of (class_name, agent_instance) or None if failed
    """
    class_name = agent_data.get('class_name', '')
    file_path = agent_data.get('path', '')
    
    if not class_name or not file_path:
        return None
    
    try:
        # Convert path to module
        module_path = path_to_module(file_path)
        
        # Import module
        module = importlib.import_module(module_path)
        
        # Get class
        if not hasattr(module, class_name):
            Logger.debug(f"Class {class_name} not found in {module_path}")
            return None
        
        agent_cls = getattr(module, class_name)
        
        # Try to instantiate with project_root
        try:
            agent_instance = agent_cls(project_root)
        except TypeError:
            # Try without project_root
            try:
                agent_instance = agent_cls()
            except Exception as e:
                Logger.warning(f"Failed to instantiate {class_name} (constructor error): {e}")
                return None
        except Exception as e:
            Logger.warning(f"Failed to instantiate {class_name} with project_root: {e}")
            return None
        
        # Verify heal_repository method exists
        if not hasattr(agent_instance, 'heal_repository'):
            # [HARDENING] Double check at runtime. Discovery JSON might be stale.
            # If instance lacks method, it cannot run in heal mode.
            Logger.debug(f"Skipping {class_name}: Missing heal_repository() at runtime")
            return None
        
        if not callable(agent_instance.heal_repository):
            Logger.debug(f"{class_name}.heal_repository is not callable")
            return None
        
        return (class_name, agent_instance)
        
    except ImportError as e:
        Logger.debug(f"Import error for {class_name}: {e}")
        return None
    except Exception as e:
        Logger.debug(f"Error instantiating {class_name}: {e}")
        return None


def build_healing_roster(
    project_root: Path,
    include_apps: bool = True,
    include_utils: bool = True,
    max_agents: Optional[int] = None
) -> List[Tuple[str, Any]]:
    """
    Build a healing roster from discovery data.
    
    Process:
    1. Load discovery data from agent_discovery_full.json
    2. Filter for agents implementing HealerMixin
    3. Sort by Layer Tier (L0 → L6)
    4. Instantiate each agent
    5. Return list of (name, instance) tuples
    
    Args:
        project_root: Project root path
        include_apps: Include Apps layer agents
        include_utils: Include Utils layer agents
        max_agents: Maximum number of agents to include (None = all)
        
    Returns:
        List of (class_name, agent_instance) tuples, sorted by layer
    """
    log_status('info', 'Loading discovery data...', source='ROSTER')
    
    # Step 1: Load discovery data
    all_agents = load_discovery_data(project_root)
    log_status('success', f'Loaded {Colors.BRIGHT_CYAN}{len(all_agents)}{Colors.RESET} agents from discovery', source='ROSTER')
    
    # Step 2: Filter for HealerMixin
    healer_agents = filter_healer_agents(all_agents)
    log_status('info', f'Filtered to {Colors.BRIGHT_GREEN}{len(healer_agents)}{Colors.RESET} healer agents', source='ROSTER')
    
    # Step 3: Filter by layer if requested
    if not include_apps:
        healer_agents = [a for a in healer_agents if a.get('layer') != 'Apps']
    if not include_utils:
        healer_agents = [a for a in healer_agents if a.get('layer') != 'Utils']
    
    # Step 4: Sort by layer
    sorted_agents = sort_by_layer(healer_agents)
    log_status('info', f'Sorted {len(sorted_agents)} agents by layer priority', source='ROSTER')
    
    # Step 5: Instantiate agents
    roster = []
    instantiation_errors = 0
    total_to_instantiate = len(sorted_agents) if not max_agents else min(max_agents, len(sorted_agents))
    
    print(f"\n{Colors.BRIGHT_CYAN}[ROSTER]{Colors.RESET} Instantiating agents...")
    for idx, agent_data in enumerate(sorted_agents):
        if max_agents and len(roster) >= max_agents:
            break
        
        # Show progress every 10 agents or at key milestones
        if idx % 10 == 0 or idx == total_to_instantiate - 1:
            print(f"   {progress_bar(idx, total_to_instantiate, width=30)}")
            
        result = instantiate_agent(agent_data, project_root)
        if result:
            roster.append(result)
        else:
            instantiation_errors += 1
    
    # Final status
    if instantiation_errors > 0:
        log_status('warning', f'Instantiated {Colors.BRIGHT_GREEN}{len(roster)}{Colors.RESET} agents ({Colors.BRIGHT_RED}{instantiation_errors} failed{Colors.RESET})', source='ROSTER')
    else:
        log_status('success', f'Instantiated {Colors.BRIGHT_GREEN}{len(roster)}{Colors.RESET} agents (0 failed)', source='ROSTER')
    
    # Log layer distribution with colors
    layer_counts = {}
    for agent_data in sorted_agents[:len(roster)]:
        layer = agent_data.get('layer', 'Unknown')
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    # Format layer distribution with colors
    layer_str = ', '.join(f"{Colors.BRIGHT_CYAN}{k}{Colors.RESET}: {v}" for k, v in sorted(layer_counts.items()))
    log_status('info', f'Layer distribution: {{{layer_str}}}', source='ROSTER')
    Logger.info(f"[ROSTER] Layer distribution: {layer_counts}")
    
    return roster


def get_roster_summary(roster: List[Tuple[str, Any]]) -> Dict[str, Any]:
    """Get summary statistics for a roster."""
    summary = {
        "total_agents": len(roster),
        "agents_by_layer": {},
        "agent_names": [name for name, _ in roster],
    }
    
    # This would require keeping track of layer info during instantiation
    # For now, just return basic info
    return summary


# Convenience function for canon_validator
def get_healing_roster(project_root: Path) -> List[Tuple[str, Any]]:
    """
    Get the healing roster for the Canon Validator.
    
    This is the main entry point for the orchestration system.
    """
    return build_healing_roster(
        project_root,
        include_apps=True,
        include_utils=True,
        max_agents=None
    )


if __name__ == "__main__":
    # Test the roster builder
    import sys
    
    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"Project root: {project_root}")
    
    roster = build_healing_roster(project_root)
    
    print(f"\n{'='*60}")
    print(f"HEALING ROSTER: {len(roster)} agents")
    print(f"{'='*60}")
    
    for i, (name, instance) in enumerate(roster, 1):
        print(f"  {i:3d}. {name}")
    
    print(f"{'='*60}")
