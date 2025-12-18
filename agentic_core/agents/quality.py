"""
agentic_core/agents/quality.py
Depth: 3
Role: Enforces code quality, style consistency, and performance standards.
"""
import ast
import os
import re
import asyncio
import time
import datetime
from typing import List, Tuple, Dict, Any

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.domain.constants import EXCLUDED_DIRS


class HygieneGuardian(SubAtomicAgent):
    """
    Unified Hygiene Agent.
    Merges GenerativeGuard (Key 45) and TheCurator (File Taxonomy).
    """
    
    GENERATIVE_PATTERNS = [
        r"_impl_impl_",
        r"generated_\d+",
        r"auto_\w+_\d+",
        r"temp_\w+_\d+"
    ]

    SCRIPT_CATEGORIES = {
        'maintenance', 'setup', 'migration', 'testing', 'archive'
    }
    
    IMMUTABLE_FILES = {
        'canon_validator_v2_agentic.py',
        'auto_canon.py',
        'setup.py',
        'README.md',
        'canon_validator_agentic.py' 
    }

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Project Hygiene...")
        await asyncio.sleep(0)
        await self._purge_generative_artifacts()
        self.ctx.signals.add("GENERATIVE_CLEAN")

    async def _purge_generative_artifacts(self):
        violations = []
        for root, dirs, files in os.walk("."):
            if any(x in root for x in EXCLUDED_DIRS): continue
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path) and file.endswith('.py'):
                    for pattern in self.GENERATIVE_PATTERNS:
                        if re.search(pattern, file):
                            violations.append(file_path)
                            break
        
        if violations:
            print(f"   🧹 Found {len(violations)} generative artifacts")
            for file_path in violations:
                try:
                    os.remove(file_path)
                    print(f"      DELETED: {file_path}")
                except Exception as e:
                    print(f"      Failed: {e}")
        else:
            self.ctx.report(self.name, 45, True, [])
    
    async def propose_hygiene_fix(self, file_path: str, issues: List[str]) -> str:
        """L5+ Use LLM with few-shot to propose hygiene fixes."""
        if not self.ctx.intelligence_enabled:
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return ""
        
        issues_summary = "\n".join([f"- {i}" for i in issues[:10]])
        
        prompt = f"""
{self.ctx.FEW_SHOT_HYGIENE}

<primary_issues>
{issues_summary}
</primary_issues>

<preserve_keywords>__all__, abstractmethod, @override, __init__, __new__, __del__</preserve_keywords>

<code_to_clean>
{content[:4000]}
</code_to_clean>

Apply the most relevant example above.
Prioritize:
- Remove unused imports
- Inline or remove unused variables
- Preserve __all__, abstract methods, dunder
- Simplify redundant boolean logic
- Remove obsolete comments only

Never remove docstrings, type hints, or intentional placeholders.
Be conservative: when in doubt, preserve.

RESPONSE FORMAT:
Return ONLY the cleaned Python code.
No unused imports. No dead variables.
Preserve __all__ and docstrings.
No trailing whitespace.
"""
        
        return await self.ctx.resilient_mutation(
            self.name, prompt, code=content, file_path=file_path, max_attempts=2
        )


class CodeStyleGuardian(SubAtomicAgent):
    """
    Unified Style & Cleanliness Agent.
    Merges CodeJanitor (Keys 10-16) and StyleGuardian (Keys 21, 47).
    """

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Code Style & Hygiene...")
        await asyncio.sleep(0)

        self._cleanup_empty_files()
        
        self.ctx.report(self.name, 11, *self._check_no_trailing_whitespace())
        self.ctx.report(self.name, 12, *self._check_no_missing_newline())
        self.ctx.report(self.name, 13, *self._check_no_tabs())
        self.ctx.report(self.name, 10, *self._check_line_length())
        self.ctx.report(self.name, 15, *self._check_magic_numbers())
        self.ctx.report(self.name, 16, *self._check_nesting_depth())
        
        doc_violations = await self._check_documentation()
        self.ctx.report(self.name, 21, len(doc_violations) == 0, doc_violations)
        
        naming_violations = await self._check_naming()
        self.ctx.report(self.name, 47, len(naming_violations) == 0, naming_violations)

    def _cleanup_empty_files(self):
        count = 0
        for root, _, files in os.walk("."):
            if any(x in root for x in EXCLUDED_DIRS): continue
            for file in files:
                p = os.path.join(root, file)
                try:
                    if os.path.getsize(p) == 0:
                        os.remove(p)
                        count += 1
                except: pass
        if count: print(f"      🗑️  Deleted {count} empty files.")

    def _check_line_length(self) -> Tuple[bool, List[str]]:
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if len(line.rstrip()) > 150: violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)

    def _check_magic_numbers(self) -> Tuple[bool, List[str]]:
        violations = []
        allowed = {0, 1, -1, 2, 10, 100, 200, 404, 500, 1000, 0.0, 1.0, 0.5}
        for f in self.ctx.python_files:
            if 'test' in f: continue
            try:
                tree = ast.parse(open(f, encoding='utf-8').read())
                for n in ast.walk(tree):
                    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                        if n.value not in allowed: violations.append(f"{f}:{n.lineno}")
            except: pass
        return (not violations, violations)
    
    def _check_nesting_depth(self) -> Tuple[bool, List[str]]:
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if (len(line) - len(line.lstrip())) > 40: violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)

    def _check_no_trailing_whitespace(self) -> Tuple[bool, List[str]]:
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if line.endswith(' \n') or line.endswith('\t\n'):
                        violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)
        
    def _check_no_missing_newline(self) -> Tuple[bool, List[str]]:
        violations = []
        for f in self.ctx.python_files:
            try:
                with open(f, 'rb') as file:
                    content = file.read()
                    if content and not content.endswith(b'\n'):
                        violations.append(f)
            except: pass
        return (not violations, violations)
        
    def _check_no_tabs(self) -> Tuple[bool, List[str]]:
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if '\t' in line: violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)
    
    async def _check_documentation(self) -> List[str]:
        violations = []
        for file_path in self.ctx.python_files:
            if 'test_' in file_path or file_path.endswith('__init__.py'):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                if not ast.get_docstring(tree):
                    violations.append(f"{file_path}: Missing module docstring")
            except: pass
        return violations

    async def _check_naming(self) -> List[str]:
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase")
            except: pass
        return violations
    
    async def propose_style_fix(self, file_path: str, violations: List[str]) -> str:
        """L5+ Use LLM with few-shot to propose style fixes."""
        if not self.ctx.intelligence_enabled:
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return ""
        
        violations_summary = "\n".join([f"- {v}" for v in violations[:10]])
        
        prompt = f"""
{self.ctx.FEW_SHOT_STYLE}

<primary_issues>
{violations_summary}
</primary_issues>

<code_to_fix>
{content[:4000]}
</code_to_fix>

Apply the most relevant example above.
Prioritize:
- Correct isort sections
- Black-compatible line wrapping
- Full type hints
- f-strings
- Google-style docstrings
- PEP8 naming

Preserve all logic and comments.

RESPONSE FORMAT:
Return ONLY the reformatted Python code.
Exact black formatting. No trailing whitespace.
No explanations. No markdown outside code block.
"""
        
        return await self.ctx.resilient_mutation(
            self.name, prompt, code=content, file_path=file_path, max_attempts=2
        )


class PerformanceEnforcer(SubAtomicAgent):
    """ROLE: Performance Guardian. Identifies and remediates computational inefficiencies."""
    
    # Performance anti-patterns for fast scanning
    PERFORMANCE_PATTERNS = {
        'n_plus_one_query': re.compile(
            r'for\s+\w+\s+in.*:\s*.*query\(|'
            r'\.query\(.*\).*\s+for\s+|'
            r'for.*in.*:\s*.*\.get\(',
            re.IGNORECASE | re.MULTILINE
        ),
        'string_concat_loop': re.compile(
            r'for\s+\w+\s+in.*:\s*.*\w+\s*\+=\s*["\']',
            re.IGNORECASE | re.MULTILINE
        ),
        'blocking_sleep': re.compile(
            r'time\.sleep\(',
            re.IGNORECASE
        ),
        'blocking_requests': re.compile(
            r'requests\.(get|post|put|delete|patch)\(',
            re.IGNORECASE
        ),
        'inefficient_list_build': re.compile(
            r'\[\]\s*;\s*for\s+\w+\s+in.*:\s*.*\.append\(',
            re.IGNORECASE | re.MULTILINE
        ),
        'nested_loops_deep': re.compile(
            r'for\s+\w+\s+in.*:\s*.*for\s+\w+\s+in.*:\s*.*for\s+\w+\s+in',
            re.IGNORECASE | re.MULTILINE
        ),
        'regex_compile_each_time': re.compile(
            r're\.(match|search|findall)\(["\'].*["\']',
            re.IGNORECASE
        )
    }
    
    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Optimizing Performance...")
        await asyncio.sleep(0)
        
        # Priority 1: Process modified files
        modified_files = getattr(self.ctx, 'modified_files', set())
        
        # Priority 2: Fall back to all Python files if no tracking
        target_files = list(modified_files) if modified_files else self.ctx.python_files
        
        if not target_files:
            print("   ✅ No files to check for performance")
            return
        
        print(f"   ⚡ Analyzing performance in {len(target_files)} files...")
        print(f"   🎯 Priority: Modified files ({len(modified_files)}) + {len(target_files) - len(modified_files)} others")
        
        # Track performance optimizations
        perf_log = []
        optimized_files = []
        
        # Scan and optimize files
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            
            result = await self._scan_and_optimize(file_path)
            if result:
                optimized_files.append(file_path)
                perf_log.append(result)
        
        # Save performance report
        self._save_performance_report(perf_log, optimized_files)
        
        if optimized_files:
            print(f"   ⚡ Performance optimized in {len(optimized_files)} files")
        else:
            print("   ✅ No performance issues detected")
    
    async def _scan_and_optimize(self, file_path: str) -> Dict | None:
        """Scan file for performance issues and apply optimizations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pass 1: Fast regex scanning
            detected_issues = self._detect_performance_issues(content)
            
            if not detected_issues:
                return None
            
            # Pass 2: AST context analysis
            perf_context = self._analyze_performance_context(content, detected_issues)
            
            # Filter by confidence
            high_confidence_issues = self._filter_by_confidence(perf_context)
            
            if not high_confidence_issues:
                print(f"   ℹ️  Low-confidence patterns in {os.path.basename(file_path)} - skipping")
                return None
            
            print(f"   ⚡ Optimizing performance: {os.path.basename(file_path)}")
            
            # Generate optimized code using Gemini
            optimized_content = await self._generate_optimized_code(
                file_path, content, high_confidence_issues
            )
            
            # Apply optimizations
            if optimized_content and optimized_content != content:
                if self.ctx.write_compliant_file(file_path, optimized_content):
                    return {
                        'file': file_path,
                        'issues': high_confidence_issues,
                        'context': perf_context,
                        'reasoning': 'Performance anti-patterns detected and optimized'
                    }
            
        except Exception as e:
            print(f"   ❌ Failed to optimize {file_path}: {e}")
            return {
                'file': file_path,
                'error': str(e),
                'reasoning': 'Failed to process file'
            }
        
        return None
    
    def _detect_performance_issues(self, content: str) -> Dict[str, List[Dict]]:
        """Fast regex-based performance issue detection."""
        issues = {}
        
        for issue_name, pattern in self.PERFORMANCE_PATTERNS.items():
            matches = list(pattern.finditer(content))
            if matches:
                issues[issue_name] = [
                    {
                        'line': content[:match.start()].count('\n') + 1,
                        'snippet': content[match.start():match.end()][:50],
                        'full_match': match.group()
                    }
                    for match in matches
                ]
        
        return issues
    
    def _analyze_performance_context(self, content: str, issues: Dict) -> Dict:
        """Analyze AST to understand performance context."""
        context = {
            'functions_with_issues': [],
            'async_functions': set(),
            'long_functions': [],
            'string_concats_in_loops': [],
            'blocking_io_in_async': []
        }
        
        try:
            tree = ast.parse(content)
            
            # Find async functions
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    context['async_functions'].add(node.name)
                    
                    # Check for blocking I/O in async functions
                    func_start = node.lineno
                    func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start
                    
                    for issue_name, issue_list in issues.items():
                        if issue_name in ['blocking_sleep', 'blocking_requests']:
                            for issue in issue_list:
                                if func_start <= issue['line'] <= func_end:
                                    context['blocking_io_in_async'].append({
                                        'function': node.name,
                                        'issue': issue_name,
                                        'line': issue['line']
                                    })
                
                # Find functions with performance issues
                elif isinstance(node, ast.FunctionDef):
                    func_start = node.lineno
                    func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start
                    func_length = func_end - func_start
                    
                    # Check for long functions (>50 lines)
                    if func_length > 50:
                        context['long_functions'].append({
                            'function': node.name,
                            'length': func_length
                        })
                    
                    # Check for issues in this function
                    for issue_name, issue_list in issues.items():
                        for issue in issue_list:
                            if func_start <= issue['line'] <= func_end:
                                context['functions_with_issues'].append({
                                    'function': node.name,
                                    'issue': issue_name,
                                    'line': issue['line']
                                })
                                
                                # Special check for string concat in loops
                                if issue_name == 'string_concat_loop':
                                    context['string_concats_in_loops'].append({
                                        'function': node.name,
                                        'line': issue['line']
                                    })
        
        except Exception as e:
            print(f"   ⚠️  AST analysis failed: {e}")
        
        return context
    
    def _filter_by_confidence(self, context: Dict) -> Dict[str, List]:
        """Filter issues by confidence level."""
        high_confidence = {
            'string_concat_loop': [],
            'blocking_sleep': [],
            'blocking_requests': [],
            'inefficient_list_build': []
        }
        
        # High confidence: String concatenation in loops
        for concat in context.get('string_concats_in_loops', []):
            high_confidence['string_concat_loop'].append(concat)
        
        # High confidence: Blocking sleep in async functions
        for blocking in context.get('blocking_io_in_async', []):
            if blocking['issue'] in ['blocking_sleep', 'blocking_requests']:
                high_confidence[blocking['issue']].append(blocking)
        
        # High confidence: Inefficient list building pattern
        # (This is always safe to optimize)
        if any('inefficient_list_build' in f.get('issue', '') for f in context.get('functions_with_issues', [])):
            high_confidence['inefficient_list_build'] = [
                f for f in context.get('functions_with_issues', [])
                if 'inefficient_list_build' in f.get('issue', '')
            ]
        
        return {k: v for k, v in high_confidence.items() if v}
    
    async def _generate_optimized_code(self, file_path: str, content: str, issues: Dict) -> str:
        """Generate optimized code using Gemini."""
        # Build optimization summary
        opt_summary = []
        for issue_name, issue_list in issues.items():
            opt_summary.append(f"- {issue_name}: {len(issue_list)} occurrences")
        
        prompt = (
            f"PERFORMANCE OPTIMIZATION TASK: Optimize Python code for better performance.\n\n"
            f"File: {file_path}\n\n"
            f"Performance Issues:\n"
            + "\n".join(opt_summary) + "\n\n"
            "Optimization Rules:\n"
            "1. Replace string concatenation in loops with ''.join() or list comprehension\n"
            "2. Replace time.sleep() with asyncio.sleep() in async functions\n"
            "3. Replace requests.get() with aiohttp or async equivalent in async functions\n"
            "4. Convert inefficient list building to list comprehensions where appropriate\n"
            "5. Pre-compile regex patterns outside loops\n"
            "6. Maintain readability and the subatomic philosophy (<200 lines per file)\n"
            "7. Add comments explaining performance improvements\n"
            "8. Preserve all existing functionality\n\n"
            "Requirements:\n"
            "1. Do not sacrifice readability for micro-optimizations\n"
            "2. Only apply optimizations that are semantically equivalent\n"
            "3. Import required modules (asyncio, aiohttp) if needed\n"
            "4. Keep functions focused and atomic\n\n"
            f"Code:\n{content}\n\n"
            "Return ONLY the complete optimized Python code."
        )
        
        return await self.ctx.request_mutation(
            self.name, prompt, content, reasoning_mode=True
        )
    
    def _save_performance_report(self, log_entries: List[Dict], optimized_files: List[str]):
        """Save the performance optimization report."""
        timestamp = int(time.time())
        report_path = f"observability/audit/performance_gains_{timestamp}.md"
        
        report_content = f"# Performance Gains Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n"
        report_content += f"- Files analyzed: {len(log_entries)}\n"
        report_content += f"- Files optimized: {len(optimized_files)}\n\n"
        
        if log_entries:
            report_content += f"## Performance Optimizations\n\n"
            for entry in log_entries:
                if 'error' in entry:
                    report_content += f"### ❌ {entry['file']}\n\n"
                    report_content += f"**Error:** {entry['error']}\n\n"
                else:
                    report_content += f"### ⚡ {entry['file']}\n\n"
                    
                    issues = entry['issues']
                    report_content += f"**Optimizations Applied:**\n"
                    for issue_name, issue_list in issues.items():
                        report_content += f"- {issue_name}: {len(issue_list)} fixes\n"
                    
                    context = entry['context']
                    if context.get('blocking_io_in_async'):
                        report_content += f"\n**Async I/O Fixes:**\n"
                        for fix in context['blocking_io_in_async']:
                            report_content += f"- {fix['function']} (line {fix['line']})\n"
                    
                    if context.get('string_concats_in_loops'):
                        report_content += f"\n**String Concat Optimizations:**\n"
                        for concat in context['string_concats_in_loops']:
                            report_content += f"- {concat['function']} (line {concat['line']})\n"
                    
                    report_content += f"\n**Reasoning:** {entry['reasoning']}\n\n"
        
        self.ctx.write_compliant_file(report_path, report_content)
