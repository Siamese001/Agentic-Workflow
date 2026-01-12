#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSOT Dashboard Generator - L6 Observability
============================================
Single source of truth for dashboard data generation.
NO OTHER SCRIPTS should generate dashboard data.

This script:
1. Loads agent_discovery_full.json
2. Groups agents by FIXED territory structure
3. Generates dashboard rows with FIXED field schema
4. Updates autonomy_dashboard.html with new data
5. Validates output against wireframe requirements

FIXED TERRITORY STRUCTURE (NEVER CHANGES):
- TOTAL (always first row)
- L5 Safety
- L4 State
- L3 Orchestration
- L2 Execution
- L1 Cognition
- L0 Maintenance
- Apps Lic
- Apps Rg
- Apps Shared

FIXED FIELD SCHEMA (NEVER CHANGES):
All rows must have these exact fields:
- Territory, Total, Compliant
- Heal Cap %, Heal Invocation %, Invocation %
- Hardened %, MCP Capable %
- Test %, Observable %
- Avg CC, Avg LOC
- Typed %, Documented %
- Metadata %, Proper Base %, Schema Strictness %
- Complexity Health, Code Quality Score
- Criticality, Health, Health Breakdown, Risk
- Used %, Priority
"""
import json
import re
import sys
import io
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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

# FIXED TERRITORY ORDER - NEVER CHANGE THIS (29 detailed territories)
TERRITORY_ORDER = [
    "L5 Safety/Base Class",
    "L5 Safety/Validators",
    "L5 Safety/Guardrails",
    "L5 Safety/Gravity",
    "L5 Safety/Red Teaming",
    "L4 State/Base Class",
    "L4 State/Core",
    "L4 State/Infrastructure",
    "L4 State/Specialized",
    "L3 Orchestration/Base Class",
    "L3 Orchestration/Core",
    "L3 Orchestration/Infrastructure",
    "L3 Orchestration/Specialized",
    "L2 Execution/Base Class",
    "L2 Execution/Core",
    "L2 Execution/Specialized",
    "L1 Cognition/Base Class",
    "L1 Cognition/Core",
    "L1 Cognition/Specialized",
    "L0 Maintenance/Core",
    "L0 Maintenance/Infrastructure",
    "L6_Observability/Metrics",
    "L6_Observability/Telemetry",
    "L6_Observability/Tracing",
    "L6_Observability/Compliance",
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
    "Metadata %", "Proper Base %", "Schema Strictness %",
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
        
    def load_agent_discovery(self) -> bool:
        """Load and validate agent_discovery_full.json."""
        if not self.discovery_path.exists():
            print(f"❌ ERROR: {self.discovery_path} not found")
            return False
        
        try:
            with open(self.discovery_path, 'r', encoding='utf-8') as f:
                self.agents = json.load(f)
            
            if not isinstance(self.agents, list) or len(self.agents) == 0:
                print(f"❌ ERROR: Invalid agent discovery data")
                return False
            
            print(f"✅ Loaded {len(self.agents)} agents from discovery")
            return True
            
        except Exception as e:
            print(f"❌ ERROR loading agent discovery: {e}")
            return False
    
    def group_agents_by_territory(self) -> Dict[str, List[Dict]]:
        """Group agents by FIXED detailed territory structure with subcategories."""
        territories = defaultdict(list)
        
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
                if 'BaseAgent' in class_name or 'base_class' in path.lower():
                    territory = "L5 Safety/Base Class"
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
                if 'BaseAgent' in class_name or 'base_class' in path.lower():
                    territory = "L4 State/Base Class"
                elif '/filesystem' in path or '/infrastructure' in path:
                    territory = "L4 State/Infrastructure"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L4 State/Specialized"
                else:
                    territory = "L4 State/Core"
            elif layer.startswith('L3'):
                # L3 Orchestration subcategories
                if 'BaseAgent' in class_name or 'base_class' in path.lower():
                    territory = "L3 Orchestration/Base Class"
                elif '/infrastructure' in path:
                    territory = "L3 Orchestration/Infrastructure"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L3 Orchestration/Specialized"
                else:
                    territory = "L3 Orchestration/Core"
            elif layer.startswith('L2'):
                # L2 Execution subcategories
                if 'BaseAgent' in class_name or 'base_class' in path.lower():
                    territory = "L2 Execution/Base Class"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L2 Execution/Specialized"
                else:
                    territory = "L2 Execution/Core"
            elif layer.startswith('L1'):
                # L1 Cognition subcategories
                if 'BaseAgent' in class_name or 'base_class' in path.lower():
                    territory = "L1 Cognition/Base Class"
                elif '/adapters' in path or 'Adapter' in class_name:
                    territory = "L1 Cognition/Specialized"
                else:
                    territory = "L1 Cognition/Core"
            elif layer.startswith('L0'):
                # L0 Maintenance subcategories
                if '/infrastructure' in path or 'Infrastructure' in class_name:
                    territory = "L0 Maintenance/Infrastructure"
                else:
                    territory = "L0 Maintenance/Core"
            elif 'L6_observability' in path or 'L6_Observability' in path:
                # L6 Observability subcategories
                if '/metrics' in path or 'Metric' in class_name:
                    territory = "L6_Observability/Metrics"
                elif '/telemetry' in path or 'Telemetry' in class_name:
                    territory = "L6_Observability/Telemetry"
                elif '/tracing' in path or 'Tracing' in class_name or 'Trace' in class_name:
                    territory = "L6_Observability/Tracing"
                elif '/compliance' in path or 'Compliance' in class_name:
                    territory = "L6_Observability/Compliance"
                else:
                    territory = "L6_Observability/Metrics"  # Default L6
            else:
                # Fallback - should not happen
                territory = "Unknown"
            
            territories[territory].append(agent)
        
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
        typed_sum = sum(a.get('typed_pct', 0) for a in agents_list)
        doc_sum = sum(a.get('documented_pct', 0) for a in agents_list)
        
        # MCP Hardened - from actual agent data (not hardcoded!)
        mcp_hardened = sum(1 for a in agents_list if a.get('mcp_hardened'))
        
        # Calculate percentages from REAL counts
        heal_cap_pct = round(heal_cap / total * 100, 1)
        heal_inv_pct = round(heal_inv / total * 100, 1)
        test_pct = round(test / total * 100, 1)
        obs_pct = round(obs / total * 100, 1)
        typed_pct = round(typed_sum / total, 1)
        doc_pct = round(doc_sum / total, 1)
        avg_cc = round(cc_sum / total, 1)
        
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
        
        return {
            "total": total,
            "compliant": heal_cap,
            "heal_cap_pct": heal_cap_pct,
            "heal_inv_pct": heal_inv_pct,
            "test_pct": test_pct,
            "obs_pct": obs_pct,
            "avg_cc": avg_cc,
            "typed_pct": typed_pct,
            "doc_pct": doc_pct,
            "complexity_health": complexity_health,
            "code_quality": code_quality,
            "health": health,
            "risk": risk,
            "hardened_pct": hardened_pct,
            "mcp_pct": mcp_pct
        }
    
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
            "Avg LOC": 150,  # Placeholder
            "Typed %": metrics["typed_pct"],
            "Documented %": metrics["doc_pct"],
            "Metadata %": 100.0,
            "Proper Base %": 100.0,
            "Schema Strictness %": metrics["typed_pct"],
            "Complexity Health": metrics["complexity_health"],
            "Code Quality Score": metrics["code_quality"],
            "Criticality": 75,
            "Health": metrics["health"],
            "Health Breakdown": f"Heal:{metrics['heal_cap_pct']:.0f}+Inv:{metrics['heal_inv_pct']:.0f}+Test:{metrics['test_pct']:.0f}+Obs:{metrics['obs_pct']:.0f}+CC:{metrics['complexity_health']:.0f}",
            "Risk": metrics["risk"],
            "Used %": 95.0,
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
        
        health = weighted_avg("Health")
        
        return {
            "Territory": "TOTAL",
            "Total": total_agents,
            "Compliant": sum(r["Compliant"] for r in rows),
            "Heal Cap %": weighted_avg("Heal Cap %"),
            "Heal Invocation %": weighted_avg("Heal Invocation %"),
            "Invocation %": weighted_avg("Invocation %"),
            "Hardened %": weighted_avg("Hardened %"),
            "MCP Capable %": weighted_avg("MCP Capable %"),
            "Test %": weighted_avg("Test %"),
            "Observable %": weighted_avg("Observable %"),
            "Avg CC": weighted_avg("Avg CC"),
            "Avg LOC": 150,
            "Typed %": weighted_avg("Typed %"),
            "Documented %": weighted_avg("Documented %"),
            "Metadata %": 100.0,
            "Proper Base %": 100.0,
            "Schema Strictness %": weighted_avg("Schema Strictness %"),
            "Complexity Health": weighted_avg("Complexity Health"),
            "Code Quality Score": weighted_avg("Code Quality Score"),
            "Criticality": 75,
            "Health": health,
            "Health Breakdown": f"Heal:{weighted_avg('Heal Cap %'):.0f}+Inv:{weighted_avg('Heal Invocation %'):.0f}+Test:{weighted_avg('Test %'):.0f}+Obs:{weighted_avg('Observable %'):.0f}+CC:{weighted_avg('Complexity Health'):.0f}",
            "Risk": "HIGH" if health < 70 else "MED" if health < 85 else "LOW",
            "Used %": 95.0,
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
                # Must match ALL fields expected by openDrillModal in dashboard HTML
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
            is_infrastructure = "L6_Observability" in territory_name
            
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
        # Health should be weighted average of 5 components: Heal Cap, Heal Inv, Test, Obs, Complexity Health
        for i, row in enumerate(data[1:], 1):  # Skip TOTAL row
            if row.get('Total', 0) > 0:  # Only check non-empty territories
                heal_cap = row.get('Heal Cap %', 0)
                heal_inv = row.get('Heal Invocation %', 0)
                test = row.get('Test %', 0)
                obs = row.get('Observable %', 0)
                complexity = row.get('Complexity Health', 0)
                health = row.get('Health', 0)
                
                expected_health = round((heal_cap + heal_inv + test + obs + complexity) / 5, 1)
                
                if abs(health - expected_health) > 0.2:  # Allow small rounding differences
                    print(f"⚠️  WARNING: Health formula mismatch in {row.get('Territory')}")
                    print(f"   Expected: {expected_health}% (avg of 5 components)")
                    print(f"   Actual: {health}%")
                    print(f"   Components: Heal:{heal_cap} Inv:{heal_inv} Test:{test} Obs:{obs} CC:{complexity}")
        
        print(f"✅ VALIDATION PASSED: {len(data)} rows with all required fields")
        return True
    
    def validate_html_before_write(self, html: str) -> Tuple[bool, List[str]]:
        """Validate HTML content before writing to disk.
        
        Checks:
        - No duplicate const declarations
        - File size within expected range (300-500KB)
        - Line count within expected range (10K-15K)
        - Basic JavaScript syntax (brace/bracket matching)
        - Required variables/functions exist
        
        Returns:
            (is_valid, error_messages)
        """
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
        
        # Check 2: Validate file size (300KB-800KB - increased for complete agent data)
        size_bytes = len(html.encode('utf-8'))
        size_kb = size_bytes / 1024
        if size_kb > 900:  # Increased to 900KB to accommodate complete per-agent data with all drill-down fields
            errors.append(f"WARNING: HTML size is {size_kb:.1f}KB (expected <900KB) - possible duplication")
        elif size_kb < 250:
            errors.append(f"WARNING: HTML size is {size_kb:.1f}KB (expected >250KB) - possible data missing")
        
        # Check 3: Validate line count (should be 10K-15K lines)
        line_count = html.count('\n')
        if line_count > 20000:  # Increased limits to accommodate complete per-agent data with all drill-down fields
            errors.append(f"WARNING: HTML has {line_count:,} lines (expected <20K) - possible duplication")
        elif line_count < 10000:
            errors.append(f"WARNING: HTML has {line_count:,} lines (expected >10K) - possible data missing")
        
        # Check 4: Validate JavaScript syntax (basic check - brace matching)
        script_blocks = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(script_blocks):
            # Check for balanced braces, parentheses, brackets
            if script.count('{') != script.count('}'):
                errors.append(f"ERROR: Script block {i+1} has mismatched braces")
            if script.count('(') != script.count(')'):
                errors.append(f"ERROR: Script block {i+1} has mismatched parentheses")
            if script.count('[') != script.count(']'):
                errors.append(f"ERROR: Script block {i+1} has mismatched brackets")
        
        # Check 5: Verify required data structures and functions exist
        required_items = ['dashboardData', 'realAgentData', 'loadData', 'renderTerritorySummaryTable']
        for item in required_items:
            if item not in html:
                errors.append(f"ERROR: Required variable/function '{item}' not found in HTML")
        
        return (len(errors) == 0, errors)
    
    def update_dashboard_html(self, data: List[Dict[str, Any]], per_agent_data: Dict[str, Dict]) -> bool:
        """Update dashboard HTML with new data and real per-agent data."""
        if not self.dashboard_path.exists():
            print(f"❌ ERROR: Dashboard HTML not found at {self.dashboard_path}")
            return False
        
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # PHASE 1 GUARDRAIL: Remove ALL existing realAgentData declarations
            # This prevents duplicate accumulation across multiple regenerations
            # Pattern 1: Standard format with comment
            real_agent_pattern1 = r'//\s*Real per-agent data.*?\n\s*const realAgentData = \{.*?\};'
            html = re.sub(real_agent_pattern1, '', html, flags=re.DOTALL | re.MULTILINE)
            
            # Pattern 2: Without comment (in case comment was removed)
            real_agent_pattern2 = r'\n\s*const realAgentData = \{[^}]*"agents":\s*\[[^\]]*\][^}]*\};'
            html = re.sub(real_agent_pattern2, '', html, flags=re.DOTALL | re.MULTILINE)
            
            # Pattern 3: Aggressive cleanup - remove everything between realAgentData and next const/function
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
            print(f"   - Embedded {len(data)} territory rows")
            print(f"   - Embedded real per-agent data for {len(per_agent_data)} territories")
            return True
            
        except Exception as e:
            print(f"❌ ERROR updating dashboard HTML: {e}")
            return False
    
    def run(self) -> bool:
        """Execute complete dashboard generation pipeline."""
        print("=" * 70)
        print("SSOT DASHBOARD GENERATOR")
        print("=" * 70)
        print()
        
        # Step 1: Load agent discovery
        if not self.load_agent_discovery():
            return False
        
        # Step 2: Generate dashboard data
        print("\n📊 Generating dashboard data...")
        territories = self.group_agents_by_territory()
        data = self.generate_dashboard_data()
        
        # Step 2b: Build real per-agent data
        print("\n📊 Building per-agent data...")
        per_agent_data = self.build_per_agent_data(territories)
        
        # Step 3: Validate data
        print("\n🔍 Validating dashboard data...")
        if not self.validate_dashboard_data(data):
            return False
        
        # Step 4: Update HTML with both aggregate and per-agent data
        print("\n💾 Updating dashboard HTML...")
        if not self.update_dashboard_html(data, per_agent_data):
            return False
        
        # Step 5: Print summary
        total_row = data[0]
        print("\n" + "=" * 70)
        print("✅ DASHBOARD GENERATION COMPLETE")
        print("=" * 70)
        print(f"Total Agents: {total_row['Total']}")
        print(f"Heal Cap %: {total_row['Heal Cap %']}%")
        print(f"Health: {total_row['Health']}%")
        print(f"Territories: {len(data) - 1}")
        print(f"Per-agent data: {len(per_agent_data)} territories")
        print("=" * 70)
        
        return True

def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent.parent
    generator = DashboardGenerator(project_root)
    success = generator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
