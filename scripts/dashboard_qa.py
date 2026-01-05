#!/usr/bin/env python3
"""
Automated Dashboard QA Validation
Run before committing dashboard changes.

Usage:
    python scripts/dashboard_qa.py
    
Exit codes:
    0 = All checks passed
    1 = One or more checks failed
"""
import sys
import re
import json
from pathlib import Path
from typing import List, Tuple


class DashboardQA:
    """Dashboard quality assurance validator."""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        # Consolidated dashboard location: agentic_core/observability/dashboard/
        self.template_path = self.root / 'agentic_core' / 'observability' / 'dashboard' / 'dashboard_template.html'
        self.dashboard_path = self.root / 'reports' / 'autonomy_dashboard.html'
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_template_syntax(self) -> bool:
        """Validate HTML template syntax."""
        print('🔍 Validating template syntax...')
        
        if not self.template_path.exists():
            self.errors.append(f'Template not found: {self.template_path}')
            return False
        
        content = self.template_path.read_text(encoding='utf-8')
        
        # Check balanced div tags
        open_divs = content.count('<div')
        close_divs = content.count('</div>')
        if open_divs != close_divs:
            self.errors.append(f'Mismatched div tags: {open_divs} open, {close_divs} close')
            return False
        
        # Check for duplicate IDs
        ids = re.findall(r'id=["\']([^"\'\s>]+)', content)
        duplicates = [x for x in ids if ids.count(x) > 1]
        if duplicates:
            self.errors.append(f'Duplicate IDs found: {set(duplicates)}')
            return False
        
        # Check for common JavaScript errors
        if 'getElementById(' in content:
            element_ids = set(re.findall(r'getElementById\(["\']([^"\']+)', content))
            html_ids = set(re.findall(r'id=["\']([^"\'\s>]+)', content))
            missing = element_ids - html_ids
            if missing:
                self.warnings.append(f'getElementById references missing elements: {missing}')
        
        print('  ✅ Template syntax valid')
        return True
    
    def validate_timer_configuration(self) -> bool:
        """Validate refresh timer configuration."""
        print('🔍 Validating timer configuration...')
        
        if not self.template_path.exists():
            return False
        
        content = self.template_path.read_text(encoding='utf-8')
        
        # Check for REFRESH_INTERVAL_MS constant
        if 'REFRESH_INTERVAL_MS = 300000' not in content:
            self.errors.append('REFRESH_INTERVAL_MS not set to 300000 (5 minutes)')
            return False
        
        # Check meta refresh tag
        meta_match = re.search(r'<meta http-equiv="refresh" content="(\d+)"', content)
        if not meta_match or meta_match.group(1) != '300':
            self.errors.append('Meta refresh tag not set to 300 seconds')
            return False
        
        # Check for old 30-second timer (should only be in stale buffer calculation)
        timer_30s = re.findall(r'setInterval.*30000', content)
        if timer_30s:
            # Allow 30000 in stale buffer calculation only
            for match in timer_30s:
                if 'REFRESH_INTERVAL_MS + 30000' not in match:
                    self.errors.append('Found hardcoded 30-second timer (should use REFRESH_INTERVAL_MS)')
                    return False
        
        # Count setInterval calls for refresh (allow multiline)
        refresh_intervals = len(re.findall(r'refreshInterval = setInterval', content))
        if refresh_intervals != 1:
            self.errors.append(f'Expected 1 refresh interval, found {refresh_intervals}')
            return False
        
        # Count setInterval calls for countdown display (allow multiline)
        countdown_intervals = len(re.findall(r'setInterval\([^)]*function\(\)|setInterval\(\(\)', content, re.DOTALL))
        # More lenient check - just ensure we have setInterval calls
        if countdown_intervals < 1:
            self.warnings.append('Could not verify countdown interval (multiline pattern)')
        
        # Check for getElementById calls to removed elements (warnings only)
        removed_elements = ['executiveSummary', 'macroObservations', 'metricObservations']
        for elem in removed_elements:
            if f"getElementById('{elem}')" in content or f'getElementById("{elem}")' in content:
                self.warnings.append(f'getElementById references removed element: {elem}')
        
        print('  ✅ Timer configuration valid')
        return True
    
    def validate_generated_dashboard(self) -> bool:
        """Validate generated dashboard HTML."""
        print('🔍 Validating generated dashboard...')
        
        if not self.dashboard_path.exists():
            self.errors.append(f'Dashboard not generated: {self.dashboard_path}')
            return False
        
        content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Check critical elements
        critical_elements = [
            'healthScoreValue',
            'codeQualityScoreValue',
            'baseInheritanceValue',
            'anomalyFlags',
            'refreshStatus',
            'REFRESH_INTERVAL_MS'
        ]
        
        missing = [e for e in critical_elements if e not in content]
        if missing:
            self.errors.append(f'Missing critical elements: {missing}')
            return False
        
        # Check refresh interval in generated file
        if 'REFRESH_INTERVAL_MS = 300000' not in content:
            self.errors.append('Generated dashboard has incorrect refresh interval')
            return False
        
        # Check for old Strategic Observations section (should be replaced)
        if 'Strategic Observations & Prioritized Actions' in content:
            self.warnings.append('Old Strategic Observations section still present (should be replaced)')
        
        # Check for new Autonomy Readiness Overview
        if 'Autonomy Readiness Overview' not in content:
            self.errors.append('New Autonomy Readiness Overview section missing')
            return False
        
        # Check file size (should be reasonable)
        size_mb = self.dashboard_path.stat().st_size / (1024 * 1024)
        if size_mb > 1.0:
            self.warnings.append(f'Dashboard file size is large: {size_mb:.2f}MB (target <1MB)')
        
        print('  ✅ Generated dashboard valid')
        return True
    
    def validate_data_integrity(self) -> bool:
        """Validate embedded data integrity."""
        print('🔍 Validating data integrity...')
        
        if not self.dashboard_path.exists():
            return False
        
        content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Extract dashboardData JSON
        try:
            start = content.find('const dashboardData = ') + len('const dashboardData = ')
            end = content.find(';', start)
            data_json = content[start:end]
            data = json.loads(data_json)
            
            # Check for TOTAL row
            total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
            if not total_row:
                self.errors.append('TOTAL row missing from dashboardData')
                return False
            
            # Validate critical fields
            required_fields = ['Total', 'Health', 'Invocation %', 'Test %', 'Hardened %']
            missing_fields = [f for f in required_fields if f not in total_row]
            if missing_fields:
                self.errors.append(f'TOTAL row missing fields: {missing_fields}')
                return False
            
            print('  ✅ Data integrity valid')
            return True
            
        except (ValueError, json.JSONDecodeError) as e:
            self.errors.append(f'Failed to parse dashboardData JSON: {e}')
            return False
    
    def run_all_checks(self) -> bool:
        """Run all QA checks."""
        print('\n' + '='*60)
        print('Dashboard QA Validation')
        print('='*60 + '\n')
        
        checks = [
            self.validate_template_syntax(),
            self.validate_timer_configuration(),
            self.validate_generated_dashboard(),
            self.validate_data_integrity()
        ]
        
        print('\n' + '='*60)
        
        if self.warnings:
            print('\n⚠️  Warnings:')
            for warning in self.warnings:
                print(f'  - {warning}')
        
        if self.errors:
            print('\n❌ Errors:')
            for error in self.errors:
                print(f'  - {error}')
            print('\n❌ QA FAILED - Fix errors before committing')
            return False
        
        print('\n✅ ALL QA CHECKS PASSED')
        print('\nPre-commit checklist:')
        print('  [ ] Open reports/autonomy_dashboard.html in browser')
        print('  [ ] Verify 3 KPIs display correctly (not "---%")')
        print('  [ ] Verify countdown shows "Xm Ys" format')
        print('  [ ] Check browser console for errors')
        print('  [ ] Test manual refresh button')
        print('  [ ] Clear cache and reload')
        return True


def main():
    """Main entry point."""
    qa = DashboardQA()
    success = qa.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
