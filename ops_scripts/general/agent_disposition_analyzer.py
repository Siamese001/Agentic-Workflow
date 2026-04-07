"""
Global Core Eviction & Agent Disposition Analysis Tool

Analyzes all files in apps_shared/base_agents/ for Functional DNA classification.
Categorizes files into: CORE FOUNDATION, ACTIVE SPECIALISTS, STATELESS TOOLS, LEGACY ARTIFACTS
"""
import ast
from pathlib import Path


class AgentDispositionAnalyzer:
    """Analyzes agent files for functional DNA classification."""

    def __init__(self, base_path: str='apps_shared/base_agents'):
        self.base_path = Path(base_path)
        self.classifications = {'CORE_FOUNDATION': [], 'ACTIVE_SPECIALISTS': [], 'STATELESS_TOOLS': [], 'LEGACY_ARTIFACTS': []}
        self.analysis_details = {}

    def analyze_file(self, file_path: Path) -> tuple[str, dict]:
        """Analyze a single Python file for functional DNA."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            try:
                tree = ast.parse(content)
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                return ('LEGACY_ARTIFACTS', {'reason': 'Syntax error - likely legacy code'})
            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classification, details = self._classify_disposition(file_path.name, content, classes, imports, functions)
            return (classification, details)
        # guardian: allow-silent-swallow
        except Exception as e:
            return ('LEGACY_ARTIFACTS', {'reason': f'Error reading file: {e}'})

    def _extract_classes(self, tree: ast.AST) -> list[dict]:
        """Extract class information from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                is_agent = node.name.endswith('Agent')
                is_dataclass = any(isinstance(dec, ast.Name) and dec.id == 'dataclass' or (isinstance(dec, ast.Attribute) and dec.attr == 'dataclass') for dec in node.decorator_list)
                classes.append({'name': node.name, 'bases': bases, 'is_agent': is_agent, 'is_dataclass': is_dataclass, 'has_agent_suffix': 'Agent' in node.name, 'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0})
        return classes

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f'{module}.{alias.name}' if module else alias.name)
        return imports

    def _extract_functions(self, tree: ast.AST) -> list[dict]:
        """Extract function information."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({'name': node.name, 'is_method': node.name.startswith('_') or node.name in ['__init__', '_process', 'run_phase'], 'args_count': len(node.args.args)})
        return functions

    def _classify_disposition(self, filename: str, content: str, classes: list[dict], imports: list[str], functions: list[dict]) -> tuple[str, dict]:
        """Classify file based on functional DNA analysis."""
        legacy_indicators = ['deprecated', 'v107', 'v12', 'old', 'legacy', 'obsolete']
        if any(indicator in content.lower() for indicator in legacy_indicators):
            return ('LEGACY_ARTIFACTS', {'reason': 'Contains legacy/deprecated markers'})
        core_patterns = ['Mixin', 'Base', 'Interface', 'Protocol', 'Abstract', 'HealerMixin', 'MCPHardenedMixin', 'SubatomicTestingMixin', 'canon_base_agent_interface', 'foundation']
        if any(pattern in filename.lower() or pattern in content for pattern in core_patterns):
            return ('CORE_FOUNDATION', {'reason': 'Contains core foundation patterns'})
        agent_classes = [c for c in classes if c['is_agent'] or c['has_agent_suffix']]
        if agent_classes and len(classes) == 1:
            has_init = any(f['name'] == '__init__' for f in functions)
            has_process = any(f['name'] in ['_process', 'run_phase', 'execute'] for f in functions)
            if has_init and (has_process or len(functions) > 3):
                return ('ACTIVE_SPECIALISTS', {'reason': 'Complete agent with initialization and processing logic', 'agent_class': agent_classes[0]['name']})
        if not agent_classes and len(functions) > 0:
            return ('STATELESS_TOOLS', {'reason': 'Functional utilities without agent state', 'function_count': len(functions)})
        validator_patterns = ['validator', 'validatoragent', 'enforcer', 'healer', 'detector']
        if any(pattern in filename.lower() for pattern in validator_patterns):
            if agent_classes:
                return ('ACTIVE_SPECIALISTS', {'reason': 'Specialized validator/enforcer agent'})
            else:
                return ('STATELESS_TOOLS', {'reason': 'Validation utility functions'})
        return ('LEGACY_ARTIFACTS', {'reason': 'Unclear classification - treating as legacy'})

    def analyze_directory(self) -> dict:
        """Analyze all Python files in the directory."""
        if not self.base_path.exists():
            return {'error': f'Directory {self.base_path} does not exist'}
        python_files = list(self.base_path.glob('*.py'))
        results = {'total_files': len(python_files), 'classifications': self.classifications.copy(), 'analysis_details': {}, 'summary': {}}
        for file_path in python_files:
            if file_path.name == '__init__.py':
                continue
            classification, details = self.analyze_file(file_path)
            self.classifications[classification].append(file_path.name)
            self.analysis_details[file_path.name] = {'classification': classification, 'details': details}
        results['classifications'] = self.classifications
        results['analysis_details'] = self.analysis_details
        results['summary'] = {category: len(files) for category, files in self.classifications.items()}
        return results

def main():
    """Run the analysis and generate disposition report."""
    print('🔍 GLOBAL CORE EVICTION & AGENT DISPOSITION ANALYSIS')
    print('=' * 60)
    analyzer = AgentDispositionAnalyzer()
    results = analyzer.analyze_directory()
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    print(f"📊 Total Files Analyzed: {results['total_files']}")
    print('\n📋 CLASSIFICATION SUMMARY:')
    print('-' * 40)
    for category, count in results['summary'].items():
        print(f"{category.replace('_', ' ')}: {count} files")
    print('\n📄 DETAILED DISPOSITION:')
    print('-' * 40)
    for category, files in results['classifications'].items():
        if files:
            print(f"\n🏷️ {category.replace('_', ' ')} ({len(files)} files):")
            for filename in sorted(files):
                details = results['analysis_details'][filename]['details']
                reason = details.get('reason', 'No specific reason')
                print(f'   • {filename} - {reason}')
    import json
    with open('agent_disposition_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('\n💾 Analysis saved to: agent_disposition_analysis.json')
    print('\n✅ Analysis complete - Ready for disposition execution!')
if __name__ == '__main__':
    main()
