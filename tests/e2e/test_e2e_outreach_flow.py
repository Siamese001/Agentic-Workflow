"""
End-to-end tests for Outreach Flow
Tests complete outreach workflow including message generation
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import actual components when available
try:
    from agentic_core.l1_planning.planners.message_planner import MessagePlanner
    from agentic_core.l2_execution.executors.contact_research_executor import ContactResearchExecutor
    from agentic_core.l2_execution.executors.message_generation_executor import MessageGenerationExecutor
    from agentic_core.l3_orchestration.engines.outreach_engine_dag import OutreachEngineDAG
    from agentic_core.l5_safety.policies.policy_engine import PolicyEngine
except ImportError:
    MessagePlanner = ContactResearchExecutor = MessageGenerationExecutor = OutreachEngineDAG = PolicyEngine = Mock


class TestE2EOutreachFlow:
    """Test end-to-end outreach flow contracts"""
    
    def test_outreach_flow_happy_path_contract(self):
        """Test complete outreach flow works end-to-end"""
        if any(cls is Mock for cls in [MessagePlanner, ContactResearchExecutor, MessageGenerationExecutor, OutreachEngineDAG]):
            pytest.skip("Components not implemented")
        
        # Initialize all components
        message_planner = MessagePlanner({})
        contact_executor = ContactResearchExecutor({})
        message_executor = MessageGenerationExecutor({})
        outreach_dag = OutreachEngineDAG({})
        policy_engine = PolicyEngine({})
        
        # Input data for outreach flow
        input_data = {
            "user_profile": {
                "name": "John Doe",
                "experience": "5 years",
                "skills": ["Python", "Machine Learning", "Data Science"],
                "current_role": "Senior Software Engineer"
            },
            "target_companies": ["TechCorp", "DataInc", "AIStartup"],
            "target_roles": ["Senior Data Scientist", "ML Engineer", "Tech Lead"]
        }
        
        # Step 1: Message planning
        message_plan_result = message_planner.plan({
            "recipient": "hiring_manager",
            "context": {
                "user_profile": input_data["user_profile"],
                "target_companies": input_data["target_companies"]
            },
            "goal": "introduce_resume_and_request_meeting"
        })
        
        assert "message_plan" in message_plan_result
        
        # Step 2: Contact research for each company
        contact_results = []
        for company in input_data["target_companies"]:
            contact_result = contact_executor.execute({
                "company_name": company,
                "target_role": input_data["target_roles"][0],
                "contact_limit": 3,
                "research_depth": "basic"
            })
            contact_results.append(contact_result)
        
        assert all("contacts" in result for result in contact_results)
        
        # Step 3: Message generation for contacts
        message_results = []
        for contact_result in contact_results:
            if contact_result.get("contacts"):
                for contact in contact_result["contacts"][:2]:  # Generate for top 2 contacts
                    message_result = message_executor.execute({
                        "recipient": contact.get("role", "hiring_manager"),
                        "context": {
                            "company": contact_result.get("company", {}),
                            "contact": contact,
                            "user_profile": input_data["user_profile"],
                            "message_plan": message_plan_result
                        },
                        "tone": "professional",
                        "goal": "introduce_resume"
                    })
                    message_results.append(message_result)
        
        assert all("message" in result for result in message_results)
        
        # Step 4: DAG orchestration
        dag_input = {
            "user_profile": input_data["user_profile"],
            "contacts": contact_results,
            "messages": message_results,
            "strategy": message_plan_result
        }
        
        dag_result = outreach_dag.execute(dag_input)
        
        assert "execution_results" in dag_result or "output" in dag_result
        
        # Step 5: Safety validation for all messages
        for message_result in message_results:
            safety_result = policy_engine.evaluate_content({
                "text": message_result.get("message", ""),
                "context": {
                    "type": "outreach_message",
                    "recipient": "hiring_manager",
                    "flow": "outreach_campaign"
                }
            })
            
            assert safety_result["allowed"] is True
        
        # Final result should be complete and safe
        assert dag_result is not None
        assert len(message_results) > 0
    
    def test_outreach_flow_failure_modes_contract(self):
        """Test outreach flow handles various failure modes"""
        if OutreachEngineDAG is Mock:
            pytest.skip("OutreachEngineDAG not implemented")
        
        dag = OutreachEngineDAG({"continue_on_failure": True})
        
        # Test failure scenarios
        failure_scenarios = [
            {
                "name": "no_companies",
                "input": {
                    "user_profile": {"name": "Test"},
                    "target_companies": [],
                    "target_roles": ["Engineer"]
                }
            },
            {
                "name": "invalid_profile",
                "input": {
                    "user_profile": {},
                    "target_companies": ["TestCorp"],
                    "target_roles": ["Engineer"]
                }
            },
            {
                "name": "no_contacts_found",
                "input": {
                    "user_profile": {"name": "Test"},
                    "target_companies": ["NonExistentCorp"],
                    "target_roles": ["ImpossibleRole"]
                }
            }
        ]
        
        for scenario in failure_scenarios:
            result = dag.execute(scenario["input"])
            
            # Should handle gracefully
            assert "error" in result or "execution_results" in result or "output" in result
            if "error" in result:
                assert result["error"]["type"] in ["validation_error", "no_contacts", "missing_data"]
    
    def test_outreach_flow_message_quality_contract(self):
        """Test outreach flow generates quality messages"""
        if MessageGenerationExecutor is Mock:
            pytest.skip("MessageGenerationExecutor not implemented")
        
        executor = MessageGenerationExecutor({})
        
        quality_inputs = [
            {
                "recipient": "hiring_manager",
                "context": {
                    "company": {"name": "TechCorp", "industry": "Software"},
                    "contact": {"name": "Jane Smith", "role": "Engineering Manager"},
                    "user_profile": {"name": "John", "skills": ["Python", "ML"]},
                    "position": "Senior Data Scientist"
                },
                "tone": "professional",
                "goal": "introduce_resume"
            }
        ]
        
        for input_data in quality_inputs:
            result = executor.execute(input_data)
            
            # Should generate quality message
            assert "message" in result
            assert len(result["message"]) > 50  # Reasonable length
            assert "TechCorp" in result["message"]  # Personalized
            assert "John" in result["message"]  # Personalized
            assert any(skill in result["message"] for skill in ["Python", "ML"])  # Skills mentioned
    
    def test_outreach_flow_rate_limiting_contract(self):
        """Test outreach flow respects rate limiting"""
        if MessageGenerationExecutor is Mock:
            pytest.skip("MessageGenerationExecutor not implemented")
        
        executor = MessageGenerationExecutor({"rate_limit": 2, "rate_window": 1})  # 2 per second
        
        input_data = {
            "recipient": "hiring_manager",
            "context": {"company": "TestCorp", "user_profile": {"name": "Test"}},
            "tone": "professional",
            "goal": "test"
        }
        
        import time
        start_time = time.time()
        
        # Generate multiple messages
        results = []
        for i in range(3):
            result = executor.execute(input_data)
            results.append(result)
        
        elapsed_time = time.time() - start_time
        
        # Should respect rate limiting
        assert elapsed_time >= 1.0  # Should take at least 1 second for 3 messages with 2/sec limit
        assert all("message" in result for result in results)
    
    def test_outreach_flow_safety_compliance_contract(self):
        """Test outreach flow complies with safety policies"""
        if PolicyEngine is Mock:
            pytest.skip("PolicyEngine not implemented")
        
        policy_engine = PolicyEngine({"policy_level": "high"})
        
        # Test various message types for safety
        test_messages = [
            "I am interested in the Senior Engineer position at TechCorp",
            "My experience in machine learning aligns well with your requirements",
            "I would like to discuss how my skills can benefit your team"
        ]
        
        for message in test_messages:
            result = policy_engine.evaluate_content({
                "text": message,
                "context": {"type": "outreach_message", "recipient": "hiring_manager"}
            })
            
            assert result["allowed"] is True
            assert result["confidence_score"] > 0.8
    
    def test_outreach_flow_performance_contract(self):
        """Test outreach flow meets performance requirements"""
        if OutreachEngineDAG is Mock:
            pytest.skip("OutreachEngineDAG not implemented")
        
        dag = OutreachEngineDAG({})
        
        input_data = {
            "user_profile": {
                "name": "Test User",
                "skills": ["Python"],
                "experience": "2 years"
            },
            "target_companies": ["TestCorp"],
            "target_roles": ["Engineer"]
        }
        
        import time
        start_time = time.time()
        
        result = dag.execute(input_data)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert elapsed_time < 45.0  # 45 seconds for complete outreach flow
        assert result is not None
