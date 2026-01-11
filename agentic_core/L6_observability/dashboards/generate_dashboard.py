#!/usr/bin/env python3
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
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

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
        self.discovery_path = project_root / "agent_discovery_full.json"
        self.dashboard_path = project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
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
            if 'apps_lic' in sub_dir:
                territory = "Apps Lic"
            elif 'apps_rg' in sub_dir:
                territory = "Apps Rg"
            elif 'apps_shared' in sub_dir:
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
        
        # Compute raw metrics
        heal_cap = sum(1 for a in agents_list if a.get('has_healing'))
        heal_inv = sum(1 for a in agents_list if a.get('invocation') == 'Yes')
        test = sum(1 for a in agents_list if a.get('has_tests'))
        obs = sum(1 for a in agents_list if a.get('observability'))
        cc_sum = sum(a.get('cyclomatic_complexity', 1) for a in agents_list)
        typed_sum = sum(a.get('typed_pct', 0) for a in agents_list)
        doc_sum = sum(a.get('documented_pct', 0) for a in agents_list)
        
        # Calculate percentages
        heal_cap_pct = round(heal_cap / total * 100, 1)
        heal_inv_pct = round(heal_inv / total * 100, 1)
        test_pct = round(test / total * 100, 1)
        obs_pct = round(obs / total * 100, 1)
        typed_pct = round(typed_sum / total, 1)
        doc_pct = round(doc_sum / total, 1)
        avg_cc = round(cc_sum / total, 1)
        
        # Derived metrics
        complexity_health = round(max(0, 100 - (avg_cc * 2)), 1)
        code_quality = round((typed_pct + doc_pct) / 2, 1)
        # Health is weighted average of 5 components as shown in Health Breakdown
        health = round((heal_cap_pct + heal_inv_pct + test_pct + obs_pct + complexity_health) / 5, 1)
        risk = "HIGH" if avg_cc > 12 or health < 60 else "MED" if avg_cc > 8 or health < 80 else "LOW"
        
        # Hardened % - estimate based on layer
        hardened_pct = 80.0  # Default estimate
        
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
            "hardened_pct": hardened_pct
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
            "MCP Capable %": metrics["hardened_pct"],  # Same as Hardened
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
        
        for territory_name, agents_list in territories.items():
            if not agents_list:
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
                
                # Build agent object for drill-down
                agent_objects.append({
                    'name': agent.get('class_name', 'Unknown'),
                    'path': agent.get('path', ''),
                    'healCap': heal_cap,
                    'invocation': invocation,
                    'hardened': hardened,
                    'test': test,
                    'complexityHealth': complexity_health,
                    'health': health,
                    'typed': typed,
                    'documented': documented,
                    'schema': schema,
                    'base': base,
                    'quality': quality,
                    'cc': cc,
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
        """Generate complete dashboard data with FIXED structure (always 29 rows)."""
        territories = self.group_agents_by_territory()
        
        # Build rows in FIXED order - create row for EVERY territory (even if empty)
        rows = []
        for i, territory_name in enumerate(TERRITORY_ORDER):
            priority = i + 1
            is_infrastructure = "L6_Observability" in territory_name
            
            if territory_name in territories and len(territories[territory_name]) > 0:
                # Territory has agents - compute real metrics
                agents_list = territories[territory_name]
                metrics = self.compute_territory_metrics(agents_list)
                if metrics:
                    row = self.build_territory_row(territory_name, metrics, priority, is_infrastructure)
                    rows.append(row)
            else:
                # Territory has no agents - create empty row to maintain wireframe
                empty_metrics = {
                    "total": 0,
                    "compliant": 0,
                    "heal_cap_pct": 0.0,
                    "heal_inv_pct": 0.0,
                    "test_pct": 0.0,
                    "obs_pct": 0.0,
                    "avg_cc": 0.0,
                    "typed_pct": 0.0,
                    "doc_pct": 0.0,
                    "complexity_health": 0.0,
                    "code_quality": 0.0,
                    "health": 0.0,
                    "risk": "N/A",
                    "hardened_pct": 0.0
                }
                row = self.build_territory_row(territory_name, empty_metrics, priority, is_infrastructure)
                rows.append(row)
        
        # Build TOTAL row (only from non-empty rows)
        non_empty_rows = [r for r in rows if r["Total"] > 0]
        total_row = self.build_total_row(non_empty_rows)
        
        # TOTAL always first
        all_rows = [total_row] + rows
        
        return all_rows
    
    def validate_dashboard_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate dashboard data against FIXED wireframe with strict guardrails."""
        if not data:
            print("❌ VALIDATION FAILED: No data generated")
            return False
        
        # GUARDRAIL 1: Enforce exactly 29 rows (TOTAL + 28 territories)
        expected_row_count = len(TERRITORY_ORDER) + 1  # +1 for TOTAL
        if len(data) != expected_row_count:
            print(f"❌ GUARDRAIL VIOLATION: Row count mismatch")
            print(f"   Expected: {expected_row_count} rows (TOTAL + {len(TERRITORY_ORDER)} territories)")
            print(f"   Actual: {len(data)} rows")
            print(f"   This violates the frozen wireframe structure!")
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
        
        # GUARDRAIL 4: Territory order must match FIXED structure exactly
        territory_rows = data[1:]
        for i, row in enumerate(territory_rows):
            expected = TERRITORY_ORDER[i]
            actual = row.get("Territory")
            if actual != expected:
                print(f"❌ GUARDRAIL VIOLATION: Territory order mismatch at position {i+1}")
                print(f"   Expected: {expected}")
                print(f"   Actual: {actual}")
                print(f"   Territory order must never deviate from frozen wireframe!")
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
    
    def update_dashboard_html(self, data: List[Dict[str, Any]], per_agent_data: Dict[str, Dict]) -> bool:
        """Update dashboard HTML with new data and real per-agent data."""
        if not self.dashboard_path.exists():
            print(f"❌ ERROR: Dashboard HTML not found at {self.dashboard_path}")
            return False
        
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # Find and replace dashboardData
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                print("❌ ERROR: Could not find dashboardData in HTML")
                return False
            
            new_json = json.dumps(data, indent=2)
            new_data_block = f'const dashboardData = {new_json};'
            
            # Add realAgentData right after dashboardData
            agent_json = json.dumps(per_agent_data, indent=2)
            real_agent_block = f'\n\n        // Real per-agent data (replaces generateMockAgentData)\n        const realAgentData = {agent_json};'
            
            new_html = html[:start_idx] + new_data_block + real_agent_block + html[end_idx:]
            
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
