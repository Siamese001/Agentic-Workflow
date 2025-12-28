#!/usr/bin/env python3
"""
AgentRegistryValidatorAgent - L3 Orchestration Framework Agent
Validates that all required agents in CANON_AGENT_REGISTRY exist and are properly configured.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

logger = logging.getLogger(__name__)


class AgentRegistryValidatorAgent:
    """
    L3 Orchestration: Agent Registry Validation
    Ensures all agents defined in CANON_AGENT_REGISTRY are present and functional.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize the AgentRegistryValidatorAgent.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path.cwd()
        self.missing_agents = []
        self.found_agents = []
        
    logger.info("[L6_AUDIT] Action at line 30")
    def validate_agent_exists(self, agent_name: str, search_paths: List[str]) -> Tuple[bool, str]:
        logger.info("[L6_AUDIT] Action at line 32")
        """
        Validate that an agent exists in one of the search paths.
        
        Args:
            agent_name: Name of the agent class
            search_paths: List of module paths to search
            
        Returns:
            Tuple of (exists, location)
        """
        import importlib
        
        for module_path in search_paths:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, agent_name):
                    return True, module_path
            except (ImportError, AttributeError):
                continue
        
        logger.info("[L6_AUDIT] Action at line 53")
        return False, ""
     logger.info("[L6_AUDIT] Action at line 55")
    
    def validate_registry(self, registry: Dict[int, List[str]]) -> Dict[str, Any]:
        """
        Validate all agents in the registry.
        
        Args:
            registry: CANON_AGENT_REGISTRY dictionary
            
        Returns:
            Validation results
        """
        self.missing_agents = []
        self.found_agents = []
        
        logger.info("[L6_AUDIT] Action at line 70")
        for key, agent_names in registry.items():
            for agent_name in agent_names:
                # Generate search paths based on key
                search_paths = self._generate_search_paths(key, agent_name)
                exists, location = self.validate_agent_exists(agent_name, search_paths)
                
                if exists:
                    self.found_agents.append({
                        'name': agent_name,
                        'key': key,
                        'location': location
                    })
                else:
                    self.missing_agents.append({
                        'name': agent_name,
                        'key': key,
                        'searched': search_paths
                    })
        
        return {
            'total_agents': sum(len(agents) for agents in registry.values()),
            'found': len(self.found_agents),
            'missing': len(self.missing_agents),
            'found_agents': self.found_agents,
            'missing_agents': self.missing_agents
        }
    
    def _generate_search_paths(self, key: int, agent_name: str) -> List[str]:
        """
        Generate search paths for an agent based on its key.
        
        Args:
            key: Canon key number
            agent_name: Name of the agent
            
        Returns:
            List of module paths to search
        """
        import re

        # Convert CamelCase to snake_case
        def camel_to_snake(name):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        module_name = camel_to_snake(agent_name)
        
        # Map keys to layer directories
        layer_map = {
            12: ['agentic_core.L3_orchestration.P1_core', 'agentic_core.L3_orchestration.S3_vitality'],
            13: ['agentic_core.L4_state.P1_core', 'agentic_core.L4_state.S1_memory'],
            19: ['agentic_core.L5_safety.P1_core', 'agentic_core.L5_safety.validators']
        }
        
        base_paths = layer_map.get(key, ['agentic_core.runtime.shared'])
        return [f"{base}.{module_name}" for base in base_paths]
    
    def run_validation(self, registry: Dict[int, List[str]]) -> bool:
        """
        Run validation and return success status.
        
        Args:
            registry: CANON_AGENT_REGISTRY dictionary
            
        Returns:
            True if all agents found, False otherwise
        """
        results = self.validate_registry(registry)
        
        if results['missing'] > 0:
            logger.warning(f"Missing {results['missing']} agents from registry")
            for agent in self.missing_agents:
                logger.warning(f"  - {agent['name']} (Key {agent['key']})")
            return False
        
        logger.info(f"All {results['found']} agents validated successfully")
        return True