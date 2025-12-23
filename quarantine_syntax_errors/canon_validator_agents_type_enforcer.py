"""
TypeEnforcer Agent - Type Guardian.
Enforces PEP 484 type hints for compile-time contracts.
"""

import ast
import asyncio
import datetime
import time
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class TypeEnforcer(SubAtomicAgent):
    """ROLE: Type Guardian. Enforces PEP 484 type hints."""

    # Mutation mode flag - when True, actively fix files instead of just reporting
    mutation_mode: bool = False

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
            # Check if mutation mode is active (from targeted remediation)
            if self.mutation_mode or any('MUTATION MODE' in i for i in self.ctx.instructions):
                print("   🔧 MUTATION MODE: Injecting missing typing imports...")
                await self._inject_typing_imports(type_log)
            else:
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

    async def _inject_typing_imports(self, type_log: List[Dict]):
        """Inject missing typing imports (Any, Dict, List) into files."""
        TYPING_IMPORTS = "from typing import Any, Dict, List, Optional, Set, Tuple"

        for entry in type_log:
            file_path = entry['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if typing imports already exist
                if 'from typing import' in content:
                    # Enhance existing import
                    lines = content.split('\n')
                    new_lines = []
                    typing_enhanced = False
                    for line in lines:
                        if line.strip().startswith('from typing import') and not typing_enhanced:
                            # Replace with comprehensive typing import
                            new_lines.append(TYPING_IMPORTS)
                            typing_enhanced = True
                        else:
                            new_lines.append(line)
                    content = '\n'.join(new_lines)
                elif 'import ' in content:
                    # Add typing import after first import
                    lines = content.split('\n')
                    new_lines = []
                    typing_added = False
                    for line in lines:
                        new_lines.append(line)
                        if line.strip().startswith('import ') and not typing_added:
                            new_lines.append(TYPING_IMPORTS)
                            typing_added = True
                    content = '\n'.join(new_lines)
                else:
                    # Add at top of file (after docstring if present)
                    if content.startswith('"""') or content.startswith("'''"):
                        # Find end of docstring
                        quote = content[:3]
                        end_idx = content.find(quote, 3)
                        if end_idx != -1:
                            end_idx += 3
                            content = content[:end_idx] + '\n\n' + TYPING_IMPORTS + '\n' + content[end_idx:]
                    else:
                        content = TYPING_IMPORTS + '\n\n' + content

                # Write the updated file
                if self.ctx.write_compliant_file(file_path, content):
                    print(f"   ✅ Injected typing imports: {file_path}")

            except Exception as e:
                print(f"   ❌ Failed to inject typing in {file_path}: {e}")
