# File: test_main_v10_0.py
# Comprehensive tests for main_v10_0.py
# Tests: Async workflow execution, CLI, integration with LangGraph

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, MagicMock, patch, AsyncMock, mock_open
from datetime import datetime

# pytest-asyncio for async test support
pytest_plugins = ('pytest_asyncio',)

try:
    from main_v10_0 import (
        setup_logging, load_job_input, run_workflow_async, main
    )
    from core_v10_0 import (
        WorkflowContext, MainGraphState,
        FileIOError, CostCeilingExceededError
    )
except ImportError:
    pytest.skip("main_v10_0 module not available", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_job_input():
    """Sample job input data"""
    return {
        "company_name": "Test Corp",
        "job_title": "Senior AI Engineer",
        "job_description": "Build cutting-edge AI systems. " * 100,  # Long description
        "required_skills": ["Python", "TensorFlow", "LangChain"],
        "location": "San Francisco, CA"
    }


@pytest.fixture
def sample_master_resume():
    """Sample master resume data"""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-0100",
        "experience": [
            {
                "company": "Previous Corp",
                "title": "AI Engineer",
                "duration": "2020-2023",
                "bullets": [
                    "Built ML pipelines",
                    "Deployed 10+ models to production"
                ]
            }
        ],
        "skills": ["Python", "PyTorch", "AWS", "Docker"]
    }


@pytest.fixture
def temp_job_file(tmp_path, sample_job_input):
    """Create temporary job input file"""
    job_file = tmp_path / "job_input.json"
    job_file.write_text(json.dumps(sample_job_input))
    return str(job_file)


@pytest.fixture
def temp_resume_file(tmp_path, sample_master_resume):
    """Create temporary resume file"""
    resume_file = tmp_path / "master_resume.json"
    resume_file.write_text(json.dumps(sample_master_resume))
    return str(resume_file)


@pytest.fixture
def mock_workflow_context():
    """Mock WorkflowContext"""
    context = MagicMock(spec=WorkflowContext)
    
    # Mock cache manager
    context.cache_manager.get_stats.return_value = {
        'hits': 10,
        'misses': 5,
        'hit_rate_pct': 66.7
    }
    
    # Mock cost tracker
    context.cost_tracker.get_cost_summary.return_value = {
        'total_workflow_cost': 1.25,
        'agent_costs': {
            'StrategyAgent': 0.30,
            'BulletGeneratorAgent': 0.45,
            'QAAgent': 0.50
        }
    }
    
    return context


@pytest.fixture
def mock_graph_app():
    """Mock LangGraph application"""
    app = MagicMock()
    
    # Mock successful workflow execution
    final_state = {
        'artifacts': {
            'artifacts': {
                'validation_results': {
                    'overall_passed': True,
                    'checks': []
                },
                'final_resume': {"generated": True}
            }
        },
        'metadata': {
            'workflow_id': 'test-workflow-123'
        }
    }
    
    app.invoke.return_value = final_state
    return app


# ============================================================================
# SETUP TESTS
# ============================================================================

class TestSetup:
    """Test setup and initialization functions"""
    
    def test_setup_logging_creates_log_dir(self, tmp_path, monkeypatch):
        """Test setup_logging creates log directory"""
        log_file = tmp_path / "logs" / "test.log"
        
        mock_config = MagicMock()
        mock_config.logging_config.log_file = str(log_file)
        
        with patch('main_v10_0.CONFIG', mock_config):
            setup_logging(debug_mode=False)
            assert log_file.parent.exists()
    
    def test_setup_logging_debug_mode(self, tmp_path, monkeypatch):
        """Test setup_logging with debug mode"""
        log_file = tmp_path / "logs" / "test.log"
        
        mock_config = MagicMock()
        mock_config.logging_config.log_file = str(log_file)
        
        with patch('main_v10_0.CONFIG', mock_config), \
             patch('logging.basicConfig') as mock_basic_config:
            setup_logging(debug_mode=True)
            # Check debug level was set
            call_args = mock_basic_config.call_args
            assert call_args is not None
    
    def test_load_job_input_success(self, temp_job_file, sample_job_input):
        """Test load_job_input successfully loads JSON"""
        data = load_job_input(temp_job_file)
        assert data == sample_job_input
        assert data['company_name'] == "Test Corp"
    
    def test_load_job_input_file_not_found(self):
        """Test load_job_input raises FileIOError for missing file"""
        with pytest.raises(FileIOError, match="Failed to load"):
            load_job_input("/nonexistent/path.json")
    
    def test_load_job_input_invalid_json(self, tmp_path):
        """Test load_job_input raises FileIOError for invalid JSON"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json content")
        
        with pytest.raises(FileIOError, match="Invalid JSON"):
            load_job_input(str(invalid_file))


# ============================================================================
# ASYNC WORKFLOW TESTS (ROW 6: Async Performance)
# ============================================================================

class TestAsyncWorkflow:
    """Test async workflow execution"""
    
    @pytest.mark.asyncio
    async def test_run_workflow_async_success(
        self, temp_job_file, temp_resume_file, mock_workflow_context, mock_graph_app
    ):
        """Test successful async workflow execution"""
        with patch('main_v10_0.redis.Redis') as mock_redis, \
             patch('main_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('main_v10_0.get_graph_app', return_value=mock_graph_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            # Setup sanitizer mock
            mock_sanitizer.return_value.run.return_value = {"sanitized": True}
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            assert result['status'] == 'SUCCESS'
            assert 'workflow_id' in result
            assert result['cost'] > 0
            assert 'cache_stats' in result
            assert result['validation']['overall_passed'] is True
    
    @pytest.mark.asyncio
    async def test_run_workflow_async_qa_failure(
        self, temp_job_file, temp_resume_file, mock_workflow_context
    ):
        """Test workflow with QA validation failure"""
        # Mock failed validation
        failed_state = {
            'artifacts': {
                'artifacts': {
                    'validation_results': {
                        'overall_passed': False,
                        'checks': [
                            {'name': 'bullet_count', 'passed': False}
                        ]
                    }
                }
            },
            'metadata': {'workflow_id': 'test-123'}
        }
        
        mock_app = MagicMock()
        mock_app.invoke.return_value = failed_state
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('main_v10_0.get_graph_app', return_value=mock_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_sanitizer.return_value.run.return_value = {}
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            assert result['status'] == 'FAILED_QA'
            assert result['validation']['overall_passed'] is False
    
    @pytest.mark.asyncio
    async def test_run_workflow_async_cost_ceiling_exceeded(
        self, temp_job_file, temp_resume_file
    ):
        """Test workflow stops when cost ceiling exceeded"""
        mock_context = MagicMock(spec=WorkflowContext)
        mock_context.cost_tracker.get_cost_summary.return_value = {
            'total_workflow_cost': 6.0  # Over 5.0 ceiling
        }
        
        mock_app = MagicMock()
        mock_app.invoke.side_effect = CostCeilingExceededError("Cost exceeded $5.00")
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext', return_value=mock_context), \
             patch('main_v10_0.get_graph_app', return_value=mock_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_sanitizer.return_value.run.return_value = {}
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            assert result['status'] == 'FAILED_COST'
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_run_workflow_async_fatal_error(
        self, temp_job_file, temp_resume_file
    ):
        """Test workflow handles fatal errors gracefully"""
        mock_app = MagicMock()
        mock_app.invoke.side_effect = Exception("Unexpected failure")
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext'), \
             patch('main_v10_0.get_graph_app', return_value=mock_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_sanitizer.return_value.run.return_value = {}
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            assert result['status'] == 'FAILED_FATAL'
            assert 'Unexpected failure' in result['error']
    
    @pytest.mark.asyncio
    async def test_run_workflow_async_pii_sanitization(
        self, temp_job_file, temp_resume_file, sample_master_resume
    ):
        """Test PII sanitization is applied"""
        mock_sanitizer = MagicMock()
        mock_sanitizer.run.return_value = {
            **sample_master_resume,
            "phone": "[REDACTED]"
        }
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext'), \
             patch('main_v10_0.get_graph_app') as mock_get_graph, \
             patch('main_v10_0.PIISanitizerAgent', return_value=mock_sanitizer), \
             patch('main_v10_0.RedisSaver'):
            
            mock_app = MagicMock()
            mock_app.invoke.return_value = {
                'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
                'metadata': {'workflow_id': 'test'}
            }
            mock_get_graph.return_value = mock_app
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            # Verify sanitizer was called
            mock_sanitizer.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_workflow_async_cache_stats_logged(
        self, temp_job_file, temp_resume_file, mock_workflow_context, mock_graph_app
    ):
        """Test cache statistics are logged"""
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext', return_value=mock_workflow_context), \
             patch('main_v10_0.get_graph_app', return_value=mock_graph_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_sanitizer.return_value.run.return_value = {}
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            # Verify cache stats were retrieved
            mock_workflow_context.cache_manager.get_stats.assert_called_once()
            assert result['cache_stats']['hit_rate_pct'] == 66.7


# ============================================================================
# CLI INTERFACE TESTS
# ============================================================================

class TestCLI:
    """Test CLI interface"""
    
    def test_main_cli_success(self, temp_job_file, temp_resume_file):
        """Test successful CLI execution"""
        test_args = [
            'main_v10_0.py',
            '--job', temp_job_file,
            '--master', temp_resume_file
        ]
        
        mock_result = {
            'status': 'SUCCESS',
            'workflow_id': 'test-123',
            'cost': 1.25,
            'cache_stats': {'hit_rate_pct': 50.0, 'hits': 5, 'misses': 5},
            'validation': {'overall_passed': True}
        }
        
        with patch('sys.argv', test_args), \
             patch('main_v10_0.asyncio.run', return_value=mock_result), \
             patch('main_v10_0.setup_logging'), \
             pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0  # Success exit code
    
    def test_main_cli_failure(self, temp_job_file, temp_resume_file):
        """Test CLI with failed workflow"""
        test_args = [
            'main_v10_0.py',
            '--job', temp_job_file,
            '--master', temp_resume_file
        ]
        
        mock_result = {
            'status': 'FAILED_QA',
            'workflow_id': 'test-123',
            'error': 'Validation failed'
        }
        
        with patch('sys.argv', test_args), \
             patch('main_v10_0.asyncio.run', return_value=mock_result), \
             patch('main_v10_0.setup_logging'), \
             pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1  # Failure exit code
    
    def test_main_cli_debug_mode(self, temp_job_file, temp_resume_file):
        """Test CLI with debug mode enabled"""
        test_args = [
            'main_v10_0.py',
            '--job', temp_job_file,
            '--master', temp_resume_file,
            '--debug'
        ]
        
        mock_result = {'status': 'SUCCESS', 'workflow_id': 'test'}
        
        with patch('sys.argv', test_args), \
             patch('main_v10_0.asyncio.run', return_value=mock_result), \
             patch('main_v10_0.setup_logging') as mock_setup, \
             pytest.raises(SystemExit):
            main()
        
        # Verify debug mode was passed
        mock_setup.assert_called_with(debug_mode=True)
    
    def test_main_cli_missing_arguments(self):
        """Test CLI fails with missing required arguments"""
        test_args = ['main_v10_0.py']  # Missing --job and --master
        
        with patch('sys.argv', test_args), \
             pytest.raises(SystemExit):
            main()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestMainIntegration:
    """Integration tests for main workflow"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_real_state(
        self, temp_job_file, temp_resume_file, sample_job_input, sample_master_resume
    ):
        """Test full workflow with real state objects"""
        mock_context = MagicMock(spec=WorkflowContext)
        mock_context.cache_manager.get_stats.return_value = {
            'hits': 0, 'misses': 10, 'hit_rate_pct': 0.0
        }
        mock_context.cost_tracker.get_cost_summary.return_value = {
            'total_workflow_cost': 0.75
        }
        
        # Mock graph app that returns realistic state
        def mock_invoke(state_dict, config):
            # Simulate workflow processing
            state = MainGraphState.from_dict(state_dict)
            state.artifacts.artifacts['validation_results'] = {
                'overall_passed': True,
                'checks': []
            }
            return state.to_dict()
        
        mock_app = MagicMock()
        mock_app.invoke = mock_invoke
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext', return_value=mock_context), \
             patch('main_v10_0.get_graph_app', return_value=mock_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_sanitizer.return_value.run.return_value = sample_master_resume
            
            result = await run_workflow_async(
                temp_job_file,
                temp_resume_file,
                debug_mode=False
            )
            
            assert result['status'] == 'SUCCESS'
            assert result['cost'] == 0.75
    
    @pytest.mark.asyncio
    async def test_workflow_with_long_job_description(
        self, tmp_path, sample_master_resume
    ):
        """Test workflow handles long job descriptions"""
        # Create job with very long description (>10KB)
        long_job = {
            "company_name": "Test Corp",
            "job_title": "Engineer",
            "job_description": "Requirements: " * 2000  # ~20KB
        }
        
        job_file = tmp_path / "long_job.json"
        job_file.write_text(json.dumps(long_job))
        
        resume_file = tmp_path / "resume.json"
        resume_file.write_text(json.dumps(sample_master_resume))
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext'), \
             patch('main_v10_0.get_graph_app') as mock_get_graph, \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_app = MagicMock()
            mock_app.invoke.return_value = {
                'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
                'metadata': {'workflow_id': 'test'}
            }
            mock_get_graph.return_value = mock_app
            mock_sanitizer.return_value.run.return_value = sample_master_resume
            
            result = await run_workflow_async(
                str(job_file),
                str(resume_file),
                debug_mode=False
            )
            
            # Should complete without error
            assert result['status'] in ['SUCCESS', 'FAILED_QA', 'FAILED_COST']


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_workflow_completes_within_timeout(
        self, temp_job_file, temp_resume_file
    ):
        """Test workflow completes within reasonable time"""
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
            'metadata': {'workflow_id': 'test'}
        }
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext'), \
             patch('main_v10_0.get_graph_app', return_value=mock_app), \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            mock_sanitizer.return_value.run.return_value = {}
            
            # Should complete in under 5 seconds (mocked)
            try:
                result = await asyncio.wait_for(
                    run_workflow_async(temp_job_file, temp_resume_file),
                    timeout=5.0
                )
                assert result is not None
            except asyncio.TimeoutError:
                pytest.fail("Workflow exceeded timeout")


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-k", "not slow"])
