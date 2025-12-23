"""
NamingEnforcer Agent - Semantic Naming Guardian.
Enforces intention-revealing names and PEP 8 compliance.
"""

import ast
import asyncio
import datetime
import time
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class NamingEnforcer(SubAtomicAgent):
    """ROLE: Semantic Naming Guardian. Enforces intention-revealing names."""

    # Mutation mode flag - when True, actively fix files instead of just reporting
    mutation_mode: bool = False

    ABBREVIATION_MAP = {
        'mgr': 'manager', 'cfg': 'config', 'val': 'value', 'var': 'variable',
        'param': 'parameter', 'temp': 'temporary', 'calc': 'calculate',
        'init': 'initialize', 'proc': 'process', 'msg': 'message',
        'ctx': 'context', 'req': 'request', 'resp': 'response',
        'func': 'function', 'attr': 'attribute', 'err': 'error',
        'res': 'result', 'idx': 'index', 'cnt': 'count',
    }

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Semantic Naming...")
        await asyncio.sleep(0)

        target_files = list(getattr(self.ctx, 'modified_files', self.ctx.python_files))

        if not target_files:
            print("   ✅ No files to check for naming")
            return

        print(f"   🔍 Analyzing naming in {len(target_files)} files...")

        naming_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = self._analyze_naming(file_path)
            if result:
                naming_log.append(result)

        if naming_log:
            print(f"   ⚠️  Naming issues found in {len(naming_log)} files")
            # Check if mutation mode is active (from targeted remediation)
            if self.mutation_mode or any('MUTATION MODE' in i for i in self.ctx.instructions):
                print("   🔧 MUTATION MODE: Fixing naming issues...")
                await self._fix_naming_issues(naming_log)
            else:
                self._save_naming_report(naming_log)
        else:
            print("   ✅ All names comply with semantic standards")

    def _analyze_naming(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            symbols = self._extract_symbols(content)
            issues = self._check_naming_issues(symbols)

            if issues:
                return {'file': file_path, 'symbols': symbols, 'issues': issues}
        except Exception:
            pass
        return None

    def _extract_symbols(self, content: str) -> Dict:
        symbols = {'classes': [], 'functions': [], 'variables': [], 'abbreviations': []}

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols['classes'].append(node.name)
                    self._check_abbreviations(node.name, symbols['abbreviations'])

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols['functions'].append(node.name)
                    self._check_abbreviations(node.name, symbols['abbreviations'])

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols['variables'].append(target.id)
                            self._check_abbreviations(target.id, symbols['abbreviations'])
        except Exception:
            pass

        return symbols

    def _check_abbreviations(self, name: str, abbreviations: List):
        name_lower = name.lower()
        for abbrev, full_word in self.ABBREVIATION_MAP.items():
            if abbrev in name_lower and name_lower != full_word:
                abbreviations.append({
                    'name': name,
                    'abbreviation': abbrev,
                    'suggestion': name_lower.replace(abbrev, full_word)
                })

    def _check_naming_issues(self, symbols: Dict) -> List[str]:
        issues = []

        if symbols['abbreviations']:
            issues.append(f"Contains {len(symbols['abbreviations'])} abbreviations")

        for name in symbols['functions'] + symbols['variables']:
            if self._is_camel_case(name):
                issues.append(f"'{name}' uses camelCase instead of snake_case")

        return issues

    def _is_camel_case(self, name: str) -> bool:
        return name != name.lower() and '_' not in name and name[0].islower()

    def _save_naming_report(self, log_entries: List[Dict]):
        timestamp = int(time.time())
        report_path = f"observability/audit/naming_refactor_{timestamp}.md"

        report_content = f"# Naming Refactor Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n- Files analyzed: {len(log_entries)}\n\n"

        for entry in log_entries:
            report_content += f"### {entry['file']}\n\n"
            for issue in entry['issues']:
                report_content += f"- {issue}\n"
            report_content += "\n"

        self.ctx.write_compliant_file(report_path, report_content)

    async def _fix_naming_issues(self, naming_log: List[Dict]):
        """Fix naming issues by expanding abbreviations and converting camelCase."""
        for entry in naming_log:
            file_path = entry['file']
            symbols = entry['symbols']

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                modified = False

                # Fix abbreviations
                for abbrev_info in symbols.get('abbreviations', []):
                    old_name = abbrev_info['name']
                    new_name = abbrev_info['suggestion']
                    if old_name in content and old_name != new_name:
                        # Only replace if it's a complete word (not part of another word)
                        import re
                        pattern = r'\b' + re.escape(old_name) + r'\b'
                        if re.search(pattern, content):
                            content = re.sub(pattern, new_name, content)
                            modified = True
                            print(f"      Renamed: {old_name} -> {new_name}")

                # Fix camelCase to snake_case for functions/variables
                for name in symbols.get('functions', []) + symbols.get('variables', []):
                    if self._is_camel_case(name):
                        snake_name = self._to_snake_case(name)
                        import re
                        pattern = r'\b' + re.escape(name) + r'\b'
                        if re.search(pattern, content):
                            content = re.sub(pattern, snake_name, content)
                            modified = True
                            print(f"      Converted: {name} -> {snake_name}")

                if modified:
                    if self.ctx.write_compliant_file(file_path, content):
                        print(f"   ✅ Fixed naming in: {file_path}")

            except Exception as e:
                print(f"   ❌ Failed to fix naming in {file_path}: {e}")

    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        import re

        # Insert underscore before uppercase letters and convert to lowercase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
