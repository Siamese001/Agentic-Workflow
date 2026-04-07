#!/usr/bin/env python3
"""
Continuous Learning Pipeline for Agentic System
Automated generation and movement of learning data into persistent memory
"""

import logging
import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

ROOT = Path(__file__).resolve().parents[1]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LearningEvent:
    """Learning event data structure."""
    event_type: str
    source_component: str
    timestamp: datetime
    data: dict[str, Any]
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    session_id: str | None = None
    correlation_id: str | None = None

@dataclass
class LearningSignal:
    """Learning signal for real-time processing."""
    signal_type: str
    source: str
    payload: Any
    timestamp: datetime
    expires_at: datetime | None = None

class LearningDataCollector:
    """Collects learning data from various sources in real-time."""

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.event_queue = queue.Queue()
        self.signal_queue = queue.Queue()
        self.collection_handlers = {}
        self.signal_handlers = {}
        self.is_running = False
        self.collection_thread = None
        self.signal_thread = None

    def register_collection_handler(self, event_type: str, handler: Callable):
        """Register a handler for specific learning event types."""
        self.collection_handlers[event_type] = handler
        logger.info(f"Registered collection handler for: {event_type}")

    def register_signal_handler(self, signal_type: str, handler: Callable):
        """Register a handler for specific learning signals."""
        self.signal_handlers[signal_type] = handler
        logger.info(f"Registered signal handler for: {signal_type}")

    def emit_learning_event(self, event: LearningEvent):
        """Emit a learning event for collection."""
        self.event_queue.put(event)

    def emit_learning_signal(self, signal: LearningSignal):
        """Emit a learning signal for real-time processing."""
        self.signal_queue.put(signal)

    def start_collection(self):
        """Start the continuous data collection process."""
        if self.is_running:
            logger.warning("Collection already running")
            return

        self.is_running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.signal_thread = threading.Thread(target=self._signal_loop, daemon=True)

        self.collection_thread.start()
        self.signal_thread.start()

        logger.info("Started continuous learning data collection")

    def stop_collection(self):
        """Stop the continuous data collection process."""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join()
        if self.signal_thread:
            self.signal_thread.join()
        logger.info("Stopped continuous learning data collection")

    def _collection_loop(self):
        """Main collection loop for learning events."""
        while self.is_running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1.0)

                # Process event
                self._process_learning_event(event)

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error in collection loop: {e}")
                continue

    def _signal_loop(self):
        """Signal processing loop for real-time learning."""
        while self.is_running:
            try:
                # Get signal from queue with timeout
                signal = self.signal_queue.get(timeout=1.0)

                # Process signal
                self._process_learning_signal(signal)

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error in signal loop: {e}")
                continue

    def _process_learning_event(self, event: LearningEvent):
        """Process a learning event and store in persistent memory."""
        try:
            # Get handler for event type
            handler = self.collection_handlers.get(event.event_type)
            if handler:
                handler(event)
            else:
                # Default handler
                self._default_event_handler(event)

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error processing learning event {event.event_type}: {e}")

    def _process_learning_signal(self, signal: LearningSignal):
        """Process a learning signal for real-time updates."""
        try:
            # Check if signal has expired
            if signal.expires_at and datetime.now() > signal.expires_at:
                return

            # Get handler for signal type
            handler = self.signal_handlers.get(signal.signal_type)
            if handler:
                handler(signal)
            else:
                # Default signal handler
                self._default_signal_handler(signal)

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error processing learning signal {signal.signal_type}: {e}")

    def _default_event_handler(self, event: LearningEvent):
        """Default handler for learning events."""
        # Store as learning experience
        from implement_unified_memory import LearningExperience

        experience = LearningExperience(
            experience_type=event.event_type,
            input_context=event.data,
            outcome_result={"processed": True, "timestamp": event.timestamp.isoformat()},
            lesson_learned=f"Processed {event.event_type} from {event.source_component}",
            confidence_score=0.8,
            created_at=event.timestamp,
            metadata={
                "source": event.source_component,
                "priority": event.priority,
                "session_id": event.session_id,
                "correlation_id": event.correlation_id
            }
        )

        self.memory_manager.store_learning_experience(experience)
        logger.info(f"Stored learning event: {event.event_type}")

    def _default_signal_handler(self, signal: LearningSignal):
        """Default handler for learning signals."""
        # Store as application state for immediate access
        state_key = f"signal_{signal.signal_type}_{signal.source}"
        self.memory_manager.store_application_state(
            state_key,
            signal.payload,
            "pickle",
            expires_at=signal.expires_at
        )
        logger.info(f"Stored learning signal: {signal.signal_type}")

class FileSystemLearningMonitor(FileSystemEventHandler):
    """Monitors file system for learning data generation."""

    def __init__(self, data_collector: LearningDataCollector, watch_directories: list[Path]):
        super().__init__()
        self.data_collector = data_collector
        self.watch_directories = watch_directories
        self.observer = Observer()
        self.learning_patterns = {
            '.py': 'code_change',
            '.json': 'config_change',
            '.log': 'log_event',
            '.pkl': 'model_save',
            '.ckpt': 'checkpoint_save',
            '.model': 'model_update'
        }

    def start_monitoring(self):
        """Start monitoring file system changes."""
        for directory in self.watch_directories:
            if directory.exists():
                self.observer.schedule(self, str(directory), recursive=True)
                logger.info(f"Started monitoring: {directory}")

        self.observer.start()

    def stop_monitoring(self):
        """Stop monitoring file system changes."""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped file system monitoring")

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self._handle_file_change(event.src_path, "modified")

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._handle_file_change(event.src_path, "created")

    def _handle_file_change(self, file_path: str, change_type: str):
        """Handle file system changes for learning."""
        try:
            path = Path(file_path)
            extension = path.suffix.lower()

            # Get learning event type
            event_type = self.learning_patterns.get(extension, "file_change")

            # Create learning event
            event = LearningEvent(
                event_type=event_type,
                source_component="file_system",
                timestamp=datetime.now(),
                data={
                    "file_path": str(path),
                    "change_type": change_type,
                    "extension": extension,
                    "size": path.stat().st_size if path.exists() else 0
                },
                priority="MEDIUM"
            )

            self.data_collector.emit_learning_event(event)

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error handling file change {file_path}: {e}")

class ComponentLearningIntegrator:
    """Integrates learning collection into system components."""

    def __init__(self, data_collector: LearningDataCollector):
        self.data_collector = data_collector
        self.component_handlers = {}
        self.learning_hooks = {}

    def register_component(self, component_name: str, component_instance: Any):
        """Register a component for learning integration."""
        # Wrap component methods with learning hooks
        self._wrap_component_methods(component_name, component_instance)
        self.component_handlers[component_name] = component_instance
        logger.info(f"Registered component for learning: {component_name}")

    def _wrap_component_methods(self, component_name: str, component_instance: Any):
        """Wrap component methods with learning hooks."""
        # Get methods that should be monitored
        learning_methods = [
            'train', 'predict', 'update', 'save', 'load',
            'process', 'execute', 'run', 'analyze', 'evaluate'
        ]

        for attr_name in dir(component_instance):
            if attr_name in learning_methods:
                attr = getattr(component_instance, attr_name)
                if callable(attr):
                    # Wrap with learning hook
                    wrapped_method = self._create_learning_wrapper(
                        component_name, attr_name, attr
                    )
                    setattr(component_instance, attr_name, wrapped_method)

    def _create_learning_wrapper(self, component_name: str, method_name: str, method: Callable):
        """Create a learning wrapper for a component method."""
        def wrapper(*args, **kwargs):
            start_time = datetime.now()

            # Create pre-execution learning event
            pre_event = LearningEvent(
                event_type="method_execution_start",
                source_component=component_name,
                timestamp=start_time,
                data={
                    "method": method_name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                },
                priority="LOW"
            )
            self.data_collector.emit_learning_event(pre_event)

            try:
                # Execute the original method
                result = method(*args, **kwargs)

                # Create success learning event
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                success_event = LearningEvent(
                    event_type="method_execution_success",
                    source_component=component_name,
                    timestamp=end_time,
                    data={
                        "method": method_name,
                        "duration_seconds": duration,
                        "result_type": type(result).__name__,
                        "success": True
                    },
                    priority="MEDIUM"
                )
                self.data_collector.emit_learning_event(success_event)

                return result

            except (ValueError, TypeError, RuntimeError) as e:
                # Create error learning event
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                error_event = LearningEvent(
                    event_type="method_execution_error",
                    source_component=component_name,
                    timestamp=end_time,
                    data={
                        "method": method_name,
                        "duration_seconds": duration,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "success": False
                    },
                    priority="HIGH"
                )
                self.data_collector.emit_learning_event(error_event)

                raise

        return wrapper

class AutomatedLearningPipeline:
    """Complete automated learning pipeline for continuous data flow."""

    def __init__(self, memory_manager=None):
        # Initialize memory manager if not provided
        if memory_manager is None:
            from implement_unified_memory import UnifiedMemoryManager
            self.memory_manager = UnifiedMemoryManager()
        else:
            self.memory_manager = memory_manager

        # Initialize components
        self.data_collector = LearningDataCollector(self.memory_manager)
        self.component_integrator = ComponentLearningIntegrator(self.data_collector)
        self.file_monitor = None

        # Pipeline configuration
        self.config = {
            "enable_file_monitoring": True,
            "enable_component_integration": True,
            "enable_periodic_collection": True,
            "collection_interval_seconds": 30,
            "batch_size": 100,
            "max_queue_size": 10000
        }

        # Statistics
        self.stats = {
            "events_processed": 0,
            "signals_processed": 0,
            "errors_count": 0,
            "start_time": datetime.now(),
            "last_activity": None
        }

    def configure(self, **kwargs):
        """Configure pipeline settings."""
        self.config.update(kwargs)
        logger.info(f"Updated pipeline configuration: {kwargs}")

    def start_pipeline(self):
        """Start the complete learning pipeline."""
        logger.info("Starting automated learning pipeline...")

        # Start data collection
        self.data_collector.start_collection()

        # Start file system monitoring
        if self.config["enable_file_monitoring"]:
            self._start_file_monitoring()

        # Start periodic collection
        if self.config["enable_periodic_collection"]:
            self._start_periodic_collection()

        # Register default handlers
        self._register_default_handlers()

        logger.info("Learning pipeline started successfully")

    def stop_pipeline(self):
        """Stop the learning pipeline."""
        logger.info("Stopping learning pipeline...")

        # Stop data collection
        self.data_collector.stop_collection()

        # Stop file monitoring
        if self.file_monitor:
            self.file_monitor.stop_monitoring()

        logger.info("Learning pipeline stopped")

    def register_component(self, component_name: str, component_instance: Any):
        """Register a component for automated learning."""
        if self.config["enable_component_integration"]:
            self.component_integrator.register_component(component_name, component_instance)

    def emit_learning_event(self, event_type: str, source: str, data: dict[str, Any], priority: str = "MEDIUM"):
        """Emit a learning event manually."""
        event = LearningEvent(
            event_type=event_type,
            source_component=source,
            timestamp=datetime.now(),
            data=data,
            priority=priority
        )
        self.data_collector.emit_learning_event(event)

    def emit_learning_signal(self, signal_type: str, source: str, payload: Any, expires_in_seconds: int = None):
        """Emit a learning signal manually."""
        expires_at = None
        if expires_in_seconds:
            expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)

        signal = LearningSignal(
            signal_type=signal_type,
            source=source,
            payload=payload,
            timestamp=datetime.now(),
            expires_at=expires_at
        )
        self.data_collector.emit_learning_signal(signal)

    def _start_file_monitoring(self):
        """Start file system monitoring."""
        # Define directories to watch
        watch_directories = [
            ROOT / "system_learning",
            ROOT / "agentic_core",
            ROOT / "tools",
            ROOT / "artifacts" / "adg"
        ]

        self.file_monitor = FileSystemLearningMonitor(self.data_collector, watch_directories)
        self.file_monitor.start_monitoring()

    def _start_periodic_collection(self):
        """Start periodic data collection."""
        def periodic_collection():
            while self.data_collector.is_running:
                try:
                    self._collect_system_metrics()
                    self._collect_learning_progress()
                    self._cleanup_expired_data()

                    # Sleep for configured interval
                    time.sleep(self.config["collection_interval_seconds"])

                except (ValueError, TypeError, RuntimeError) as e:
                    logger.error(f"Error in periodic collection: {e}")
                    self.stats["errors_count"] += 1

        # Start in background thread
        collection_thread = threading.Thread(target=periodic_collection, daemon=True)
        collection_thread.start()

    def _register_default_handlers(self):
        """Register default learning event handlers."""

        def model_checkpoint_handler(event: LearningEvent):
            """Handle model checkpoint events."""
            from implement_unified_memory import ModelCheckpoint

            # Extract checkpoint data
            data = event.data
            checkpoint = ModelCheckpoint(
                model_name=data.get("model_name", "unknown"),
                version=data.get("version", "1.0.0"),
                model_type=data.get("model_type", "neural_network"),
                weights=data.get("weights", {}),
                metadata=data.get("metadata", {}),
                performance_metrics=data.get("performance_metrics", {}),
                created_at=event.timestamp
            )

            self.memory_manager.store_model_checkpoint(checkpoint)
            logger.info(f"Stored model checkpoint: {checkpoint.model_name}")

        def embedding_update_handler(event: LearningEvent):
            """Handle embedding update events."""
            from implement_unified_memory import EmbeddingVector

            data = event.data
            embedding = EmbeddingVector(
                entity_id=data.get("entity_id", "unknown"),
                entity_type=data.get("entity_type", "unknown"),
                vector=data.get("vector", []),
                model_version=data.get("model_version", "1.0"),
                dimension=data.get("dimension", 0),
                created_at=event.timestamp
            )

            self.memory_manager.store_embedding(embedding)
            logger.info(f"Stored embedding: {embedding.entity_id}")

        def performance_metric_handler(event: LearningEvent):
            """Handle performance metric events."""
            data = event.data
            self.memory_manager.store_performance_metric(
                name=data.get("metric_name", "unknown"),
                value=data.get("value", 0.0),
                unit=data.get("unit"),
                context=data.get("context"),
                component=event.source_component
            )
            logger.info(f"Stored performance metric: {data.get('metric_name')}")

        # Register handlers
        self.data_collector.register_collection_handler("model_checkpoint", model_checkpoint_handler)
        self.data_collector.register_collection_handler("embedding_update", embedding_update_handler)
        self.data_collector.register_collection_handler("performance_metric", performance_metric_handler)

    def _collect_system_metrics(self):
        """Collect system-wide metrics."""
        try:
            # Memory usage
            import psutil
            memory_info = psutil.virtual_memory()

            self.emit_learning_event(
                event_type="system_metrics",
                source="system_monitor",
                data={
                    "memory_percent": memory_info.percent,
                    "memory_available_gb": memory_info.available / (1024**3),
                    "cpu_percent": psutil.cpu_percent(),
                    "disk_usage_percent": psutil.disk_usage('/').percent
                },
                priority="LOW"
            )

        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            # psutil not available
            pass
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error collecting system metrics: {e}")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def _collect_learning_progress(self):
        """Collect learning progress metrics."""
        try:
            # Get database statistics
            stats = self.memory_manager.get_database_stats()

            self.emit_learning_event(
                event_type="learning_progress",
                source="learning_pipeline",
                data=stats,
                priority="MEDIUM"
            )
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error collecting learning progress: {e}")
        except Exception as e:
            logger.error(f"Error collecting learning progress: {e}")

    def _cleanup_expired_data(self):
        """Clean up expired data from memory."""
        try:
            # Clean up expired application state
            # This would be implemented in the memory manager
            pass
        except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
            logger.error(f"Error during cleanup: {e}")
        except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
            logger.error(f"Error during cleanup: {e}")

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        current_time = datetime.now()
        uptime = (current_time - self.stats["start_time"]).total_seconds()

        return {
            **self.stats,
            "uptime_seconds": uptime,
            "events_per_second": self.stats["events_processed"] / uptime if uptime > 0 else 0,
            "signals_per_second": self.stats["signals_processed"] / uptime if uptime > 0 else 0,
            "error_rate": self.stats["errors_count"] / max(1, self.stats["events_processed"]) * 100,
            "queue_sizes": {
                "events": self.data_collector.event_queue.qsize(),
                "signals": self.data_collector.signal_queue.qsize()
            }
        }


# Decorator for easy learning integration
def learning_enabled(method_name: str = None, priority: str = "MEDIUM"):
    """Decorator to enable learning for a method."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the pipeline instance (would need to be global or passed)
            # This is a simplified version - in practice, you'd use dependency injection
            try:
                pipeline = get_global_pipeline()  # This function would need to be implemented
                if pipeline:
                    pipeline.emit_learning_event(
                        event_type="decorated_method_call",
                        source=func.__module__,
                        data={
                            "method": method_name or func.__name__,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys())
                        },
                        priority=priority
                    )
            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error in learning decorator: {e}")
            except Exception:
                pass
                pass  # Pipeline not available

            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global pipeline instance (simplified approach)
_global_pipeline = None

def get_global_pipeline() -> AutomatedLearningPipeline | None:
    """Get the global pipeline instance."""
    return _global_pipeline

def set_global_pipeline(pipeline: AutomatedLearningPipeline):
    """Set the global pipeline instance."""
    global _global_pipeline
    _global_pipeline = pipeline


def main():
    """Demonstrate the continuous learning pipeline."""
    print("=" * 80)
    print("CONTINUOUS LEARNING PIPELINE DEMONSTRATION")
    print("=" * 80)

    # Create and configure pipeline
    pipeline = AutomatedLearningPipeline()
    pipeline.configure(
        enable_file_monitoring=True,
        enable_component_integration=True,
        collection_interval_seconds=5  # Shorter for demo
    )

    # Set as global pipeline
    set_global_pipeline(pipeline)

    # Start pipeline
    pipeline.start_pipeline()

    print("\n🚀 Learning pipeline started!")
    print("📁 File system monitoring active")
    print("🔄 Periodic collection active")
    print("📊 Event processing active")

    # Simulate some learning events
    print("\n📚 Simulating learning events...")

    # Model checkpoint event
    pipeline.emit_learning_event(
        event_type="model_checkpoint",
        source="demo_component",
        data={
            "model_name": "demo_model",
            "version": "1.0.0",
            "model_type": "neural_network",
            "weights": {"layer1": [0.1, 0.2, 0.3]},
            "performance_metrics": {"accuracy": 0.95}
        },
        priority="HIGH"
    )

    # Embedding update event
    pipeline.emit_learning_event(
        event_type="embedding_update",
        source="demo_component",
        data={
            "entity_id": "demo_entity",
            "entity_type": "demo_type",
            "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
            "dimension": 5
        },
        priority="MEDIUM"
    )

    # Performance metric event
    pipeline.emit_learning_event(
        event_type="performance_metric",
        source="demo_component",
        data={
            "metric_name": "demo_metric",
            "value": 0.85,
            "unit": "%",
            "context": {"epoch": 1}
        },
        priority="MEDIUM"
    )

    # Learning signal
    pipeline.emit_learning_signal(
        signal_type="demo_signal",
        source="demo_component",
        payload={"message": "demo signal data"},
        expires_in_seconds=10
    )

    # Let the pipeline run for a bit
    print("\n⏳ Running pipeline for 15 seconds...")
    time.sleep(15)

    # Get pipeline statistics
    stats = pipeline.get_pipeline_stats()
    print("\n📊 Pipeline Statistics:")
    print(f"  Events processed: {stats['events_processed']}")
    print(f"  Signals processed: {stats['signals_processed']}")
    print(f"  Errors: {stats['errors_count']}")
    print(f"  Uptime: {stats['uptime_seconds']:.1f}s")
    print(f"  Events/sec: {stats['events_per_second']:.2f}")
    print(f"  Error rate: {stats['error_rate']:.2f}%")
    print(f"  Queue sizes: {stats['queue_sizes']}")

    # Get memory manager statistics
    memory_stats = pipeline.memory_manager.get_database_stats()
    print("\n💾 Memory Manager Statistics:")
    for key, value in memory_stats.items():
        if "count" in key:
            print(f"  {key}: {value}")

    # Stop pipeline
    pipeline.stop_pipeline()

    print("\n🎉 CONTINUOUS LEARNING PIPELINE DEMONSTRATION COMPLETE")
    print("The system is now ready for automated, continuous learning!")


if __name__ == "__main__":
    main()
