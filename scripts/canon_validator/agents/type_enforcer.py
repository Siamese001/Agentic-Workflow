"""
TypeEnforcer Agent - Type Guardian.
Enforces PEP 484 type hints for compile-time contracts.
"""

import ast
import asyncio
import time
import datetime
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class TypeEnforcer(SubAtomicAgent):
    """ROLE: Type Guardian. Enforces PEP 484 type hints."""

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Type Contracts...")
        await asyncio.sleep(0)

        modified_files = getattr(self.ctx, 'modified_files', set())
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   ✅ No files to check for typing")
            return

        print(f"   🔍 Analyzing types in {len(target_files)} files...")

        type_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = self._analyze_typing(file_path)
            if result:
                type_log.append(result)

        if type_log:
            print(f"   ⚠️  Type issues in {len(type_log)} files")
            self._save_type_report(type_log)
        else:
            print("   ✅ All functions properly typed")

    def _analyze_typing(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            analysis = self._check_type_hints(content)

            if not analysis['is_fully_typed']:
                return {'file': file_path, 'analysis': analysis}
        except Exception:
            pass
        return None

    def _check_type_hints(self, content: str) -> Dict:
        analysis = {
            'is_fully_typed': False,
            'untyped_functions': [],
            'partially_typed': []
        }

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private and test methods
                    if node.name.startswith('_') or 'test' in node.name.lower():
                        continue

                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'return_annotated': node.returns is not None
                    }

                    # Check parameter annotations
                    all_args_typed = True
                    for arg in node.args.args:
                        if arg.annotation is None:
                            all_args_typed = False

                    if not all_args_typed or not func_info['return_annotated']:
                        if all_args_typed or func_info['return_annotated']:
                            analysis['partially_typed'].append(func_info)
                        else:
                            analysis['untyped_functions'].append(func_info)

            analysis['is_fully_typed'] = (
                not analysis['untyped_functions'] and
                not analysis['partially_typed']
            )

        except Exception:
            pass

        return analysis

    def _save_type_report(self, log_entries: List[Dict]):
        timestamp = int(time.time())
        report_path = f"observability/audit/type_refinement_{timestamp}.md"

        report_content = f"# Type Refinement Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n- Files analyzed: {len(log_entries)}\n\n"

        for entry in log_entries:
            report_content += f"### {entry['file']}\n\n"
            analysis = entry['analysis']
            if analysis['untyped_functions']:
                report_content += f"- Untyped functions: {len(analysis['untyped_functions'])}\n"
            if analysis['partially_typed']:
                report_content += f"- Partially typed: {len(analysis['partially_typed'])}\n"
            report_content += "\n"

        self.ctx.write_compliant_file(report_path, report_content)
