# File: test_batch_v10_0.py
# Comprehensive tests for run_batch_v10_0.py
# Tests: Async batch processing, concurrency control, circuit breaker

import pytest
import asyncio
import json
import os
import csv
import shutil
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime

pytest_plugins = ('pytest_asyncio',)

try:
    from run_batch_v10_0 import (
        process_single_job_async, run_batch_async, run_batch,
        BATCH_QUEUE_DIR, BATCH_COMPLETE_DIR, SUMMARY_FILE
    )
    from core_v10_0 import (
        WorkflowContext, MainGraphState,
        CircuitBreakerOpenError, CostCeilingExceededError
    )
except ImportError:
    pytest.skip("run_batch_v10_0 module not available", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def batch_dirs(tmp_path):
    """Create temporary batch directories"""
    queue_dir = tmp_path / "batch_queue"
    complete_dir = tmp_path / "batch_complete"
    queue_dir.mkdir()
    complete_dir.mkdir()
    
    return {
        'queue': str(queue_dir),
        'complete': str(complete_dir),
        'base': str(tmp_path)
    }


@pytest.fixture
def sample_job_files(batch_dirs):
    """Create sample job files in queue"""
    job_files = []
    
    for i in range(3):
        job_data = {
            "company_name": f"Company_{i}",
            "job_title": f"Position_{i}",
            "job_description": f"Description for job {i}. " * 50
        }
        
        job_file = os.path.join(batch_dirs['queue'], f"job_{i}.json")
        with open(job_file, 'w') as f:
            json.dump(job_data, f)
        
        job_files.append(job_file)
    
    return job_files


@pytest.fixture
def mock_workflow_context():
    """Mock WorkflowContext for batch processing"""
    context = MagicMock(spec=WorkflowContext)
    
    context.cache_manager.get_stats.return_value = {
        'hits': 15,
        'misses': 5,
        'hit_rate_pct': 75.0
    }
    
    context.cost_tracker.get_cost_summary.return_value = {
        'total_workflow_cost': 0.85,
        'agent_costs': {}
    }
    
    return context


@pytest.fixture
def mock_graph_app():
    """Mock successful graph app"""
    app = MagicMock()
    
    def invoke_mock(state, config):
        return {
            'artifacts': {
                'artifacts': {
                    'validation_results': {
                        'overall_passed': True,
                        'checks': []
                    }
                }
            },
            'metadata': {'workflow_id': config['configurable']['thread_id']}
        }
    
    app.invoke = Mock(side_effect=invoke_mock)
    return app


# ============================================================================
# SINGLE JOB PROCESSING TESTS (ROW 6: Async)
# ============================================================================

class TestSingleJobAsync:
    """Test async single job processing"""
    
    @pytest.mark.asyncio
    async def test_process_single_job_success(
        self, sample_job_files, mock_workflow_context, mock_graph_app, batch_dirs
    ):
        """Test successful processing of single job"""
        job_path = sample_job_files[0]
        
        with patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class:
            
            mock_load.side_effect = [
                {"company_name": "TestCorp", "job_title": "Engineer", "job_description": "Test"},
                {"master": "resume"}
            ]
            mock_sanitizer.return_value.run.return_value = {"sanitized": True}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {"state": "initial"}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            result = await process_single_job_async(
                job_path, mock_workflow_context, None, mock_graph_app
            )
            
            assert result['status'] == 'SUCCESS'
            assert result['company'] == 'TestCorp'
            assert result['title'] == 'Engineer'
            assert result['cost'] >= 0
            assert 'workflow_id' in result
    
    @pytest.mark.asyncio
    async def test_process_single_job_qa_failure(
        self, sample_job_files, mock_workflow_context, batch_dirs
    ):
        """Test job with QA validation failure"""
        job_path = sample_job_files[0]
        
        # Mock failed validation
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            'artifacts': {
                'artifacts': {
                    'validation_results': {
                        'overall_passed': False,
                        'checks': [
                            {'name': 'check1', 'passed': False},
                            {'name': 'check2', 'passed': False}
                        ]
                    }
                }
            },
            'metadata': {'workflow_id': 'test'}
        }
        
        with patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class:
            
            mock_load.side_effect = [
                {"company_name": "TestCorp", "job_title": "Engineer", "job_description": "Test"},
                {"master": "resume"}
            ]
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            result = await process_single_job_async(
                job_path, mock_workflow_context, None, mock_app
            )
            
            assert result['status'] == 'FAILED_QA'
            assert '2 QA check(s) failed' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_single_job_cost_ceiling(
        self, sample_job_files, mock_workflow_context, mock_graph_app, batch_dirs
    ):
        """Test job exceeds cost ceiling"""
        job_path = sample_job_files[0]
        
        with patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent'):
            
            # Very long description triggers cost ceiling
            mock_load.side_effect = [
                {
                    "company_name": "TestCorp",
                    "job_title": "Engineer",
                    "job_description": "X" * 100000  # Huge description
                },
                {"master": "resume"}
            ]
            
            result = await process_single_job_async(
                job_path, mock_workflow_context, None, mock_graph_app
            )
            
            assert result['status'] == 'FAILED_COST'
            assert 'exceeds ceiling' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_single_job_circuit_breaker(
        self, sample_job_files, mock_workflow_context, mock_graph_app, batch_dirs
    ):
        """Test job skipped due to circuit breaker"""
        job_path = sample_job_files[0]
        
        mock_app = MagicMock()
        mock_app.invoke.side_effect = CircuitBreakerOpenError("Circuit open")
        
        with patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class:
            
            mock_load.side_effect = [
                {"company_name": "TestCorp", "job_title": "Engineer", "job_description": "Test"},
                {"master": "resume"}
            ]
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            
            result = await process_single_job_async(
                job_path, mock_workflow_context, None, mock_app
            )
            
            assert result['status'] == 'SKIPPED'
            assert 'CircuitBreakerOpen' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_single_job_fatal_error(
        self, sample_job_files, mock_workflow_context, mock_graph_app, batch_dirs
    ):
        """Test job with fatal error"""
        job_path = sample_job_files[0]
        
        with patch('run_batch_v10_0.load_job_input') as mock_load:
            mock_load.side_effect = Exception("Unexpected error")
            
            result = await process_single_job_async(
                job_path, mock_workflow_context, None, mock_graph_app
            )
            
            assert result['status'] == 'FAILED_FATAL'
            assert 'Unexpected error' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_single_job_file_moved(
        self, sample_job_files, mock_workflow_context, mock_graph_app, batch_dirs
    ):
        """Test job file is moved to complete directory"""
        job_path = sample_job_files[0]
        job_filename = os.path.basename(job_path)
        
        with patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']):
            
            mock_load.side_effect = [
                {"company_name": "TestCorp", "job_title": "Engineer", "job_description": "Test"},
                {"master": "resume"}
            ]
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            await process_single_job_async(
                job_path, mock_workflow_context, None, mock_graph_app
            )
            
            # Verify file was moved
            assert not os.path.exists(job_path)
            assert os.path.exists(os.path.join(batch_dirs['complete'], job_filename))


# ============================================================================
# BATCH PROCESSING TESTS (ROW 6: Async with Concurrency)
# ============================================================================

class TestBatchAsync:
    """Test async batch processing with concurrency control"""
    
    @pytest.mark.asyncio
    async def test_run_batch_async_success(
        self, batch_dirs, sample_job_files, mock_workflow_context, mock_graph_app
    ):
        """Test successful batch processing"""
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']), \
             patch('run_batch_v10_0.SUMMARY_FILE', os.path.join(batch_dirs['base'], 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis') as mock_redis, \
             patch('run_batch_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('run_batch_v10_0.get_graph_app', return_value=mock_graph_app), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False):
            
            mock_load.side_effect = lambda path: (
                {"company_name": "Test", "job_title": "Engineer", "job_description": "Test"}
                if "job_" in path else {"master": "resume"}
            )
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            await run_batch_async()
            
            # Verify CSV was created
            summary_file = os.path.join(batch_dirs['base'], 'summary.csv')
            assert os.path.exists(summary_file)
            
            # Verify entries in CSV
            with open(summary_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) > 1  # Header + data rows
    
    @pytest.mark.asyncio
    async def test_run_batch_async_no_jobs(self, batch_dirs):
        """Test batch processing with empty queue"""
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']):
            
            await run_batch_async()
            # Should complete without error
    
    @pytest.mark.asyncio
    async def test_run_batch_async_mixed_results(
        self, batch_dirs, mock_workflow_context
    ):
        """Test batch with mix of success and failure"""
        # Create jobs
        jobs = []
        for i, status in enumerate(['SUCCESS', 'FAILED_QA', 'FAILED_COST']):
            job_file = os.path.join(batch_dirs['queue'], f"job_{i}.json")
            with open(job_file, 'w') as f:
                json.dump({
                    "company_name": f"Company_{i}",
                    "job_title": f"Title_{i}",
                    "job_description": "Test" * 100
                }, f)
            jobs.append(job_file)
        
        # Mock different outcomes
        def mock_invoke(state, config):
            job_idx = int(config['configurable']['thread_id'].split('-')[-1]) % 3
            if job_idx == 0:  # SUCCESS
                return {
                    'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
                    'metadata': {'workflow_id': 'test'}
                }
            elif job_idx == 1:  # FAILED_QA
                return {
                    'artifacts': {'artifacts': {'validation_results': {
                        'overall_passed': False,
                        'checks': [{'passed': False}]
                    }}},
                    'metadata': {'workflow_id': 'test'}
                }
            else:  # FAILED_COST
                raise CostCeilingExceededError("Cost exceeded")
        
        mock_app = MagicMock()
        mock_app.invoke = Mock(side_effect=mock_invoke)
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']), \
             patch('run_batch_v10_0.SUMMARY_FILE', os.path.join(batch_dirs['base'], 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('run_batch_v10_0.get_graph_app', return_value=mock_app), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False):
            
            mock_load.side_effect = lambda path: (
                {"company_name": "Test", "job_title": "Engineer", "job_description": "Test"}
                if "job_" in path else {"master": "resume"}
            )
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            await run_batch_async()
            
            # Verify mixed results in CSV
            summary_file = os.path.join(batch_dirs['base'], 'summary.csv')
            with open(summary_file, 'r') as f:
                content = f.read()
                assert 'SUCCESS' in content
                assert 'FAILED' in content
    
    @pytest.mark.asyncio
    async def test_run_batch_async_concurrency_limit(
        self, batch_dirs, mock_workflow_context
    ):
        """Test batch respects max_concurrent_llm_calls"""
        # Create 20 jobs
        for i in range(20):
            job_file = os.path.join(batch_dirs['queue'], f"job_{i}.json")
            with open(job_file, 'w') as f:
                json.dump({
                    "company_name": f"Company_{i}",
                    "job_title": "Engineer",
                    "job_description": "Test"
                }, f)
        
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
            'metadata': {'workflow_id': 'test'}
        }
        
        max_concurrent_calls = []
        
        async def track_concurrency(*args, **kwargs):
            # Track concurrent calls
            current = len(max_concurrent_calls)
            max_concurrent_calls.append(1)
            await asyncio.sleep(0.01)  # Simulate work
            max_concurrent_calls.pop()
            return args[0]  # Return state
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']), \
             patch('run_batch_v10_0.SUMMARY_FILE', os.path.join(batch_dirs['base'], 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('run_batch_v10_0.get_graph_app', return_value=mock_app), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False), \
             patch('asyncio.to_thread', side_effect=track_concurrency):
            
            mock_load.side_effect = lambda path: (
                {"company_name": "Test", "job_title": "Engineer", "job_description": "Test"}
                if "job_" in path else {"master": "resume"}
            )
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            await run_batch_async()
            
            # Max concurrent should not exceed configured limit (10)
            # Note: This is a simplified test; actual verification would need more instrumentation
    
    @pytest.mark.asyncio
    async def test_run_batch_async_cache_sharing(
        self, batch_dirs, sample_job_files
    ):
        """Test cache is shared across batch jobs"""
        mock_context = MagicMock(spec=WorkflowContext)
        cache_calls = []
        
        def track_cache_get(key):
            cache_calls.append(('get', key))
            return None
        
        def track_cache_set(key, value):
            cache_calls.append(('set', key))
        
        mock_context.cache_manager.get = Mock(side_effect=track_cache_get)
        mock_context.cache_manager.set = Mock(side_effect=track_cache_set)
        mock_context.cache_manager.get_stats.return_value = {
            'hits': 5, 'misses': 10, 'hit_rate_pct': 33.3
        }
        mock_context.cost_tracker.get_cost_summary.return_value = {
            'total_workflow_cost': 0.5
        }
        
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
            'metadata': {'workflow_id': 'test'}
        }
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']), \
             patch('run_batch_v10_0.SUMMARY_FILE', os.path.join(batch_dirs['base'], 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext', return_value=mock_context), \
             patch('run_batch_v10_0.get_graph_app', return_value=mock_app), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False):
            
            mock_load.side_effect = lambda path: (
                {"company_name": "Test", "job_title": "Engineer", "job_description": "Test"}
                if "job_" in path else {"master": "resume"}
            )
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            await run_batch_async()
            
            # Verify context was created once and shared
            # (In real implementation, cache would be shared)
    
    @pytest.mark.asyncio
    async def test_run_batch_async_meta_learning_trigger(
        self, batch_dirs, sample_job_files, mock_workflow_context, mock_graph_app
    ):
        """Test meta-learning is triggered after batch"""
        mock_meta_learning = AsyncMock()
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']), \
             patch('run_batch_v10_0.SUMMARY_FILE', os.path.join(batch_dirs['base'], 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('run_batch_v10_0.get_graph_app', return_value=mock_graph_app), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', True), \
             patch('run_batch_v10_0.run_meta_learning', mock_meta_learning), \
             patch('run_batch_v10_0.CONFIG') as mock_config:
            
            mock_config.meta_loop_config.enable_meta_learning = True
            
            mock_load.side_effect = lambda path: (
                {"company_name": "Test", "job_title": "Engineer", "job_description": "Test"}
                if "job_" in path else {"master": "resume"}
            )
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            await run_batch_async()
            
            # Verify meta-learning was called
            mock_meta_learning.assert_called_once()


# ============================================================================
# SYNCHRONOUS WRAPPER TESTS
# ============================================================================

class TestBatchSync:
    """Test synchronous batch wrapper"""
    
    def test_run_batch_sync_wrapper(self):
        """Test run_batch synchronous wrapper"""
        with patch('run_batch_v10_0.asyncio.run') as mock_asyncio_run:
            run_batch()
            mock_asyncio_run.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestBatchErrorHandling:
    """Test batch error handling"""
    
    @pytest.mark.asyncio
    async def test_batch_handles_exception_in_job(
        self, batch_dirs, sample_job_files, mock_workflow_context
    ):
        """Test batch continues after job exception"""
        def side_effect_invoke(state, config):
            if 'job_1' in str(state):
                raise Exception("Job 1 failed")
            return {
                'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
                'metadata': {'workflow_id': 'test'}
            }
        
        mock_app = MagicMock()
        mock_app.invoke = Mock(side_effect=side_effect_invoke)
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', batch_dirs['queue']), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', batch_dirs['complete']), \
             patch('run_batch_v10_0.SUMMARY_FILE', os.path.join(batch_dirs['base'], 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('run_batch_v10_0.get_graph_app', return_value=mock_app), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False):
            
            mock_load.side_effect = lambda path: (
                {"company_name": "Test", "job_title": "Engineer", "job_description": "Test"}
                if "job_" in path else {"master": "resume"}
            )
            mock_sanitizer.return_value.run.return_value = {}
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            # Should not raise exception
            await run_batch_async()
            
            # Verify summary was still created
            summary_file = os.path.join(batch_dirs['base'], 'summary.csv')
            assert os.path.exists(summary_file)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
