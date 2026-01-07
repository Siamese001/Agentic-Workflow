"""
Sovereign Dashboard Loader
Loads agent data from the canonical agent_discovery_full.json SSOT.

VIOLATION JUSTIFICATION: Exclusive reliance on the 283-agent SSOT prevents
metric drift between the filesystem and the UI.
"""
import json
from pathlib import Path
import subprocess
import datetime
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Canonical SSOT files
CANONICAL_JSON = Path('agent_discovery_full.json')
MANIFEST_JSON = Path('agent_discovery_full.manifest.json')
SOVEREIGN_MANIFEST = Path('sovereign_state_final_v283.json')

# Configuration
MAX_STALE_HOURS = 24  # Force refresh if older
EXPECTED_AGENT_COUNT = 283  # Sovereign baseline - Phase B complete

def load_agents(refresh_if_stale: bool = True) -> List[Dict[str, Any]]:
    """
    Load agents from canonical SSOT.
    Optionally auto-refresh if stale or missing.
    
    Args:
        refresh_if_stale: If True, automatically refresh stale data
        
    Returns:
        List of agent dictionaries from the canonical registry
        
    Raises:
        RuntimeError: If canonical data is missing or invalid
    """
    # Check if canonical JSON exists
    if not CANONICAL_JSON.exists():
        logger.warning("Canonical JSON missing → running fresh discovery")
        _run_discovery(full=True)
    
    # Check if data is stale
    if refresh_if_stale and MANIFEST_JSON.exists():
        try:
            manifest = json.loads(MANIFEST_JSON.read_text(encoding='utf-8'))
            generated = datetime.datetime.fromisoformat(
                manifest['generated_at'].replace('Z', '+00:00')
            )
            age_hours = (datetime.datetime.now(datetime.timezone.utc) - generated).total_seconds() / 3600
            if age_hours > MAX_STALE_HOURS:
                logger.info(f"JSON stale ({age_hours:.1f}h old) → refreshing")
                _run_discovery(incremental=True)
        except Exception as e:
            logger.warning(f"Manifest error ({e}) → forcing incremental refresh")
            _run_discovery(incremental=True)
    
    # Load canonical data
    try:
        agents = json.loads(CANONICAL_JSON.read_text(encoding='utf-8'))
        agent_count = len(agents)
        
        # Validate against sovereign baseline
        if agent_count != EXPECTED_AGENT_COUNT:
            logger.error(
                f"SOVEREIGN BASELINE VIOLATION: Expected {EXPECTED_AGENT_COUNT} agents, "
                f"found {agent_count}. Registry integrity compromised."
            )
            raise RuntimeError(
                f"Agent count mismatch: expected {EXPECTED_AGENT_COUNT}, got {agent_count}. "
                f"Run full_agent_discovery.py to verify registry integrity."
            )
        
        logger.info(f"Dashboard: Loaded {agent_count} agents (canonical SSOT ✓)")
        return agents
        
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse canonical agent data: {e}. JSON may be corrupted.")
    except FileNotFoundError:
        raise RuntimeError(
            f"Canonical agent data not found at {CANONICAL_JSON}. "
            f"Run scripts/full_agent_discovery.py to generate."
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load canonical agent data: {e}")

def _run_discovery(full: bool = False, incremental: bool = False):
    """
    Run agent discovery script to refresh canonical data.
    
    Args:
        full: Run full discovery scan
        incremental: Run incremental discovery (faster)
    """
    cmd = ["python", "scripts/full_agent_discovery.py"]
    if incremental and not full:
        cmd.append("--incremental")
    
    try:
        logger.info(f"Running discovery: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Discovery completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Discovery failed: {e.stderr}")
        raise RuntimeError(f"Failed to run agent discovery: {e}")

def get_metrics_summary(agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary metrics from agent data.
    
    Args:
        agents: List of agent dictionaries
        
    Returns:
        Dictionary with summary metrics
    """
    total_agents = len(agents)
    
    if total_agents == 0:
        return {
            "total_agents": 0,
            "healing_percentage": 0,
            "testing_percentage": 0,
            "layer_distribution": {},
            "top_folders": {}
        }
    
    # Calculate metrics
    healing_count = sum(1 for a in agents if a.get('has_healing'))
    testing_count = sum(1 for a in agents if a.get('has_testing'))
    
    # Layer distribution
    layer_distribution = {}
    for agent in agents:
        layer = agent.get('layer', 'unknown')
        layer_distribution[layer] = layer_distribution.get(layer, 0) + 1
    
    # Top-level folder distribution
    folder_distribution = {}
    for agent in agents:
        folder = agent.get('top_level_folder', 'unknown')
        folder_distribution[folder] = folder_distribution.get(folder, 0) + 1
    
    return {
        "total_agents": total_agents,
        "healing_percentage": round(healing_count / total_agents * 100, 1),
        "testing_percentage": round(testing_count / total_agents * 100, 1),
        "layer_distribution": layer_distribution,
        "top_folders": folder_distribution,
        "baseline_status": "LOCKED" if total_agents == EXPECTED_AGENT_COUNT else "VIOLATION"
    }

def validate_sovereign_integrity() -> bool:
    """
    Validate that the canonical registry matches the sovereign baseline.
    
    Returns:
        True if integrity check passes, False otherwise
    """
    try:
        agents = load_agents(refresh_if_stale=False)
        return len(agents) == EXPECTED_AGENT_COUNT
    except Exception as e:
        logger.error(f"Integrity check failed: {e}")
        return False
