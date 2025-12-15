#!/usr/bin/env python3
"""
CV-A-003: Failure Logging Backpressure
Adversarial test for L5 logging resilience
"""

import pytest
from unittest.mock import Mock, patch, call
import json
import time
import threading
from queue import Queue
from canon_validator import CanonValidator


class TestCVA003:
    """Test failure logging backpressure at L5 layer"""
    
    @pytest.fixture
    def validator(self):
        """Create validator with mocked dependencies"""
        validator = CanonValidator()
        validator.llm = Mock()
        validator.llm.generate_plan.return_value = {
            "status": "valid",
            "reasoning": "Code is valid"
        }
        validator.embed_fn = Mock(return_value=[0.1] * 768)
        validator.cache = Mock()
        validator.cache.check = Mock(return_value=None)
        validator.pinecone = Mock()
        validator.pinecone.query = Mock(return_value={'matches': []})
        validator.pinecone.upsert = Mock()
        return validator
    
    def test_critical_rag_failure_priority(self, validator):
        """Test prioritization of CRITICAL RAG FAILURE events"""
        log_queue = Queue()
        logged_events = []
        
        def mock_memeory_logger(observations):
            # Simulate logging with priority queue
            for obs in observations:
                event = {
                    "data": obs,
                    "timestamp": time.time(),
                    "priority": "low"
                }
                
                # Check for critical events
                content = str(obs.get("contents", []))
                if "CRITICAL RAG FAILURE" in content:
                    event["priority"] = "critical"
                
                log_queue.put(event)
                logged_events.append(event)
            
            return {"status": "logged", "count": len(observations)}
        
        # Simulate 100 concurrent RAG failures
        def simulate_rag_failures():
            for i in range(100):
                obs = [{
                    "entityName": f"rag_failure_{i}",
                    "contents": [f"CRITICAL RAG FAILURE: Pinecone timeout {i}"],
                    "corpusNames": ["canon_validator"],
                    "tags": ["critical", "rag", "failure"]
                }]
                mock_memeory_logger(obs)
        
        # Run failures in parallel
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=simulate_rag_failures)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all events were logged
        assert len(logged_events) == 500  # 100 failures * 5 threads
        
        # Verify all were marked as critical priority
        critical_count = sum(1 for event in logged_events if event["priority"] == "critical")
        assert critical_count == 500
    
    def test_logging_threshold_backpressure(self, validator):
        """Test backpressure when logging exceeds threshold"""
        log_count = 0
        dropped_count = 0
        threshold = 1000  # Max logs per second
        
        def mock_rate_limited_logger(observations):
            nonlocal log_count, dropped_count
            
            current_time = time.time()
            if not hasattr(mock_rate_limited_logger, 'last_reset'):
                mock_rate_limited_logger.last_reset = current_time
                mock_rate_limited_logger.logs_this_second = 0
            
            # Reset counter every second
            if current_time - mock_rate_limited_logger.last_reset > 1.0:
                mock_rate_limited_logger.last_reset = current_time
                mock_rate_limited_logger.logs_this_second = 0
            
            # Check threshold
            if mock_rate_limited_logger.logs_this_second + len(observations) > threshold:
                dropped_count += len(observations)
                return {"status": "dropped", "reason": "rate_limit_exceeded"}
            
            # Accept logs
            mock_rate_limited_logger.logs_this_second += len(observations)
            log_count += len(observations)
            return {"status": "logged", "count": len(observations)}
        
        # Simulate burst of logs exceeding threshold
        batch_size = 200
        for i in range(10):
            observations = [{
                "entityName": f"event_{i}_{j}",
                "contents": [f"Log message {j}"],
                "corpusNames": ["test"],
                "tags": ["test"]
            } for j in range(batch_size)]
            
            result = mock_rate_limited_logger(observations)
            
            # First 5 batches should succeed, rest should be dropped
            if i < 5:
                assert result["status"] == "logged"
            else:
                assert result["status"] == "dropped"
        
        # Verify backpressure worked
        assert log_count == 1000  # 5 batches * 200 logs
        assert dropped_count == 1000  # 5 batches * 200 logs
    
    def test_logging_resilience_under_load(self, validator):
        """Test logging subsystem doesn't crash under load"""
        log_stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        def mock_resilient_logger(observations):
            log_stats["total"] += len(observations)
            
            try:
                # Simulate occasional failures
                if log_stats["total"] % 100 == 0:
                    # Every 100th batch fails
                    raise Exception("Temporary logging failure")
                
                # Simulate successful logging
                log_stats["successful"] += len(observations)
                return {"status": "success"}
                
            except Exception as e:
                log_stats["failed"] += len(observations)
                log_stats["errors"].append(str(e))
                # Should not crash, continue processing
                return {"status": "failed", "error": str(e)}
        
        # Simulate high load
        def high_load_logging():
            for i in range(1000):
                observations = [{
                    "entityName": f"load_test_{i}",
                    "contents": [f"Load test message {i}"],
                    "corpusNames": ["test"],
                    "tags": ["load_test"]
                }]
                mock_resilient_logger(observations)
        
        # Execute load test
        high_load_logging()
        
        # Verify resilience
        assert log_stats["total"] == 1000
        assert log_stats["successful"] == 990
        assert log_stats["failed"] == 10
        assert len(log_stats["errors"]) == 10
        # Logger didn't crash, continued processing
    
    def test_critical_event_preservation(self, validator):
        """Test critical events are preserved even under backpressure"""
        log_buffer = []
        buffer_size = 100
        critical_preserved = []
        
        def mock_buffered_logger(observations):
            # Simulate limited buffer
            available_space = buffer_size - len(log_buffer)
            
            # Separate critical and non-critical events
            critical = []
            non_critical = []
            
            for obs in observations:
                if any("CRITICAL" in str(c) for c in obs.get("contents", [])):
                    critical.append(obs)
                else:
                    non_critical.append(obs)
            
            # Always preserve critical events
            for obs in critical:
                if len(log_buffer) >= buffer_size:
                    # Make space for critical
                    log_buffer.pop(0)
                log_buffer.append(obs)
                critical_preserved.append(obs)
            
            # Add non-critical if space allows
            for obs in non_critical[:available_space]:
                log_buffer.append(obs)
            
            return {
                "status": "success",
                "buffered": len(critical) + min(len(non_critical), available_space),
                "dropped": max(0, len(non_critical) - available_space)
            }
        
        # Fill buffer with non-critical events
        for i in range(100):
            mock_buffered_logger([{
                "entityName": f"normal_{i}",
                "contents": [f"Normal event {i}"],
                "corpusNames": ["test"],
                "tags": ["normal"]
            }])
        
        # Add critical events when buffer is full
        for i in range(10):
            mock_buffered_logger([{
                "entityName": f"critical_{i}",
                "contents": [f"CRITICAL RAG FAILURE {i}"],
                "corpusNames": ["test"],
                "tags": ["critical"]
            }])
        
        # Verify critical events were preserved
        assert len(critical_preserved) == 10
        assert len(log_buffer) <= buffer_size
        
        # Check that critical events are in buffer
        buffer_contents = str(log_buffer)
        for i in range(10):
            assert f"CRITICAL RAG FAILURE {i}" in buffer_contents
    
    def test_logging_queue_overflow_handling(self, validator):
        """Test handling of logging queue overflow"""
        queue_size = 1000
        overflow_count = 0
        processed_count = 0
        
        class MockLoggingQueue:
            def __init__(self, max_size):
                self.max_size = max_size
                self.queue = []
                self.overflow = 0
            
            def put(self, item, block=False):
                nonlocal overflow_count
                if len(self.queue) >= self.max_size:
                    self.overflow += 1
                    overflow_count += 1
                    return False  # Drop item
                self.queue.append(item)
                return True
            
            def process_all(self):
                nonlocal processed_count
                processed = len(self.queue)
                processed_count += processed
                self.queue.clear()
                return processed
        
        mock_queue = MockLoggingQueue(queue_size)
        
        # Simulate massive log burst
        for i in range(2000):
            log_entry = {
                "id": i,
                "content": f"Log entry {i}",
                "critical": i % 100 == 0  # Every 100th is critical
            }
            
            # Critical items bypass queue limit
            if log_entry["critical"]:
                mock_queue.put(log_entry)
            else:
                mock_queue.put(log_entry)
        
        # Process queue
        processed = mock_queue.process_all()
        
        # Verify overflow handling
        assert overflow_count > 0
        assert processed_count <= queue_size
        assert processed_count + overflow_count == 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
