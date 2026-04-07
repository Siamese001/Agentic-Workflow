#!/usr/bin/env python3
"""
Demo: Continuous Learning Integration with Existing System Components
Shows how to integrate the pipeline with system_learning components
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add root to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuous_learning_pipeline import (
    AutomatedLearningPipeline,
    get_global_pipeline,
    set_global_pipeline,
)


class MockActivator:
    """Mock version of system_learning/stores/activator.py"""

    def __init__(self):
        self.pipeline = get_global_pipeline()
        self.active_version = "1.0.0"
        self.activation_history = []

    def activate_version(self, version: str):
        """Mock version activation with learning integration."""
        print(f"🔄 Activating version: {version}")

        # Simulate activation work
        time.sleep(0.5)

        # Mock activation result
        result = {
            "success": True,
            "time_taken": 0.5,
            "previous_version": self.active_version,
        }

        # Emit learning event
        if self.pipeline:
            self.pipeline.emit_learning_event(
                event_type="version_activation",
                source="activator",
                data={
                    "version": version,
                    "success": result["success"],
                    "activation_time": result["time_taken"],
                    "previous_version": result["previous_version"],
                },
                priority="HIGH",
            )

        # Update state
        self.active_version = version
        self.activation_history.append({
            "version": version,
            "timestamp": datetime.now(),
            "success": result["success"],
        })

        print(f"✅ Version {version} activated successfully")
        return result

    def store_checkpoint(self, checkpoint_data: dict):
        """Mock checkpoint storage with learning integration."""
        print("💾 Storing checkpoint...")

        # Simulate checkpoint work
        time.sleep(0.2)

        # Emit learning signal
        if self.pipeline:
            self.pipeline.emit_learning_signal(
                signal_type="checkpoint_available",
                source="activator",
                payload=checkpoint_data,
                expires_in_seconds=300,  # 5 minutes
            )

        print("✅ Checkpoint stored")

class MockConfigProvider:
    """Mock version of system_learning/stores/config_provider.py"""

    def __init__(self):
        self.pipeline = get_global_pipeline()
        self.config = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "model_version": "1.0.0",
            "optimization_level": "medium",
        }

    def update_config(self, config_key: str, config_value: Any):
        """Mock config update with learning integration."""
        print(f"⚙️ Updating config: {config_key} = {config_value}")

        old_value = self.config.get(config_key)

        # Simulate config update work
        time.sleep(0.1)

        # Update config
        self.config[config_key] = config_value

        # Mock impact assessment
        impact = self._assess_impact(config_key, old_value, config_value)

        # Emit learning event
        if self.pipeline:
            self.pipeline.emit_learning_event(
                event_type="config_change",
                source="config_provider",
                data={
                    "config_key": config_key,
                    "old_value": old_value,
                    "new_value": config_value,
                    "change_timestamp": datetime.now().isoformat(),
                    "impact_assessment": impact,
                },
                priority="MEDIUM",
            )

        print(f"✅ Config updated: {config_key} = {config_value} (impact: {impact['level']})")
        return {"success": True, "impact": impact}

    def _assess_impact(self, key: str, old_val: Any, new_val: Any) -> dict:
        """Mock impact assessment."""
        high_impact_keys = ["learning_rate", "batch_size", "model_version"]

        if key in high_impact_keys:
            return {"level": "HIGH", "areas_affected": ["training", "performance"]}
        else:
            return {"level": "LOW", "areas_affected": ["configuration"]}

class MockMetaAdapter:
    """Mock version of system_learning/adapters/l1_meta_adapter.py"""

    def __init__(self):
        self.pipeline = get_global_pipeline()
        self.processing_count = 0

    def process_learning_signal(self, signal_data: dict):
        """Mock learning signal processing with integration."""
        print(f"🧠 Processing learning signal: {signal_data.get('type', 'unknown')}")

        # Simulate processing work
        start_time = time.time()
        time.sleep(0.3)
        processing_time = time.time() - start_time

        # Mock processing result
        result = {
            "quality_score": 0.85 + (self.processing_count % 10) * 0.01,
            "adaptations": ["parameter_tuning", "learning_rate_adjustment"],
            "insights": ["pattern_detected", "efficiency_improved"],
            "confidence": 0.8 + (self.processing_count % 5) * 0.02,
        }

        # Emit learning event
        if self.pipeline:
            self.pipeline.emit_learning_event(
                event_type="meta_learning_processing",
                source="l1_meta_adapter",
                data={
                    "signal_type": signal_data.get("type"),
                    "processing_time": processing_time,
                    "result_quality": result["quality_score"],
                    "adaptations_made": result["adaptations"],
                    "learning_insights": result["insights"],
                },
                priority="HIGH",
            )

        # Store learning experience
        if self.pipeline:
            from tools.implement_unified_memory import LearningExperience
            experience = LearningExperience(
                experience_type="meta_learning",
                input_context=signal_data,
                outcome_result=result,
                lesson_learned=f"Processed {signal_data.get('type')} signal with quality {result['quality_score']:.2f}",
                confidence_score=result["confidence"],
                created_at=datetime.now(),
                metadata={
                    "adapter": "l1_meta_adapter",
                    "processing_time": processing_time,
                },
            )
            self.pipeline.memory_manager.store_learning_experience(experience)

        self.processing_count += 1
        print(f"✅ Signal processed: quality={result['quality_score']:.2f}, adaptations={len(result['adaptations'])}")
        return result

class MockModelTrainer:
    """Mock model trainer with continuous learning integration."""

    def __init__(self, model_name: str = "demo_model"):
        self.pipeline = get_global_pipeline()
        self.model_name = model_name
        self.training_session_id = f"session_{int(time.time())}"
        self.current_epoch = 0
        self.best_loss = float('inf')

    def train_epoch(self, epoch: int, num_batches: int = 10):
        """Mock training epoch with learning integration."""
        print(f"🎓 Training epoch {epoch}...")

        start_time = time.time()
        loss_history = []

        # Simulate training batches
        for batch_idx in range(num_batches):
            # Simulate batch processing
            time.sleep(0.1)
            loss = 1.0 - (epoch * 0.1) - (batch_idx * 0.01) + (hash(str(batch_idx)) % 100) * 0.001
            loss_history.append(loss)

            # Emit learning signal every few batches
            if batch_idx % 3 == 0 and self.pipeline:
                self.pipeline.emit_learning_signal(
                    signal_type="training_progress",
                    source="model_trainer",
                    payload={
                        "epoch": epoch,
                        "batch": batch_idx,
                        "loss": loss,
                        "learning_rate": 0.001,
                    },
                    expires_in_seconds=60,
                )

        epoch_time = time.time() - start_time
        avg_loss = sum(loss_history) / len(loss_history)

        # Emit learning event for epoch completion
        if self.pipeline:
            self.pipeline.emit_learning_event(
                event_type="training_epoch",
                source="model_trainer",
                data={
                    "session_id": self.training_session_id,
                    "epoch": epoch,
                    "avg_loss": avg_loss,
                    "loss_history": loss_history,
                    "epoch_time": epoch_time,
                    "model_performance": {
                        "accuracy": max(0.5, 0.9 - avg_loss),
                        "validation_score": max(0.4, 0.85 - avg_loss),
                    },
                },
                priority="HIGH",
            )

        # Store checkpoint if performance improved
        if avg_loss < self.best_loss:
            self._store_model_checkpoint(epoch, avg_loss)
            self.best_loss = avg_loss

        self.current_epoch = epoch
        print(f"✅ Epoch {epoch} completed: loss={avg_loss:.4f}, time={epoch_time:.2f}s")
        return avg_loss

    def _store_model_checkpoint(self, epoch: int, loss: float):
        """Store model checkpoint with learning integration."""
        if not self.pipeline:
            return

        from tools.implement_unified_memory import ModelCheckpoint

        checkpoint = ModelCheckpoint(
            model_name=self.model_name,
            version=f"epoch_{epoch}",
            model_type="neural_network",
            weights={
                "layer1": [0.1, 0.2, 0.3],
                "layer2": [0.4, 0.5, 0.6],
                "output": [0.7, 0.8, 0.9],
            },
            metadata={
                "epoch": epoch,
                "training_session": self.training_session_id,
                "optimizer_state": {"learning_rate": 0.001, "momentum": 0.9},
            },
            performance_metrics={
                "loss": loss,
                "accuracy": max(0.5, 0.9 - loss),
                "validation_score": max(0.4, 0.85 - loss),
            },
            created_at=datetime.now(),
        )

        model_id = self.pipeline.memory_manager.store_model_checkpoint(checkpoint)
        print(f"💾 Model checkpoint stored: epoch_{epoch} (ID: {model_id})")

class MockUserInteractionLearner:
    """Mock user interaction learner with continuous learning."""

    def __init__(self):
        self.pipeline = get_global_pipeline()
        self.session_id = f"session_{int(time.time())}"
        self.interaction_count = 0

    def process_user_interaction(self, user_input: str, system_response: str, user_feedback: dict = None):
        """Mock user interaction processing with learning."""
        self.interaction_count += 1
        print(f"👤 Processing user interaction #{self.interaction_count}")

        # Simulate interaction analysis
        time.sleep(0.2)

        interaction_data = {
            "quality_score": 0.7 + (self.interaction_count % 5) * 0.05,
            "response_time_ms": 150 + (self.interaction_count % 10) * 10,
            "intent": "help_request" if "help" in user_input.lower() else "general_query",
            "entities": ["user", "system"] + user_input.split()[:3],
            "confidence": 0.8 + (self.interaction_count % 3) * 0.05,
        }

        # Emit learning event
        if self.pipeline:
            self.pipeline.emit_learning_event(
                event_type="user_interaction",
                source="interaction_learner",
                data={
                    "session_id": self.session_id,
                    "user_input_length": len(user_input),
                    "system_response_length": len(system_response),
                    "interaction_quality": interaction_data["quality_score"],
                    "user_satisfaction": user_feedback.get("satisfaction") if user_feedback else None,
                    "response_time_ms": interaction_data["response_time_ms"],
                    "intent_detected": interaction_data["intent"],
                    "entities_extracted": interaction_data["entities"],
                },
                priority="MEDIUM",
            )

        # Store learning experience
        if self.pipeline:
            from tools.implement_unified_memory import LearningExperience
            experience = LearningExperience(
                experience_type="user_interaction",
                input_context={"user_input": user_input, "session_id": self.session_id},
                outcome_result={
                    "system_response": system_response,
                    "interaction_analysis": interaction_data,
                    "user_feedback": user_feedback,
                },
                lesson_learned=f"User interaction with intent: {interaction_data['intent']}",
                confidence_score=interaction_data["confidence"],
                created_at=datetime.now(),
                metadata={
                    "session_id": self.session_id,
                    "interaction_quality": interaction_data["quality_score"],
                },
            )
            self.pipeline.memory_manager.store_learning_experience(experience)

        print(f"✅ Interaction processed: intent={interaction_data['intent']}, quality={interaction_data['quality_score']:.2f}")
        return interaction_data

def demonstrate_component_integration():
    """Demonstrate integration with mock system components."""
    print("=" * 80)
    print("CONTINUOUS LEARNING - COMPONENT INTEGRATION DEMONSTRATION")
    print("=" * 80)

    # Initialize and start pipeline
    print("\n🚀 Initializing Learning Pipeline...")
    pipeline = AutomatedLearningPipeline()
    pipeline.configure(
        enable_file_monitoring=True,
        enable_component_integration=True,
        collection_interval_seconds=5,  # Faster for demo
    )

    # Set as global pipeline
    set_global_pipeline(pipeline)
    pipeline.start_pipeline()

    print("✅ Learning pipeline started!")

    # Create mock system components
    print("\n🔧 Creating System Components...")
    activator = MockActivator()
    config_provider = MockConfigProvider()
    meta_adapter = MockMetaAdapter()
    model_trainer = MockModelTrainer()
    interaction_learner = MockUserInteractionLearner()

    # Register components with pipeline
    print("\n📝 Registering Components with Pipeline...")
    pipeline.register_component("activator", activator)
    pipeline.register_component("config_provider", config_provider)
    pipeline.register_component("meta_adapter", meta_adapter)
    pipeline.register_component("model_trainer", model_trainer)
    pipeline.register_component("interaction_learner", interaction_learner)

    print("✅ All components registered!")

    # Demonstrate component operations
    print("\n" + "=" * 60)
    print("DEMONSTRATING COMPONENT OPERATIONS")
    print("=" * 60)

    # 1. Activator operations
    print("\n🔄 ACTIVATOR OPERATIONS:")
    activator.activate_version("1.1.0")
    activator.activate_version("1.2.0")
    activator.store_checkpoint({"version": "1.2.0", "timestamp": time.time()})

    # 2. Config provider operations
    print("\n⚙️ CONFIG PROVIDER OPERATIONS:")
    config_provider.update_config("learning_rate", 0.002)
    config_provider.update_config("batch_size", 64)
    config_provider.update_config("optimization_level", "high")

    # 3. Meta adapter operations
    print("\n🧠 META ADAPTER OPERATIONS:")
    meta_adapter.process_learning_signal({"type": "pattern_recognition", "data": "sample"})
    meta_adapter.process_learning_signal({"type": "adaptation_request", "priority": "high"})

    # 4. Model training operations
    print("\n🎓 MODEL TRAINING OPERATIONS:")
    model_trainer.train_epoch(1, num_batches=5)
    model_trainer.train_epoch(2, num_batches=5)

    # 5. User interaction operations
    print("\n👤 USER INTERACTION OPERATIONS:")
    interaction_learner.process_user_interaction(
        "Help me debug this issue",
        "I'll help you debug the issue. Let me analyze the problem...",
        {"satisfaction": 4, "helpful": True},
    )
    interaction_learner.process_user_interaction(
        "How do I optimize performance?",
        "To optimize performance, you should consider several factors...",
        {"satisfaction": 5, "resolved": True},
    )

    # Let pipeline process events
    print("\n⏳ Processing Learning Events...")
    time.sleep(10)

    # Show pipeline statistics
    print("\n" + "=" * 60)
    print("PIPELINE STATISTICS")
    print("=" * 60)

    stats = pipeline.get_pipeline_stats()
    print(f"📊 Events processed: {stats['events_processed']}")
    print(f"📊 Signals processed: {stats['signals_processed']}")
    print(f"📊 Errors: {stats['errors_count']}")
    print(f"📊 Uptime: {stats['uptime_seconds']:.1f}s")
    print(f"📊 Events/sec: {stats['events_per_second']:.2f}")
    print(f"📊 Error rate: {stats['error_rate']:.2f}%")
    print(f"📊 Queue sizes: {stats['queue_sizes']}")

    # Show memory manager statistics
    print("\n💾 MEMORY MANAGER STATISTICS:")
    memory_stats = pipeline.memory_manager.get_database_stats()
    for key, value in memory_stats.items():
        if "count" in key:
            print(f"  {key}: {value}")

    print(f"  Database size: {memory_stats.get('database_size_mb', 0):.2f} MB")

    # Show recent learning experiences
    print("\n📚 RECENT LEARNING EXPERIENCES:")
    experiences = pipeline.memory_manager.get_learning_experiences(limit=5)
    for i, exp in enumerate(experiences, 1):
        print(f"  {i}. {exp.experience_type}: {exp.lesson_learned[:50]}...")

    # Show recent performance metrics
    print("\n📈 RECENT PERFORMANCE METRICS:")
    metrics = pipeline.memory_manager.get_performance_metrics(limit=5)
    for i, metric in enumerate(metrics, 1):
        print(f"  {i}. {metric['name']}: {metric['value']:.3f} {metric.get('unit', '')}")

    # Stop pipeline
    print("\n🛑 Stopping Learning Pipeline...")
    pipeline.stop_pipeline()

    print("\n🎉 COMPONENT INTEGRATION DEMONSTRATION COMPLETE!")
    print("The system successfully demonstrated continuous learning with:")
    print("  ✅ Real-time event collection")
    print("  ✅ Component integration")
    print("  ✅ Persistent memory storage")
    print("  ✅ Learning experience accumulation")
    print("  ✅ Performance metrics tracking")
    print("  ✅ Automated insight generation")

def main():
    """Main demonstration function."""
    try:
        demonstrate_component_integration()
    # guardian: allow-silent-swallow - acceptable exception handling
    except KeyboardInterrupt:
        print("\n⚠️ Demonstration interrupted by user")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"\n❌ Demonstration error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
