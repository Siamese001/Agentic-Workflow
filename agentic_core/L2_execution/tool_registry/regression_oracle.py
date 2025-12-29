import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import logging
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE: Any = True
except ImportError:
    PINECONE_AVAILABLE: Any = False
from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE: Any = True
except ImportError:
    GENAI_AVAILABLE: Any = False
    genai: Any = None
    types: Any = None
logger: Any = logging.getLogger(__name__)

@dataclass
class method_change:
    """Represents a changed method requiring test generation."""
    file_path: str
    method_name: str
    before_code: str
    after_code: str
    is_new: bool
    is_modified: bool
    is_deleted: bool

@dataclass
class generated_test:
    """Represents a generated test case."""
    test_file: str
    test_name: str
    test_code: str
    target_method: str
    edge_cases: List[str]
    passed: bool
    error_message: Optional[str]

class method_change_detector:
    """Detects method changes between two versions of a file."""

    def __init__(self, ctx):
        self.ctx = ctx

    def detect_method_changes(self, file_path: str) -> List[MethodChange]:
        """Detect which methods changed in a file."""
        changes: Any = []
        if not hasattr(self.ctx, 'healing_history'):
            return changes
        history: Any = self.ctx.healing_history.get(file_path, {})
        for key_id, data in history.items():
            before_code: Any = data.get('before_code', '')
            after_code: Any = data.get('after_code', '')
            if not before_code and (not after_code):
                continue
            try:
                before_tree: Any = ast.parse(before_code) if before_code else None
                after_tree: Any = ast.parse(after_code) if after_code else None
            except SyntaxError:
                logger.warning(f'Syntax error parsing {file_path} for method changes. Skipping.')
                continue
            before_methods: Any = self._extract_methods(before_tree, before_code) if before_tree else {}
            after_methods: Any = self._extract_methods(after_tree, after_code) if after_tree else {}
            all_methods: Any = set(before_methods.keys()) | set(after_methods.keys())
            for method_name in all_methods:
                before_method_code: Any = before_methods.get(method_name)
                after_method_code: Any = after_methods.get(method_name)
                if not before_method_code and after_method_code:
                    changes.append(MethodChange(file_path=file_path, method_name=method_name, before_code='', after_code=after_method_code, is_new=True, is_modified=False, is_deleted=False))
                elif before_method_code and (not after_method_code):
                    changes.append(MethodChange(file_path=file_path, method_name=method_name, before_code=before_method_code, after_code='', is_new=False, is_modified=False, is_deleted=True))
                elif before_method_code != after_method_code:
                    changes.append(MethodChange(file_path=file_path, method_name=method_name, before_code=before_method_code, after_code=after_method_code, is_new=False, is_modified=True, is_deleted=False))
        return changes

    def _extract_methods(self, tree: ast.AST, source: str) -> Dict[str, str]:
        """Extract method source code from AST."""
        methods = {}
        lines = source.split('\n')
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno - 1
                end = node.end_lineno if node.end_lineno else start + 1
                method_code = '\n'.join(lines[start:end])
                methods[node.name] = method_code
        return methods

class regression_test_generator:
    """Generates pytest code and creates test files."""

    def __init__(self, ctx, test_dir: Path, pinecone_available: bool, pinecone_index, genai_available: bool, genai_client):
        self.ctx = ctx
        self.test_dir = test_dir
        self.pinecone_available = pinecone_available
        self.pinecone_index = pinecone_index
        self.genai_available = genai_available
        self.genai_client = genai_client

    async def generate_test_code_and_file(self, change: MethodChange) -> Tuple[Optional[str], Optional[Path], List[str]]:
        """
        Generates test code, creates a test file, and returns the code, file path, and edge cases.
        Returns (None, None, []) if the method is deleted.
        """
        if change.is_deleted:
            return (None, None, [])
        edge_cases: Any = await self._query_edge_cases(change)
        test_code: Any = await self._synthesize_test_code(change, edge_cases)
        test_file: Any = self._create_test_file(change, test_code)
        return (test_code, test_file, edge_cases)

    async def _query_edge_cases(self, change: MethodChange) -> List[str]:
        """Query Pinecone for historical edge cases."""
        if not self.pinecone_available:
            return self._generate_default_edge_cases(change)
        try:
            return self._generate_default_edge_cases(change)
        except Exception as e:
            logger.warning(f'Could not query Pinecone: {e}')
            return self._generate_default_edge_cases(change)

    def _generate_default_edge_cases(self, change: MethodChange) -> List[str]:
        """Generate default edge cases based on method signature."""
        edge_cases = ['None input', 'Empty input', 'Large input (1000+ items)', 'Invalid type', 'Boundary values']
        return edge_cases

    async def _synthesize_test_code(self, change: MethodChange, edge_cases: List[str]) -> str:
        """Synthesize pytest code for method using Gemini 2.5."""
        if self.genai_available and self.genai_client:
            try:
                return await self._synthesize_with_gemini(change, edge_cases)
            except Exception as e:
                logger.warning(f'Gemini synthesis failed: {e}, falling back to template')
        return self._synthesize_with_template(change, edge_cases)

    async def _synthesize_with_gemini(self, change: MethodChange, edge_cases: List[str]) -> str:
        """Use Gemini 2.5 to synthesize intelligent test code."""
        module_path = change.file_path.replace('\\', '/').replace('.py', '').replace('/', '.')
        prompt = f"Write a comprehensive pytest test case for this Python method.\n\nFILE: {change.file_path}\nMETHOD: {change.method_name}\n\nBEFORE CODE (preserve this behavior):\n{change.before_code}\n```\n\nAFTER CODE (test this):\n{change.after_code}\n```\n\nREQUIREMENTS:\n1. Import from: {module_path}\n2. Use unittest.mock for all external dependencies\n3. Assert that the specific logic from BEFORE is preserved\n4. Test these edge cases: {', '.join(edge_cases)}\n5. Use descriptive test names and docstrings\n6. Include both positive and negative test cases\n7. Mock any file I/O, network calls, or external services\n\nOUTPUT FORMAT:\nReturn ONLY the complete Python test file code, starting with imports.\nUse pytest fixtures where appropriate.\nInclude clear assertions that verify behavior hasn't regressed.\n"
        response = await self.genai_client.models.generate_content_async(model='gemini-2.5-flash', contents=prompt, generation_config=types.GenerationConfig(temperature=0.2, max_output_tokens=2048))
        test_code = response.text
        if '```python' in test_code:
            test_code = test_code.split('```python')[1].split('```')[0].strip()
        elif '```' in test_code:
            test_code = test_code.split('```')[1].split('```')[0].strip()
        return test_code

    def _synthesize_with_template(self, change: MethodChange, edge_cases: List[str]) -> str:
        """Fallback template-based test generation."""
        module_path = change.file_path.replace('\\', '/').replace('.py', '').replace('/', '.')
        test_code = f'''"""\nAuto-generated regression test for {change.method_name}\nGenerated by Regression Oracle on {datetime.now(timezone.utc).isoformat()}\n\nEdge cases tested:\n{chr(10).join((f'- {case}' for case in edge_cases))}\n"""\n\nimport pytest\nfrom unittest.mock import Mock, patch\nfrom {module_path} import {change.method_name}\n\n\n# NAMING FIXED: Test → test\nclass test{change.method_name.title().replace('_', '')}:\n    """Regression tests for {change.method_name}."""\n\n    def test_{change.method_name}_basic(self):\n        """Test basic functionality."""\n        # TODO: Add basic test case\n        # This is a placeholder - Oracle needs Gemini to generate actual test\n        pass\n\n    def test_{change.method_name}_none_input(self):\n        """Test None input handling."""\n        # Edge case: None input\n        pass\n\n    def test_{change.method_name}_empty_input(self):\n        """Test empty input handling."""\n        # Edge case: Empty input\n        pass\n\n    def test_{change.method_name}_large_input(self):\n        """Test large input handling."""\n        # Edge case: Large input (1000+ items)\n        pass\n\n    def test_{change.method_name}_invalid_type(self):\n        """Test invalid type handling."""\n        # Edge case: Invalid type\n        with pytest.raises((TypeError, ValueError)):\n            # TODO: Add invalid type test\n            pass\n\n    def test_{change.method_name}_boundary_values(self):\n        """Test boundary value handling."""\n        # Edge case: Boundary values\n        pass\n'''
        return test_code

    def _create_test_file(self, change: MethodChange, test_code: str) -> Path:
        """Create test file in tests/autogen/."""
        file_name = Path(change.file_path).stem
        test_file = self.test_dir / f'test_{file_name}_{change.method_name}.py'
        with open(test_file, 'w') as f:
            f.write(test_code)
        logger.info(f'   Generated test: {test_file}')
        return test_file

class regression_test_runner:
    """Runs generated tests, performs self-correction, and reports results."""

    def __init__(self, ctx, test_dir: Path, genai_available: bool, genai_client, emit_signal_callback: Callable[[str, str], None]):
        self.ctx = ctx
        self.test_dir = test_dir
        self.genai_available = genai_available
        self.genai_client = genai_client
        self.emit_signal_callback = emit_signal_callback

    async def run_and_correct_test(self, change: MethodChange, test_file: Path, test_code: str) -> Tuple[bool, Optional[str]]:
        """Run a test and attempt self-correction if it fails."""
        passed, error_msg = await self._run_test(test_file)
        if not passed:
            passed, error_msg = await self._self_correct(change, test_code, error_msg)
        if passed:
            self.emit_signal_callback(change.file_path, change.method_name)
        return (passed, error_msg)

    async def _run_test(self, test_file: Path) -> Tuple[bool, Optional[str]]:
        """Run pytest on generated test."""
        try:
            result = subprocess.run(['pytest', str(test_file), '-v'], capture_output=True, text=True, timeout=30)
            passed = result.returncode == 0
            error_msg = result.stderr if not passed else None
            return (passed, error_msg)
        except Exception as e:
            logger.error(f'Error running test: {e}')
            return (False, str(e))

    async def _self_correct(self, change: MethodChange, test_code: str, error_msg: str) -> Tuple[bool, Optional[str]]:
        """
        Self-correction: Decide if test is bad or code is broken.
        Uses Gemini to analyze failure and determine root cause.
        """
        logger.warning(f'   Test failed for {change.method_name}, attempting self-correction...')
        if not self.genai_available or not self.genai_client:
            logger.warning('   Gemini not available for self-correction')
            return (False, f'Self-correction unavailable: {error_msg}')
        try:
            analysis_prompt = f'Analyze this test failure and determine the root cause.\n\nMETHOD: {change.method_name}\nFILE: {change.file_path}\n\nBEFORE CODE (expected behavior):\n{change.before_code}\n```\n\nAFTER CODE (actual implementation):\n{change.after_code}\n```\n\nGENERATED TEST:\n{test_code}\n```\n\nTEST FAILURE:\n{error_msg}\n\nANALYSIS REQUIRED:\n1. Is the test incorrectly written? (missing mocks, wrong assertions, syntax errors)\n2. Is the new code actually broken? (regression, logic error, breaking change)\n3. What is the root cause of the failure?\n\nOUTPUT FORMAT:\nProvide a JSON response with:\n{{\n    "root_cause": "test_error" or "code_regression",\n    "explanation": "detailed explanation of the issue",\n    "fix_suggestion": "what should be fixed"\n}}\n'
            response = await self.genai_client.models.generate_content_async(model='gemini-2.5-flash', contents=analysis_prompt, generation_config=types.GenerationConfig(temperature=0.1, max_output_tokens=1024))
            analysis = response.text
            if 'code_regression' in analysis.lower():
                logger.error(f'   [ALERT] REGRESSION DETECTED in {change.method_name}')
                logger.error(f'   Analysis: {analysis}')
                if hasattr(self.ctx, 'signals'):
                    self.ctx.signals.add(f'REGRESSION_DETECTED:{change.file_path}:{change.method_name}')
                return (False, f'REGRESSION DETECTED: {analysis}')
            elif 'test_error' in analysis.lower():
                logger.warning(f'   Test error detected, attempting auto-fix...')
                fixed_test = await self._auto_fix_test(change, test_code, error_msg, analysis)
                if fixed_test:
                    test_file = self._create_test_file_for_correction(change, fixed_test)
                    passed, new_error = await self._run_test(test_file)
                    if passed:
                        logger.info(f'   [OK] Test auto-fixed and now passes')
                        return (True, None)
                    else:
                        logger.warning(f'   Fixed test still fails: {new_error}')
                        return (False, f'Auto-fix failed: {new_error}')
                else:
                    return (False, f'Could not auto-fix test: {analysis}')
            else:
                logger.warning(f'   Unclear root cause, flagging for human review')
                return (False, f'Unclear failure: {analysis}')
        except Exception as e:
            logger.error(f'Self-correction failed: {e}')
            return (False, f'Self-correction error: {e}')

    async def _auto_fix_test(self, change: MethodChange, test_code: str, error_msg: str, analysis: str) -> Optional[str]:
        """
        Attempt to automatically fix a broken test.
        Uses Gemini to generate a corrected version.
        """
        try:
            fix_prompt = f"Fix this broken pytest test based on the analysis.\n\nORIGINAL TEST:\n{test_code}\n```\n\nERROR:\n{error_msg}\n\nANALYSIS:\n{analysis}\n\nREQUIREMENTS:\n1. Fix the identified issues (missing mocks, wrong imports, incorrect assertions)\n2. Preserve the test's intent and coverage\n3. Ensure all dependencies are properly mocked\n4. Return ONLY the complete fixed test code\n\nOUTPUT FORMAT:\nReturn the complete corrected Python test file code.\n"
            response = await self.genai_client.models.generate_content_async(model='gemini-2.5-flash', contents=fix_prompt, generation_config=types.GenerationConfig(temperature=0.2, max_output_tokens=2048))
            fixed_code = response.text
            if '```python' in fixed_code:
                fixed_code = fixed_code.split('```python')[1].split('```')[0].strip()
            elif '```' in fixed_code:
                fixed_code = fixed_code.split('```')[1].split('```')[0].strip()
            return fixed_code
        except Exception as e:
            logger.error(f'Auto-fix failed: {e}')
            return None

    def _create_test_file_for_correction(self, change: MethodChange, test_code: str) -> Path:
        """Helper to create/overwrite a test file during self-correction."""
        file_name = Path(change.file_path).stem
        test_file = self.test_dir / f'test_{file_name}_{change.method_name}.py'
        with open(test_file, 'w') as f:
            f.write(test_code)
        logger.info(f'   Re-generated test file for correction: {test_file}')
        return test_file

    def report_results(self, generated_tests: List[GeneratedTest]) -> Any:
        """Report test generation results."""
        total_tests: Any = len(generated_tests)
        passed_tests: Any = sum((1 for t in generated_tests if t.passed))
        failed_tests: Any = total_tests - passed_tests
        logger.info(f"\n{'=' * 80}")
        logger.info('🔮 REGRESSION ORACLE REPORT')
        logger.info(f"{'=' * 80}")
        logger.info(f'Total Tests Generated: {total_tests}')
        logger.info(f'  Passed: {passed_tests}')
        logger.info(f'  Failed: {failed_tests}')
        if failed_tests > 0:
            logger.warning(f'\n[!]  FAILED TESTS:')
            for test in generated_tests:
                if not test.passed:
                    logger.warning(f'  {test.test_name}: {test.error_message}')
        if passed_tests > 0:
            logger.info(f'\n[OK] PASSED TESTS:')
            for test in generated_tests:
                if test.passed:
                    logger.info(f'  {test.test_name} → {test.test_file}')
        logger.info(f"{'=' * 80}\n")

class regression_oracle(SubAtomicAgent):
    """
    The Regression Oracle - Automated Test Synthesizer
    
    Subscribes to AtomicBlackboard FILE_MODIFIED signals.
    Generates pytest cases for changed methods.
    Queries Pinecone for historical edge cases.
    Runs tests and performs self-correction.
    
    Process:
    1. Detect file modification
    2. Identify changed methods via diff
    3. Query Pinecone for failure patterns
    4. Generate pytest with edge cases
    5. Run test and self-correct if needed
    6. Emit REGRESSION_CHECK_PASS signal
    """

    def __init__(self, ctx):
        """
        Initialize Regression Oracle.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        self.test_dir = Path('tests/autogen')
        self.test_dir.mkdir(parents=True, exist_ok=True)
        pinecone_available = PINECONE_AVAILABLE
        pinecone_index = None
        if PINECONE_AVAILABLE:
            api_key = self.ctx.get_env('PINECONE_API_KEY') if hasattr(self.ctx, 'get_env') else None
            if api_key:
                try:
                    pc = Pinecone(api_key=api_key)
                    pinecone_index = pc.Index('canon-healing-patterns')
                    logger.info('[OK] Regression Oracle connected to Pinecone')
                except Exception as e:
                    logger.warning(f'[!]  Could not connect to Pinecone: {e}')
                    pinecone_available = False
        genai_available = GENAI_AVAILABLE
        genai_client = None
        if GENAI_AVAILABLE:
            api_key = self.ctx.get_env('GEMINI_API_KEY') if hasattr(self.ctx, 'get_env') else None
            if api_key:
                try:
                    genai_client = genai.Client(api_key=api_key)
                    logger.info('[OK] Regression Oracle connected to Gemini 2.5')
                except Exception as e:
                    logger.warning(f'[!]  Could not connect to Gemini: {e}')
                    genai_available = False
        self.change_detector = MethodChangeDetector(self.ctx)
        self.test_generator = RegressionTestGenerator(self.ctx, self.test_dir, pinecone_available, pinecone_index, genai_available, genai_client)
        self.test_runner = RegressionTestRunner(self.ctx, self.test_dir, genai_available, genai_client, self._emit_regression_check_pass)
        self.generated_tests: List[GeneratedTest] = []

    async def execute(self) -> Any:
        """
        Execute regression oracle monitoring.
        
        Listens for FILE_MODIFIED signals and generates tests.
        """
        logger.info('🔮 Regression Oracle: Monitoring for FILE_MODIFIED signals...')
        modified_files_to_process: Any = []
        if hasattr(self.ctx, 'signals'):
            modified_signals: Any = [s for s in self.ctx.signals if s.startswith('FILE_MODIFIED:')]
            if modified_signals:
                logger.info(f'   Detected {len(modified_signals)} FILE_MODIFIED signals')
                modified_files_to_process.extend([s.replace('FILE_MODIFIED:', '') for s in modified_signals])
            else:
                logger.info('   No FILE_MODIFIED signals detected')
        if hasattr(self.ctx, 'modified_files') and self.ctx.modified_files:
            logger.info(f'   Processing {len(self.ctx.modified_files)} modified files from context')
            modified_files_to_process.extend(self.ctx.modified_files)
        unique_modified_files: Any = list(set(modified_files_to_process))
        if not unique_modified_files:
            logger.info('   No modified files to test')
            return
        for file_path in unique_modified_files:
            await self._process_modified_file(file_path)
        self.test_runner.report_results(self.generated_tests)

    async def _process_modified_file(self, file_path: str):
        """Process a modified file and generate tests."""
        logger.info(f'   Analyzing {file_path}...')
        changes = self.change_detector.detect_method_changes(file_path)
        if not changes:
            logger.info(f'   No method changes detected in {file_path}')
            return
        for change in changes:
            test_code, test_file, edge_cases = await self.test_generator.generate_test_code_and_file(change)
            if test_code and test_file:
                passed, error_msg = await self.test_runner.run_and_correct_test(change, test_file, test_code)
                self.generated_tests.append(GeneratedTest(test_file=str(test_file), test_name=f'test_{change.method_name}', test_code=test_code, target_method=change.method_name, edge_cases=edge_cases, passed=passed, error_message=error_msg))

    def _emit_regression_check_pass(self, file_path: str, method_name: str):
        """Emit REGRESSION_CHECK_PASS signal to blackboard."""
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals.add(f'REGRESSION_CHECK_PASS:{file_path}:{method_name}')
            logger.info(f'   [OK] Regression check passed for {method_name}')
_regression_oracle = None

def get_regression_oracle(ctx: Any) -> RegressionOracle:
    """Get or create global Regression Oracle instance."""
    global _regression_oracle
    if _regression_oracle is None:
        _regression_oracle = RegressionOracle(ctx)
    return _regression_oracle
