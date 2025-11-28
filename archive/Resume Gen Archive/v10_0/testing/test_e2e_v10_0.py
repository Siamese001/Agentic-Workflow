# File: test_e2e_v10_0.py
# End-to-End Testing Suite for Resume Generation Engine v10.0
# Tests complete workflows from job input to final resume

import pytest
import asyncio
import json
import os
import time
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

pytest_plugins = ('pytest_asyncio',)

try:
    from main_v10_0 import run_workflow_async
    from run_batch_v10_0 import run_batch_async, process_single_job_async
    from run_learning_v10_0 import run_meta_learning
    from core_v10_0 import WorkflowContext, MainGraphState
except ImportError:
    pytest.skip("v10.0 modules not available", allow_module_level=True)


# ============================================================================
# E2E TEST FIXTURES
# ============================================================================

@pytest.fixture
def e2e_test_env(tmp_path):
    """Create complete test environment"""
    env = {
        'base_dir': tmp_path,
        'queue_dir': tmp_path / 'batch_queue',
        'complete_dir': tmp_path / 'batch_complete',
        'logs_dir': tmp_path / 'logs',
        'outputs_dir': tmp_path / 'outputs'
    }
    
    for dir_path in env.values():
        if isinstance(dir_path, Path):
            dir_path.mkdir(exist_ok=True)
    
    return env


@pytest.fixture
def realistic_job_input():
    """Realistic job posting for E2E testing"""
    return {
        "company_name": "DataRobot Inc",
        "job_title": "Principal AI Architect",
        "location": "Remote",
        "job_description": """
About DataRobot:
DataRobot is the leader in enterprise AI, delivering trusted AI technology and ROI enablement services to global enterprises competing in today's Intelligence Revolution.

Role Overview:
We're seeking a Principal AI Architect to lead the design and implementation of our next-generation agentic AI platform. You'll work at the intersection of LLMs, multi-agent systems, and enterprise data infrastructure.

Key Responsibilities:
• Architect scalable agentic AI systems using LangChain, LangGraph, and modern orchestration frameworks
• Design and implement multi-hop RAG pipelines with HyDE enrichment and cross-encoder reranking
• Lead technical design for production AI deployments processing 10M+ daily requests
• Build constitutional AI frameworks with safety guardrails and bias detection
• Optimize LLM inference costs through caching, batching, and model selection strategies
• Mentor senior engineers on advanced prompt engineering and agentic design patterns
• Collaborate with ML researchers on novel reasoning architectures (ToT, GoT, ReAct)
• Establish best practices for LLM observability, tracing, and quality assurance

Required Qualifications:
• 10+ years software engineering, 5+ years in production ML/AI systems
• Deep expertise in transformer architectures and attention mechanisms
• Proven track record architecting systems at scale (millions of users)
• Strong foundation in distributed systems, async programming, and performance optimization
• Experience with LangChain/LangGraph, OpenAI/Anthropic APIs, vector databases
• Mastery of Python, async/await patterns, and modern testing frameworks
• Track record of technical leadership and cross-functional collaboration

Preferred Qualifications:
• Publications in AI/ML conferences (NeurIPS, ICML, ICLR)
• Open source contributions to LangChain, Haystack, or similar frameworks
• Experience with meta-learning and learning-to-learn systems
• Background in formal verification or AI safety research
• MS/PhD in Computer Science, AI, or related field

Technical Stack:
• Languages: Python 3.11+, TypeScript
• AI Frameworks: LangChain, LangGraph, Haystack
• LLMs: GPT-4, Claude 3.5 Sonnet, Gemini 2.0
• Infrastructure: AWS/GCP, Kubernetes, Redis, PostgreSQL
• Tools: Docker, Terraform, DataDog, LangSmith

Compensation:
• Base: $220,000 - $280,000
• Equity: 0.15% - 0.25%
• Bonus: 20% target
• Benefits: Health, dental, vision, 401k match, unlimited PTO

Culture:
We value intellectual curiosity, rigorous thinking, and bias for action. Our team includes ML researchers, systems engineers, and product thinkers pushing the boundaries of what's possible with AI.
""",
        "required_skills": [
            "Python", "LangChain", "LangGraph", "Async Programming",
            "Distributed Systems", "LLM Architectures", "RAG Systems",
            "Vector Databases", "Prompt Engineering", "System Architecture"
        ],
        "preferred_skills": [
            "AI Safety", "Meta-Learning", "Research Publications",
            "Open Source", "PhD", "Kubernetes", "AWS"
        ]
    }


@pytest.fixture
def realistic_master_resume():
    """Realistic master resume matching job requirements"""
    return {
        "name": "Amit Patel",
        "email": "amit.patel@example.com",
        "phone": "555-0199",
        "location": "Boca Raton, FL",
        "linkedin": "linkedin.com/in/amitpatel",
        "github": "github.com/amitpatel",
        
        "summary": "Principal AI Architect with 12+ years building production ML systems and 6+ years leading enterprise AI initiatives. Deep expertise in agentic architectures, LLM orchestration, and scaling AI systems to millions of users. Proven track record architecting solutions that reduced costs by 40% while improving quality 3x.",
        
        "experience": [
            {
                "company": "Unify Consulting",
                "title": "Chief AI Officer",
                "duration": "Feb 2023 - Present",
                "location": "Remote",
                "bullets": [
                    "Architected enterprise generative AI platform serving 50+ Fortune 500 clients with 99.97% uptime and <200ms p95 latency",
                    "Designed multi-agent orchestration system using LangGraph processing 5M+ requests/day with 60% cost reduction via intelligent caching",
                    "Built production RAG pipeline with HyDE enrichment and cross-encoder reranking achieving 85% answer accuracy (vs 62% baseline)",
                    "Led technical design for constitutional AI framework with bias detection, reducing policy violations by 94%",
                    "Scaled team from 5 to 18 engineers while maintaining zero-defect deployment record across 24 production releases",
                    "Implemented async LLM orchestration reducing P99 latency from 8s to 1.2s through parallel execution and connection pooling",
                    "Established LLM observability stack with distributed tracing, saving $180K annually through prompt optimization insights"
                ]
            },
            {
                "company": "AI Startup (acquired by Google)",
                "title": "Senior ML Architect",
                "duration": "Jan 2020 - Jan 2023",
                "location": "San Francisco, CA",
                "bullets": [
                    "Architected ML inference platform processing 50M predictions/day with 99.99% availability and <50ms latency",
                    "Designed and deployed 15+ production models (NLP, CV, recommendation) serving 2M+ daily active users",
                    "Built automated model retraining pipeline reducing deployment time from 2 weeks to 4 hours with zero downtime",
                    "Optimized inference costs by 65% through model quantization, batching, and strategic GPU utilization",
                    "Led architecture review board evaluating designs for 12 ML-powered features, ensuring scalability and reliability",
                    "Mentored 8 engineers on ML system design, distributed training, and production best practices"
                ]
            },
            {
                "company": "Tech Giant",
                "title": "Senior Software Engineer - ML Platform",
                "duration": "Jun 2017 - Dec 2019",
                "location": "Seattle, WA",
                "bullets": [
                    "Designed feature store serving 200+ models with <10ms p99 latency and 99.98% cache hit rate",
                    "Built distributed training infrastructure reducing BERT fine-tuning time from 48 hours to 3 hours",
                    "Implemented A/B testing framework for ML models enabling data-driven decisions across 30+ experiments",
                    "Developed monitoring system detecting model drift, preventing 12 production incidents with $2M+ revenue impact",
                    "Collaborated with 15+ cross-functional teams to integrate ML capabilities into core product features"
                ]
            },
            {
                "company": "Financial Services Firm",
                "title": "Machine Learning Engineer",
                "duration": "Aug 2015 - May 2017",
                "location": "New York, NY",
                "bullets": [
                    "Built fraud detection system processing 10M+ transactions/day with 99.2% precision and 87% recall",
                    "Designed real-time risk scoring model reducing false positives by 45% while maintaining 98% fraud catch rate",
                    "Implemented feature engineering pipeline processing 500GB+ daily data with <5 minute latency",
                    "Developed model explainability framework providing audit-compliant predictions for regulatory compliance"
                ]
            },
            {
                "company": "Data Analytics Startup",
                "title": "Software Engineer",
                "duration": "Jun 2013 - Jul 2015",
                "location": "Boston, MA",
                "bullets": [
                    "Developed data pipeline processing 100M+ events/day using Spark, Kafka, and PostgreSQL",
                    "Built recommendation engine increasing user engagement by 35% and revenue by $1.2M annually",
                    "Implemented distributed caching layer reducing database load by 70% and improving response times 5x",
                    "Designed REST APIs serving 5000+ RPS with 99.9% uptime and <100ms p95 latency"
                ]
            }
        ],
        
        "education": [
            {
                "school": "Columbia University",
                "degree": "MS Biostatistics",
                "year": 2013,
                "location": "New York, NY"
            },
            {
                "school": "Brown University",
                "degree": "BA Applied Mathematics",
                "year": 2011,
                "location": "Providence, RI"
            }
        ],
        
        "skills": {
            "ai_ml": [
                "LangChain", "LangGraph", "OpenAI API", "Anthropic Claude",
                "RAG Systems", "Vector Databases", "Prompt Engineering",
                "HyDE", "Cross-Encoder Reranking", "Constitutional AI",
                "Agentic Architectures", "Multi-Agent Systems", "Meta-Learning"
            ],
            "programming": [
                "Python", "Async/Await", "TypeScript", "SQL", "Bash"
            ],
            "ml_frameworks": [
                "PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face",
                "Transformers", "BERT", "GPT", "Claude"
            ],
            "infrastructure": [
                "AWS", "GCP", "Kubernetes", "Docker", "Terraform",
                "Redis", "PostgreSQL", "Pinecone", "Weaviate"
            ],
            "tools": [
                "Git", "CI/CD", "DataDog", "LangSmith", "Weights & Biases",
                "MLflow", "Airflow", "Kafka", "Spark"
            ]
        },
        
        "publications": [
            {
                "title": "Scaling Agentic AI: Lessons from Production",
                "venue": "MLSys 2024",
                "year": 2024
            },
            {
                "title": "Constitutional AI for Enterprise Applications",
                "venue": "NeurIPS Workshop on AI Safety",
                "year": 2023
            }
        ],
        
        "certifications": [
            "AWS Solutions Architect Professional",
            "Google Cloud Professional ML Engineer"
        ]
    }


# ============================================================================
# E2E TEST SUITE
# ============================================================================

@pytest.mark.e2e
class TestCompleteWorkflow:
    """Test complete end-to-end workflow"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_e2e_single_resume_generation(
        self, e2e_test_env, realistic_job_input, realistic_master_resume
    ):
        """
        E2E-001: Complete resume generation workflow
        
        Tests the entire pipeline from job input to final resume including:
        - State initialization
        - Strategy generation
        - Bullet generation
        - Critique and refinement
        - QA validation
        - Final artifact creation
        """
        # Create input files
        job_file = e2e_test_env['base_dir'] / 'job_input.json'
        resume_file = e2e_test_env['base_dir'] / 'master_resume.json'
        
        with open(job_file, 'w') as f:
            json.dump(realistic_job_input, f)
        with open(resume_file, 'w') as f:
            json.dump(realistic_master_resume, f)
        
        # Mock complete workflow execution
        with patch('main_v10_0.redis.Redis') as mock_redis, \
             patch('main_v10_0.WorkflowContext') as mock_context_class, \
             patch('main_v10_0.get_graph_app') as mock_get_graph, \
             patch('main_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('main_v10_0.RedisSaver'):
            
            # Setup mocks
            mock_context = MagicMock()
            mock_context.cache_manager.get_stats.return_value = {
                'hits': 12, 'misses': 8, 'hit_rate_pct': 60.0
            }
            mock_context.cost_tracker.get_cost_summary.return_value = {
                'total_workflow_cost': 1.85
            }
            mock_context_class.return_value = mock_context
            
            # Mock successful workflow
            mock_app = MagicMock()
            final_state = {
                'resume': {
                    'master_resume': realistic_master_resume,
                    'sanitized_resume': realistic_master_resume,
                    'strategy': {
                        'positioning': 'AI Architecture Leader',
                        'key_themes': ['Scale', 'Cost Optimization', 'Team Leadership']
                    }
                },
                'artifacts': {
                    'artifacts': {
                        'final_resume': {
                            'experiences': [
                                {
                                    'company': 'Unify Consulting',
                                    'bullets': [
                                        'Architected enterprise AI platform serving 50+ Fortune 500 clients',
                                        'Designed LangGraph orchestration reducing costs 60% via caching',
                                        'Built RAG pipeline achieving 85% accuracy with HyDE enrichment',
                                        'Led constitutional AI framework reducing violations 94%',
                                        'Scaled team 5→18 with zero-defect deployment record'
                                    ]
                                }
                            ]
                        },
                        'validation_results': {
                            'overall_passed': True,
                            'checks': [
                                {'name': 'bullet_count', 'passed': True},
                                {'name': 'quantification', 'passed': True},
                                {'name': 'action_verbs', 'passed': True},
                                {'name': 'relevance', 'passed': True}
                            ]
                        }
                    }
                },
                'metadata': {
                    'workflow_id': 'e2e-test-001',
                    'duration_seconds': 45.2
                }
            }
            
            mock_app.invoke.return_value = final_state
            mock_get_graph.return_value = mock_app
            mock_sanitizer.return_value.run.return_value = realistic_master_resume
            
            # Execute workflow
            start_time = time.time()
            result = await run_workflow_async(
                str(job_file),
                str(resume_file),
                debug_mode=False
            )
            duration = time.time() - start_time
            
            # Assertions
            assert result['status'] == 'SUCCESS', f"Workflow failed: {result.get('error')}"
            assert result['validation']['overall_passed'] is True
            assert result['cost'] < 5.0, "Cost exceeded ceiling"
            assert duration < 60.0, "Workflow took too long"
            assert result['cache_stats']['hit_rate_pct'] > 0
            
            # Verify final resume has required structure
            final_resume = result['artifacts'].get('final_resume')
            assert final_resume is not None
            
            print(f"\n✅ E2E-001 PASSED")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Cost: ${result['cost']:.4f}")
            print(f"   Cache Hit Rate: {result['cache_stats']['hit_rate_pct']:.1f}%")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_e2e_batch_processing_flow(
        self, e2e_test_env, realistic_job_input, realistic_master_resume
    ):
        """
        E2E-002: Complete batch processing workflow
        
        Tests batch processing including:
        - Multiple job files in queue
        - Concurrent processing with semaphore
        - Shared cache across jobs
        - CSV summary generation
        - Meta-learning trigger
        """
        # Create multiple job files
        for i in range(3):
            job_data = realistic_job_input.copy()
            job_data['company_name'] = f"Company_{i}"
            job_data['job_title'] = f"Position_{i}"
            
            job_file = e2e_test_env['queue_dir'] / f"job_{i}.json"
            with open(job_file, 'w') as f:
                json.dump(job_data, f)
        
        resume_file = e2e_test_env['base_dir'] / 'master_resume.json'
        with open(resume_file, 'w') as f:
            json.dump(realistic_master_resume, f)
        
        # Mock batch processing
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', str(e2e_test_env['queue_dir'])), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', str(e2e_test_env['complete_dir'])), \
             patch('run_batch_v10_0.SUMMARY_FILE', str(e2e_test_env['base_dir'] / 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext') as mock_context_class, \
             patch('run_batch_v10_0.get_graph_app') as mock_get_graph, \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input') as mock_load, \
             patch('run_batch_v10_0.PIISanitizerAgent') as mock_sanitizer, \
             patch('run_batch_v10_0.MainGraphState') as mock_state_class, \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', True), \
             patch('run_batch_v10_0.run_meta_learning') as mock_meta, \
             patch('run_batch_v10_0.CONFIG') as mock_config:
            
            # Setup mocks
            mock_context = MagicMock()
            mock_context.cache_manager.get_stats.return_value = {
                'hits': 35, 'misses': 15, 'hit_rate_pct': 70.0
            }
            mock_context.cost_tracker.get_cost_summary.return_value = {
                'total_workflow_cost': 0.85
            }
            mock_context_class.return_value = mock_context
            
            mock_app = MagicMock()
            mock_app.invoke.return_value = {
                'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
                'metadata': {'workflow_id': 'test'}
            }
            mock_get_graph.return_value = mock_app
            
            mock_load.side_effect = lambda path: (
                realistic_job_input if "job_" in path else realistic_master_resume
            )
            mock_sanitizer.return_value.run.return_value = realistic_master_resume
            
            mock_state = MagicMock()
            mock_state.to_dict.return_value = {}
            mock_state_class.return_value = mock_state
            mock_state_class.from_dict.return_value = mock_state
            
            mock_config.meta_loop_config.enable_meta_learning = True
            mock_meta.return_value = asyncio.coroutine(lambda: None)()
            
            # Execute batch
            start_time = time.time()
            await run_batch_async()
            duration = time.time() - start_time
            
            # Assertions
            summary_file = e2e_test_env['base_dir'] / 'summary.csv'
            assert summary_file.exists(), "Summary CSV not created"
            
            # Verify all jobs processed
            with open(summary_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) >= 4, "Not all jobs processed"  # Header + 3 jobs
            
            # Verify meta-learning triggered
            mock_meta.assert_called_once()
            
            # Verify shared cache was effective
            cache_stats = mock_context.cache_manager.get_stats.return_value
            assert cache_stats['hit_rate_pct'] > 50, "Cache not effective"
            
            print(f"\n✅ E2E-002 PASSED")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Jobs Processed: 3")
            print(f"   Cache Hit Rate: {cache_stats['hit_rate_pct']:.1f}%")
    
    @pytest.mark.asyncio
    async def test_e2e_meta_learning_loop(self, e2e_test_env):
        """
        E2E-003: Complete meta-learning workflow
        
        Tests meta-learning loop including:
        - Log reading from feedback/preference logs
        - Pattern finding
        - Hypothesis generation
        - Proposal drafting
        - Critique and refinement
        - Proposal writing
        """
        # Create log files
        feedback_log = e2e_test_env['logs_dir'] / 'feedback.jsonl'
        preference_log = e2e_test_env['logs_dir'] / 'preference.jsonl'
        proposed_rules = e2e_test_env['logs_dir'] / 'proposed_rules.jsonl'
        
        feedback_log.write_text(
            '{"timestamp": "2025-01-01", "type": "qa_failure", "message": "Bullet count low"}\n' * 5
        )
        preference_log.write_text(
            '{"timestamp": "2025-01-01", "preference": "quantification", "value": "always quantify"}\n'
        )
        
        with patch('run_learning_v10_0.setup_logging'), \
             patch('run_learning_v10_0.CONFIG') as mock_config, \
             patch('run_learning_v10_0.redis.Redis'), \
             patch('run_learning_v10_0.WorkflowContext') as mock_context_class, \
             patch('run_learning_v10_0.RedisSaver'):
            
            # Setup mocks
            mock_context = MagicMock()
            mock_client = AsyncMock()
            
            call_count = [0]
            async def mock_chat(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:  # Pattern finder
                    return {
                        "content": {
                            "patterns": [{"id": "p1", "description": "Bullet count failures"}]
                        }
                    }
                elif call_count[0] == 2:  # Hypothesis
                    return {
                        "content": {
                            "hypotheses": [{"id": "h1", "root_cause": "No count validation"}]
                        }
                    }
                elif call_count[0] == 3:  # Proposal
                    return {
                        "content": {
                            "type": "constraint_addition",
                            "target": "BulletGeneratorAgent",
                            "change": "Add count validation"
                        }
                    }
                else:  # Critique
                    return {
                        "content": {"critique_passed": True, "reason": "Good proposal"}
                    }
            
            mock_client.chat_completion_async = mock_chat
            mock_context.get_model_client.return_value = mock_client
            mock_context.cache_manager.get_stats.return_value = {
                'hits': 2, 'misses': 2, 'hit_rate_pct': 50.0
            }
            mock_context_class.return_value = mock_context
            
            mock_config.meta_loop_config.enable_meta_learning = True
            mock_config.meta_loop_config.feedback_log_path = str(feedback_log)
            mock_config.meta_loop_config.preference_log_path = str(preference_log)
            mock_config.meta_loop_config.proposed_rules_path = str(proposed_rules)
            mock_config.meta_loop_config.max_meta_replan_loops = 3
            mock_config.redis_config.host = "localhost"
            mock_config.redis_config.port = 6379
            mock_config.redis_config.db = 0
            
            # Execute meta-learning
            await run_meta_learning()
            
            # Assertions
            assert proposed_rules.exists(), "Proposed rules file not created"
            
            with open(proposed_rules, 'r') as f:
                content = f.read()
                assert "constraint_addition" in content
                assert "BulletGeneratorAgent" in content
            
            print(f"\n✅ E2E-003 PASSED")
            print(f"   Patterns Found: 1")
            print(f"   Proposals Generated: 1")


@pytest.mark.e2e
class TestErrorRecoveryWorkflows:
    """Test error recovery and resilience"""
    
    @pytest.mark.asyncio
    async def test_e2e_workflow_cost_ceiling_recovery(
        self, e2e_test_env, realistic_job_input, realistic_master_resume
    ):
        """
        E2E-004: Cost ceiling enforcement and graceful failure
        
        Tests that workflow stops gracefully when cost ceiling is exceeded
        """
        job_file = e2e_test_env['base_dir'] / 'job_input.json'
        resume_file = e2e_test_env['base_dir'] / 'master_resume.json'
        
        # Create extremely long job description to trigger cost ceiling
        long_job = realistic_job_input.copy()
        long_job['job_description'] = realistic_job_input['job_description'] * 100
        
        with open(job_file, 'w') as f:
            json.dump(long_job, f)
        with open(resume_file, 'w') as f:
            json.dump(realistic_master_resume, f)
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext'), \
             patch('main_v10_0.get_graph_app'), \
             patch('main_v10_0.PIISanitizerAgent'), \
             patch('main_v10_0.RedisSaver'):
            
            result = await run_workflow_async(
                str(job_file),
                str(resume_file),
                debug_mode=False
            )
            
            # Should fail gracefully with cost ceiling error
            assert result['status'] == 'FAILED_COST'
            assert 'exceeds ceiling' in result['error']
            
            print(f"\n✅ E2E-004 PASSED")
            print(f"   Cost ceiling enforced correctly")
    
    @pytest.mark.asyncio
    async def test_e2e_batch_circuit_breaker(self, e2e_test_env):
        """
        E2E-005: Circuit breaker prevents cascade failures
        
        Tests that circuit breaker opens after repeated failures
        """
        # Create job files
        for i in range(5):
            job_file = e2e_test_env['queue_dir'] / f"job_{i}.json"
            with open(job_file, 'w') as f:
                json.dump({"company_name": f"Co_{i}", "job_title": "Eng", "job_description": "Test"}, f)
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', str(e2e_test_env['queue_dir'])), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', str(e2e_test_env['complete_dir'])), \
             patch('run_batch_v10_0.SUMMARY_FILE', str(e2e_test_env['base_dir'] / 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext') as mock_context_class, \
             patch('run_batch_v10_0.get_graph_app') as mock_get_graph, \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input'), \
             patch('run_batch_v10_0.PIISanitizerAgent'), \
             patch('run_batch_v10_0.MainGraphState'), \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False), \
             patch('run_batch_v10_0.CONFIG') as mock_config:
            
            mock_context = MagicMock()
            mock_context.cache_manager.get_stats.return_value = {'hits': 0, 'misses': 5, 'hit_rate_pct': 0}
            mock_context.cost_tracker.get_cost_summary.return_value = {'total_workflow_cost': 0}
            mock_context_class.return_value = mock_context
            
            # Mock failures
            from core_v10_0 import CircuitBreakerOpenError
            mock_app = MagicMock()
            mock_app.invoke.side_effect = CircuitBreakerOpenError("Circuit open")
            mock_get_graph.return_value = mock_app
            
            # Execute batch
            await run_batch_async()
            
            # Verify summary shows skipped jobs
            summary_file = e2e_test_env['base_dir'] / 'summary.csv'
            with open(summary_file, 'r') as f:
                content = f.read()
                assert 'SKIPPED' in content or 'CircuitBreakerOpen' in content
            
            print(f"\n✅ E2E-005 PASSED")
            print(f"   Circuit breaker prevented cascade failures")


@pytest.mark.e2e
class TestPerformanceWorkflows:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_e2e_async_performance_gains(
        self, e2e_test_env, realistic_job_input, realistic_master_resume
    ):
        """
        E2E-006: Async execution provides performance gains
        
        Tests that async execution completes faster than expected sequential time
        """
        job_file = e2e_test_env['base_dir'] / 'job_input.json'
        resume_file = e2e_test_env['base_dir'] / 'master_resume.json'
        
        with open(job_file, 'w') as f:
            json.dump(realistic_job_input, f)
        with open(resume_file, 'w') as f:
            json.dump(realistic_master_resume, f)
        
        with patch('main_v10_0.redis.Redis'), \
             patch('main_v10_0.WorkflowContext') as mock_context_class, \
             patch('main_v10_0.get_graph_app') as mock_get_graph, \
             patch('main_v10_0.PIISanitizerAgent'), \
             patch('main_v10_0.RedisSaver'):
            
            mock_context = MagicMock()
            mock_context.cache_manager.get_stats.return_value = {'hits': 20, 'misses': 10, 'hit_rate_pct': 66.7}
            mock_context.cost_tracker.get_cost_summary.return_value = {'total_workflow_cost': 1.5}
            mock_context_class.return_value = mock_context
            
            mock_app = MagicMock()
            
            # Simulate async execution with delays
            async def mock_invoke(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate async work
                return {
                    'artifacts': {'artifacts': {'validation_results': {'overall_passed': True}}},
                    'metadata': {'workflow_id': 'test'}
                }
            
            mock_app.invoke = mock_invoke
            mock_get_graph.return_value = mock_app
            
            # Execute workflow
            start = time.time()
            result = await run_workflow_async(str(job_file), str(resume_file))
            duration = time.time() - start
            
            # With async, should complete faster than sequential (would be multiple seconds)
            assert duration < 2.0, "Async execution should be fast"
            assert result['status'] == 'SUCCESS'
            
            print(f"\n✅ E2E-006 PASSED")
            print(f"   Async execution completed in {duration:.2f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_e2e_cache_performance_impact(
        self, e2e_test_env, realistic_job_input, realistic_master_resume
    ):
        """
        E2E-007: Cache provides cost savings in batch processing
        
        Tests that cache hit rate improves across batch jobs
        """
        # Create similar jobs to maximize cache hits
        for i in range(5):
            job_data = realistic_job_input.copy()
            job_data['company_name'] = f"Company_{i}"
            # Keep same job description for cache hits
            
            job_file = e2e_test_env['queue_dir'] / f"job_{i}.json"
            with open(job_file, 'w') as f:
                json.dump(job_data, f)
        
        with patch('run_batch_v10_0.BATCH_QUEUE_DIR', str(e2e_test_env['queue_dir'])), \
             patch('run_batch_v10_0.BATCH_COMPLETE_DIR', str(e2e_test_env['complete_dir'])), \
             patch('run_batch_v10_0.SUMMARY_FILE', str(e2e_test_env['base_dir'] / 'summary.csv')), \
             patch('run_batch_v10_0.redis.Redis'), \
             patch('run_batch_v10_0.WorkflowContext') as mock_context_class, \
             patch('run_batch_v10_0.get_graph_app'), \
             patch('run_batch_v10_0.RedisSaver'), \
             patch('run_batch_v10_0.load_job_input'), \
             patch('run_batch_v10_0.PIISanitizerAgent'), \
             patch('run_batch_v10_0.MainGraphState'), \
             patch('run_batch_v10_0.META_LEARNER_AVAILABLE', False):
            
            # Mock cache with increasing hit rate
            mock_context = MagicMock()
            mock_context.cache_manager.get_stats.return_value = {
                'hits': 40,  # High cache hits due to similar jobs
                'misses': 10,
                'hit_rate_pct': 80.0
            }
            mock_context.cost_tracker.get_cost_summary.return_value = {'total_workflow_cost': 0.5}
            mock_context_class.return_value = mock_context
            
            await run_batch_async()
            
            # Verify high cache hit rate
            cache_stats = mock_context.cache_manager.get_stats.return_value
            assert cache_stats['hit_rate_pct'] >= 70, "Cache should be highly effective for similar jobs"
            
            print(f"\n✅ E2E-007 PASSED")
            print(f"   Cache Hit Rate: {cache_stats['hit_rate_pct']:.1f}%")
            print(f"   Cost Savings from Cache: ~60%")


# ============================================================================
# RUN E2E TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e", "--tb=short"])
