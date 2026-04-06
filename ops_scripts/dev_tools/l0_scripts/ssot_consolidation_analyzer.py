"""
Phase 19: SSOT Consolidation & Logic Audit Tool

Performs Logic-First Comparison between utils/core_extensions/ and base_agents/ files
to establish agentic_core/base_agents/ as the Single Source of Truth.
"""
import ast
import json
from pathlib import Path



class SSOTConsolidationAnalyzer:
    """Analyzes and consolidates agent logic into base_agents SSOT."""

    def __init__(self):
        self.utils_path = Path('agentic_core/utils/core_extensions')
        self.base_path = Path('agentic_core/base_agents')
        self.comparison_results = {}
        self.merge_decisions = {}

    def analyze_file_sovereign_features(self, file_path: Path) -> dict:
        """Analyze file for Sovereign V2.5 features."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            try:
                tree = ast.parse(content)
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                return {'error': 'Syntax error - cannot analyze'}
            features = {'has_immutable_staging_buffer': 'ImmutableStagingBuffer' in content, 'has_healer_mixin': 'HealerMixin' in content, 'has_mcp_hardened': 'MCPHardenedMixin' in content, 'has_abc_inheritance': 'ABC' in content and 'from abc import' in content, 'has_dataclass': '@dataclass' in content, 'has_injection_mixin': 'instructional_injection_mixin' in content, 'has_tracing': 'tracing_mixin' in content or 'TraceRegistry' in content, 'has_standard_heal': '@standard_heal' in content, 'has_sovereign_base': 'SovereignBaseAgent' in content, 'class_count': 0, 'agent_classes': [], 'mixin_classes': [], 'line_count': len(content.split('\n')), 'complexity_score': 0}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    features['class_count'] += 1
                    bases = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                    class_info = {'name': node.name, 'bases': bases, 'is_agent': node.name.endswith('Agent'), 'is_mixin': 'Mixin' in node.name, 'is_base': 'Base' in node.name, 'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0}
                    if class_info['is_agent']:
                        features['agent_classes'].append(class_info)
                    elif class_info['is_mixin']:
                        features['mixin_classes'].append(class_info)
            features['complexity_score'] = features['class_count'] * 10 + len(features['agent_classes']) * 20 + len(features['mixin_classes']) * 15 + (1 if features['has_immutable_staging_buffer'] else 0) * 25 + (1 if features['has_healer_mixin'] else 0) * 20 + (1 if features['has_mcp_hardened'] else 0) * 20 + (1 if features['has_abc_inheritance'] else 0) * 10 + (1 if features['has_standard_heal'] else 0) * 15
            return features
        except Exception as e:
            return {'error': f'Error analyzing file: {e}'}

    def compare_file_versions(self, filename: str) -> dict:
        """Compare utils version vs base_agents version."""
        utils_file = self.utils_path / filename
        base_file = self.base_path / filename
        utils_features = self.analyze_file_sovereign_features(utils_file) if utils_file.exists() else None
        base_features = self.analyze_file_sovereign_features(base_file) if base_file.exists() else None
        comparison = {'filename': filename, 'utils_exists': utils_file.exists(), 'base_exists': base_file.exists(), 'utils_features': utils_features, 'base_features': base_features, 'decision': None, 'reason': None, 'merge_required': False}
        if not utils_features and (not base_features):
            comparison['decision'] = 'SKIP'
            comparison['reason'] = 'Neither version exists'
        elif not base_features:
            comparison['decision'] = 'USE_UTILS'
            comparison['reason'] = 'Only utils version exists'
        elif not utils_features:
            comparison['decision'] = 'USE_BASE'
            comparison['reason'] = 'Only base version exists'
        else:
            utils_score = utils_features.get('complexity_score', 0)
            base_score = base_features.get('complexity_score', 0)
            utils_has_critical = utils_features.get('has_healer_mixin', False) or utils_features.get('has_mcp_hardened', False) or utils_features.get('has_immutable_staging_buffer', False)
            base_has_critical = base_features.get('has_healer_mixin', False) or base_features.get('has_mcp_hardened', False) or base_features.get('has_immutable_staging_buffer', False)
            if utils_has_critical and (not base_has_critical):
                comparison['decision'] = 'USE_UTILS'
                comparison['reason'] = 'Utils version has critical Sovereign V2.5 features'
            elif base_has_critical and (not utils_has_critical):
                comparison['decision'] = 'USE_BASE'
                comparison['reason'] = 'Base version has critical Sovereign V2.5 features'
            elif utils_score > base_score * 1.2:
                comparison['decision'] = 'USE_UTILS'
                comparison['reason'] = f'Utils version significantly more advanced ({utils_score} vs {base_score})'
            elif base_score > utils_score * 1.2:
                comparison['decision'] = 'USE_BASE'
                comparison['reason'] = f'Base version significantly more advanced ({base_score} vs {utils_score})'
            else:
                comparison['decision'] = 'MERGE'
                comparison['reason'] = 'Both versions have value - zero-loss merge required'
                comparison['merge_required'] = True
        return comparison

    def analyze_all_files(self) -> dict:
        """Analyze all files for SSOT consolidation."""
        print('🔍 PHASE 19: SSOT Consolidation & Logic Audit')
        print('=' * 60)
        utils_files = set()
        base_files = set()
        if self.utils_path.exists():
            utils_files = {f.name for f in self.utils_path.rglob('*.py') if f.name != '__init__.py'}
        if self.base_path.exists():
            base_files = {f.name for f in self.base_path.rglob('*.py') if f.name != '__init__.py'}
        all_files = utils_files.union(base_files)
        print(f'📊 Found {len(all_files)} total files to analyze')
        print(f'   Utils files: {len(utils_files)}')
        print(f'   Base files: {len(base_files)}')
        results = {'total_files': len(all_files), 'comparisons': {}, 'summary': {'USE_UTILS': 0, 'USE_BASE': 0, 'MERGE': 0, 'SKIP': 0}}
        for filename in sorted(all_files):
            print(f'\n🔍 Analyzing: {filename}')
            comparison = self.compare_file_versions(filename)
            results['comparisons'][filename] = comparison
            results['summary'][comparison['decision']] += 1
            print(f"   Decision: {comparison['decision']}")
            print(f"   Reason: {comparison['reason']}")
        return results

def main():
    """Run the SSOT consolidation analysis."""
    analyzer = SSOTConsolidationAnalyzer()
    results = analyzer.analyze_all_files()
    print('\n' + '=' * 60)
    print('📋 SSOT CONSOLIDATION SUMMARY')
    print('=' * 60)
    for decision, count in results['summary'].items():
        print(f'{decision}: {count} files')
    with open('ssot_consolidation_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('\n💾 Analysis saved to: ssot_consolidation_analysis.json')
    print('\n✅ Ready for SSOT consolidation execution!')
    return results
if __name__ == '__main__':
    main()
