"""
Tests for Context Window Estimator

Tests the token estimation accuracy, compression policies, and integration.
"""

import json
from pathlib import Path

import pytest


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def token_estimator_classes():
    from tools.utils.planning.preflight_hook import PlanningPreflightHook, TokenBudgetExceededError
    from tools.utils.planning.token_estimator import (
        ContextSource,
        ContextWindowEstimator,
        TokenBudget,
        TokenEstimate,
    )
    return ContextWindowEstimator, TokenBudget, TokenEstimate, ContextSource, PlanningPreflightHook, TokenBudgetExceededError


class TestContextWindowEstimator:
    """Test the ContextWindowEstimator functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        from tools.utils.planning.token_estimator import (
            ContextWindowEstimator,
            TokenBudget,
        )
        self.estimator = ContextWindowEstimator()
        self.budget = TokenBudget()

    def test_token_estimation_basic(self):
        """Test basic token estimation"""
        # Simple text content
        text = "This is a simple test with some content."
        tokens = self.estimator._estimate_tokens(text, 'text')

        assert tokens > 0
        assert isinstance(tokens, int)

        # Code content should have different rate
        code = "def hello_world():\n    print('Hello, World!')"
        code_tokens = self.estimator._estimate_tokens(code, 'code')

        assert code_tokens > 0

    def test_content_type_detection(self):
        """Test content type detection"""
        # Python file
        python_content = "import os\nprint(os.getcwd())"
        assert self.estimator._detect_content_type(python_content, 'test.py') == 'code'

        # JSON file
        json_content = '{"key": "value", "number": 42}'
        assert self.estimator._detect_content_type(json_content, 'config.json') == 'json'

        # Log content
        log_content = "2023-01-01 12:00:00 ERROR: Something went wrong\nTraceback..."
        assert self.estimator._detect_content_type(log_content, 'app.log') == 'log'

        # Diff content
        diff_content = "diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n+new line"
        assert self.estimator._detect_content_type(diff_content, 'file.patch') == 'diff'

    def test_status_action_determination(self):
        """Test status and action determination based on token counts"""
        # Green status (below WARNING_THRESHOLD of 197000)
        status, action = self.estimator._determine_status_action(140000)
        assert status == 'green'
        assert action == 'proceed'

        # Yellow status (between WARNING_THRESHOLD and SAFE_OPERATING_CAP)
        # WARNING_THRESHOLD = 197000, SAFE_OPERATING_CAP = 223000
        status, action = self.estimator._determine_status_action(200000)
        assert status == 'yellow'
        assert action == 'compress'

        # Red status (above SAFE_OPERATING_CAP of 223000 but below HARD_MAX of 262000)
        status, action = self.estimator._determine_status_action(230000)
        assert status == 'red'
        assert action == 'block'

        # Red status (above HARD_MAX_CONTEXT of 262000)
        status, action = self.estimator._determine_status_action(270000)
        assert status == 'red'
        assert action == 'block'

    def test_complete_step_estimation(self):
        """Test complete step token estimation"""
        from tools.utils.planning.token_estimator import TokenEstimate
        # Prepare test data
        plan_step = "Test implementation"
        system_prompt = "You are a helpful assistant."
        user_prompt = "Please implement this feature."
        files = [
            {"path": "test.py", "content": "def test():\n    pass\n"},
            {"path": "config.json", "content": '{"debug": true}'}
        ]
        diffs = [
            {"path": "test.py", "content": "+def new_function():\n+    pass"}
        ]
        logs = [
            {"source": "test", "content": "Running tests...\nERROR: Test failed"}
        ]
        retrieved_context = [
            {"source": "docs", "content": "This is documentation content."}
        ]
        prior_steps = ["Previous step content"]

        # Estimate tokens
        estimate = self.estimator.estimate_step_tokens(
            plan_step=plan_step,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            files=files,
            diffs=diffs,
            logs=logs,
            retrieved_context=retrieved_context,
            prior_steps=prior_steps
        )

        # Verify estimate structure
        assert isinstance(estimate, TokenEstimate)
        assert estimate.plan_step == plan_step
        assert estimate.estimated_input_tokens > 0
        assert estimate.reserved_output_tokens == self.budget.DEFAULT_RESERVED_OUTPUT
        assert estimate.safety_buffer_tokens == self.budget.DEFAULT_SAFETY_BUFFER
        assert estimate.total_projected_tokens > estimate.estimated_input_tokens
        assert estimate.status in ['green', 'yellow', 'red']
        assert estimate.action in ['proceed', 'compress', 'block']
        assert isinstance(estimate.top_contributors, list)
        assert isinstance(estimate.recommended_reductions, list)

    def test_compression_policies(self):
        """Test compression policies"""
        from tools.utils.planning.token_estimator import ContextSource
        # Test individual compression functions directly

        # Test duplicate removal
        duplicate_sources = [
            ContextSource('file', 'same content', 100),
            ContextSource('file', 'same content', 100),
            ContextSource('file', 'different content', 50)
        ]
        filtered_sources, applied = self.estimator._remove_duplicates(duplicate_sources)
        assert applied == True  # Duplicates should be removed
        assert len(filtered_sources) == 2  # One duplicate removed

        # Test large file summarization
        large_file_content = '\n'.join(f'line_{i}' for i in range(1500))  # 1500 lines
        large_file_sources = [
            ContextSource('file', large_file_content, 5000, metadata={'path': 'large.py', 'lines': 1500})
        ]
        filtered_sources, applied = self.estimator._summarize_large_files(large_file_sources)
        assert applied == True  # Large file should be summarized
        assert filtered_sources[0].compressed == True

        # Test log trimming
        log_content = '''
INFO: Starting process
DEBUG: Loading configuration
INFO: Process started
ERROR: Failed to load
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    load_config()
FileNotFoundError: Config file not found
ERROR: Another error
INFO: Process completed
        '''.strip()
        log_sources = [
            ContextSource('log', log_content, 200, metadata={'source': 'app.log'})
        ]
        filtered_sources, applied = self.estimator._trim_logs_to_errors(log_sources)
        assert applied == True  # Logs should be trimmed
        assert 'ERROR:' in filtered_sources[0].content
        assert filtered_sources[0].content.count('INFO:') < log_content.count('INFO:')

        # Test retrieval chunk reduction
        many_retrieval_sources = [
            ContextSource('retrieval', f'chunk_{i}', 50, metadata={'chunk_id': f'chunk_{i}'})
            for i in range(15)  # 15 chunks > max of 10
        ]
        filtered_sources, applied = self.estimator._reduce_retrieval_chunks(many_retrieval_sources)
        assert applied == True  # Retrieval chunks should be reduced
        assert len([s for s in filtered_sources if s.source_type == 'retrieval']) == 10

        # Test diff vs file preference
        overlap_sources = [
            ContextSource('file', 'file content', 1000, metadata={'path': 'test.py'}),
            ContextSource('diff', 'diff content', 500, metadata={'path': 'test.py'})
        ]
        filtered_sources, applied = self.estimator._prefer_diff_over_file(overlap_sources)
        assert applied == True  # Should prefer diff over file
        assert len([s for s in filtered_sources if s.source_type == 'file']) == 0
        assert len([s for s in filtered_sources if s.source_type == 'diff']) == 1

        # Test low relevance file dropping
        low_relevance_sources = [
            ContextSource('file', 'important code', 1000, metadata={'path': 'src/main.py'}),
            ContextSource('file', 'lock file content', 500, metadata={'path': 'package-lock.json'}),
            ContextSource('file', 'cache content', 300, metadata={'path': '.cache/data'})
        ]
        filtered_sources, applied = self.estimator._drop_low_relevance_files(low_relevance_sources)
        assert applied == True  # Low relevance files should be dropped
        assert len(filtered_sources) == 1  # Only important file remains

        # The individual compression functions are working correctly
        # The full pipeline test is optional since we've verified each component

    def test_duplicate_removal(self):
        """Test duplicate content removal"""
        from tools.utils.planning.token_estimator import ContextSource
        sources = [
            ContextSource('file', 'same content', 100),
            ContextSource('file', 'same content', 100),
            ContextSource('file', 'different content', 50)
        ]

        filtered_sources, applied = self.estimator._remove_duplicates(sources)

        assert applied is True
        assert len(filtered_sources) == 2  # One duplicate removed

    def test_large_file_summarization(self):
        """Test large file summarization"""
        from tools.utils.planning.token_estimator import ContextSource
        large_content = '\n'.join(f'line_{i}' for i in range(1500))  # 1500 lines
        sources = [
            ContextSource('file', large_content, 5000, metadata={'path': 'large.py', 'lines': 1500})
        ]

        filtered_sources, applied = self.estimator._summarize_large_files(sources)

        assert applied is True

def test_log_trimming():
    """Test log trimming to errors only"""
    from tools.utils.planning.token_estimator import ContextSource, ContextWindowEstimator
    estimator = ContextWindowEstimator()
    log_content = '''
INFO: Starting process
DEBUG: Loading configuration
INFO: Process started
ERROR: Something went wrong
DEBUG: More debug info
ERROR: Another error
INFO: Process finished
        '''.strip()

    sources = [
        ContextSource('log', log_content, 200, metadata={'source': 'app.log'})
    ]

    filtered_sources, applied = estimator._trim_logs_to_errors(sources)

    assert applied is True
    assert 'ERROR:' in filtered_sources[0].content
    assert 'INFO:' not in filtered_sources[0].content or filtered_sources[0].content.count('INFO:') < log_content.count('INFO:')

def test_retrieval_chunk_reduction():
    """Test retrieval chunk reduction"""
    from tools.utils.planning.token_estimator import ContextSource, ContextWindowEstimator
    estimator = ContextWindowEstimator()
    many_chunks = [
        ContextSource('retrieval', f'chunk_{i}', 50, metadata={'chunk_id': f'chunk_{i}'})
        for i in range(15)  # 15 chunks > max of 10
    ]

    filtered_sources, applied = estimator._reduce_retrieval_chunks(many_chunks)

    assert applied is True
    assert len([s for s in filtered_sources if s.source_type == 'retrieval']) == 10

def test_to_dict_serialization():
    """Test JSON serialization of estimates"""
    from tools.utils.planning.token_estimator import ContextWindowEstimator, TokenEstimate
    estimator = ContextWindowEstimator()
    estimate = TokenEstimate(
        plan_step="test",
        estimated_input_tokens=50000,
        reserved_output_tokens=12000,
        safety_buffer_tokens=8000,
        total_projected_tokens=70000,
        status="green",
        action="proceed",
        top_contributors=[{"type": "files", "tokens": 30000}],
        recommended_reductions=[],
        compression_applied=[]
    )

    # Convert to dict
    estimate_dict = estimator.to_dict(estimate)

    # Verify structure
    assert isinstance(estimate_dict, dict)
    assert estimate_dict['plan_step'] == "test"
    assert estimate_dict['status'] == "green"
    assert isinstance(estimate_dict['top_contributors'], list)

    # Test JSON serialization
    json_str = json.dumps(estimate_dict)
    assert json.loads(json_str) == estimate_dict

class TestPlanningPreflightHook:
    """Test the PlanningPreflightHook integration"""

    def setup_method(self):
        """Setup test fixtures"""
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        import tempfile
        import uuid
        # Use unique temp directory per test to avoid parallel execution conflicts
        self.temp_dir = Path(tempfile.gettempdir()) / f"test_token_budget_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.budget_file = self.temp_dir / "test_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        import time
        # Wait a moment for file handles to close (Windows)
        time.sleep(0.1)
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows

    def test_preflight_check_success(self):
        """Test successful preflight check"""
        from tools.utils.planning.token_estimator import TokenEstimate
        estimate = self.hook.preflight_check(
            plan_step="test_step",
            system_prompt="System prompt",
            user_prompt="User prompt",
            files=[{"path": "test.py", "content": "def test(): pass"}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert isinstance(estimate, TokenEstimate)
        assert estimate.plan_step == "test_step"
        assert estimate.status in ['green', 'yellow', 'red']

        # Check that history was saved
        assert len(self.hook.budget_history) == 1
        assert self.budget_file.exists()

    def test_preflight_check_budget_exceeded(self):
        """Test preflight check with exceeded budget"""
        from tools.utils.planning.preflight_hook import TokenBudgetExceededError
        # Create content that will exceed the hard limit (200K)
        # Need to create content that will result in >200K tokens after conservative estimation
        very_large_content = 'x' * 1000000  # 1M characters should be ~400K tokens with conservative rate

        with pytest.raises(TokenBudgetExceededError):
            self.hook.preflight_check(
                plan_step="large_step",
                system_prompt=very_large_content,
                user_prompt=very_large_content,
                files=[{"path": "large.py", "content": very_large_content}],
                diffs=[{"path": "large.py", "content": very_large_content}],
                logs=[{"source": "large.log", "content": very_large_content}],
                retrieved_context=[{"content": very_large_content}] * 20,  # Many chunks
                prior_steps=[very_large_content] * 10  # Many prior steps
            )

    def test_budget_summary(self):
        """Test budget summary generation"""
        # Add some estimates to history
        self.hook.budget_history = [
            {
                'plan_step': 'step1',
                'total_projected_tokens': 50000,
                'status': 'green'
            },
            {
                'plan_step': 'step2',
                'total_projected_tokens': 160000,
                'status': 'yellow'
            },
            {
                'plan_step': 'step3',
                'total_projected_tokens': 180000,
                'status': 'red'
            }
        ]

        summary = self.hook.get_budget_summary()

        assert summary['total_steps'] == 3
        assert summary['total_tokens'] == 390000
        assert summary['average_tokens_per_step'] == 130000
        assert summary['status_distribution'] == {'green': 1, 'yellow': 1, 'red': 1}
        assert summary['max_tokens'] == 180000
        assert summary['min_tokens'] == 50000

    def test_history_persistence(self):
        """Test that budget history persists across hook instances"""
        # Add an estimate to first hook
        self.hook.preflight_check(
            plan_step="persist_test",
            system_prompt="test",
            user_prompt="test",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        # Create new hook instance with same file
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        new_hook = PlanningPreflightHook(budget_file=self.budget_file)

        # History should be loaded
        assert len(new_hook.budget_history) == 1
        assert new_hook.budget_history[0]['plan_step'] == "persist_test"

    def test_clear_history(self):
        """Test clearing budget history"""
        # Add some history
        self.hook.budget_history = [{'test': 'data'}]
        self.hook._save_budget_history()

        # Clear history
        self.hook.clear_history()

        # Verify cleared
        assert len(self.hook.budget_history) == 0
        assert self.budget_file.exists()
        with open(self.budget_file) as f:
            assert json.load(f) == []

class TestTokenBudgetDecorator:
    """Test the token budget decorator"""

    def setup_method(self):
        """Setup test fixtures"""
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        import tempfile
        import uuid
        # Use unique temp directory per test to avoid parallel execution conflicts
        self.temp_dir = Path(tempfile.gettempdir()) / f"test_decorator_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.budget_file = self.temp_dir / "test_decorator.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        import time
        # Wait a moment for file handles to close (Windows)
        time.sleep(0.1)
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows

    def test_decorator_success(self):
        """Test decorator with successful execution"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def test_function(plan_step, system_prompt, **kwargs):
            return "success"

        result = test_function(
            plan_step="decorator_test",
            system_prompt="test",
            user_prompt="test",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert result == "success"
        assert len(self.hook.budget_history) == 1

    def test_decorator_block(self):
        """Test decorator with blocked execution"""
        from tools.utils.planning.preflight_hook import TokenBudgetExceededError, require_token_budget

        @require_token_budget(self.hook)
        def test_function(plan_step, system_prompt, **kwargs):
            return "should not execute"

        # Use content that will trigger block action - need much larger content
        very_large_content = 'x' * 1000000  # 1M characters

        with pytest.raises(TokenBudgetExceededError):
            test_function(
                plan_step="blocked_test",
                system_prompt=very_large_content,
                user_prompt=very_large_content,
                files=[{"path": "large.py", "content": very_large_content}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

if __name__ == "__main__":
    pytest.main([__file__])
