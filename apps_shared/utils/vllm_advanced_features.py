"""VLLM Advanced Features - Batch Processing and Analytics.

This module provides advanced vLLM capabilities including batch processing,
performance analytics, and multi-model support.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

# guardian: allow-silent-degradation -- Qwen vLLM is optional for advanced features; graceful fallback to disabled state
try:
    from apps_qwen import (
        AppsQwenGateway,
        AppsQwenInferenceWorker,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )
    from apps_qwen.apps_qwen_config import (
        AppsQwenModelConfig,
        AppsQwenPromptConfig,
    )

    _QWEN_AVAILABLE = True
except ImportError:
    AppsQwenGateway = None  # type: ignore[assignment]
    AppsQwenRequest = None  # type: ignore[assignment]
    AppsQwenInferenceWorker = None  # type: ignore[assignment]
    apps_qwen_telemetry = None  # type: ignore[assignment]
    AppsQwenModelConfig = None  # type: ignore[assignment]
    AppsQwenPromptConfig = None  # type: ignore[assignment]
    _QWEN_AVAILABLE = False

_log = logging.getLogger(__name__)


@dataclass
class BatchRequest:
    """Individual request in a batch processing operation."""

    id: str
    prompt: str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    max_tokens: int | None = None
    temperature: float | None = None


@dataclass
class BatchResult:
    """Result of a batch processing operation."""

    batch_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency_ms: float
    average_confidence: float
    results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class PerformanceMetrics:
    """Performance metrics for vLLM operations."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    average_confidence: float = 0.0
    total_tokens_used: int = 0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    model_usage: dict[str, int] = field(default_factory=dict)
    app_usage: dict[str, int] = field(default_factory=dict)


class VLLMBatchProcessor:
    """Advanced batch processing for vLLM operations."""

    def __init__(self, app_name: str, max_concurrent_requests: int = 5):
        """Initialize batch processor.

        Args:
            app_name: Name of the application
            max_concurrent_requests: Maximum concurrent requests
        """
        self.app_name = app_name
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        if _QWEN_AVAILABLE:
            self._gateway = AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")
            if apps_qwen_telemetry is not None:
                self._session_id = apps_qwen_telemetry.start_session(f"{app_name}_batch")
            else:
                self._session_id = None
        else:
            self._gateway = None
            self._session_id = None

    async def process_batch(self, requests: list[BatchRequest], batch_id: str | None = None) -> BatchResult:
        """Process a batch of vLLM requests.

        Args:
            requests: List of batch requests
            batch_id: Optional batch identifier

        Returns:
            Batch processing results
        """
        if not self._gateway:
            raise RuntimeError("vLLM gateway not available")

        batch_id = batch_id or f"batch_{int(time.time())}"
        start_time = time.time()

        # Validate batch requests
        if not requests:
            return BatchResult(
                batch_id=batch_id,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_latency_ms=0.0,
                average_confidence=0.0,
                results=[],
                errors=[{"error": "empty_batch"}],
                processing_time_seconds=time.time() - start_time,
            )

        # Validate individual requests
        for request in requests:
            if not request.id or not request.prompt:
                return BatchResult(
                    batch_id=batch_id,
                    total_requests=len(requests),
                    successful_requests=0,
                    failed_requests=len(requests),
                    average_latency_ms=0.0,
                    average_confidence=0.0,
                    results=[],
                    errors=[{"request_id": request.id, "error": "invalid_request"}],
                    processing_time_seconds=time.time() - start_time,
                )

        _log.info(f"Starting batch processing for {len(requests)} requests (batch_id: {batch_id})")

        # Process requests concurrently with rate limiting
        tasks = []
        for request in requests:
            task = self._process_single_request(request, batch_id)
            tasks.append(task)

        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        successful_results = []
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(
                    {"request_id": requests[i].id, "error": str(result), "metadata": requests[i].metadata}
                )
            elif result.get("success", False):
                successful_results.append(result)
            else:
                errors.append(
                    {
                        "request_id": requests[i].id,
                        "error": result.get("error", "Unknown error"),
                        "metadata": requests[i].metadata,
                    }
                )

        processing_time = time.time() - start_time

        # Calculate metrics
        total_requests = len(requests)
        successful_count = len(successful_results)
        failed_count = len(errors)

        avg_latency = sum(r.get("latency_ms", 0) for r in successful_results) / max(successful_count, 1)
        avg_confidence = sum(r.get("confidence", 0) for r in successful_results) / max(successful_count, 1)

        batch_result = BatchResult(
            batch_id=batch_id,
            total_requests=total_requests,
            successful_requests=successful_count,
            failed_requests=failed_count,
            average_latency_ms=avg_latency,
            average_confidence=avg_confidence,
            results=successful_results,
            errors=errors,
            processing_time_seconds=processing_time,
        )

        _log.info(
            f"Batch processing completed: {successful_count}/{total_requests} successful in {processing_time:.2f}s"
        )

        return batch_result

    async def _process_single_request(self, request: BatchRequest, batch_id: str) -> dict[str, Any]:
        """Process a single request with rate limiting."""
        async with self.semaphore:
            try:
                # Create Qwen request
                qwen_request = AppsQwenRequest(
                    app_name=self.app_name,
                    prompt=request.prompt,
                    confidence_threshold=request.confidence_threshold,
                    max_tokens=request.max_tokens or 2048,
                    temperature=request.temperature or 0.3,
                )

                # Record telemetry start
                if apps_qwen_telemetry is not None and self._session_id is not None:
                    apps_qwen_telemetry.record_request_start(
                        session_id=self._session_id,
                        app_name=self.app_name,
                        model_id="Qwen/Qwen2.5-7B-Instruct",
                    )

                # Perform inference
                response = await self._gateway.infer(qwen_request)

                # Record telemetry result
                if apps_qwen_telemetry is not None and self._session_id is not None:
                    if response.success:
                        apps_qwen_telemetry.record_request_success(
                            session_id=self._session_id,
                            app_name=self.app_name,
                            model_id=response.model_used,
                            latency_ms=response.latency_ms,
                            confidence=response.confidence,
                            tokens_used=len(request.prompt.split()) + len(response.response.split())
                            if response.response
                            else 0,
                        )
                    else:
                        apps_qwen_telemetry.record_request_error(
                            session_id=self._session_id,
                            app_name=self.app_name,
                            model_id=response.model_used,
                            error_message=response.error_message or "unknown_error",
                        )

                # Build result
                result = {
                    "request_id": request.id,
                    "batch_id": batch_id,
                    "success": response.success,
                    "content": response.response,
                    "confidence": response.confidence,
                    "model_used": response.model_used,
                    "latency_ms": response.latency_ms,
                    "error_message": response.error_message,
                    "metadata": request.metadata,
                }

                return result

            except Exception as e:
                _log.error(f"Request {request.id} failed: {e}")
                return {
                    "request_id": request.id,
                    "batch_id": batch_id,
                    "success": False,
                    "error": str(e),
                    "metadata": request.metadata,
                }


class VLLMAnalytics:
    """Analytics and monitoring for vLLM operations."""

    def __init__(self):
        """Initialize analytics collector."""
        self.metrics = PerformanceMetrics()
        self.request_history: list[dict[str, Any]] = []
        self.batch_history: list[BatchResult] = []

    def record_request(self, request_result: dict[str, Any]) -> None:
        """Record a single request result.

        Args:
            request_result: Result from vLLM request
        """
        self.metrics.total_requests += 1

        if request_result.get("success", False):
            self.metrics.successful_requests += 1
            self.metrics.average_latency_ms = (
                self.metrics.average_latency_ms * (self.metrics.successful_requests - 1)
                + request_result.get("latency_ms", 0)
            ) / self.metrics.successful_requests
            self.metrics.average_confidence = (
                self.metrics.average_confidence * (self.metrics.successful_requests - 1)
                + request_result.get("confidence", 0)
            ) / self.metrics.successful_requests

            # Track model usage
            model = request_result.get("model_used", "unknown")
            self.metrics.model_usage[model] = self.metrics.model_usage.get(model, 0) + 1

            # Track token usage
            if "content" in request_result and request_result["content"]:
                self.metrics.total_tokens_used += len(request_result["content"].split())
        else:
            self.metrics.failed_requests += 1

        # Track app usage
        app_name = request_result.get("app_name", "unknown")
        self.metrics.app_usage[app_name] = self.metrics.app_usage.get(app_name, 0) + 1

        # Update error rate
        self.metrics.error_rate = self.metrics.failed_requests / max(self.metrics.total_requests, 1)

        # Store in history
        request_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.request_history.append(request_result)

        # Keep history manageable (last 1000 requests)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    def record_batch(self, batch_result: BatchResult) -> None:
        """Record batch processing results.

        Args:
            batch_result: Result from batch processing
        """
        self.batch_history.append(batch_result)

        # Update metrics
        self.metrics.total_requests += batch_result.total_requests
        self.metrics.successful_requests += batch_result.successful_requests
        self.metrics.failed_requests += batch_result.failed_requests

        # Update error rate
        self.metrics.error_rate = self.metrics.failed_requests / max(self.metrics.total_requests, 1)

        # Keep history manageable (last 100 batches)
        if len(self.batch_history) > 100:
            self.batch_history = self.batch_history[-100:]

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary.

        Returns:
            Performance summary dictionary
        """
        # Calculate requests per second
        if self.request_history:
            time_span = len(self.request_history)  # Simplified - could use actual timestamps
            self.metrics.requests_per_second = self.metrics.total_requests / max(time_span, 1)

        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": (self.metrics.successful_requests / max(self.metrics.total_requests, 1)) * 100,
            "error_rate": self.metrics.error_rate * 100,
            "average_latency_ms": self.metrics.average_latency_ms,
            "average_confidence": self.metrics.average_confidence,
            "total_tokens_used": self.metrics.total_tokens_used,
            "requests_per_second": self.metrics.requests_per_second,
            "model_usage": dict(self.metrics.model_usage),
            "app_usage": dict(self.metrics.app_usage),
            "recent_batches": len(self.batch_history),
            "recent_requests": len(self.request_history),
        }

    def export_analytics(self, filepath: str) -> None:
        """Export analytics data to file.

        Args:
            filepath: Path to export file
        """
        analytics_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "performance_metrics": self.get_performance_summary(),
            "request_history": self.request_history[-100:],  # Last 100 requests
            "batch_history": self.batch_history[-20:],  # Last 20 batches
        }

        with open(filepath, "w") as f:
            json.dump(analytics_data, f, indent=2)

        _log.info(f"Analytics exported to {filepath}")


class MultiModelManager:
    """Multi-model vLLM management for advanced use cases."""

    def __init__(self):
        """Initialize multi-model manager."""
        self.models: dict[str, AppsQwenGateway] = {}
        self.model_configs: dict[str, dict[str, Any]] = {}

        if _QWEN_AVAILABLE:
            self._initialize_default_models()

    def _initialize_default_models(self) -> None:
        """Initialize default model configurations."""
        default_models = {
            "qwen-7b": {
                "model_id": "Qwen/Qwen2.5-7B-Instruct",
                "max_tokens": 2048,
                "temperature": 0.3,
                "description": "General purpose model",
            },
            "qwen-7b-creative": {
                "model_id": "Qwen/Qwen2.5-7B-Instruct",
                "max_tokens": 3072,
                "temperature": 0.7,
                "description": "Creative content generation",
            },
            "qwen-7b-analytical": {
                "model_id": "Qwen/Qwen2.5-7B-Instruct",
                "max_tokens": 2048,
                "temperature": 0.1,
                "description": "Analytical and technical tasks",
            },
        }

        for model_name, config in default_models.items():
            self.add_model(model_name, config)

    def add_model(self, model_name: str, config: dict[str, Any]) -> None:
        """Add a new model configuration.

        Args:
            model_name: Name for the model
            config: Model configuration
        """
        if not _QWEN_AVAILABLE:
            _log.warning("Cannot add model: Qwen not available")
            return

        try:
            gateway = AppsQwenGateway(model_id=config["model_id"])
            self.models[model_name] = gateway
            self.model_configs[model_name] = config
            _log.info(f"Added model: {model_name}")
        except Exception as e:
            _log.error(f"Failed to add model {model_name}: {e}")

    def get_model(self, model_name: str) -> AppsQwenGateway | None:
        """Get a model by name.

        Args:
            model_name: Name of the model

        Returns:
            Model gateway or None if not found
        """
        return self.models.get(model_name)

    def list_models(self) -> dict[str, dict[str, Any]]:
        """List all available models.

        Returns:
            Dictionary of model configurations
        """
        return dict(self.model_configs)

    async def generate_with_model(self, model_name: str, prompt: str, **kwargs) -> dict[str, Any]:
        """Generate content using a specific model.

        Args:
            model_name: Name of the model to use
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Generation result
        """
        gateway = self.get_model(model_name)
        if not gateway:
            return {"success": False, "error": f"Model {model_name} not available", "content": None}

        try:
            config = self.model_configs.get(model_name, {})

            request = AppsQwenRequest(
                app_name="multimodel",
                prompt=prompt,
                confidence_threshold=kwargs.get("confidence_threshold", 0.7),
                max_tokens=kwargs.get("max_tokens", config.get("max_tokens", 2048)),
                temperature=kwargs.get("temperature", config.get("temperature", 0.3)),
            )

            response = await gateway.infer(request)

            return {
                "success": response.success,
                "content": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "model_name": model_name,
                "latency_ms": response.latency_ms,
                "error_message": response.error_message,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"generation_failed: {str(e)}",
                "content": None,
                "model_name": model_name,
            }


# Global instances for shared usage
_global_analytics = VLLMAnalytics()
_global_multimodel = MultiModelManager()


def get_analytics() -> VLLMAnalytics:
    """Get global analytics instance."""
    return _global_analytics


def get_multimodel_manager() -> MultiModelManager:
    """Get global multi-model manager."""
    return _global_multimodel
