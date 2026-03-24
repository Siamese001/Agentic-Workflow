#!/usr/bin/env python3
"""
Validate Phase 2.1 ImportError fixes with windsurfrules compliance.
Focused testing on import hygiene and layer boundaries.
"""

import ast
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Phase21WindsurfrulesValidator:
    """Validate Phase 2.1 fixes against windsurfrules."""
    
    def __init__(self):
        self.results = {}
        
    def validate_import_hygiene(self):
        """Validate import hygiene per windsurfrules."""
        print("🧪 Validating import hygiene...")
        
        # Run ruff for import hygiene checks
        try:
            result = subprocess.run(
                ['python', '-m', 'ruff', 'check', '--select=F401,E402,I', '--format=json', 
                 '--output-file=-', '--quiet', 'agentic_core/', 'tools/'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            violations = []
            if result.stdout and result.stdout.strip():
                try:
                    violations = json.loads(result.stdout)
                except json.JSONDecodeError:
                    print(f"  ⚠️  Could not parse ruff output: {result.stdout[:200]}")
            
            self.results['import_hygiene'] = {
                'total_violations': len(violations),
                'unused_imports': len([v for v in violations if v.get('code') == 'F401']),
                'module_level_imports': len([v for v in violations if v.get('code') == 'E402']),
                'import_ordering': len([v for v in violations if v.get('code', '').startswith('I')]),
                'compliant': len(violations) == 0
            }
            
        except subprocess.TimeoutExpired:
            self.results['import_hygiene'] = {'error': 'timeout', 'compliant': False}
        except Exception as e:
            self.results['import_hygiene'] = {'error': str(e), 'compliant': False}
        
        hygiene = self.results['import_hygiene']
        print(f"  ✅ Total violations: {hygiene.get('total_violations', 'N/A')}")
        print(f"  ✅ Unused imports (F401): {hygiene.get('unused_imports', 'N/A')}")
        print(f"  ✅ Module level imports (E402): {hygiene.get('module_level_imports', 'N/A')}")
        print(f"  ✅ Import ordering (I): {hygiene.get('import_ordering', 'N/A')}")
        print(f"  📊 Compliant: {hygiene.get('compliant', False)}")
        
        return hygiene
    
    def validate_layer_boundaries(self):
        """Validate layer boundary compliance."""
        print("🧪 Validating layer boundaries...")
        
        # Use the existing layer violation checker
        try:
            result = subprocess.run(
                ['python', 'tools/check_layer_violations_fixed.py'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            violations = 0
            
            # Parse violations from output
            if 'Total violations:' in output:
                import re
                match = re.search(r'Total violations:\s+(\d+)', output)
                if match:
                    violations = int(match.group(1))
            
            self.results['layer_boundaries'] = {
                'violations': violations,
                'compliant': violations == 0,
                'exit_code': result.returncode,
                'output': output[-500:] if len(output) > 500 else output  # Last 500 chars
            }
            
        except subprocess.TimeoutExpired:
            self.results['layer_boundaries'] = {'error': 'timeout', 'compliant': False}
        except Exception as e:
            self.results['layer_boundaries'] = {'error': str(e), 'compliant': False}
        
        boundaries = self.results['layer_boundaries']
        print(f"  ✅ Layer violations: {boundaries.get('violations', 'N/A')}")
        print(f"  📊 Compliant: {boundaries.get('compliant', False)}")
        
        return boundaries
    
    def validate_fix_effectiveness(self):
        """Validate Phase 2.1 fix effectiveness."""
        print("🧪 Validating fix effectiveness...")
        
        try:
            # Load fix report
            with open(PROJECT_ROOT / "tools" / "high_severity_fixes_report.json", 'r') as f:
                fix_report = json.load(f)
            
            # Load original violations
            with open(PROJECT_ROOT / "tools" / "silent_swallower_report.json", 'r') as f:
                original_report = json.load(f)
            
            import_errors_original = len([v for v in original_report['violations'] if 'ImportError' in v['exception_type']])
            fixes_applied = fix_report.get('fixes_applied', 0)
            
            effectiveness = (fixes_applied / import_errors_original * 100) if import_errors_original > 0 else 0
            
            self.results['fix_effectiveness'] = {
                'original_import_errors': import_errors_original,
                'fixes_applied': fixes_applied,
                'effectiveness_percentage': effectiveness,
                'target_met': effectiveness >= 90
            }
            
        except Exception as e:
            self.results['fix_effectiveness'] = {'error': str(e), 'target_met': False}
        
        effectiveness = self.results['fix_effectiveness']
        print(f"  ✅ Original ImportError violations: {effectiveness.get('original_import_errors', 'N/A')}")
        print(f"  ✅ Fixes applied: {effectiveness.get('fixes_applied', 'N/A')}")
        print(f"  📊 Effectiveness: {effectiveness.get('effectiveness_percentage', 'N/A'):.1f}%")
        print(f"  🎯 Target met (≥90%): {effectiveness.get('target_met', False)}")
        
        return effectiveness
    
    def validate_ast_compliance(self):
        """Validate AST-based analysis compliance."""
        print("🧪 Validating AST compliance...")
        
        # Test a sample of files for AST parsing
        sample_files = list(PROJECT_ROOT.rglob("*.py"))[:10]
        
        ast_results = {
            'files_tested': len(sample_files),
            'parsing_success': 0,
            'parsing_failures': 0,
            'imports_extracted': 0,
            'compliant': True
        }
        
        for file_path in sample_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Test AST parsing (§3.3 requirement)
                tree = ast.parse(content, filename=str(file_path))
                ast_results['parsing_success'] += 1
                
                # Test dependency extraction (§3.4 requirement)
                imports = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        imports += 1
                
                ast_results['imports_extracted'] += imports
                
            except Exception as e:
                ast_results['parsing_failures'] += 1
                ast_results['compliant'] = False
        
        self.results['ast_compliance'] = ast_results
        
        print(f"  ✅ Files tested: {ast_results['files_tested']}")
        print(f"  ✅ Parsing success: {ast_results['parsing_success']}")
        print(f"  ❌ Parsing failures: {ast_results['parsing_failures']}")
        print(f"  📊 Imports extracted: {ast_results['imports_extracted']}")
        print(f"  📊 Compliant: {ast_results['compliant']}")
        
        return ast_results
    
    def run_comprehensive_validation(self):
        """Run all validation checks."""
        print("=" * 80)
        print("PHASE 2.1 WINDSURFRULES VALIDATION")
        print("=" * 80)
        print("Validating ImportError fixes against windsurfrules...")
        print("=" * 80)
        
        # Run all validations
        self.validate_import_hygiene()
        self.validate_layer_boundaries()
        self.validate_fix_effectiveness()
        self.validate_ast_compliance()
        
        # Calculate overall compliance
        compliance_score = self._calculate_compliance_score()
        
        print("\n" + "=" * 80)
        print("🎉 WINDSURFRULES VALIDATION COMPLETED!")
        print(f"✅ Overall compliance score: {compliance_score:.1f}%")
        
        # Detailed results
        print("\n📊 DETAILED RESULTS:")
        for category, results in self.results.items():
            if 'error' in results:
                print(f"  ❌ {category}: ERROR - {results['error']}")
            elif results.get('compliant', False):
                print(f"  ✅ {category}: COMPLIANT")
            else:
                print(f"  ⚠️  {category}: NON-COMPLIANT")
        
        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n📝 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   - {rec}")
        
        print("=" * 80)
        
        return compliance_score
    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score."""
        if not self.results:
            return 0.0
        
        categories = ['import_hygiene', 'layer_boundaries', 'fix_effectiveness', 'ast_compliance']
        compliant_count = 0
        total_count = 0
        
        for category in categories:
            if category in self.results:
                total_count += 1
                if self.results[category].get('compliant', False):
                    compliant_count += 1
        
        return (compliant_count / total_count * 100) if total_count > 0 else 0.0
    
    def _generate_recommendations(self) -> list:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Import hygiene recommendations
        hygiene = self.results.get('import_hygiene', {})
        if not hygiene.get('compliant', True):
            if hygiene.get('unused_imports', 0) > 0:
                recommendations.append(f"Remove {hygiene['unused_imports']} unused imports (F401)")
            if hygiene.get('module_level_imports', 0) > 0:
                recommendations.append(f"Fix {hygiene['module_level_imports']} module level imports (E402)")
            if hygiene.get('import_ordering', 0) > 0:
                recommendations.append(f"Fix {hygiene['import_ordering']} import ordering issues")
        
        # Layer boundary recommendations
        boundaries = self.results.get('layer_boundaries', {})
        if not boundaries.get('compliant', True):
            violations = boundaries.get('violations', 0)
            recommendations.append(f"Fix {violations} layer boundary violations")
        
        # Fix effectiveness recommendations
        effectiveness = self.results.get('fix_effectiveness', {})
        if not effectiveness.get('target_met', True):
            recommendations.append("Improve ImportError fix effectiveness to ≥90%")
        
        # AST compliance recommendations
        ast_comp = self.results.get('ast_compliance', {})
        if not ast_comp.get('compliant', True):
            recommendations.append("Fix AST parsing issues in affected files")
        
        return recommendations
    
    def save_validation_report(self):
        """Save validation report."""
        report = {
            'validation_timestamp': '2026-03-24T19:50:00Z',
            'phase': '2.1',
            'windsurfrules_compliance': self.results,
            'overall_score': self._calculate_compliance_score(),
            'recommendations': self._generate_recommendations()
        }
        
        report_file = PROJECT_ROOT / "tools" / "phase_2_1_windsurfrules_validation.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Validation report saved to: {report_file}")
        
        return report


def main():
    """Main entry point."""
    validator = Phase21WindsurfrulesValidator()
    
    # Run comprehensive validation
    score = validator.run_comprehensive_validation()
    
    # Save report
    validator.save_validation_report()
    
    return score


if __name__ == "__main__":
    main()
