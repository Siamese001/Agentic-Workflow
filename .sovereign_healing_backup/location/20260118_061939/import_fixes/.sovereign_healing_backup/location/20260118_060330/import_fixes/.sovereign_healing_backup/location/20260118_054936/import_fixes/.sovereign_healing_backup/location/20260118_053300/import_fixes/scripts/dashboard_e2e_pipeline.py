#!/usr/bin/env python3
"""
AUTOMATED DASHBOARD E2E PIPELINE
=================================

Complete end-to-end pipeline that:
1. Fixes heal invocation gaps (adds super().heal_repository() calls)
2. Regenerates agent discovery data
3. Regenerates dashboard HTML
4. Validates all data integrity
5. Provides visual confirmation of updates

Run this after ANY code changes to ensure dashboard reflects reality.
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Import SSOT paths
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    get_validated_project_root,
    DASHBOARD_DIR
)

class DashboardE2EPipeline:
    """Automated dashboard end-to-end pipeline."""
    
    def __init__(self):
        self.project_root = get_validated_project_root()
        self.discovery_path = self.project_root / 'agent_discovery_full.json'
        self.dashboard_path = self.project_root / DASHBOARD_DIR / 'autonomy_dashboard.html'
        self.stats = {
            'heal_fixes': 0,
            'agents_discovered': 0,
            'dashboard_rows': 0,
            'heal_invocation_before': 0,
            'heal_invocation_after': 0
        }
    
    def print_header(self, title: str):
        """Print section header."""
        print()
        print("=" * 80)
        print(title)
        print("=" * 80)
        print()
    
    def print_step(self, step: str):
        """Print pipeline step."""
        print(f"📍 {step}")
    
    def step1_analyze_heal_invocation(self) -> Tuple[int, List[Dict]]:
        """Step 1: Analyze current heal invocation coverage."""
        self.print_step("STEP 1: Analyzing heal invocation coverage...")
        
        if not self.discovery_path.exists():
            print("⚠️  agent_discovery_full.json not found - will regenerate")
            return 0, []
        
        data = json.load(open(self.discovery_path))
        total = len(data)
        has_invocation = sum(1 for a in data if a.get('invocation') == 'Yes')
        needs_fix = [a for a in data if a.get('has_healing') and a.get('invocation') != 'Yes']
        
        coverage = has_invocation / total * 100 if total > 0 else 0
        self.stats['heal_invocation_before'] = coverage
        
        print(f"   Total agents: {total}")
        print(f"   Heal invocation: {has_invocation} ({coverage:.1f}%)")
        print(f"   Needs fix: {len(needs_fix)}")
        
        return len(needs_fix), needs_fix
    
    def step2_fix_heal_invocation(self, agents_to_fix: List[Dict]) -> int:
        """Step 2: Automatically fix heal invocation gaps."""
        self.print_step("STEP 2: Fixing heal invocation gaps...")
        
        if not agents_to_fix:
            print("   ✅ No fixes needed - all agents have heal invocation")
            return 0
        
        fixed_count = 0
        
        for agent in agents_to_fix:
            path = Path(agent['path'])
            name = agent['class_name']
            
            if not path.exists():
                print(f"   ⚠️  SKIP: {name} - file not found")
                continue
            
            try:
                content = path.read_text(encoding='utf-8')
                
                # Find heal_repository method
                pattern = r'(    def heal_repository\([^)]*\)[^:]*:.*?)(\n        (?:""".*?"""|\'\'\'.*?\'\'\')\s*\n)?(.*?)(\n    def |\n\nclass |\Z)'
                matches = list(re.finditer(pattern, content, re.DOTALL))
                
                if not matches:
                    print(f"   ⚠️  SKIP: {name} - no heal_repository method")
                    continue
                
                match = matches[0]
                method_sig = match.group(1)
                docstring = match.group(2) or ""
                method_body = match.group(3)
                next_section = match.group(4)
                
                # Check if super() call already exists
                if 'super().heal_repository' in method_body:
                    continue
                
                # Find first non-comment line
                lines = method_body.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                        insert_index = i
                        break
                
                # Insert super() call
                indent = "        "
                super_call = f"{indent}super().heal_repository()\n"
                lines.insert(insert_index, super_call)
                new_method_body = '\n'.join(lines)
                
                # Reconstruct and write
                new_method = method_sig + docstring + new_method_body + next_section
                new_content = content[:match.start()] + new_method + content[match.end():]
                path.write_text(new_content, encoding='utf-8')
                
                print(f"   ✅ Fixed: {name}")
                fixed_count += 1
                
            except Exception as e:
                print(f"   ❌ ERROR: {name} - {str(e)}")
        
        self.stats['heal_fixes'] = fixed_count
        print(f"\n   Fixed {fixed_count} agents")
        return fixed_count
    
    def step3_regenerate_discovery(self) -> bool:
        """Step 3: Regenerate agent discovery data."""
        self.print_step("STEP 3: Regenerating agent discovery data...")
        
        # Use the working discovery script
        discovery_script = self.project_root / 'scripts' / 'agent_discovery_audit.py'
        
        if not discovery_script.exists():
            print("   ❌ Discovery script not found")
            return False
        
        try:
            print("   ⏳ Running discovery (this may take 2-3 minutes)...")
            # Run discovery script with longer timeout
            result = subprocess.run(
                [sys.executable, str(discovery_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode != 0:
                print(f"   ❌ Discovery failed: {result.stderr}")
                return False
            
            # Verify discovery file was updated
            if not self.discovery_path.exists():
                print("   ❌ Discovery file not created")
                return False
            
            data = json.load(open(self.discovery_path))
            self.stats['agents_discovered'] = len(data)
            
            # Calculate new heal invocation coverage
            has_invocation = sum(1 for a in data if a.get('invocation') == 'Yes')
            coverage = has_invocation / len(data) * 100 if len(data) > 0 else 0
            self.stats['heal_invocation_after'] = coverage
            
            print(f"   ✅ Discovered {len(data)} agents")
            print(f"   ✅ Heal invocation: {has_invocation} ({coverage:.1f}%)")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("   ❌ Discovery timed out")
            return False
        except Exception as e:
            print(f"   ❌ Discovery error: {e}")
            return False
    
    def step4_regenerate_dashboard(self) -> bool:
        """Step 4: Regenerate dashboard HTML."""
        self.print_step("STEP 4: Regenerating dashboard HTML...")
        
        dashboard_script = self.project_root / 'agentic_core' / 'L6_observability' / 'dashboards' / 'generate_dashboard.py'
        
        if not dashboard_script.exists():
            print("   ❌ Dashboard generator not found")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(dashboard_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"   ❌ Dashboard generation failed: {result.stderr}")
                return False
            
            if not self.dashboard_path.exists():
                print("   ❌ Dashboard file not created")
                return False
            
            # Extract dashboard data
            html = self.dashboard_path.read_text(encoding='utf-8')
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx)
            
            if start_idx != -1 and end_idx != -1:
                json_str = html[start_idx+len(start_marker)-1:end_idx+1]
                territories = json.loads(json_str)
                self.stats['dashboard_rows'] = len(territories)
                print(f"   ✅ Generated dashboard with {len(territories)} rows")
            else:
                print("   ⚠️  Dashboard generated but data structure unclear")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Dashboard generation error: {e}")
            return False
    
    def step5_run_e2e_tests(self) -> bool:
        """Step 5: Run end-to-end validation tests."""
        self.print_step("STEP 5: Running end-to-end validation tests...")
        
        test_script = self.project_root / 'scripts' / 'test_dashboard_end_to_end.py'
        
        if not test_script.exists():
            print("   ❌ Test script not found")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30,
                env={'PYTHONPATH': str(self.project_root)}
            )
            
            # Print test output
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"   ❌ Tests failed")
                if result.stderr:
                    print(result.stderr)
                return False
            
            print("   ✅ All tests passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Test execution error: {e}")
            return False
    
    def step6_visual_confirmation(self):
        """Step 6: Display visual confirmation of updates."""
        self.print_step("STEP 6: Visual confirmation of updates...")
        
        print()
        print("┏" + "━" * 78 + "┓")
        print("┃" + " " * 25 + "DASHBOARD UPDATE SUMMARY" + " " * 29 + "┃")
        print("┣" + "━" * 78 + "┫")
        
        # Heal invocation improvement
        before = self.stats['heal_invocation_before']
        after = self.stats['heal_invocation_after']
        improvement = after - before
        
        print(f"┃  Heal Invocation Coverage:                                              ┃")
        print(f"┃    Before: {before:5.1f}%  →  After: {after:5.1f}%  (Δ +{improvement:4.1f}%)                    ┃")
        
        if after >= 100.0:
            print(f"┃    🎯 TARGET ACHIEVED: 100% heal invocation coverage!                   ┃")
        elif after >= 99.0:
            print(f"┃    ⚠️  Nearly complete: {100-after:.1f}% gap remaining                             ┃")
        else:
            print(f"┃    ⚠️  Gap: {100-after:.1f}% ({int((100-after)/100*self.stats['agents_discovered'])} agents)                                      ┃")
        
        print(f"┃                                                                              ┃")
        print(f"┃  Agents Fixed: {self.stats['heal_fixes']:3d}                                                      ┃")
        print(f"┃  Agents Discovered: {self.stats['agents_discovered']:3d}                                                ┃")
        print(f"┃  Dashboard Rows: {self.stats['dashboard_rows']:2d}                                                   ┃")
        print(f"┃                                                                              ┃")
        print(f"┃  Dashboard Location:                                                         ┃")
        print(f"┃    {str(self.dashboard_path.relative_to(self.project_root)):<74}┃")
        print("┗" + "━" * 78 + "┛")
        print()
    
    def run(self) -> bool:
        """Run complete pipeline."""
        self.print_header("AUTOMATED DASHBOARD E2E PIPELINE")
        
        # Step 1: Analyze
        needs_fix_count, agents_to_fix = self.step1_analyze_heal_invocation()
        
        # Step 2: Fix heal invocation
        if needs_fix_count > 0:
            self.step2_fix_heal_invocation(agents_to_fix)
        
        # Step 3: Regenerate discovery
        if not self.step3_regenerate_discovery():
            print("\n❌ PIPELINE FAILED at discovery regeneration")
            return False
        
        # Step 4: Regenerate dashboard
        if not self.step4_regenerate_dashboard():
            print("\n❌ PIPELINE FAILED at dashboard regeneration")
            return False
        
        # Step 5: Run tests
        if not self.step5_run_e2e_tests():
            print("\n❌ PIPELINE FAILED at validation tests")
            return False
        
        # Step 6: Visual confirmation
        self.step6_visual_confirmation()
        
        self.print_header("✅ PIPELINE COMPLETE - Dashboard is up to date!")
        
        return True


def main():
    """Main entry point."""
    pipeline = DashboardE2EPipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
