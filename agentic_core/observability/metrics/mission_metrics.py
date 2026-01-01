# mission_metrics.py
# Prometheus Metrics for Canon Validator Mission
# PURPOSE: Provides Metric definitions and server initialization for mission observability
# LOCATION: agentic_core/observability/metrics/ (SSOT-compliant)

import os
from typing import Any


# Attempt to load prometheus_client, provide null fallback if unavailable
try:
    from prometheus_client import Counter, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class NullMetric:
    """
    Comprehensive dummy Metric to prevent ANY AttributeError downstream.
    Used when prometheus_client is not available.
    """
    def __getattr__(self, name: str) -> Any:
        def noop(*args, **kwargs):
            return self
        return noop


def initialize_metrics(verbose: bool = True) -> dict:
    """
    Initialize Prometheus metrics for the Canon Validator mission.
    
    Args:
        verbose: Whether to print status messages
        
    Returns:
        Dictionary containing all Metric objects:
        - violations_total: Counter for structural violations
        - healing_attempts: Counter for healing attempts by agent
        - agent_failures: Counter for agent execution failures
        - active_files: Gauge for files currently under processing
    """
    if PROMETHEUS_AVAILABLE:
        # Define metrics with minimal labels to reduce cardinality
        violations_total = Counter(
            'canon_violations_total', 
            'Total structural violations detected', 
            ['type']
        )
        healing_attempts = Counter(
            'canon_healing_attempts_total', 
            'Healing attempts by agent', 
            ['agent', 'outcome']
        )
        agent_failures = Counter(
            'canon_agent_failures_total', 
            'Agent execution failures', 
            ['agent']
        )
        active_files = Gauge(
            'canon_active_files', 
            'Number of files currently under active processing'
        )

        metrics_port = int(os.getenv('PROMETHEUS_PORT', '8000'))
        enabled = os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true'
        
        if enabled:
            try:
                start_http_server(metrics_port)
                if verbose:
                    print(f"   [OK] Prometheus metrics server started -> http://localhost:{metrics_port}/metrics")
            except Exception as e:
                if verbose:
                    print(f"   [!] Prometheus server failed to start: {e}")
        else:
            if verbose:
                print("   [INFO] Prometheus metrics disabled - set PROMETHEUS_ENABLED=true to enable")
        
        return {
            "violations_total": violations_total,
            "healing_attempts": healing_attempts,
            "agent_failures": agent_failures,
            "active_files": active_files,
            "available": True
        }
    else:
        if verbose:
            print("   [INFO] prometheus_client not available - running with null metrics")
        
        null_metric = NullMetric()
        return {
            "violations_total": null_metric,
            "healing_attempts": null_metric,
            "agent_failures": null_metric,
            "active_files": null_metric,
            "available": False
        }


# Default metrics instance (lazy initialization)
_default_metrics = None


def get_metrics(verbose: bool = False) -> dict:
    """
    Get the default metrics instance, initializing if necessary.
    
    Args:
        verbose: Whether to print status messages on first initialization
        
    Returns:
        Dictionary containing all Metric objects
    """
    global _default_metrics
    if _default_metrics is None:
        _default_metrics = initialize_metrics(verbose=verbose)
    return _default_metrics
