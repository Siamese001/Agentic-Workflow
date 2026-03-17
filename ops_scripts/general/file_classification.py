"""
_emit_reads_through("l4", "file_classification", "urg_read_1")
_emit_reads_through("l4", "file_classification", "urg_read_2")
_emit_reads_through("l4", "file_classification", "urg_read_3")
_emit_reads_through("l4", "file_classification", "urg_read_4")
_emit_reads_through("l4", "file_classification", "urg_read_5")
_emit_reads_through("l4", "file_classification", "urg_read_6")
_emit_reads_through("l4", "file_classification", "urg_read_7")
_emit_reads_through("l4", "file_classification", "urg_read_8")
_emit_reads_through("l4", "file_classification", "urg_read_9")
_emit_reads_through("l4", "file_classification", "urg_read_10")
_emit_reads_through("l4", "file_classification", "urg_read_11")
_emit_reads_through("l4", "file_classification", "urg_read_12")
_emit_reads_through("l4", "file_classification", "urg_read_13")
_emit_reads_through("l4", "file_classification", "urg_read_14")
_emit_reads_through("l4", "file_classification", "urg_read_15")
_emit_reads_through("l4", "file_classification", "urg_read_16")
_emit_reads_through("l4", "file_classification", "urg_read_17")
_emit_reads_through("l4", "file_classification", "urg_read_18")
_emit_reads_through("l4", "file_classification", "urg_read_19")
_emit_reads_through("l4", "file_classification", "urg_read_20")
_emit_reads_through("l4", "file_classification", "urg_read_21")
_emit_reads_through("l4", "file_classification", "urg_read_22")
_emit_reads_through("l4", "file_classification", "urg_read_23")
_emit_reads_through("l4", "file_classification", "urg_read_24")
_emit_reads_through("l4", "file_classification", "urg_read_25")
_emit_reads_through("l4", "file_classification", "urg_read_26")
_emit_reads_through("l4", "file_classification", "urg_read_27")
_emit_reads_through("l4", "file_classification", "urg_read_28")
_emit_reads_through("l4", "file_classification", "urg_read_29")
_emit_reads_through("l4", "file_classification", "urg_read_30")
_emit_reads_through("l4", "file_classification", "urg_read_31")
_emit_reads_through("l4", "file_classification", "urg_read_32")
_emit_reads_through("l4", "file_classification", "urg_read_33")
_emit_reads_through("l4", "file_classification", "urg_read_34")
_emit_reads_through("l4", "file_classification", "urg_read_35")
_emit_reads_through("l4", "file_classification", "urg_read_36")
_emit_reads_through("l4", "file_classification", "urg_read_37")
AST-Based Agent Consolidation Audit Script (V2.5).

Performs AST-level analysis of apps_lic/ to enforce Sovereign Specialist pattern.
"""
import ast
import json
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through


@dataclass
class FileClassification:
    """Classification result for a Python file."""
    path: Path
    category: str
    class_name: str = ''
    base_classes: list[str] = field(default_factory=list)
    has_v2_base: bool = False
    has_enum: bool = False
    has_k_node: bool = False
    has_state_manager: bool = False
    has_immutable_buffer: bool = False
    issues: list[str] = field(default_factory=list)

class AppsLicASTAuditor:
    """AST-based auditor for apps_lic/ directory."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.classifications: list[FileClassification] = []

    def discover_and_classify(self) -> list[FileClassification]:
        """Discover all Python files and classify them via AST analysis."""
        py_files = list(self.root_path.rglob('*.py'))
        for py_file in py_files:
            if '__pycache__' in str(py_file) or '__init__.py' in py_file.name:
                continue
            classification = self._classify_audit_category(py_file)
            self.classifications.append(classification)
        return self.classifications

    def _classify_audit_category(self, file_path: Path) -> FileClassification:
        """Classify a single file using AST analysis."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
        # guardian: allow-silent-swallow
        except Exception as e:
            return FileClassification(path=file_path, category='UNKNOWN', issues=[f'Parse error: {str(e)}'])
        classification = FileClassification(path=file_path, category='UNKNOWN')
        imports = self._extract_imports(tree)
        classification.has_immutable_buffer = 'ImmutableStagingBuffer' in imports
        classification.has_state_manager = 'StateManager' in imports or 'state_mgr' in content.lower()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classification.class_name = node.name
                classification.base_classes = self._extract_base_classes(node)
                if any(b in classification.base_classes for b in ['V2AgentBase', 'SubatomicTestingMixin', 'MCPHardenedMixin', 'HealerMixin']):
                    classification.has_v2_base = True
                    classification.category = 'SOVEREIGN_AGENT'
                if 'Enum' in classification.base_classes or 'IntEnum' in classification.base_classes:
                    classification.has_enum = True
                    classification.category = 'SUPPORT_STRUCTURE'
                    if 'Agent' in node.name:
                        classification.issues.append("Enum mislabeled as 'Agent'")
                if 'BaseModel' in classification.base_classes:
                    classification.category = 'SUPPORT_STRUCTURE'
                if 'Agent' in node.name and (not classification.base_classes) and (classification.category == 'UNKNOWN'):
                    classification.category = 'SPECIALIST_NODE'
        if self._has_k_node_logic(content):
            classification.has_k_node = True
            if classification.category == 'UNKNOWN':
                classification.category = 'SPECIALIST_NODE'
        if classification.has_state_manager and (not classification.has_immutable_buffer):
            classification.issues.append('Uses deprecated StateManager instead of ImmutableStagingBuffer')
            if 'DEPRECATED' in content or 'deprecated' in content.lower():
                classification.category = 'DEPRECATED'
        if 'HOP2_ResearchAgent' in file_path.name and 'DEPRECATED' in content:
            classification.category = 'DEPRECATED'
        return classification

    def _extract_imports(self, tree: ast.AST) -> set[str]:
        """Extract all imported names from AST."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
        return imports

    def _extract_base_classes(self, class_node: ast.ClassDef) -> list[str]:
        """Extract base class names from a class definition."""
        bases = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
        return bases

    def _has_k_node_logic(self, content: str) -> bool:
        """Check if file contains K-Node logic patterns."""
        k_node_patterns = ['K.1', 'K.2', 'K.3', 'K.4', 'K.5', 'K.6', 'K.7', 'CXO_PRECEDENCE', 'GATE_', 'ENTRANCE_GATE', 'K_NODE_ID', 'RETRIEVAL_PLAN', 'MESSAGE_ARCHITECT']
        return any(pattern in content for pattern in k_node_patterns)

    def generate_audit_ledger(self) -> str:
        """Generate audit ledger table."""
        lines = []
        lines.append('# AST-Based Audit Ledger (V2.5)')
        lines.append('')
        lines.append('| File | Category | Class | Base Classes | Issues |')
        lines.append('|------|----------|-------|--------------|--------|')
        for c in sorted(self.classifications, key=lambda x: (x.category, x.path.name)):
            file_name = c.path.name
            category = c.category
            class_name = c.class_name or 'N/A'
            bases = ', '.join(c.base_classes[:3]) if c.base_classes else 'N/A'
            issues = '; '.join(c.issues) if c.issues else 'None'
            lines.append(f'| {file_name} | {category} | {class_name} | {bases} | {issues} |')
        return '\n'.join(lines)

    def generate_statistics(self) -> dict[str, int]:
        """Generate statistics by category."""
        stats = {}
        for c in self.classifications:
            stats[c.category] = stats.get(c.category, 0) + 1
        return stats

    def identify_consolidation_opportunities(self) -> list[tuple[str, list[Path]]]:
        """Identify files that should be consolidated."""
        opportunities = []
        name_groups = {}
        for c in self.classifications:
            base_name = c.path.stem.lower().replace('_', '').replace('agent', '')
            if base_name not in name_groups:
                name_groups[base_name] = []
            name_groups[base_name].append(c.path)
        for base_name, paths in name_groups.items():
            if len(paths) > 1:
                opportunities.append((base_name, paths))
        return opportunities

    def generate_refactoring_recommendations(self) -> list[str]:
        """Generate refactoring recommendations."""
        recommendations = []
        for c in self.classifications:
            if c.has_enum and 'Agent' in c.class_name:
                new_name = c.path.stem.replace('Agent', '').lower() + '_types.py'
                recommendations.append(f'RENAME: {c.path.name} → {new_name} (Enum, not Agent)')
            if c.has_state_manager and (not c.has_immutable_buffer):
                recommendations.append(f'REFACTOR: {c.path.name} - Replace StateManager with ImmutableStagingBuffer')
            if 'Agent' in c.class_name and (not c.has_v2_base) and (not c.has_enum):
                if c.category not in ['DEPRECATED', 'SUPPORT_STRUCTURE']:
                    recommendations.append(f'UPGRADE: {c.path.name} - Add V2AgentBase inheritance')
        return recommendations

def main():
    """Run the audit."""
    root = Path('C:/Git/Agentic-Workflow/apps_lic')
    auditor = AppsLicASTAuditor(root)
    print('🔍 Discovering and classifying files...')
    classifications = auditor.discover_and_classify()
    print(f'\n✅ Analyzed {len(classifications)} files\n')
    stats = auditor.generate_statistics()
    print('📊 Statistics by Category:')
    for category, count in sorted(stats.items()):
        print(f'  {category}: {count}')
    print('\n' + '=' * 80)
    ledger = auditor.generate_audit_ledger()
    print(ledger)
    print('\n' + '=' * 80)
    print('\n🔄 Consolidation Opportunities:')
    opportunities = auditor.identify_consolidation_opportunities()
    for base_name, paths in opportunities:
        print(f'\n  Group: {base_name}')
        for path in paths:
            print(f'    - {path.name}')
    print('\n' + '=' * 80)
    print('\n🛠️ Refactoring Recommendations:')
    recommendations = auditor.generate_refactoring_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f'  {i}. {rec}')
    output_path = Path('agentic_core/L0_routing/utils/audit_apps_lic_ast_results.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = {'total_files': len(classifications), 'statistics': stats, 'classifications': [{'file': str(c.path.relative_to(root)), 'category': c.category, 'class_name': c.class_name, 'base_classes': c.base_classes, 'issues': c.issues} for c in classifications], 'recommendations': recommendations}
    output_path.write_text(json.dumps(results, indent=2))
    print(f'\n💾 Results saved to: {output_path}')
if __name__ == '__main__':
    main()
