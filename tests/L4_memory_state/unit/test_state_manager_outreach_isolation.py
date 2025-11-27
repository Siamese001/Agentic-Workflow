"""
Tests for L4 state manager outreach workflow isolation and serialization.

Validates TemporalContext and EpisodicMemory functionality for outreach workflows.
Tests MUST NOT import L1 or L2 modules.
"""

import json
import threading
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from l4.state_manager import TemporalContext, EpisodicMemory


class TestStateManagerOutreachIsolation:
    """Test suite for outreach workflow state management and isolation."""
    
    def test_temporal_context_json_round_trip(self):
        """Test TemporalContext round-trip JSON serialization/deserialization."""
        original_context = TemporalContext(
            processing_window="60d",
            temporal_relationships={
                "outreach_campaign": "2024-01-15",
                "follow_up_required": True,
                "archetype": "senior_ta"
            }
        )
        
        # Serialize to JSON
        json_str = json.dumps({
            "current_time": original_context.current_time.isoformat(),
            "processing_window": original_context.processing_window,
            "temporal_relationships": original_context.temporal_relationships
        })
        assert isinstance(json_str, str)
        
        # Deserialize from JSON
        data = json.loads(json_str)
        restored_context = TemporalContext(
            current_time=datetime.fromisoformat(data["current_time"]),
            processing_window=data["processing_window"],
            temporal_relationships=data["temporal_relationships"]
        )
        
        # Verify round-trip integrity
        assert restored_context.processing_window == original_context.processing_window
        assert restored_context.temporal_relationships == original_context.temporal_relationships
    
    def test_episodic_memory_json_round_trip(self):
        """Test EpisodicMemory round-trip JSON serialization/deserialization."""
        original_memory = EpisodicMemory(
            max_interactions=50,
            interactions=[
                {
                    "type": "outreach_sent",
                    "archetype": "executive",
                    "company": "TestCorp",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                {
                    "type": "follow_up_scheduled",
                    "archetype": "c_level",
                    "company": "ExecutiveCorp",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        )
        
        # Serialize to JSON
        json_str = json.dumps({
            "max_interactions": original_memory.max_interactions,
            "interactions": original_memory.interactions
        })
        assert isinstance(json_str, str)
        
        # Deserialize from JSON
        data = json.loads(json_str)
        restored_memory = EpisodicMemory(
            max_interactions=data["max_interactions"],
            interactions=data["interactions"]
        )
        
        # Verify round-trip integrity
        assert restored_memory.max_interactions == original_memory.max_interactions
        assert len(restored_memory.interactions) == len(original_memory.interactions)
        assert restored_memory.interactions[0]["type"] == "outreach_sent"
        assert restored_memory.interactions[1]["archetype"] == "c_level"
    
    def test_outreach_workflow_isolation(self):
        """Test outreach workflow isolation from resume workflows."""
        outreach_context = TemporalContext(
            processing_window="30d",
            temporal_relationships={
                "workflow_type": "outreach",
                "target_company": "IsolationCorp",
                "archetype": "executive",
                "contacts_researched": ["contact_1", "contact_2"],
                "companies_researched": ["company_x"],
                "messages_generated": ["message_1"]
            }
        )
        
        # Verify outreach-specific fields are present
        assert "workflow_type" in outreach_context.temporal_relationships
        assert outreach_context.temporal_relationships["workflow_type"] == "outreach"
        assert "target_company" in outreach_context.temporal_relationships
        assert "archetype" in outreach_context.temporal_relationships
        
        # Verify resume-specific fields are NOT present
        assert "resume_file_path" not in outreach_context.temporal_relationships
        assert "resume_sections" not in outreach_context.temporal_relationships
        assert "skills_extracted" not in outreach_context.temporal_relationships
        
        # Test JSON isolation
        json_data = {
            "current_time": outreach_context.current_time.isoformat(),
            "processing_window": outreach_context.processing_window,
            "temporal_relationships": outreach_context.temporal_relationships
        }
        
        assert "target_company" in json_data["temporal_relationships"]
        assert "archetype" in json_data["temporal_relationships"]
        assert "resume_file_path" not in json_data["temporal_relationships"]
    
    def test_workflow_type_transitions(self):
        """Test workflow_type transitions using temporal relationships."""
        # Initial resume workflow (created but not used directly)
        TemporalContext(
            processing_window="30d",
            temporal_relationships={
                "workflow_type": "resume",
                "resume_file": "test_resume.pdf",
                "job_target": "Software Engineer"
            }
        )
        
        # Transition to outreach workflow
        outreach_context = TemporalContext(
            processing_window="30d",
            temporal_relationships={
                "workflow_type": "outreach",
                "target_company": "TransitionCorp",
                "archetype": "c_level",
                "parent_workflow": "resume",
                "resume_file": "test_resume.pdf"
            }
        )
        
        assert outreach_context.temporal_relationships["workflow_type"] == "outreach"
        assert outreach_context.temporal_relationships["parent_workflow"] == "resume"
        
        # Transition to combined workflow
        combined_context = TemporalContext(
            processing_window="30d",
            temporal_relationships={
                "workflow_type": "resume_outreach",
                "resume_workflow_id": "resume_123",
                "outreach_workflow_id": "outreach_456",
                "target_company": "CombinedCorp",
                "archetype": "senior_ta"
            }
        )
        
        assert combined_context.temporal_relationships["workflow_type"] == "resume_outreach"
        assert "resume_workflow_id" in combined_context.temporal_relationships
        assert "outreach_workflow_id" in combined_context.temporal_relationships
    
    def test_episodic_memory_outreach_tracking(self):
        """Test episodic memory tracking for outreach workflows."""
        memory = EpisodicMemory(max_interactions=100)
        
        # Add outreach interactions
        memory.add_interaction({
            "type": "contact_research",
            "archetype": "recruiter",
            "target_company": "TestCorp",
            "results_count": 5,
            "quality_score": 0.8
        })
        
        memory.add_interaction({
            "type": "message_generated",
            "archetype": "executive",
            "recipient": "manager@testcorp.com",
            "sections": 5,
            "safety_check": "passed"
        })
        
        memory.add_interaction({
            "type": "follow_up_scheduled",
            "archetype": "c_level",
            "executive": "ceo@testcorp.com",
            "follow_up_date": "2024-02-01"
        })
        
        # Verify interactions are stored
        assert len(memory.interactions) == 3
        assert memory.interactions[0]["type"] == "contact_research"
        assert memory.interactions[1]["archetype"] == "executive"
        assert memory.interactions[2]["follow_up_date"] == "2024-02-01"
        
        # Verify timestamps are added automatically
        for interaction in memory.interactions:
            assert "timestamp" in interaction
            assert isinstance(interaction["timestamp"], str)
        
        # Test recent interactions retrieval
        recent = memory.get_recent_interactions(count=2)
        assert len(recent) == 2
        assert recent[0]["type"] == "message_generated"
        assert recent[1]["type"] == "follow_up_scheduled"
    
    def test_temporal_context_outreach_window_validation(self):
        """Test temporal context window validation for outreach workflows."""
        # Test 30-day window (default)
        context_30d = TemporalContext(processing_window="30d")
        
        # Test within window
        recent_time = datetime.now(timezone.utc) - timedelta(days=15)
        assert context_30d.is_within_window(recent_time) is True
        
        # Test outside window
        old_time = datetime.now(timezone.utc) - timedelta(days=45)
        assert context_30d.is_within_window(old_time) is False
        
        # Test edge case (exactly at window)
        edge_time = datetime.now(timezone.utc) - timedelta(days=30)
        assert context_30d.is_within_window(edge_time) is True
        
        # Test custom window
        context_60d = TemporalContext(processing_window="60d")
        old_time_60d = datetime.now(timezone.utc) - timedelta(days=45)
        assert context_60d.is_within_window(old_time_60d) is True
        
        very_old_time = datetime.now(timezone.utc) - timedelta(days=90)
        assert context_60d.is_within_window(very_old_time) is False
    
    def test_episodic_memory_size_limits(self):
        """Test episodic memory size limits and cleanup for outreach workflows."""
        memory = EpisodicMemory(max_interactions=3)
        
        # Add interactions up to limit
        for i in range(3):
            memory.add_interaction({
                "type": f"outreach_step_{i}",
                "archetype": "senior_ta",
                "step_number": i
            })
        
        assert len(memory.interactions) == 3
        
        # Add one more interaction (should trigger cleanup)
        memory.add_interaction({
            "type": "outreach_step_3",
            "archetype": "executive",
            "step_number": 3
        })
        
        # Should maintain size limit
        assert len(memory.interactions) == 3
        # Should keep most recent interactions
        assert memory.interactions[-1]["type"] == "outreach_step_3"
        assert memory.interactions[0]["type"] == "outreach_step_1"  # Should be removed
        assert memory.interactions[0]["type"] == "outreach_step_2"  # Should be first remaining
    
    def test_outreach_state_persistence_and_retrieval(self):
        """Test state persistence and retrieval operations for outreach workflows."""
        outreach_context = TemporalContext(
            processing_window="45d",
            temporal_relationships={
                "workflow_id": "outreach_test_789",
                "target_company": "PersistenceCorp",
                "archetype": "executive",
                "contacts_researched": ["contact_a", "contact_b"],
                "companies_researched": ["company_x"],
                "messages_generated": ["message_1"]
            }
        )
        
        outreach_memory = EpisodicMemory(
            interactions=[
                {"type": "research_completed", "timestamp": datetime.now(timezone.utc).isoformat()},
                {"type": "message_sent", "timestamp": datetime.now(timezone.utc).isoformat()}
            ]
        )
        
        # Mock persistence operations
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.write = Mock()
            
            # Save state
            state_data = {
                "temporal_context": {
                    "current_time": outreach_context.current_time.isoformat(),
                    "processing_window": outreach_context.processing_window,
                    "temporal_relationships": outreach_context.temporal_relationships
                },
                "episodic_memory": {
                    "interactions": outreach_memory.interactions,
                    "max_interactions": outreach_memory.max_interactions
                }
            }
            
            json.dump(state_data, mock_open.return_value.__enter__.return_value)
            
            # Verify save operation
            mock_open.assert_called()
        
        # Mock retrieval operations
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read = Mock(
                return_value=json.dumps(state_data)
            )
            
            # Load state
            loaded_data = json.load(mock_open.return_value.__enter__.return_value)
            
            # Verify retrieval
            assert loaded_data["temporal_context"]["workflow_id"] == "outreach_test_789"
            assert loaded_data["temporal_context"]["archetype"] == "hiring_manager"
            assert len(loaded_data["episodic_memory"]["interactions"]) == 2
    
    def test_concurrent_outreach_state_access(self):
        """Test concurrent state access and thread safety for outreach workflows."""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker_thread(worker_id):
            try:
                context = TemporalContext(
                    processing_window="30d",
                    temporal_relationships={
                        "worker_id": worker_id,
                        "target_company": f"ConcurrentCorp_{worker_id}",
                        "archetype": "recruiter"
                    }
                )
                
                memory = EpisodicMemory()
                memory.add_interaction({
                    "type": "worker_interaction",
                    "worker_id": worker_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                results.append({
                    "worker_id": worker_id,
                    "workflow_id": context.temporal_relationships["worker_id"],
                    "interactions_count": len(memory.interactions)
                })
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        assert len(set(r["worker_id"] for r in results)) == 5  # All worker IDs should be unique
    
    def test_outreach_state_cleanup_and_archival(self):
        """Test state cleanup and archival operations for outreach workflows."""
        # Create old outreach state
        old_date = datetime.now(timezone.utc) - timedelta(days=90)
        old_context = TemporalContext(
            current_time=old_date,
            processing_window="30d",
            temporal_relationships={
                "workflow_id": "old_outreach_123",
                "target_company": "OldCorp",
                "archetype": "c_level",
                "created_date": old_date.isoformat()
            }
        )
        
        # Create recent outreach state
        recent_context = TemporalContext(
            processing_window="30d",
            temporal_relationships={
                "workflow_id": "recent_outreach_456",
                "target_company": "RecentCorp",
                "archetype": "senior_ta",
                "created_date": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Test cleanup logic
        days_old = 30
        old_state_age = (datetime.now(timezone.utc) - old_context.current_time).days
        recent_state_age = (datetime.now(timezone.utc) - recent_context.current_time).days
        
        # Should identify old state for archival
        assert old_state_age > days_old
        assert recent_state_age <= days_old
        
        # Mock archival operation
        archived_states = []
        
        def archive_state(context, age_days):
            if age_days > days_old:
                archived_states.append(context.temporal_relationships["workflow_id"])
                return True
            return False
        
        # Apply archival logic
        archive_state(old_context, old_state_age)
        archive_state(recent_context, recent_state_age)
        
        # Verify archival results
        assert len(archived_states) == 1
        assert "old_outreach_123" in archived_states
        assert "recent_outreach_456" not in archived_states
    
    def test_outreach_state_error_handling(self):
        """Test state manager error handling and recovery for outreach workflows."""
        # Test handling of corrupted JSON
        corrupted_json = '{"current_time": "invalid", "temporal_relationships": invalid}'
        
        with pytest.raises(json.JSONDecodeError):
            json.loads(corrupted_json)
        
        # Test handling of missing required fields
        incomplete_context_data = {
            "current_time": datetime.now(timezone.utc).isoformat(),
            # Missing processing_window and temporal_relationships
        }
        
        # Should handle gracefully with defaults
        try:
            context = TemporalContext(
                current_time=datetime.fromisoformat(incomplete_context_data["current_time"]),
                processing_window="30d",  # Default
                temporal_relationships={}  # Default
            )
            assert context.processing_window == "30d"
            assert context.temporal_relationships == {}
        except Exception as e:
            # If it fails, it should be a predictable error
            assert isinstance(e, (KeyError, TypeError))
        
        # Test episodic memory error handling
        try:
            memory = EpisodicMemory(max_interactions=-1)  # Invalid max_interactions
            # Should handle gracefully or raise predictable error
            assert memory.max_interactions >= 0
        except Exception as e:
            assert isinstance(e, (ValueError, TypeError))
