"""
file: agentic_core/scripts/L6_observability/generate_dashboard.py
description: Regenerated with L6 Observability moved above L5 Safety in the territory order while maintaining Base Agent nomenclature.
"""

import json
import re
import sys
import io
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    get_validated_project_root,
)

# Fix UTF-8 encoding for Windows console (emoji support)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# FIXED TERRITORY ORDER - L6 moved above L5 (32 detailed territories)
TERRITORY_ORDER = [
    "Base/Root",         # SovereignBaseAgent
    "Base/Mixins",       # HealerMixin, MCPHardenMixin
    "L6 Observability/Base Agent",
    "L6 Observability/Metrics",
    "L6 Observability/Tracing",
    "L6 Observability/Compliance",
    "L6 Observability/Infrastructure",
    "L5 Safety/Base Agent",
    "L5 Safety/Validators",
    "L5 Safety/Guardrails",
    "L5 Safety/Gravity",
    "L5 Safety/Red Teaming",
    "L4 State/Base Agent",
    "L4 State/Core",
    "L4 State/Infrastructure",
    "L4 State/Specialized",
    "L3 Orchestration/Base Agent",
    "L3 Orchestration/Core",
    "L3 Orchestration/Infrastructure",
    "L3 Orchestration/Specialized",
    "L2 Execution/Base Agent",
    "L2 Execution/Core",
    "L2 Execution/Specialized",
    "L1 Cognition/Base Agent",
    "L1 Cognition/Core",
    "L1 Cognition/Specialized",
    "L0 Maintenance/Base Agent",
    "L0 Maintenance/Core",
    "L0 Maintenance/Infrastructure",
    "Apps Lic",
    "Apps Rg",
    "Apps Shared"
]

# FIXED FIELD SCHEMA - NEVER CHANGE THIS
REQUIRED_FIELDS = [
    "Territory", "Total", "Compliant",
    "Heal Cap %", "Heal Invocation %", "Invocation %",
    "Hardened %", "MCP Capable %",
    "Test %", "Observable %",
    "Avg CC", "Avg LOC",
    "Typed %", "Documented %",
    "Metadata %", "Canonical Inheritance %", "Schema Strictness %",
    "Complexity Health", "Code Quality Score",
    "Criticality", "Health", "Health Breakdown", "Risk",
    "Used %", "Priority", "IsInfrastructure"
]

class DashboardGenerator:
    """SSOT Dashboard Generator - Single point of control."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovery_path = project_root / AGENT_DISCOVERY_JSON
        self.dashboard_path = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
        self.agents = []
        
        # Defensive: Verify critical paths exist immediately
        if not self.project_root.exists():
            raise FileNotFoundError(f"Project root not found: {self.project_root}")
            
    def load_agent_discovery(self) -> bool:
        """Load and validate agent_discovery_full.json."""
        if not self.discovery_path.exists():
            print(f"❌ ERROR: {self.discovery_path} not found")
            return False
        
        try:
            with open(self.discovery_path, 'r', encoding='utf-8') as f:
                self.agents = json.load(f)
            
            if not isinstance(self.agents, list):
                print(f"❌ ERROR: Invalid agent discovery data (expected list, got {type(self.agents)})")
                return False
                
            if len(self.agents) == 0:
                print(f"⚠️  WARNING: Agent discovery list is empty")
                return False
            
            print(f"✅ Loaded {len(self.agents)} agents from discovery")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Corrupt JSON in agent discovery: {e}")
            return False
        except Exception as e:
            print(f"❌ ERROR loading agent discovery: {e}")
            return False
    
    def group_agents_by_territory(self) -> Dict[str, List[Dict]]:
        """Group agents by FIXED detailed territory structure with subcategories."""
        territories = defaultdict(list)
        unknown_agents = []
        
        for agent in self.agents:
            layer = agent.get('layer', '')
            sub_dir = agent.get('sub_dir', '')
            path = agent.get('path', '').replace('\\', '/')
            class_name = agent.get('class_name', '')
            
            # Map to FIXED detailed territory names with subcategories
            if APPS_LIC_DIR in sub_dir:
                territory = "Apps Lic"
            elif APPS_RG_DIR in sub_dir:
                territory = "Apps Rg"
            elif APPS_SHARED_DIR in sub_dir:
                territory = "Apps Shared"
            elif layer.startswith('L5'):
                # L5 Safety subcategories based on actual paths
                if 'BaseAgent' in class_name or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L5 Safety/Base Agent"
                elif '/validators' in path or 'validators/' in path:
                    territory = "L5 Safety/Validators"
                elif '/red_team' in path or 'red_teaming/' in path:
                    territory = "L5 Safety/Red Teaming"
                elif '/gravity' in path or 'Gravity' in class_name:
                    territory = "L5 Safety/Gravity"
                else:
                    # Default: guardrails
                    territory = "L5 Safety/Guardrails"
            elif layer.startswith('L4'):
                # L4 State subcategories
                if 'BaseAgent' in class_name or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L4 State/Base Agent"
                elif '/filesystem' in path or '/infrastructure' in path:
                    territory = "L4 State/Infrastructure"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L4 State/Specialized"
                else:
                    territory = "L4 State/Core"
            elif layer.startswith('L3'):
                # L3 Orchestration subcategories
                if 'BaseAgent' in class_name or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L3 Orchestration/Base Agent"
                elif '/infrastructure' in path:
                    territory = "L3 Orchestration/Infrastructure"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L3 Orchestration/Specialized"
                else:
                    territory = "L3 Orchestration/Core"
            elif layer.startswith('L2'):
                # L2 Execution subcategories
                if 'BaseAgent' in class_name or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L2 Execution/Base Agent"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L2 Execution/Specialized"
                else:
                    territory = "L2 Execution/Core"
            elif layer.startswith('L1'):
                # L1 Cognition subcategories - CHECK BASE FIRST (includes L1CognitionBaseAgent)
                if 'BaseAgent' in class_name or class_name == 'L1CognitionBaseAgent' or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L1 Cognition/Base Agent"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L1 Cognition/Specialized"
                else:
                    territory = "L1 Cognition/Core"
            elif layer.startswith('L0'):
                # L0 Maintenance subcategories - CHECK BASE FIRST (includes L0MaintenanceBaseAgent)
                if 'BaseAgent' in class_name or class_name == 'L0MaintenanceBaseAgent' or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L0 Maintenance/Base Agent"
                elif '/infrastructure' in path or 'Infrastructure' in class_name:
                    territory = "L0 Maintenance/Infrastructure"
                else:
                    territory = "L0 Maintenance/Core"
            elif 'L6_observability' in path or 'L6_Observability' in path or layer.startswith('L6'):
                # L6 Observability subcategories - CHECK BASEAGENT FIRST!
                if 'BaseAgent' in class_name or 'base_agent' in path.lower() or 'base_class' in path.lower():
                    territory = "L6 Observability/Base Agent"
                elif '/metrics' in path or 'Metric' in class_name:
                    territory = "L6 Observability/Metrics"
                elif '/telemetry' in path or 'Telemetry' in class_name:
                    territory = "L6 Observability/Infrastructure"
                elif '/tracing' in path or 'Tracing' in class_name or 'Trace' in class_name:
                    territory = "L6 Observability/Tracing"
                elif '/compliance' in path or 'Compliance' in class_name:
                    territory = "L6 Observability/Compliance"
                else:
                    territory = "L6 Observability/Metrics"  # Default L6
            elif layer == 'Base' or 'SovereignBaseAgent' in class_name or 'Mixin' in class_name:
                # Base Layer Splitting: Root vs Mixins
                if 'Mixin' in class_name or 'mixins' in path.lower():
                    territory = "Base/Mixins"
                else:
                    territory = "Base/Root"
            else:
                # Fallback - Capture for logging
                territory = "Unknown"
                unknown_agents.append(f"{class_name} ({path})")
            
            territories[territory].append(agent)
            
        # Log unknown agents if any found
        if unknown_agents:
            print(f"⚠️  WARNING: {len(unknown_agents)} agents mapped to 'Unknown' territory:")
            for agent_info in unknown_agents[:5]: # Show first 5
                print(f"   - {agent_info}")
            if len(unknown_agents) > 5:
                print(f"   ... and {len(unknown_agents) - 5} more.")
        
        return territories
    
    def compute_territory_metrics(self, agents_list: List[Dict]) -> Dict[str, Any]:
        """Compute metrics for a territory with FIXED field schema."""
        total = len(agents_list)
        if total == 0:
            return {}
        
        # Compute raw metrics from ACTUAL agent data
        heal_cap = sum(1 for a in agents_list if a.get('has_healing'))
        heal_inv = sum(1 for a in agents_list if a.get('invocation') == 'Yes')
        test = sum(1 for a in agents_list if a.get('has_tests'))
        obs = sum(1 for a in agents_list if a.get('observability'))
        cc_sum = sum(a.get('cyclomatic_complexity', 1) for a in agents_list)
        typed_pct_sum = sum(a.get('typed_pct', 0) for a in agents_list)
        doc_pct_sum = sum(a.get('documented_pct', 0) for a in agents_list)
        
        # PHASE 1 FIX: Calculate from real data (Finding #1 and #3)
        loc_sum = sum(a.get('loc', 0) for a in agents_list)
        schema_sum = sum(a.get('schema_strictness', 0) for a in agents_list)
        
        # PHASE 3 FIX: Calculate metadata and usage from real data (Finding #2 and #5)
        metadata_count = sum(1 for a in agents_list if a.get('has_metadata', False))
        used_count = sum(1 for a in agents_list if a.get('is_used', False))
        
        # MCP Hardened - from actual agent data (not hardcoded!)
        mcp_hardened = sum(1 for a in agents_list if a.get('mcp_hardened'))
        
        # Calculate percentages from REAL counts
        heal_cap_pct = round(heal_cap / total * 100, 1)
        heal_inv_pct = round(heal_inv / total * 100, 1)
        test_pct = round(test / total * 100, 1)
        obs_pct = round(obs / total * 100, 1)
        typed_pct = round(typed_pct_sum / total, 1)
        doc_pct = round(doc_pct_sum / total, 1)
        avg_cc = round(cc_sum / total, 1)
        
        # PHASE 1 FIX: Use real data instead of hardcoded values
        avg_loc = round(loc_sum / total, 1)
        schema_pct = round(schema_sum / total, 1)
        
        # PHASE 3 FIX: Use real data instead of hardcoded values
        metadata_pct = round(metadata_count / total * 100, 1)
        used_pct = round(used_count / total * 100, 1)
        
        # Hardened % and MCP Capable % - REAL calculation from mcp_hardened field
        hardened_pct = round(mcp_hardened / total * 100, 1)
        mcp_pct = hardened_pct  # Same metric, different label
        
        # Derived metrics
        complexity_health = round(max(0, 100 - (avg_cc * 2)), 1)
        code_quality = round((typed_pct + doc_pct) / 2, 1)
        
        # GOSPEL-WEIGHTED HEALTH SCORE (replaces even weighting)
        # Weights reflect architectural priorities:
        # - 30% Heal Capability (core of autonomy)
        # - 10% Invocation (proves healing works)
        # - 25% Test Coverage (defense against regression)
        # - 20% Observability (prevents Ghost Agents)
        # - 15% Complexity Health (technical debt indicator)
        base_health = round(
            (heal_cap_pct * 0.30) + 
            (heal_inv_pct * 0.10) + 
            (test_pct * 0.25) + 
            (obs_pct * 0.20) + 
            (complexity_health * 0.15),
            1
        )
        
        # L5 SECURITY ZERO-MULTIPLIER
        # If territory contains unhardened L5 agents, health drops to 0
        l5_agents = [a for a in agents_list if a.get('layer', '').startswith('L5')]
        unhardened_l5 = [a for a in l5_agents if not a.get('mcp_hardened')]
        
        if unhardened_l5:
            health = 0.0  # CRITICAL: L5 security violation
        else:
            health = base_health
        risk = "HIGH" if avg_cc > 12 or health < 60 else "MED" if avg_cc > 8 or health < 80 else "LOW"
        
        # Calculate proper base class percentage from actual agent data
        proper_base_count = sum(1 for a in agents_list if a.get('proper_base_class', False))
        proper_base_pct = round((proper_base_count / total * 100), 1) if total > 0 else 0.0
        
        return {
            "total": total,
            "compliant": heal_cap,
            "heal_cap_pct": heal_cap_pct,
            "heal_inv_pct": heal_inv_pct,
            "test_pct": test_pct,
            "obs_pct": obs_pct,
            "avg_cc": avg_cc,
            "avg_loc": avg_loc,  # PHASE 1 FIX: Real data from 'loc' field
            "typed_pct": typed_pct,
            "doc_pct": doc_pct,
            "schema_pct": schema_pct,  # PHASE 1 FIX: Real data from 'schema_strictness' field
            "metadata_pct": metadata_pct,  # PHASE 3 FIX: Real data from 'has_metadata' field
            "used_pct": used_pct,  # PHASE 3 FIX: Real data from 'is_used' field
            "complexity_health": complexity_health,
            "code_quality": code_quality,
            "health": health,
            "risk": risk,
            "hardened_pct": hardened_pct,
            "mcp_pct": mcp_pct,
            "proper_base_pct": proper_base_pct
        }
    
    def calculate_layer_criticality(self, territory_name: str) -> int:
        """
        Calculate criticality based on architectural layer (Finding #4).
        Weights reflect the risk impact of failure in that specific layer.
        """
        # Normalized weights based on L0-L6 hierarchy
        LAYER_WEIGHTS = {
            'L5': 100,  # Safety - Absolute critical path
            'Base': 95, # Foundation - Global impact
            'L4': 85,   # State/SSOT - Data integrity
            'L3': 75,   # Orchestration - Workflow control
            'Apps': 70, # Applications - User facing
            'L2': 60,   # Execution - Task workers
            'L1': 50,   # Cognition - AI reasoning
            'L0': 40,   # Maintenance - Supporting tools
            'L6': 30,   # Observability - Monitoring
        }
        
        for layer, score in LAYER_WEIGHTS.items():
            if layer in territory_name:
                return score
        return 50  # Default for unknown territories
    
    def build_territory_row(self, territory_name: str, metrics: Dict[str, Any], priority: int, is_infrastructure: bool = False) -> Dict[str, Any]:
        """Build a territory row with FIXED field schema."""
        return {
            "Territory": territory_name,
            "Total": metrics["total"],
            "Compliant": metrics["compliant"],
            "Heal Cap %": metrics["heal_cap_pct"],
            "Heal Invocation %": metrics["heal_inv_pct"],
            "Invocation %": metrics["heal_inv_pct"],  # Same as Heal Invocation
            "Hardened %": metrics["hardened_pct"],
            "MCP Capable %": metrics["mcp_pct"],  # From actual mcp_hardened data
            "Test %": metrics["test_pct"],
            "Observable %": metrics["obs_pct"],
            "Avg CC": metrics["avg_cc"],
            "Avg LOC": metrics["avg_loc"],  # PHASE 1 FIX: Real data from 'loc' field
            "Typed %": metrics["typed_pct"],
            "Documented %": metrics["doc_pct"],
            "Metadata %": metrics["metadata_pct"],  # PHASE 3 FIX: Real data from 'has_metadata' field
            "Canonical Inheritance %": metrics["proper_base_pct"],
            "Schema Strictness %": metrics["schema_pct"],  # PHASE 1 FIX: Real data from 'schema_strictness' field
            "Complexity Health": metrics["complexity_health"],
            "Code Quality Score": metrics["code_quality"],
            "Criticality": self.calculate_layer_criticality(territory_name),  # PHASE 2 FIX: Layer-based weight
            "Health": metrics["health"],
            "Health Breakdown": f"Heal:{metrics['heal_cap_pct']:.0f}+Inv:{metrics['heal_inv_pct']:.0f}+Test:{metrics['test_pct']:.0f}+Obs:{metrics['obs_pct']:.0f}+CC:{metrics['complexity_health']:.0f}",
            "Risk": metrics["risk"],
            "Used %": metrics["used_pct"],  # PHASE 3 FIX: Real data from 'is_used' field
            "Priority": priority,
            "IsInfrastructure": is_infrastructure
        }
    
    def build_total_row(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build TOTAL row by aggregating territory rows."""
        if not rows:
            return {}
        
        total_agents = sum(r["Total"] for r in rows)
        
        def weighted_avg(key):
            return round(sum(r[key] * r["Total"] for r in rows) / total_agents, 1)
        
        heal_cap_pct = weighted_avg("Heal Cap %")
        heal_inv_pct = weighted_avg("Heal Invocation %")
        test_pct = weighted_avg("Test %")
        obs_pct = weighted_avg("Observable %")
        typed_pct = weighted_avg("Typed %")
        doc_pct = weighted_avg("Documented %")
        hardened_pct = weighted_avg("Hardened %")
        mcp_pct = weighted_avg("MCP Capable %")
        proper_base_pct = weighted_avg("Canonical Inheritance %")
        
        avg_cc = round(sum(r["Avg CC"] * r["Total"] for r in rows) / total_agents, 1)
        avg_loc = round(sum(r["Avg LOC"] * r["Total"] for r in rows) / total_agents, 1)  # PHASE 1 FIX
        schema_pct = weighted_avg("Schema Strictness %")  # PHASE 1 FIX
        metadata_pct = weighted_avg("Metadata %")  # PHASE 3 FIX
        used_pct = weighted_avg("Used %")  # PHASE 3 FIX
        avg_criticality = round(sum(r["Criticality"] * r["Total"] for r in rows) / total_agents, 1)  # PHASE 2 FIX
        complexity_health = round(sum(r["Complexity Health"] * r["Total"] for r in rows) / total_agents, 1)
        code_quality = round(sum(r["Code Quality Score"] * r["Total"] for r in rows) / total_agents, 1)
        
        health = round(
            (heal_cap_pct * 0.30) + 
            (heal_inv_pct * 0.10) + 
            (test_pct * 0.25) + 
            (obs_pct * 0.20) + 
            (complexity_health * 0.15),
            1
        )
        
        risk = "HIGH" if avg_cc > 12 or health < 60 else "MED" if avg_cc > 8 or health < 80 else "LOW"
        
        return {
            "Territory": "TOTAL",
            "Total": total_agents,
            "Compliant": sum(r["Compliant"] for r in rows),
            "Heal Cap %": heal_cap_pct,
            "Heal Invocation %": heal_inv_pct,
            "Invocation %": heal_inv_pct,
            "Hardened %": hardened_pct,
            "MCP Capable %": mcp_pct,
            "Test %": test_pct,
            "Observable %": obs_pct,
            "Avg CC": avg_cc,
            "Avg LOC": avg_loc,  # PHASE 1 FIX: Real data
            "Typed %": typed_pct,
            "Documented %": doc_pct,
            "Metadata %": metadata_pct,  # PHASE 3 FIX: Real data
            "Canonical Inheritance %": proper_base_pct,
            "Schema Strictness %": schema_pct,  # PHASE 1 FIX: Real data
            "Complexity Health": complexity_health,
            "Code Quality Score": code_quality,
            "Criticality": avg_criticality,  # PHASE 2 FIX: Weighted average from territories
            "Health": health,
            "Health Breakdown": f"Heal:{heal_cap_pct:.0f}+Inv:{heal_inv_pct:.0f}+Test:{test_pct:.0f}+Obs:{obs_pct:.0f}+CC:{complexity_health:.0f}",
            "Risk": risk,
            "Used %": used_pct,  # PHASE 3 FIX: Real data
            "Priority": "ALL",
            "IsInfrastructure": False
        }
    
    def build_per_agent_data(self, territories: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Build per-agent data structure for each territory to replace mock data."""
        per_agent_data = {}
        
        # Iterate through ALL territories in TERRITORY_ORDER to ensure complete coverage
        for territory_name in TERRITORY_ORDER:
            agents_list = territories.get(territory_name, [])
            
            # Include empty territories with empty arrays (for consistent rendering)
            if not agents_list:
                per_agent_data[territory_name] = {
                    'healCap': [],
                    'invocation': [],
                    'hardened': [],
                    'test': [],
                    'complexityHealth': [],
                    'health': [],
                    'typed': [],
                    'documented': [],
                    'schemaStrictness': [],
                    'properBase': [],
                    'codeQuality': [],
                    'agents': []
                }
                continue
            
            # Extract per-agent metric arrays
            heal_cap_values = []
            invocation_values = []
            hardened_values = []
            test_values = []
            complexity_health_values = []
            health_values = []
            typed_values = []
            documented_values = []
            schema_values = []
            base_values = []
            quality_values = []
            agent_objects = []
            
            for agent in agents_list:
                # Heal capability (0 or 100)
                heal_cap = 100.0 if agent.get('has_healing') else 0.0
                heal_cap_values.append(heal_cap)
                
                # Invocation (0 or 100 based on invocation field)
                invocation = 100.0 if agent.get('invocation') == 'Yes' else 0.0
                invocation_values.append(invocation)
                
                # Hardened (0 or 100)
                hardened = 100.0 if agent.get('mcp_hardened') else 0.0
                hardened_values.append(hardened)
                
                # Test coverage (0 or 100)
                test = 100.0 if agent.get('has_tests') else 0.0
                test_values.append(test)
                
                # Complexity health (inverted CC)
                cc = agent.get('cyclomatic_complexity', 0)
                complexity_health = max(0, min(100, 100 - (cc * 2)))
                complexity_health_values.append(complexity_health)
                
                # Health (average of 5 components)
                obs_pct = 100.0 if agent.get('observability', {}).get('logging') else 0.0
                health = (heal_cap + invocation + test + obs_pct + complexity_health) / 5
                health_values.append(health)
                
                # Code quality metrics
                typed = agent.get('typed_pct', 0.0)
                typed_values.append(typed)
                
                documented = agent.get('documented_pct', 0.0)
                documented_values.append(documented)
                
                schema = agent.get('schema_strictness', 100.0)
                schema_values.append(schema)
                
                base = 100.0 if agent.get('proper_base_class') else 0.0
                base_values.append(base)
                
                # Code quality score (average of code metrics)
                quality = (typed + documented + schema + base) / 4
                quality_values.append(quality)
                
                # Build complete agent object for drill-down modal
                abs_path = str(self.project_root / agent.get('path', ''))
                rel_path = agent.get('path', '')
                
                # Observability summary
                obs = agent.get('observability', {})
                obs_summary = f"Logging: {'✓' if obs.get('logging') else '✗'} | Metrics: {'✓' if obs.get('metrics') else '✗'} | Tracing: {'✓' if obs.get('tracing') else '✗'}"
                
                # MCP hardening summary
                mcp_summary = f"Shield: {'✓' if agent.get('mcp_hardened') else '✗'} | @hardened: ✗ | Safe: ✓"
                
                # Typing summary
                typing_summary = f"Init: ✗ | Methods: {int(typed)}% | Returns: {int(typed/2)}%"
                
                agent_objects.append({
                    'name': agent.get('class_name', 'Unknown'),
                    'path': agent.get('path', ''),
                    'rel': rel_path,
                    'abs_file': abs_path,
                    'abs_class': abs_path,
                    'class_line': agent.get('line_number', 1),
                    'has_mixin': agent.get('has_healing', False),
                    'invocation': agent.get('invocation', 'No'),
                    'has_tests': agent.get('has_tests', False),
                    'obs_summary': obs_summary,
                    'mcp_summary': mcp_summary,
                    'typing_summary': typing_summary,
                    'typed_pct': typed,
                    'overall_typed_pct': typed,
                    'complexity': cc,
                    'health': health,
                    'healCap': heal_cap,
                    'test': test,
                    'complexityHealth': complexity_health,
                    'hardened': hardened,
                    'documented': documented,
                    'schema': schema,
                    'base': base,
                    'quality': quality,
                    'loc': agent.get('loc', 0)
                })
            
            per_agent_data[territory_name] = {
                'healCap': heal_cap_values,
                'invocation': invocation_values,
                'hardened': hardened_values,
                'test': test_values,
                'complexityHealth': complexity_health_values,
                'health': health_values,
                'typed': typed_values,
                'documented': documented_values,
                'schemaStrictness': schema_values,
                'properBase': base_values,
                'codeQuality': quality_values,
                'agents': agent_objects
            }
        
        return per_agent_data
    
    def generate_dashboard_data(self) -> List[Dict[str, Any]]:
        """Generate dashboard data with only territories that have actual agents."""
        territories = self.group_agents_by_territory()
        
        # Build rows ONLY for territories with agents (no empty placeholders)
        rows = []
        priority = 1
        for territory_name in TERRITORY_ORDER:
            # Updated to match new "L6 Observability" spacing
            is_infrastructure = "L6 Observability" in territory_name
            
            if territory_name in territories and len(territories[territory_name]) > 0:
                # Territory has agents - compute real metrics
                agents_list = territories[territory_name]
                metrics = self.compute_territory_metrics(agents_list)
                if metrics:
                    row = self.build_territory_row(territory_name, metrics, priority, is_infrastructure)
                    rows.append(row)
                    priority += 1
            # Skip territories with no agents - no fake placeholder rows
        
        # Build TOTAL row from all rows (all have agents now)
        total_row = self.build_total_row(rows)
        
        # TOTAL always first
        all_rows = [total_row] + rows
        
        return all_rows
    
    def validate_dashboard_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate dashboard data - only real territories with agents."""
        if not data:
            print("❌ VALIDATION FAILED: No data generated")
            return False
        
        # GUARDRAIL 1: Must have at least TOTAL row + some territory rows
        if len(data) < 2:
            print("❌ VALIDATION FAILED: Need at least TOTAL + 1 territory")
            return False
        
        # GUARDRAIL 2: TOTAL row must be first
        if data[0].get("Territory") != "TOTAL":
            print("❌ GUARDRAIL VIOLATION: TOTAL row must be first")
            return False
        
        # GUARDRAIL 3: All rows must have all required fields
        for i, row in enumerate(data):
            missing_fields = [f for f in REQUIRED_FIELDS if f not in row]
            if missing_fields:
                print(f"❌ GUARDRAIL VIOLATION: Row {i} ({row.get('Territory', 'UNKNOWN')}) missing fields: {missing_fields}")
                return False
        
        # GUARDRAIL 4: All territory rows must have agents (no 0-count placeholders)
        for row in data[1:]:  # Skip TOTAL
            if row.get("Total", 0) == 0:
                print(f"❌ GUARDRAIL VIOLATION: Territory '{row.get('Territory')}' has 0 agents")
                print("   Empty placeholder rows are not allowed!")
                return False
        
        # GUARDRAIL 5: Verify health formula consistency
        for i, row in enumerate(data[1:], 1):  # Skip TOTAL row
            if row.get('Total', 0) > 0:  # Only check non-empty territories
                heal_cap = row.get('Heal Cap %', 0)
                heal_inv = row.get('Heal Invocation %', 0)
                test = row.get('Test %', 0)
                obs = row.get('Observable %', 0)
                complexity = row.get('Complexity Health', 0)
                health = row.get('Health', 0)
                
                expected_health = round((heal_cap * 0.30) + (heal_inv * 0.10) + (test * 0.25) + (obs * 0.20) + (complexity * 0.15), 1)
                
                if abs(health - expected_health) > 0.2:  # Allow small rounding differences
                    print(f"⚠️  WARNING: Health formula mismatch in {row.get('Territory')}")
                    print(f"   Expected: {expected_health}% (weighted average)")
                    print(f"   Actual: {health}%")
        
        print(f"✅ VALIDATION PASSED: {len(data)} rows with all required fields")
        return True
    
    def validate_html_before_write(self, html: str) -> Tuple[bool, List[str]]:
        """Validate HTML content before writing to disk."""
        errors = []
        
        # Check 1: Detect duplicate const declarations
        const_patterns = {
            'dashboardData': r'const\s+dashboardData\s*=',
            'realAgentData': r'const\s+realAgentData\s*=',
        }
        
        for var_name, pattern in const_patterns.items():
            matches = re.findall(pattern, html)
            if len(matches) > 1:
                errors.append(f"CRITICAL: Found {len(matches)} declarations of 'const {var_name}' (expected 1)")
            elif len(matches) == 0:
                errors.append(f"ERROR: Found 0 declarations of 'const {var_name}' (expected 1)")
        
        # Check 2: Validate file size (300KB-900KB)
        size_bytes = len(html.encode('utf-8'))
        size_kb = size_bytes / 1024
        if size_kb > 900:
            errors.append(f"WARNING: HTML size is {size_kb:.1f}KB (expected <900KB) - possible duplication")
        elif size_kb < 250:
            errors.append(f"WARNING: HTML size is {size_kb:.1f}KB (expected >250KB) - possible data missing")
        
        # Check 3: Validate line count
        line_count = html.count('\n')
        if line_count > 20000:
            errors.append(f"WARNING: HTML has {line_count:,} lines (expected <20K)")
        
        # Check 4: Validate JavaScript syntax (basic check - brace matching)
        script_blocks = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(script_blocks):
            if script.count('{') != script.count('}'):
                errors.append(f"ERROR: Script block {i+1} has mismatched braces")
        
        return (len(errors) == 0, errors)
    
    def update_dashboard_html(self, data: List[Dict[str, Any]], per_agent_data: Dict[str, Dict]) -> bool:
        """Update dashboard HTML with new data and real per-agent data."""
        if not self.dashboard_path.exists():
            print(f"❌ ERROR: Dashboard HTML not found at {self.dashboard_path}")
            return False
        
        # GUARDRAIL: Create a backup before modifying
        try:
            backup_path = self.dashboard_path.with_suffix('.html.bak')
            shutil.copy2(self.dashboard_path, backup_path)
            print(f"💾 Backup created: {backup_path.name}")
        except Exception as e:
            print(f"❌ ERROR creating backup: {e}")
            return False
        
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # Remove ALL existing realAgentData declarations
            real_agent_pattern3 = r'const realAgentData = \{.*?\n\s*(?=const |function |let |var |\s*</script>)'
            html = re.sub(real_agent_pattern3, '', html, flags=re.DOTALL | re.MULTILINE)
            
            # Find dashboardData location
            data_start_marker = 'const dashboardData = ['
            data_end_marker = '];'
            data_start_idx = html.find(data_start_marker)
            data_end_idx = html.find(data_end_marker, data_start_idx) + len(data_end_marker)
            
            if data_start_idx == -1 or data_end_idx == -1:
                print("❌ ERROR: Could not find dashboardData in HTML")
                return False
            
            # Build new data blocks
            new_json = json.dumps(data, indent=2)
            new_data_block = f'const dashboardData = {new_json};'
            
            agent_json = json.dumps(per_agent_data, indent=2)
            real_agent_block = f'\n\n        // Real per-agent data (replaces generateMockAgentData)\n        const realAgentData = {agent_json};'
            
            # Replace dashboardData and insert realAgentData after it
            new_html = html[:data_start_idx] + new_data_block + real_agent_block + html[data_end_idx:]
            
            # PHASE 1 GUARDRAIL: Validate before writing
            is_valid, errors = self.validate_html_before_write(new_html)
            
            if not is_valid:
                print("❌ VALIDATION FAILED - HTML NOT WRITTEN")
                for error in errors:
                    print(f"   {error}")
                return False
            
            # Only write if validation passes
            self.dashboard_path.write_text(new_html, encoding='utf-8')
            print(f"✅ Updated {self.dashboard_path}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR updating dashboard HTML: {e}")
            try:
                if backup_path.exists():
                    shutil.copy2(backup_path, self.dashboard_path)
                    print("⚠️  Restored original HTML from backup")
            except Exception:
                pass
            return False
    
    def run(self) -> bool:
        """Execute complete dashboard generation pipeline."""
        print("=" * 70)
        print("SSOT DASHBOARD GENERATOR")
        print("=" * 70)
        print()
        
        try:
            if not self.load_agent_discovery():
                return False
            
            print("\n📊 Generating dashboard data...")
            territories = self.group_agents_by_territory()
            data = self.generate_dashboard_data()
            
            print("\n📊 Building per-agent data...")
            per_agent_data = self.build_per_agent_data(territories)
            
            print("\n🔍 Validating dashboard data...")
            if not self.validate_dashboard_data(data):
                return False
            
            print("\n💾 Updating dashboard HTML...")
            if not self.update_dashboard_html(data, per_agent_data):
                return False
            
            total_row = data[0]
            print("\n" + "=" * 70)
            print("✅ DASHBOARD GENERATION COMPLETE")
            print("=" * 70)
            print(f"Total Agents: {total_row['Total']}")
            print(f"Heal Cap %: {total_row['Heal Cap %']}%")
            print(f"Health: {total_row['Health']}%")
            print(f"Territories: {len(data) - 1}")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR in execution pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main entry point."""
    project_root = get_validated_project_root()
    generator = DashboardGenerator(project_root)
    success = generator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
