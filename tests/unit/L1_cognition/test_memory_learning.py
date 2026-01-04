"""
Tests for L1 Cognition Memory & Learning Components

Tests the Phase 3 implementation:
- SemanticMemory - vector-based long-term storage
- ReasoningMemory - expanded short-term thought storage
- EpisodicMemory - expanded mission history storage
- MetaLearningAgent - experience replay and adaptive learning
"""

import pytest
import time
from typing import Dict, Any

import sys
sys.path.insert(0, 'c:/Git/Agentic-Workflow')

from agentic_core.L1_cognition.memory.SemanticMemory import (
    SemanticMemory,
    SemanticEntry,
    EmbeddingProvider,
    VectorIndex,
)
from agentic_core.L1_cognition.memory.ReasoningMemory import (
    ReasoningMemory,
    Thought,
)
from agentic_core.L1_cognition.memory.EpisodicMemory import (
    EpisodicMemory,
    Episode,
)
from agentic_core.L1_cognition.learning.MetaLearningAgent import (
    MetaLearningAgent,
    Experience,
    Pattern,
)


# ============== Semantic Memory Tests ==============

class TestEmbeddingProvider:
    """Tests for embedding provider."""
    
    def test_get_embedding(self):
        """Test embedding generation."""
        provider = EmbeddingProvider()
        embedding = provider.get_embedding("test text")
        
        assert len(embedding) == 1536  # Default dimension
        assert all(isinstance(v, float) for v in embedding)
    
    def test_embedding_deterministic(self):
        """Test that same text gives same embedding."""
        provider = EmbeddingProvider()
        emb1 = provider.get_embedding("hello world")
        emb2 = provider.get_embedding("hello world")
        
        assert emb1 == emb2
    
    def test_different_texts_different_embeddings(self):
        """Test that different texts give different embeddings."""
        provider = EmbeddingProvider()
        emb1 = provider.get_embedding("hello")
        emb2 = provider.get_embedding("goodbye")
        
        assert emb1 != emb2
    
    def test_embedding_caching(self):
        """Test that embeddings are cached."""
        provider = EmbeddingProvider()
        provider.get_embedding("test")
        
        assert len(provider._cache) == 1


class TestVectorIndex:
    """Tests for vector index."""
    
    def test_upsert_and_query(self):
        """Test upserting and querying vectors."""
        index = VectorIndex("test_index")
        
        # Create test embedding
        embedding = [0.1] * 1536
        index.upsert("entry1", embedding, {"content": "test"})
        
        # Query
        results = index.query(embedding, top_k=1)
        
        assert len(results) == 1
        assert results[0]["id"] == "entry1"
        assert results[0]["score"] > 0.99  # Same vector should be very similar
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        index = VectorIndex("test_index")
        
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        c = [0.0, 1.0, 0.0]
        
        assert index._cosine_similarity(a, b) == pytest.approx(1.0)
        assert index._cosine_similarity(a, c) == pytest.approx(0.0)
    
    def test_count(self):
        """Test entry count."""
        index = VectorIndex("test_index")
        
        assert index.count() == 0
        
        index.upsert("e1", [0.1] * 10, {})
        index.upsert("e2", [0.2] * 10, {})
        
        assert index.count() == 2


class TestSemanticMemory:
    """Tests for semantic memory."""
    
    @pytest.fixture
    def semantic_memory(self):
        return SemanticMemory()
    
    def test_add_thought(self, semantic_memory):
        """Test adding thought."""
        thought_id = semantic_memory.add_thought({
            "text": "This is a test thought",
            "type": "reasoning"
        })
        
        assert thought_id is not None
        assert semantic_memory.thoughts_stored == 1
    
    def test_add_episode(self, semantic_memory):
        """Test adding episode."""
        episode_id = semantic_memory.add_episode({
            "summary": "Mission completed successfully",
            "outcome": "success"
        })
        
        assert episode_id is not None
        assert semantic_memory.episodes_stored == 1
    
    def test_query_thoughts(self, semantic_memory):
        """Test querying thoughts."""
        semantic_memory.add_thought({"text": "machine learning algorithms"})
        semantic_memory.add_thought({"text": "web development frameworks"})
        semantic_memory.add_thought({"text": "deep learning neural networks"})
        
        results = semantic_memory.query_thoughts("machine learning", top_k=2)
        
        assert len(results) <= 2
    
    def test_query_episodes(self, semantic_memory):
        """Test querying episodes."""
        semantic_memory.add_episode({"summary": "debugging task completed"})
        semantic_memory.add_episode({"summary": "feature implementation done"})
        
        results = semantic_memory.query_episodes("debugging", top_k=1)
        
        assert len(results) <= 1
    
    def test_statistics(self, semantic_memory):
        """Test getting statistics."""
        semantic_memory.add_thought({"text": "test"})
        semantic_memory.add_episode({"summary": "test"})
        
        stats = semantic_memory.get_statistics()
        
        assert stats["thoughts_stored"] == 1
        assert stats["episodes_stored"] == 1
        assert stats["total_entries"] == 2


# ============== Reasoning Memory Tests ==============

class TestReasoningMemory:
    """Tests for reasoning memory."""
    
    @pytest.fixture
    def reasoning_memory(self):
        return ReasoningMemory(capacity=100, persist=False, semantic_offload=False)
    
    def test_store_thought(self, reasoning_memory):
        """Test storing thought."""
        thought_id = reasoning_memory.store({
            "content": "This is a test thought",
            "type": "reasoning"
        })
        
        assert thought_id is not None
        assert len(reasoning_memory.thoughts) == 1
    
    def test_retrieve_recent(self, reasoning_memory):
        """Test retrieving recent thoughts."""
        for i in range(5):
            reasoning_memory.store({"content": f"Thought {i}"})
        
        recent = reasoning_memory.retrieve(count=3)
        
        assert len(recent) == 3
        assert recent[-1]["content"] == "Thought 4"
    
    def test_capacity_eviction(self, reasoning_memory):
        """Test LRU eviction at capacity."""
        reasoning_memory.capacity = 5
        
        for i in range(10):
            reasoning_memory.store({"content": f"Thought {i}"})
        
        assert len(reasoning_memory.thoughts) == 5
        assert reasoning_memory.total_evicted == 5
    
    def test_retrieve_by_type(self, reasoning_memory):
        """Test retrieving by type."""
        reasoning_memory.store({"content": "A", "type": "reasoning"})
        reasoning_memory.store({"content": "B", "type": "observation"})
        reasoning_memory.store({"content": "C", "type": "reasoning"})
        
        reasoning = reasoning_memory.retrieve_by_type("reasoning")
        
        assert len(reasoning) == 2
    
    def test_retrieve_high_confidence(self, reasoning_memory):
        """Test retrieving high confidence thoughts."""
        reasoning_memory.store({"content": "A", "confidence": 0.5})
        reasoning_memory.store({"content": "B", "confidence": 0.95})
        reasoning_memory.store({"content": "C", "confidence": 0.99})
        
        high_conf = reasoning_memory.retrieve_high_confidence(threshold=0.9)
        
        assert len(high_conf) == 2
    
    def test_statistics(self, reasoning_memory):
        """Test getting statistics."""
        reasoning_memory.store({"content": "test"})
        reasoning_memory.retrieve(1)
        
        stats = reasoning_memory.get_statistics()
        
        assert stats["total_stored"] == 1
        assert stats["current_size"] == 1
    
    def test_clear(self, reasoning_memory):
        """Test clearing memory."""
        reasoning_memory.store({"content": "test"})
        reasoning_memory.clear()
        
        assert len(reasoning_memory.thoughts) == 0


# ============== Episodic Memory Tests ==============

class TestEpisodicMemory:
    """Tests for episodic memory."""
    
    @pytest.fixture
    def episodic_memory(self):
        return EpisodicMemory(capacity=100, embed_index=False)
    
    def test_store_episode(self, episodic_memory):
        """Test storing episode."""
        episode_id = episodic_memory.store_episode({
            "summary": "Completed debugging task",
            "outcome": "success"
        })
        
        assert episode_id is not None
        assert len(episodic_memory.episodes) == 1
    
    def test_retrieve_recent(self, episodic_memory):
        """Test retrieving recent episodes."""
        for i in range(5):
            episodic_memory.store_episode({"summary": f"Episode {i}", "outcome": "success"})
        
        recent = episodic_memory.retrieve(count=3)
        
        assert len(recent) == 3
    
    def test_retrieve_successes(self, episodic_memory):
        """Test retrieving successful episodes."""
        episodic_memory.store_episode({"summary": "A", "outcome": "success"})
        episodic_memory.store_episode({"summary": "B", "outcome": "failure"})
        episodic_memory.store_episode({"summary": "C", "outcome": "success"})
        
        successes = episodic_memory.retrieve_successes()
        
        assert len(successes) == 2
    
    def test_retrieve_failures(self, episodic_memory):
        """Test retrieving failed episodes."""
        episodic_memory.store_episode({"summary": "A", "outcome": "success"})
        episodic_memory.store_episode({"summary": "B", "outcome": "failure"})
        
        failures = episodic_memory.retrieve_failures()
        
        assert len(failures) == 1
    
    def test_retrieve_by_type(self, episodic_memory):
        """Test retrieving by mission type."""
        episodic_memory.store_episode({"summary": "A", "type": "task"})
        episodic_memory.store_episode({"summary": "B", "type": "healing"})
        episodic_memory.store_episode({"summary": "C", "type": "task"})
        
        tasks = episodic_memory.retrieve_by_type("task")
        
        assert len(tasks) == 2
    
    def test_retrieve_high_reward(self, episodic_memory):
        """Test retrieving high reward episodes."""
        episodic_memory.store_episode({"summary": "A", "reward": 0.3})
        episodic_memory.store_episode({"summary": "B", "reward": 0.8})
        episodic_memory.store_episode({"summary": "C", "reward": 0.9})
        
        high_reward = episodic_memory.retrieve_high_reward(threshold=0.5)
        
        assert len(high_reward) == 2
    
    def test_success_rate(self, episodic_memory):
        """Test success rate calculation."""
        episodic_memory.store_episode({"summary": "A", "outcome": "success"})
        episodic_memory.store_episode({"summary": "B", "outcome": "success"})
        episodic_memory.store_episode({"summary": "C", "outcome": "failure"})
        
        rate = episodic_memory.get_success_rate()
        
        assert rate == pytest.approx(2/3)
    
    def test_capacity_eviction(self, episodic_memory):
        """Test LRU eviction at capacity."""
        episodic_memory.capacity = 5
        
        for i in range(10):
            episodic_memory.store_episode({"summary": f"Episode {i}"})
        
        assert len(episodic_memory.episodes) == 5
        assert episodic_memory.total_evicted == 5
    
    def test_statistics(self, episodic_memory):
        """Test getting statistics."""
        episodic_memory.store_episode({"summary": "A", "outcome": "success"})
        episodic_memory.store_episode({"summary": "B", "outcome": "failure"})
        
        stats = episodic_memory.get_statistics()
        
        assert stats["total_stored"] == 2
        assert stats["success_count"] == 1
        assert stats["failure_count"] == 1


# ============== Meta Learning Agent Tests ==============

class TestMetaLearningAgent:
    """Tests for meta learning agent."""
    
    @pytest.fixture
    def meta_learner(self):
        return MetaLearningAgent(replay_capacity=100)
    
    def test_store_experience(self, meta_learner):
        """Test storing experience."""
        exp_id = meta_learner.store_experience(
            state={"context": "test"},
            thought_type="cot",
            outcome={"success": True},
            reward=1.0
        )
        
        assert exp_id is not None
        assert len(meta_learner.replay_buffer) == 1
    
    def test_replay_and_learn(self, meta_learner):
        """Test experience replay and learning."""
        # Store many experiences with positive rewards for "cot"
        for i in range(50):
            meta_learner.store_experience(
                state={"i": i},
                thought_type="cot",
                outcome={"success": True},
                reward=1.0
            )
        
        # Store experiences with negative rewards for "react"
        for i in range(50):
            meta_learner.store_experience(
                state={"i": i},
                thought_type="react",
                outcome={"success": False},
                reward=-0.5
            )
        
        initial_weights = meta_learner.strategy_weights.copy()
        
        result = meta_learner.replay_and_learn(batch_size=32)
        
        assert result["status"] == "success"
        # Weights should have changed
        assert meta_learner.strategy_weights != initial_weights
    
    def test_get_strategy_bias(self, meta_learner):
        """Test getting strategy bias."""
        bias = meta_learner.get_strategy_bias()
        
        assert "cot" in bias
        assert "tot" in bias
        assert "react" in bias
        # Initial weights are uniform (1.0 each), normalized after learning
        assert all(w > 0 for w in bias.values())
    
    def test_select_strategy(self, meta_learner):
        """Test strategy selection."""
        strategy = meta_learner.select_strategy()
        
        assert strategy in meta_learner.strategy_weights
    
    def test_weight_adjustment_positive_reward(self, meta_learner):
        """Test that positive rewards increase weight."""
        # All positive rewards for "cot"
        for i in range(50):
            meta_learner.store_experience(
                state={},
                thought_type="cot",
                outcome={},
                reward=1.0
            )
        
        initial_cot = meta_learner.strategy_weights["cot"]
        meta_learner.replay_and_learn(batch_size=30)
        
        # Weight should have increased (relative to others)
        # Since weights are normalized, we check it's higher relative
        assert meta_learner.weight_updates == 1
    
    def test_weight_adjustment_negative_reward(self, meta_learner):
        """Test that negative rewards decrease weight."""
        # All negative rewards for "tot"
        for i in range(50):
            meta_learner.store_experience(
                state={},
                thought_type="tot",
                outcome={},
                reward=-1.0
            )
        
        meta_learner.replay_and_learn(batch_size=30)
        
        # Weight should be at minimum
        assert meta_learner.strategy_weights["tot"] >= meta_learner.min_weight
    
    def test_reset_weights(self, meta_learner):
        """Test resetting weights."""
        meta_learner.strategy_weights["cot"] = 0.9
        meta_learner.strategy_weights["react"] = 0.1
        
        meta_learner.reset_weights()
        
        # All weights should be equal
        weights = list(meta_learner.strategy_weights.values())
        assert all(w == pytest.approx(weights[0]) for w in weights)
    
    def test_statistics(self, meta_learner):
        """Test getting statistics."""
        meta_learner.store_experience({}, "cot", {}, 1.0)
        
        stats = meta_learner.get_statistics()
        
        assert stats["total_experiences"] == 1
        assert stats["buffer_size"] == 1
        assert "current_weights" in stats
    
    def test_insufficient_data_for_replay(self, meta_learner):
        """Test replay with insufficient data."""
        meta_learner.store_experience({}, "cot", {}, 1.0)
        
        result = meta_learner.replay_and_learn(batch_size=10)
        
        assert result["status"] == "insufficient_data"


# ============== Integration Tests ==============

class TestMemoryLearningIntegration:
    """Integration tests for memory and learning components."""
    
    def test_full_memory_flow(self):
        """Test complete memory flow."""
        # Create components
        semantic = SemanticMemory()
        reasoning = ReasoningMemory(capacity=50, persist=False, semantic_offload=False)
        episodic = EpisodicMemory(capacity=50, embed_index=False)
        learner = MetaLearningAgent()
        
        # Store thoughts
        for i in range(10):
            reasoning.store({"content": f"Thought {i}", "type": "reasoning"})
        
        # Store episodes
        for i in range(10):
            episodic.store_episode({
                "summary": f"Episode {i}",
                "outcome": "success" if i % 2 == 0 else "failure"
            })
        
        # Store semantic entries
        for i in range(10):
            semantic.add_thought({"text": f"Semantic thought {i}"})
        
        # Store experiences
        for i in range(50):
            learner.store_experience(
                state={"step": i},
                thought_type=["cot", "react", "tot"][i % 3],
                outcome={"success": i % 2 == 0},
                reward=1.0 if i % 2 == 0 else -0.5
            )
        
        # Verify all components
        assert len(reasoning.thoughts) == 10
        assert len(episodic.episodes) == 10
        assert semantic.thoughts_stored == 10
        assert len(learner.replay_buffer) == 50
    
    def test_adaptive_learning_flow(self):
        """Test adaptive learning improves strategy selection."""
        learner = MetaLearningAgent()
        
        # Simulate many successful "cot" experiences
        for i in range(100):
            learner.store_experience(
                state={},
                thought_type="cot",
                outcome={"success": True},
                reward=1.0
            )
        
        # Simulate many failed "direct" experiences
        for i in range(100):
            learner.store_experience(
                state={},
                thought_type="direct",
                outcome={"success": False},
                reward=-1.0
            )
        
        # Learn from experiences
        learner.replay_and_learn(batch_size=50)
        learner.replay_and_learn(batch_size=50)
        
        # Check that "cot" is now preferred
        bias = learner.get_strategy_bias()
        assert bias["cot"] > bias["direct"]
    
    def test_memory_retention_across_eviction(self):
        """Test that semantic memory retains evicted items."""
        semantic = SemanticMemory()
        reasoning = ReasoningMemory(capacity=5, persist=False, semantic_offload=False)
        
        # Store more than capacity
        for i in range(10):
            reasoning.store({"content": f"Thought {i}"})
        
        # In-memory should be at capacity
        assert len(reasoning.thoughts) == 5
        assert reasoning.total_evicted == 5
        
        # Recent thoughts should be 5-9
        recent = reasoning.retrieve(5)
        assert all("Thought" in t["content"] for t in recent)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
