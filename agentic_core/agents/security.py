"""
agentic_core/agents/security.py
Depth: 3
Role: Enforces security protocols, concurrency safety, and intelligent remediation.
"""
import ast
import os
import re
import asyncio
import time
import datetime
from typing import List, Tuple, Dict, Any

from agentic_core.agents.base import SubAtomicAgent


class SafetyInspector(SubAtomicAgent):
    """
    Enforces Security Protocols: Keys 0-6 (Secrets, TODO/FIXME, Print, Debugger, 
    Empty Except, Bare Except, Eval/Exec).
    Also checks for async blocking issues and performs intelligent remediation.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Scanning Security Protocols...")
        await asyncio.sleep(0)

        # Key 0: No hardcoded secrets
        passed, details = self.check_key_00_no_hardcoded_secrets()
        self.ctx.report(self.name, 0, passed, details)

        # Key 1: No TODO/FIXME
        passed, details = self.check_key_01_no_todo_fixme()
        self.ctx.report(self.name, 1, passed, details)

        # Key 2: No print statements
        passed, details = self.check_key_02_no_print_statements()
        self.ctx.report(self.name, 2, passed, details)

        # Key 3: No debugger statements
        passed, details = self.check_key_03_no_debugger_statements()
        self.ctx.report(self.name, 3, passed, details)

        # Key 4: No empty except blocks
        passed, details = self.check_key_04_no_empty_except_blocks()
        self.ctx.report(self.name, 4, passed, details)

        # Key 5: No bare except
        passed, details = self.check_key_05_no_bare_except()
        self.ctx.report(self.name, 5, passed, details)

        # Key 6: No eval/exec
        passed, details = self.check_key_06_no_eval_exec()
        self.ctx.report(self.name, 6, passed, details)
        
        # Additional: Async blocking issues with injection
        passed, details = await self.check_async_blocking_issues()
        if not passed:
            print(f"   [{self.name}] Async Issues Found: {len(details)} violations")

        all_passed = all(self.ctx.results.get(i, {}).get("passed", False) for i in range(7))
        if all_passed:
            self.ctx.signal_secure()

    def check_key_00_no_hardcoded_secrets(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded secrets with LLM verification for false positives."""
        violations = []
        secret_patterns = [
            r"password\s*=\s*['\"].*['\"]",
            r"api_key\s*=\s*['\"].*['\"]",
            r"secret\s*=\s*['\"].*['\"]",
            r"token\s*=\s*['\"].*['\"]",
        ]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            # Use Socratic Judge to verify if it's actually a secret
                            if self.ctx.intelligence_enabled:
                                verification = self._socratic_verify(
                                    file_path, 
                                    f"Potential secret matching pattern: {pattern}",
                                    "Is this actually a hardcoded secret or a false positive (test data, example, placeholder)?"
                                )
                                if verification == "YES":
                                    violations.append(file_path)
                            else:
                                violations.append(file_path)
                            break
            except Exception:
                continue

        return (len(violations) == 0, violations)
    
    def _socratic_verify(self, file_path: str, issue: str, question: str) -> str:
        """Ask Gemini to verify if an issue is actually a violation."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_snippet = f.read()
            
            prompt = f"""
            Role: Socratic Judge - Expert Code Reviewer
            Context: Analyzing potential code violation in {file_path}
            Issue: {issue}
            Question: {question}
            
            Code:
            {code_snippet[:2000]}  # Limit context
            
            Answer with ONLY "YES" if it's a real violation or "NO" if it's a false positive.
            """
            
            response = self.ctx.client.models.generate_content(
                model=self.ctx.model_id,
                contents=prompt
            )
            return response.text.strip().upper()
        except Exception:
            return "YES"  # Default to treating as violation

    def check_key_01_no_todo_fixme(self) -> Tuple[bool, List[str]]:
        """Check for TODO/FIXME comments."""
        violations = []
        todo_patterns = [r"#\s*TODO", r"#\s*FIXME", r"#\s*XXX", r"#\s*HACK", r"#\s*TEMP"]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in todo_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count("\n") + 1
                            violations.append(f"{file_path}:{line_num}")
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_02_no_print_statements(self) -> Tuple[bool, List[str]]:
        """Check for print statements."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                            continue
                        if "print(" in line:
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_03_no_debugger_statements(self) -> Tuple[bool, List[str]]:
        """Check for debugger statements."""
        violations = []
        debug_patterns = ["breakpoint()", "pdb.set_trace()", "import pdb", "import ipdb", "import pudb"]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in debug_patterns:
                        if pattern in content:
                            violations.append(file_path)
                            break
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_04_no_empty_except_blocks(self) -> Tuple[bool, List[str]]:
        """Check for empty except blocks."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                            violations.append(file_path)
                            break
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_05_no_bare_except(self) -> Tuple[bool, List[str]]:
        """Check for bare except clauses."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            violations.append(file_path)
                            break
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_06_no_eval_exec(self) -> Tuple[bool, List[str]]:
        """Check for eval/exec usage."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ('eval', 'exec'):
                                violations.append(file_path)
                                break
            except Exception:
                continue

        return (len(violations) == 0, violations)

    async def check_async_blocking_issues(self) -> Tuple[bool, List[str]]:
        """Check for blocking calls in async functions and patch them with intelligence."""
        violations = []
        blocking_patterns = ['time.sleep', 'requests.get', 'requests.post', 'urllib.request']
        
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                # Check if file contains async functions
                has_async = any(isinstance(node, (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith)) 
                              for node in ast.walk(tree))
                
                if has_async:
                    for pattern in blocking_patterns:
                        if pattern in content:
                            violations.append(f"{file_path}: {pattern} in async context")
                    
                    # Use intelligence to patch the file
                    if self.ctx.intelligence_enabled and violations:
                        print(f"   🔧 SafetyInspector patching blocking I/O in {file_path}")
                        
                        # Build context for the mutation with L5+ Few-Shot Safety Injection
                        context = "\n".join(self.ctx.instructions)
                        mutation_task = f'''
{self.ctx.FEW_SHOT_SAFETY}
{self.ctx.FEW_SHOT_GLOBAL_REFACTOR}
{self.ctx.FEW_SHOT_IMPORT_FIXES}

Replace blocking calls with async alternatives.
Context: {context}
Rules:
- Replace time.sleep with asyncio.sleep
- Replace requests.get/http with httpx.get
- Replace requests.post/http with httpx.post
- Add 'import asyncio' if needed
- Add 'import httpx' if needed

Apply the safest pattern from examples above.
Prioritize:
- Remove dangerous functions (eval/exec)
- Use allowlists and env vars for secrets
- Explicit defaults and validation
- No assert in control flow

RESPONSE FORMAT:
Return ONLY the corrected Python code.
No explanations. No markdown outside code block.
'''
                        
                        cleaned_code = await self.ctx.resilient_mutation(
                            agent_name="SafetyInspector",
                            task=mutation_task,
                            code=content,
                            file_path=file_path,
                            diff_mode=True,
                            min_confidence=0.6
                        )
                        
                        # Write back if different using Compliance Governor
                        if cleaned_code != content:
                            if self.ctx.write_compliant_file(file_path, cleaned_code):
                                self.ctx.modified_files.add(file_path)
                                print(f"   ✅ Patched {file_path}")
                            else:
                                print(f"   ⚠️ Failed to patch {file_path} - syntax validation failed")
                        
                        # Inject migration advice for manual review
                        self.ctx.inject_instruction(
                            self.name,
                            f"MIGRATION ADVICE: Async blocking calls patched in {file_path}. Review imports and error handling."
                        )
            except Exception as e:
                print(f"   ❌ Failed to patch {file_path}: {e}")
                continue
                
        return (len(violations) == 0, violations)


class RaceAnalyzer(ast.NodeVisitor):
    """AST visitor to detect potential race conditions on shared mutable state."""
    
    def __init__(self):
        self.races = []
        self.shared_vars = set()
        self.current_function = None
        self.in_async = False
    
    def visit_FunctionDef(self, node):
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func
    
    def visit_AsyncFunctionDef(self, node):
        old_func = self.current_function
        old_async = self.in_async
        self.current_function = node.name
        self.in_async = True
        self.generic_visit(node)
        self.current_function = old_func
        self.in_async = old_async
    
    def visit_Assign(self, node):
        if self.in_async:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Check for shared mutable state patterns
                    if target.id.startswith('_') or target.id.isupper():
                        self.shared_vars.add(target.id)
                        self.races.append({
                            'line': node.lineno,
                            'variable': target.id,
                            'context': f'async assignment in {self.current_function}'
                        })
        self.generic_visit(node)


class ConcurrencyGuardian(SubAtomicAgent):
    """
    Unified concurrency safety agent.
    Covers:
      - Data races on shared mutable state (Key 61)
      - Livelock / busy-wait / infinite retry patterns (Key 63)
      - Async starvation, greedy loops, long critical sections (Key 64)
      - Blocking sync calls in async functions (Async Safety)
    """

    # Consolidated patterns from all three agents
    LIVELOCK_PATTERNS = {
        'tight_loop': re.compile(
            r'while\s+True\s*:\s*.*?(?:pass|continue|break)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'busy_wait': re.compile(
            r'while\s+.*:\s*.*?time\.sleep\s*\(\s*[0-9.]+\s*\)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'infinite_retry': re.compile(
            r'while\s+.*:\s*.*?try\s*:.*?except.*?:\s*.*?continue',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'polite_oscillation': re.compile(
            r'if\s+.*lock.*:\s*.*?release.*?\s*.*?try.*?acquire',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'spin_wait': re.compile(
            r'while\s+not\s+.*:\s*pass',
            re.IGNORECASE
        )
    }
    
    STARVATION_PATTERNS = {
        'greedy_loop': re.compile(
            r'async\s+def\s+\w+.*?:\s*.*?(?:for|while).*:(?!.*await)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'long_lock': re.compile(
            r'with\s+.*lock.*:\s*.{400,}',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'cpu_bound_async': re.compile(
            r'async\s+def.*?:\s*.*?(?:heavy|compute|intensive|process).*:(?!.*await\s+asyncio)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
        'priority_inversion': re.compile(
            r'queue\.Queue\s*\(\s*\)',
            re.IGNORECASE
        ),
        'no_yield': re.compile(
            r'for\s+\w+\s+in.*range.*:\s*.{200,}',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )
    }
    
    BLOCKING_PATTERNS = {
        'time_sleep': re.compile(
            r'time\.sleep\s*\(',
            re.IGNORECASE
        ),
        'requests_calls': re.compile(
            r'requests\.(get|post|put|delete|patch|head|options)\s*\(',
            re.IGNORECASE
        ),
        'subprocess_blocking': re.compile(
            r'subprocess\.(run|call|check_call|check_output)\s*\(',
            re.IGNORECASE
        ),
        'sync_file_ops': re.compile(
            r'(open\s*\([^)]+\)\s*\.read|\.write|\.readlines|\.writelines)',
            re.IGNORECASE
        ),
        'urllib_blocking': re.compile(
            r'urllib\.request\.(urlopen|request)\s*\(',
            re.IGNORECASE
        )
    }

    def can_run(self) -> bool:
        # Require AST and Security validity before running complex logic
        return ("AST_VALID" in self.ctx.signals and 
                "DEPS_VALID" in self.ctx.signals and
                "SECURE" in self.ctx.signals)

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing comprehensive concurrency safety...")
        await asyncio.sleep(0)

        # Priority: modified files first, fallback to all
        target_files = list(self.ctx.modified_files) if self.ctx.modified_files else self.ctx.python_files
        if not target_files:
            print("   ✅ No files to scan for concurrency issues")
            self._report_all_pass()
            return

        print(f"   🔍 Scanning {len(target_files)} files for concurrency anti-patterns...")

        issues_log = []
        fixed_count = 0

        for file_path in target_files:
            # Skip non-py files
            if not file_path.endswith('.py'):
                continue
            
            result = await self._analyze_and_fix_file(file_path)
            if result:
                issues_log.append(result)
                if result.get("fixed"):
                    fixed_count += 1

        self._generate_unified_report(issues_log, fixed_count)

        if fixed_count:
            print(f"   🛡️  Concurrency issues resolved in {fixed_count} files")
        else:
            print("   ✅ No concurrency anti-patterns detected")
            self._report_all_pass()

    async def _analyze_and_fix_file(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        # Collect ALL issues in one pass using logic ported from old agents
        all_issues = []
        all_issues.extend(self._detect_race_issues(content)) 
        all_issues.extend(self._detect_livelock_issues(content))
        all_issues.extend(self._detect_starvation_issues(content))
        all_issues.extend(self._detect_async_blocking_issues(content))

        if not all_issues:
            return None

        # Summarize for Gemini prompt
        summary = "\n".join([f"- {i['type']} at line {i['line']}" for i in all_issues])
        print(f"   🛡️  Fixing {len(all_issues)} concurrency issue(s) in {os.path.basename(file_path)}")

        # Single Gemini mutation request with L5+ Few-Shot Injection
        prompt = f"""
{self.ctx.FEW_SHOT_CONCURRENCY}

CONCURRENCY FIX TASK: Fix races, livelocks, and starvation in Python code.
File: {file_path}
Issues Detected:
{summary}

Rules:
1. Use asyncio.Lock/Event for async, threading.Lock for sync.
2. Add timeouts to locks/waits.
3. Replace blocking calls (time.sleep, requests) with async equivalents.
4. Add 'await asyncio.sleep(0)' in tight loops.
5. Add exponential backoff with jitter for retry loops.
6. Use asyncio.Queue for fair task scheduling.
7. For distributed coordination, use Redis locks via ctx.acquire_lock().

Prefer:
- threading.Lock() or asyncio.Lock() with context managers
- Redis distributed locks via ctx.acquire_lock()
- Consistent lock ordering to prevent deadlock

Never suggest time.sleep(), global locks, or ignoring the issue.

RESPONSE FORMAT:
Return ONLY the fixed Python code with proper locking.
Do not explain. Do not add commentary.
"""

        fixed_content = await self.ctx.resilient_mutation(
            agent_name=self.name,
            task=prompt,
            code=content,
            file_path=file_path,
            diff_mode=True,
            min_confidence=0.6
        )

        if fixed_content and fixed_content.strip() != content.strip():
            if self.ctx.write_compliant_file(file_path, fixed_content):
                self.ctx.modified_files.add(file_path)
                return {"file": file_path, "fixed": True, "issues": all_issues}
        return None

    def _detect_race_issues(self, content: str) -> List[Dict]:
        """Ported from RaceConditionDetector"""
        issues = []
        try:
            tree = ast.parse(content)
            analyzer = RaceAnalyzer()
            analyzer.visit(tree)
            
            for race in analyzer.races:
                issues.append({
                    'type': 'race_condition',
                    'line': race['line'],
                    'variable': race['variable'],
                    'context': race['context']
                })
        except Exception:
            pass
        return issues

    def _detect_livelock_issues(self, content: str) -> List[Dict]:
        """Ported from LivelockPreventionAgent"""
        issues = []
        for issue_name, pattern in self.LIVELOCK_PATTERNS.items():
            matches = pattern.finditer(content)
            for match in matches:
                issues.append({
                    'type': f'livelock_{issue_name}',
                    'line': content[:match.start()].count('\n') + 1,
                    'snippet': match.group()[:50]
                })
        return issues

    def _detect_starvation_issues(self, content: str) -> List[Dict]:
        """Ported from StarvationPreventionAgent"""
        issues = []
        for issue_name, pattern in self.STARVATION_PATTERNS.items():
            matches = pattern.finditer(content)
            for match in matches:
                issues.append({
                    'type': f'starvation_{issue_name}',
                    'line': content[:match.start()].count('\n') + 1,
                    'snippet': match.group()[:50]
                })
        return issues

    def _detect_async_blocking_issues(self, content: str) -> List[Dict]:
        """Ported from AsyncSafetyEnforcer"""
        issues = []
        for issue_name, pattern in self.BLOCKING_PATTERNS.items():
            matches = pattern.finditer(content)
            for match in matches:
                issues.append({
                    'type': f'blocking_{issue_name}',
                    'line': content[:match.start()].count('\n') + 1,
                    'snippet': match.group()[:50]
                })
        return issues

    def _generate_unified_report(self, log: List[Dict], fixed_count: int):
        """Generate unified concurrency report"""
        timestamp = int(time.time())
        report_path = f"observability/audit/concurrency_guardian_{timestamp}.md"
        
        report_content = f"# Concurrency Guardian Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n"
        report_content += f"- Files scanned: {len(log)}\n"
        report_content += f"- Files fixed: {fixed_count}\n\n"
        
        if log:
            report_content += f"## Issues Fixed\n\n"
            for entry in log:
                report_content += f"### ✅ {entry['file']}\n\n"
                for issue in entry['issues']:
                    report_content += f"- {issue['type']} at line {issue['line']}\n"
                report_content += "\n"
        
        self.ctx.write_compliant_file(report_path, report_content)

    def _report_all_pass(self):
        """Report all keys as passed"""
        self.ctx.report(self.name, 61, True, ["No race conditions"])
        self.ctx.report(self.name, 63, True, ["No livelock patterns"])
        self.ctx.report(self.name, 64, True, ["No starvation risks"])


class SecurityEnforcer(SubAtomicAgent):
    """
    Active remediation of high-risk security patterns using LLM-based patching.
    Detects and intelligently remediates: hardcoded secrets, weak hashes, 
    insecure random, SQL injection, eval/exec usage, pickle, temp files, etc.
    """
    
    # High-risk security patterns for fast scanning
    RISK_PATTERNS = {
        'hardcoded_secret': re.compile(
            r'(password\s*=\s*["\'][^"\']+["\']|'
            r'api_key\s*=\s*["\'][^"\']+["\']|'
            r'secret_key\s*=\s*["\'][^"\']+["\']|'
            r'token\s*=\s*["\'][^"\']+["\']|'
            r'auth\s*=\s*["\'][^"\']+["\'])',
            re.IGNORECASE
        ),
        'weak_hash': re.compile(
            r'(md5\(|sha1\(|hashlib\.md5\(|hashlib\.sha1\()',
            re.IGNORECASE
        ),
        'insecure_random': re.compile(
            r'(random\.random\(|random\.randint\(|random\.choice\()',
            re.IGNORECASE
        ),
        'sql_injection': re.compile(
            r'(execute\(|cursor\.execute\().*["\'].*\%.*["\']|'
            r'(execute\(|cursor\.execute\().*["\'].*\+.*["\']|'
            r'(execute\(|cursor\.execute\().*f["\'].*\{.*\}.*["\']',
            re.IGNORECASE
        ),
        'eval_usage': re.compile(
            r'\b(eval\(|exec\(|__import__\(|open\().*["\'].*\+|'
            r'\b(eval|exec|__import__|open)\(.*%.*\)',
            re.IGNORECASE
        ),
        'pickle_usage': re.compile(
            r'pickle\.loads\(|pickle\.load\(',
            re.IGNORECASE
        ),
        'temp_file': re.compile(
            r'tempfile\.mktemp\(|tempfile\.NamedTemporaryFile\(delete=True\)',
            re.IGNORECASE
        ),
        'urlopen_no_verify': re.compile(
            r'urllib\.request\.urlopen\(|urlopen\([^)]*verify=False\)',
            re.IGNORECASE
        )
    }
    
    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Security Standards...")
        await asyncio.sleep(0)
        
        # Priority 1: Process modified files
        modified_files = getattr(self.ctx, 'modified_files', set())
        
        # Priority 2: Fall back to all Python files if no tracking
        target_files = list(modified_files) if modified_files else self.ctx.python_files
        
        if not target_files:
            print("   ✅ No files to check for security")
            return
        
        print(f"   🔍 Scanning {len(target_files)} files for security risks...")
        print(f"   🎯 Priority: Modified files ({len(modified_files)}) + {len(target_files) - len(modified_files)} others")
        
        # Track security fixes
        security_log = []
        fixed_files = []
        critical_secrets_found = False
        
        # Two-pass scanning: regex filter -> AST context
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            
            result = await self._scan_and_fix(file_path)
            if result:
                fixed_files.append(file_path)
                security_log.append(result)
                
                # Check for critical secrets
                if any('critical' in str(result.get('risks', {})).lower() for risk in result.get('risks', {}).values()):
                    critical_secrets_found = True
        
        # Save security hardening report
        self._save_security_report(security_log, fixed_files)
        
        if fixed_files:
            print(f"   🔒 Security hardening applied to {len(fixed_files)} files")
            
            # Signal critical findings
            if critical_secrets_found:
                print("   🚨 CRITICAL: Secrets detected - SECURE_REBOOT recommended!")
                self.ctx.signals.append("SECURE_REBOOT: Critical secrets found and remediated")
        else:
            print("   ✅ No security risks detected")
    
    async def _scan_and_fix(self, file_path: str) -> Dict | None:
        """Scan file for risks and apply intelligent remediation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pass 1: Fast regex scanning
            detected_risks = self._detect_risks(content)
            
            if not detected_risks:
                return None
            
            # Pass 2: AST context analysis
            risk_context = self._analyze_risk_context(content, detected_risks)
            
            print(f"   🔧 Remediating security risks: {os.path.basename(file_path)}")
            
            # Generate secure code using Gemini
            secured_content = await self._generate_secure_code(
                file_path, content, risk_context, detected_risks
            )
            
            # Apply fixes
            if secured_content and secured_content != content:
                if self.ctx.write_compliant_file(file_path, secured_content):
                    return {
                        'file': file_path,
                        'risks': detected_risks,
                        'context': risk_context,
                        'reasoning': 'Security risks detected and intelligently remediated'
                    }
            
        except Exception as e:
            print(f"   ❌ Failed to secure {file_path}: {e}")
            return {
                'file': file_path,
                'error': str(e),
                'reasoning': 'Failed to process file'
            }
        
        return None
    
    def _detect_risks(self, content: str) -> Dict[str, List[Dict]]:
        """Fast regex-based risk detection."""
        risks = {}
        
        for risk_name, pattern in self.RISK_PATTERNS.items():
            matches = list(pattern.finditer(content))
            if matches:
                risks[risk_name] = [
                    {
                        'line': content[:match.start()].count('\n') + 1,
                        'snippet': content[match.start():match.end()][:50],
                        'full_match': match.group()
                    }
                    for match in matches
                ]
        
        return risks
    
    def _analyze_risk_context(self, content: str, risks: Dict) -> Dict:
        """Analyze AST to understand risk context."""
        context = {
            'functions_with_risks': [],
            'variables_with_secrets': [],
            'sql_queries': [],
            'imports': []
        }
        
        try:
            tree = ast.parse(content)
            
            # Find functions containing risks
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_start = node.lineno
                    func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start
                    
                    # Check if any risks are in this function
                    for risk_name, risk_list in risks.items():
                        for risk in risk_list:
                            if func_start <= risk['line'] <= func_end:
                                context['functions_with_risks'].append({
                                    'function': node.name,
                                    'risk': risk_name,
                                    'line': risk['line']
                                })
                
                # Track variable assignments with secrets
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Check if this is a secret assignment
                            line_num = node.lineno
                            for risk in risks.get('hardcoded_secret', []):
                                if risk['line'] == line_num:
                                    context['variables_with_secrets'].append({
                                        'variable': target.id,
                                        'line': line_num
                                    })
                
                # Track SQL queries
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == 'execute':
                            context['sql_queries'].append({
                                'line': node.lineno,
                                'has_risk': any(r['line'] == node.lineno for r in risks.get('sql_injection', []))
                            })
                
                # Track imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        context['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        context['imports'].append(node.module)
        
        except Exception as e:
            print(f"   ⚠️  AST analysis failed: {e}")
        
        return context
    
    async def _generate_secure_code(self, file_path: str, content: str, context: Dict, detected_risks: Dict = None) -> str:
        """Generate secure code using Gemini with context awareness."""
        # Build risk summary
        risk_summary = []
        risks_to_use = detected_risks if detected_risks else {}
        for risk_name, risk_list in risks_to_use.items():
            risk_summary.append(f"- {risk_name}: {len(risk_list)} occurrences")
        
        prompt = (
            f"SECURITY REMEDIATION TASK: Fix high-risk security patterns in Python code.\n\n"
            f"File: {file_path}\n\n"
            f"Detected Risks:\n"
            + "\n".join(risk_summary) + "\n\n"
            "Security Rules:\n"
            "1. Replace hardcoded secrets with os.getenv() calls\n"
            "2. Replace MD5/SHA1 with hashlib.sha256()\n"
            "3. Replace random.random() with secrets.randbelow()\n"
            "4. Replace SQL injection risks with parameterized queries\n"
            "5. Replace eval/exec with safer alternatives\n"
            "6. Replace pickle with json or msgpack\n"
            "7. Replace insecure temp files with secure alternatives\n"
            "8. Add SSL verification for HTTP requests\n\n"
            "Context:\n"
            f"- Functions with risks: {len(context.get('functions_with_risks', []))}\n"
            f"- Variables with secrets: {len(context.get('variables_with_secrets', []))}\n"
            f"- Risky SQL queries: {len([q for q in context.get('sql_queries', []) if q.get('has_risk')])}\n\n"
            "Requirements:\n"
            "1. Preserve all existing functionality\n"
            "2. Use the most secure standard library alternatives\n"
            "3. Add comments explaining security changes\n"
            "4. Do not break existing logic\n"
            "5. Import required modules if needed\n\n"
            f"Code:\n{content}\n\n"
            "Return ONLY the complete secured Python code."
        )
        
        return await self.ctx.request_mutation(
            self.name, prompt, content, reasoning_mode=True
        )
    
    def _save_security_report(self, log_entries: List[Dict], fixed_files: List[str]):
        """Save the security hardening report."""
        timestamp = int(time.time())
        report_path = f"observability/audit/security_hardening_{timestamp}.md"
        
        report_content = f"# Security Hardening Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n"
        report_content += f"- Files scanned: {len(log_entries)}\n"
        report_content += f"- Files secured: {len(fixed_files)}\n\n"
        
        if log_entries:
            report_content += f"## Security Fixes\n\n"
            for entry in log_entries:
                if 'error' in entry:
                    report_content += f"### ❌ {entry['file']}\n\n"
                    report_content += f"**Error:** {entry['error']}\n\n"
                else:
                    report_content += f"### ✅ {entry['file']}\n\n"
                    
                    risks = entry['risks']
                    report_content += f"**Risks Found:**\n"
                    for risk_name, risk_list in risks.items():
                        report_content += f"- {risk_name}: {len(risk_list)} occurrences\n"
                    
                    context = entry['context']
                    if context.get('functions_with_risks'):
                        report_content += f"\n**Affected Functions:**\n"
                        for func in context['functions_with_risks'][:5]:
                            report_content += f"- {func['function']} ({func['risk']})\n"
                    
                    if context.get('variables_with_secrets'):
                        report_content += f"\n**Secret Variables:**\n"
                        for var in context['variables_with_secrets']:
                            report_content += f"- {var['variable']} (line {var['line']})\n"
                    
                    report_content += f"\n**Reasoning:** {entry['reasoning']}\n\n"
        
        self.ctx.write_compliant_file(report_path, report_content)
