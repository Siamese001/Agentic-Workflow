"""
DocEnforcer Agent - Documentation Surgeon.
Ensures 100% docstring coverage for subatomic units.
"""

import ast
import asyncio
import time
import datetime
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class DocEnforcer(SubAtomicAgent):
    """ROLE: Documentation Surgeon. Ensures 100% docstring coverage."""

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Documentation Standards...")
        await asyncio.sleep(0)

        modified_files = getattr(self.ctx, 'modified_files', set())
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   ✅ No files to check for documentation")
            return

        print(f"   📝 Checking documentation for {len(target_files)} files...")

        doc_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = self._analyze_documentation(file_path)
            if result:
                doc_log.append(result)

        if doc_log:
            print(f"   ⚠️  Documentation issues in {len(doc_log)} files")
            self._save_doc_report(doc_log)
        else:
            print("   ✅ All documentation meets standards")

    def _analyze_documentation(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            analysis = self._check_docstrings(content)

            if not analysis['is_complete']:
                return {'file': file_path, 'analysis': analysis}
        except Exception:
            pass
        return None

    def _check_docstrings(self, content: str) -> Dict:
        analysis = {
            'is_complete': False,
            'has_module_doc': False,
            'missing_class_docs': [],
            'missing_function_docs': [],
        }

        try:
            tree = ast.parse(content)

            # Check module docstring
            if ast.get_docstring(tree):
                analysis['has_module_doc'] = True

            # Check classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        analysis['missing_class_docs'].append(node.name)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith('_'):
                        continue
                    if not ast.get_docstring(node):
                        analysis['missing_function_docs'].append(node.name)

            analysis['is_complete'] = (
                analysis['has_module_doc'] and
                not analysis['missing_class_docs'] and
                not analysis['missing_function_docs']
            )

        except Exception:
            pass

        return analysis

    def _save_doc_report(self, log_entries: List[Dict]):
        timestamp = int(time.time())
        report_path = f"observability/audit/doc_refinement_{timestamp}.md"

        report_content = f"# Documentation Refinement Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n- Files analyzed: {len(log_entries)}\n\n"

        for entry in log_entries:
            report_content += f"### {entry['file']}\n\n"
            analysis = entry['analysis']
            report_content += f"- Module doc: {'✅' if analysis['has_module_doc'] else '❌'}\n"
            if analysis['missing_class_docs']:
                report_content += f"- Missing class docs: {', '.join(analysis['missing_class_docs'])}\n"
            if analysis['missing_function_docs']:
                report_content += f"- Missing function docs: {', '.join(analysis['missing_function_docs'][:5])}\n"
            report_content += "\n"

        self.ctx.write_compliant_file(report_path, report_content)
