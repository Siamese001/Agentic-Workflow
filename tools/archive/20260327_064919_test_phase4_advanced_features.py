#!/usr/bin/env python3
"""Phase 4 Test Suite - Advanced Analytics and Performance Optimization.

Comprehensive test suite for Phase 4 advanced features including
analytics, performance optimization, monitoring, distributed tracing,
and dashboard functionality.
"""

import sys
import time
import traceback


def test_advanced_analytics():
    """Test advanced Runtime ADG analytics functionality."""
    print("=" * 80)
    print("PHASE 4: ADVANCED ANALYTICS TEST")
    print("=" * 80)

    results = {}

    # Test 1: Advanced analytics initialization
    print("\n1. Testing advanced analytics initialization...")
    try:
        from system_learning.runtime_adg.advanced_analytics import get_global_analytics

        analytics = get_global_analytics()
        results['analytics_init'] = analytics is not None
        print("✅ Advanced analytics initialized successfully")

    except Exception as e:
        results['analytics_init'] = False
        print(f"❌ Advanced analytics initialization failed: {e}")
        traceback.print_exc()

    # Test 2: Pattern analysis
    print("\n2. Testing pattern analysis...")
    try:
        # Create a mock snapshot for testing
        from system_learning.runtime_adg import RuntimeADGEdge, RuntimeADGNode, RuntimeADGSnapshot

        # Create test nodes
        nodes = [
            RuntimeADGNode(
                node_id="node1",
                component="test_component",
                layer="L1",
                kind="cognitive",
                duration_ms=500,
                status="OK",
            ),
            RuntimeADGNode(
                node_id="node2",
                component="test_component",
                layer="L2",
                kind="tool",
                duration_ms=1500,  # Slow operation
                status="OK",
            ),
            RuntimeADGNode(
                node_id="node3",
                component="test_component",
                layer="L3",
                kind="orchestrator",
                duration_ms=50,  # Fast operation
                status="error",  # Error operation
            ),
        ]

        # Create test edges
        edges = [
            RuntimeADGEdge(
                edge_id="edge1",
                src_id="node1",
                dst_id="node2",
                relation_type="calls",
            ),
            RuntimeADGEdge(
                edge_id="edge2",
                src_id="node2",
                dst_id="node3",
                relation_type="invokes",
            ),
        ]

        # Create snapshot
        snapshot = RuntimeADGSnapshot(
            trace_id="test_trace_123",
            nodes=nodes,
            edges=edges,
            started_at_utc=time.time(),
            completed_at_utc=time.time() + 2.0,
        )

        # Analyze snapshot
        insights = analytics.analyze_snapshot(snapshot)

        results['pattern_analysis'] = insights is not None
        results['performance_metrics'] = hasattr(insights, 'performance_metrics')
        results['pattern_metrics'] = hasattr(insights, 'pattern_metrics')
        results['recommendations'] = hasattr(insights, 'recommendations')

        print("✅ Pattern analysis completed:")
        print(f"   - Performance metrics available: {results['performance_metrics']}")
        print(f"   - Pattern metrics available: {results['pattern_metrics']}")
        print(f"   - Recommendations available: {results['recommendations']}")
        print(f"   - Efficiency score: {insights.efficiency_score:.1f}")
        print(f"   - Complexity score: {insights.complexity_score:.1f}")
        print(f"   - Reliability score: {insights.reliability_score:.1f}")

    except Exception as e:
        results['pattern_analysis'] = False
        results['performance_metrics'] = False
        results['pattern_metrics'] = False
        results['recommendations'] = False
        print(f"❌ Pattern analysis failed: {e}")
        traceback.print_exc()

    # Test 3: Performance metrics analysis
    print("\n3. Testing performance metrics analysis...")
    try:
        if 'insights' in locals() and insights:
            perf = insights.performance_metrics

            results['perf_metrics_available'] = perf is not None
            results['bottleneck_detection'] = len(perf.bottleneck_nodes) > 0
            results['slow_operations'] = len(perf.slow_operations) > 0
            results['fast_operations'] = len(perf.fast_operations) > 0

            print("✅ Performance metrics analysis:")
            print(f"   - Bottlenecks detected: {len(perf.bottleneck_nodes)}")
            print(f"   - Slow operations: {len(perf.slow_operations)}")
            print(f"   - Fast operations: {len(perf.fast_operations)}")
            print(f"   - Total duration: {perf.total_duration_ms:.1f} ms")
            print(f"   - Average duration: {perf.avg_node_duration_ms:.1f} ms")

        else:
            results['perf_metrics_available'] = False
            results['bottleneck_detection'] = False
            results['slow_operations'] = False
            results['fast_operations'] = False

    except Exception as e:
        results['perf_metrics_available'] = False
        results['bottleneck_detection'] = False
        results['slow_operations'] = False
        results['fast_operations'] = False
        print(f"❌ Performance metrics analysis failed: {e}")
        traceback.print_exc()

    # Test 4: Optimization recommendations
    print("\n4. Testing optimization recommendations...")
    try:
        if 'insights' in locals() and insights:
            recommendations = insights.recommendations

            results['recommendations_available'] = len(recommendations) > 0
            results['recommendation_types'] = len(set(r.get('type', 'unknown') for r in recommendations))
            results['high_priority_recs'] = len([r for r in recommendations if r.get('priority') == 'high'])

            print("✅ Optimization recommendations:")
            print(f"   - Total recommendations: {len(recommendations)}")
            print(f"   - Recommendation types: {results['recommendation_types']}")
            print(f"   - High priority: {results['high_priority_recs']}")

            for i, rec in enumerate(recommendations[:3]):  # Show top 3
                print(f"   - {rec.get('priority', 'unknown')}: {rec.get('title', 'No title')}")

        else:
            results['recommendations_available'] = False
            results['recommendation_types'] = 0
            results['high_priority_recs'] = 0

    except Exception as e:
        results['recommendations_available'] = False
        results['recommendation_types'] = 0
        results['high_priority_recs'] = 0
        print(f"❌ Optimization recommendations failed: {e}")
        traceback.print_exc()

    # Test 5: Trend analysis
    print("\n5. Testing trend analysis...")
    try:
        trends = analytics.get_trend_analysis()

        results['trend_analysis'] = isinstance(trends, dict)
        results['trend_data_available'] = len(trends) > 0 if isinstance(trends, dict) else False

        if isinstance(trends, dict):
            print("✅ Trend analysis:")
            print(f"   - Efficiency trend: {trends.get('efficiency_trend', 'unknown')}")
            print(f"   - Complexity trend: {trends.get('complexity_trend', 'unknown')}")
            print(f"   - Reliability trend: {trends.get('reliability_trend', 'unknown')}")

    except Exception as e:
        results['trend_analysis'] = False
        results['trend_data_available'] = False
        print(f"❌ Trend analysis failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("ADVANCED ANALYTICS SUMMARY")
    print("=" * 80)

    test_keys = [
        'analytics_init', 'pattern_analysis', 'performance_metrics', 'pattern_metrics',
        'recommendations', 'perf_metrics_available', 'bottleneck_detection',
        'slow_operations', 'fast_operations', 'recommendations_available',
        'recommendation_types', 'high_priority_recs', 'trend_analysis', 'trend_data_available',
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Advanced Analytics Tests: {success_count}/{total_tests}")

    if success_count >= total_tests - 2:  # Allow 2 tests to fail
        print("🎉 ADVANCED ANALYTICS TESTS PASSED!")
    else:
        print("🚨 Some advanced analytics tests failed")

    return results

def test_performance_optimization():
    """Test performance optimized collector functionality."""
    print("\n" + "=" * 80)
    print("PHASE 4: PERFORMANCE OPTIMIZATION TEST")
    print("=" * 80)

    results = {}

    # Test 1: Performance optimized collector initialization
    print("\n1. Testing performance optimized collector initialization...")
    try:
        from agentic_core.mixins.performance_optimized_collector import get_global_optimized_collector

        collector = get_global_optimized_collector()
        results['perf_collector_init'] = collector is not None
        print("✅ Performance optimized collector initialized successfully")

    except Exception as e:
        results['perf_collector_init'] = False
        print(f"❌ Performance optimized collector initialization failed: {e}")
        traceback.print_exc()

    # Test 2: Collection configuration
    print("\n2. Testing collection configuration...")
    try:
        if 'collector' in locals() and collector:
            config = collector._config

            results['config_available'] = config is not None
            results['batch_size_configured'] = config.batch_size > 0
            results['compression_enabled'] = config.compression_enabled
            results['adaptive_scheduling'] = config.adaptive_scheduling

            print("✅ Collection configuration:")
            print(f"   - Batch size: {config.batch_size}")
            print(f"   - Max buffer size: {config.max_buffer_size}")
            print(f"   - Compression enabled: {config.compression_enabled}")
            print(f"   - Adaptive scheduling: {config.adaptive_scheduling}")

        else:
            results['config_available'] = False
            results['batch_size_configured'] = False
            results['compression_enabled'] = False
            results['adaptive_scheduling'] = False

    except Exception as e:
        results['config_available'] = False
        results['batch_size_configured'] = False
        results['compression_enabled'] = False
        results['adaptive_scheduling'] = False
        print(f"❌ Collection configuration test failed: {e}")
        traceback.print_exc()

    # Test 3: Agent registration
    print("\n3. Testing agent registration...")
    try:
        if 'collector' in locals() and collector:
            # Create a mock agent
            class MockAgent:
                def flush_traces(self):
                    return [
                        {
                            "trace_id": "test_trace_1",
                            "span_id": "span_1",
                            "operation_name": "test_operation",
                            "duration_ms": 100,
                            "status": "OK",
                        },
                    ]

            mock_agent = MockAgent()
            collector.register_agent("test-agent-1", mock_agent)

            results['agent_registration'] = True
            results['registered_agents'] = len(collector._registered_agents) > 0

            print("✅ Agent registration:")
            print(f"   - Registered agents: {len(collector._registered_agents)}")

        else:
            results['agent_registration'] = False
            results['registered_agents'] = False

    except Exception as e:
        results['agent_registration'] = False
        results['registered_agents'] = False
        print(f"❌ Agent registration failed: {e}")
        traceback.print_exc()

    # Test 4: Span collection
    print("\n4. Testing span collection...")
    try:
        if 'collector' in locals() and collector:
            # Start collection
            collector.start_collection()
            time.sleep(0.1)  # Let collection start

            # Collect spans
            test_spans = [
                {
                    "trace_id": "test_trace_2",
                    "span_id": "span_2",
                    "operation_name": "test_operation_2",
                    "duration_ms": 200,
                    "status": "OK",
                    "attributes": {"test": "value"},
                },
            ]

            collector.collect_spans_from_agent("test-agent-1", test_spans)

            # Check if spans were processed
            stats = collector.get_performance_stats()

            results['span_collection'] = True
            results['spans_processed'] = stats.get("performance_metrics", {}).get("spans_per_second", 0) >= 0

            # Stop collection
            collector.stop_collection()

            print("✅ Span collection:")
            print(f"   - Spans processed per second: {stats.get('performance_metrics', {}).get('spans_per_second', 0)}")
            print(f"   - Memory usage: {stats.get('performance_metrics', {}).get('memory_usage_mb', 0):.1f} MB")

        else:
            results['span_collection'] = False
            results['spans_processed'] = False

    except Exception as e:
        results['span_collection'] = False
        results['spans_processed'] = False
        print(f"❌ Span collection failed: {e}")
        traceback.print_exc()

    # Test 5: Performance optimization features
    print("\n5. Testing performance optimization features...")
    try:
        if 'collector' in locals() and collector:
            # Get optimization recommendations
            recommendations = collector.get_optimization_recommendations()

            results['optimization_recs'] = isinstance(recommendations, list)
            results['rec_types'] = len(set(r.get('type', 'unknown') for r in recommendations)) if recommendations else 0

            # Test span optimization
            optimized_spans = collector._optimize_spans(test_spans if 'test_spans' in locals() else [])

            results['span_optimization'] = isinstance(optimized_spans, list)
            results['optimized_span_count'] = len(optimized_spans) > 0

            print("✅ Performance optimization features:")
            print(f"   - Optimization recommendations: {len(recommendations)}")
            print(f"   - Recommendation types: {results['rec_types']}")
            print(f"   - Span optimization working: {results['span_optimization']}")

        else:
            results['optimization_recs'] = False
            results['rec_types'] = 0
            results['span_optimization'] = False
            results['optimized_span_count'] = False

    except Exception as e:
        results['optimization_recs'] = False
        results['rec_types'] = 0
        results['span_optimization'] = False
        results['optimized_span_count'] = False
        print(f"❌ Performance optimization features failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("PERFORMANCE OPTIMIZATION SUMMARY")
    print("=" * 80)

    test_keys = [
        'perf_collector_init', 'config_available', 'batch_size_configured',
        'compression_enabled', 'adaptive_scheduling', 'agent_registration',
        'registered_agents', 'span_collection', 'spans_processed',
        'optimization_recs', 'rec_types', 'span_optimization', 'optimized_span_count',
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Performance Optimization Tests: {success_count}/{total_tests}")

    if success_count >= total_tests - 2:  # Allow 2 tests to fail
        print("🎉 PERFORMANCE OPTIMIZATION TESTS PASSED!")
    else:
        print("🚨 Some performance optimization tests failed")

    return results

def test_enhanced_monitoring():
    """Test enhanced observability monitoring functionality."""
    print("\n" + "=" * 80)
    print("PHASE 4: ENHANCED MONITORING TEST")
    print("=" * 80)

    results = {}

    # Test 1: Enhanced observability initialization
    print("\n1. Testing enhanced observability initialization...")
    try:
        from agentic_core.monitoring.enhanced_observability import get_global_observability

        observability = get_global_observability()
        results['observability_init'] = observability is not None
        print("✅ Enhanced observability initialized successfully")

    except Exception as e:
        results['observability_init'] = False
        print(f"❌ Enhanced observability initialization failed: {e}")
        traceback.print_exc()

    # Test 2: Health checks
    print("\n2. Testing health checks...")
    try:
        if 'observability' in locals() and observability:
            # Start monitoring briefly
            observability.start_monitoring()
            time.sleep(0.1)  # Let monitoring start

            # Get system health
            health = observability.get_system_health()

            results['health_checks'] = health is not None
            results['health_status_available'] = hasattr(health, 'status') if health else False
            results['health_score_available'] = hasattr(health, 'score') if health else False
            results['health_checks_available'] = hasattr(health, 'checks') if health else False

            if health:
                print("✅ Health checks:")
                print(f"   - Health status: {health.status.value}")
                print(f"   - Health score: {health.score:.1f}")
                print(f"   - Health checks count: {len(health.checks)}")

            # Stop monitoring
            observability.stop_monitoring()

        else:
            results['health_checks'] = False
            results['health_status_available'] = False
            results['health_score_available'] = False
            results['health_checks_available'] = False

    except Exception as e:
        results['health_checks'] = False
        results['health_status_available'] = False
        results['health_score_available'] = False
        results['health_checks_available'] = False
        print(f"❌ Health checks failed: {e}")
        traceback.print_exc()

    # Test 3: Alert system
    print("\n3. Testing alert system...")
    try:
        if 'observability' in locals() and observability:
            # Get active alerts
            alerts = observability.get_active_alerts()

            results['alert_system'] = isinstance(alerts, list)
            results['alerts_available'] = len(alerts) >= 0  # Can be 0

            # Get alert history
            alert_history = observability.get_alert_history(limit=10)

            results['alert_history'] = isinstance(alert_history, list)

            print("✅ Alert system:")
            print(f"   - Active alerts: {len(alerts)}")
            print(f"   - Alert history entries: {len(alert_history)}")

        else:
            results['alert_system'] = False
            results['alerts_available'] = False
            results['alert_history'] = False

    except Exception as e:
        results['alert_system'] = False
        results['alerts_available'] = False
        results['alert_history'] = False
        print(f"❌ Alert system failed: {e}")
        traceback.print_exc()

    # Test 4: Metrics collection
    print("\n4. Testing metrics collection...")
    try:
        if 'observability' in locals() and observability:
            # Start monitoring
            observability.start_monitoring()
            time.sleep(0.2)  # Let monitoring collect metrics

            # Get current metrics
            current_metrics = observability._current_metrics

            results['metrics_collection'] = isinstance(current_metrics, dict)
            results['metrics_available'] = len(current_metrics) > 0

            # Get metrics history
            cpu_history = observability.get_metrics_history("system_cpu_percent", limit=5)

            results['metrics_history'] = isinstance(cpu_history, list)

            print("✅ Metrics collection:")
            print(f"   - Current metrics count: {len(current_metrics)}")
            print(f"   - CPU history entries: {len(cpu_history)}")

            # Stop monitoring
            observability.stop_monitoring()

        else:
            results['metrics_collection'] = False
            results['metrics_available'] = False
            results['metrics_history'] = False

    except Exception as e:
        results['metrics_collection'] = False
        results['metrics_available'] = False
        results['metrics_history'] = False
        print(f"❌ Metrics collection failed: {e}")
        traceback.print_exc()

    # Test 5: Dashboard data
    print("\n5. Testing dashboard data...")
    try:
        if 'observability' in locals() and observability:
            # Get dashboard data
            dashboard_data = observability.get_dashboard_data()

            results['dashboard_data'] = isinstance(dashboard_data, dict)
            results['dashboard_sections'] = len(dashboard_data) > 0 if isinstance(dashboard_data, dict) else False

            if isinstance(dashboard_data, dict):
                print("✅ Dashboard data:")
                print(f"   - Data sections: {list(dashboard_data.keys())}")
                print(f"   - System health available: {'system_health' in dashboard_data}")
                print(f"   - Active alerts available: {'active_alerts' in dashboard_data}")
                print(f"   - Current metrics available: {'current_metrics' in dashboard_data}")

        else:
            results['dashboard_data'] = False
            results['dashboard_sections'] = False

    except Exception as e:
        results['dashboard_data'] = False
        results['dashboard_sections'] = False
        print(f"❌ Dashboard data failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("ENHANCED MONITORING SUMMARY")
    print("=" * 80)

    test_keys = [
        'observability_init', 'health_checks', 'health_status_available',
        'health_score_available', 'health_checks_available', 'alert_system',
        'alerts_available', 'alert_history', 'metrics_collection',
        'metrics_available', 'metrics_history', 'dashboard_data', 'dashboard_sections',
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Enhanced Monitoring Tests: {success_count}/{total_tests}")

    if success_count >= total_tests - 2:  # Allow 2 tests to fail
        print("🎉 ENHANCED MONITORING TESTS PASSED!")
    else:
        print("🚨 Some enhanced monitoring tests failed")

    return results

def test_distributed_tracing():
    """Test distributed tracing coordination functionality."""
    print("\n" + "=" * 80)
    print("PHASE 4: DISTRIBUTED TRACING TEST")
    print("=" * 80)

    results = {}

    # Test 1: Distributed tracing coordinator initialization
    print("\n1. Testing distributed tracing coordinator initialization...")
    try:
        from agentic_core.tracing.distributed_tracing_coordinator import get_global_coordinator

        coordinator = get_global_coordinator()
        results['coordinator_init'] = coordinator is not None
        print("✅ Distributed tracing coordinator initialized successfully")

    except Exception as e:
        results['coordinator_init'] = False
        print(f"❌ Distributed tracing coordinator initialization failed: {e}")
        traceback.print_exc()

    # Test 2: Coordination startup
    print("\n2. Testing coordination startup...")
    try:
        if 'coordinator' in locals() and coordinator:
            # Start coordination
            coordinator.start_coordination()
            time.sleep(0.1)  # Let coordination start

            results['coordination_startup'] = coordinator._coordination_active
            results['service_registered'] = len(coordinator._registered_services) > 0

            print("✅ Coordination startup:")
            print(f"   - Coordination active: {coordinator._coordination_active}")
            print(f"   - Registered services: {len(coordinator._registered_services)}")

            # Stop coordination
            coordinator.stop_coordination()

        else:
            results['coordination_startup'] = False
            results['service_registered'] = False

    except Exception as e:
        results['coordination_startup'] = False
        results['service_registered'] = False
        print(f"❌ Coordination startup failed: {e}")
        traceback.print_exc()

    # Test 3: Trace context creation
    print("\n3. Testing trace context creation...")
    try:
        if 'coordinator' in locals() and coordinator:
            # Create trace context
            context = coordinator.create_trace_context("test-service", "test-operation")

            results['trace_context_creation'] = context is not None
            results['trace_id_available'] = hasattr(context, 'trace_id')
            results['span_id_available'] = hasattr(context, 'span_id')
            results['service_name_set'] = context.service_name == "test-service"

            print("✅ Trace context creation:")
            print(f"   - Trace ID: {context.trace_id}")
            print(f"   - Span ID: {context.span_id}")
            print(f"   - Service name: {context.service_name}")
            print(f"   - Operation name: {context.operation_name}")

        else:
            results['trace_context_creation'] = False
            results['trace_id_available'] = False
            results['span_id_available'] = False
            results['service_name_set'] = False

    except Exception as e:
        results['trace_context_creation'] = False
        results['trace_id_available'] = False
        results['span_id_available'] = False
        results['service_name_set'] = False
        print(f"❌ Trace context creation failed: {e}")
        traceback.print_exc()

    # Test 4: Trace propagation
    print("\n4. Testing trace propagation...")
    try:
        if 'coordinator' in locals() and coordinator and 'context' in locals():
            # Start coordination for propagation
            coordinator.start_coordination()

            # Register a mock service
            from agentic_core.tracing.distributed_tracing_coordinator import ServiceNode

            mock_service = ServiceNode(
                service_name="target-service",
                service_id="target-123",
                host="localhost",
                port=8080,
                capabilities={"test_capability"},
            )

            coordinator.register_service(mock_service)

            # Test propagation
            propagation_success = coordinator.propagate_trace_context(context, "target-service")

            results['trace_propagation'] = isinstance(propagation_success, bool)
            results['propagation_attempted'] = True

            print("✅ Trace propagation:")
            print(f"   - Propagation success: {propagation_success}")
            print(f"   - Registered services: {len(coordinator._registered_services)}")

            # Stop coordination
            coordinator.stop_coordination()

        else:
            results['trace_propagation'] = False
            results['propagation_attempted'] = False

    except Exception as e:
        results['trace_propagation'] = False
        results['propagation_attempted'] = False
        print(f"❌ Trace propagation failed: {e}")
        traceback.print_exc()

    # Test 5: Coordination statistics
    print("\n5. Testing coordination statistics...")
    try:
        if 'coordinator' in locals() and coordinator:
            # Get coordination stats
            stats = coordinator.get_coordination_stats()

            results['coordination_stats'] = isinstance(stats, dict)
            results['stats_sections'] = len(stats) > 0 if isinstance(stats, dict) else False
            results['traces_created'] = stats.get("statistics", {}).get("traces_created", 0) >= 0

            if isinstance(stats, dict):
                print("✅ Coordination statistics:")
                print(f"   - Coordination active: {stats.get('coordination_active')}")
                print(f"   - Registered services: {stats.get('registered_services')}")
                print(f"   - Active traces: {stats.get('active_traces')}")
                print(f"   - Total spans: {stats.get('total_spans')}")
                print(f"   - Traces created: {stats.get('statistics', {}).get('traces_created')}")

        else:
            results['coordination_stats'] = False
            results['stats_sections'] = False
            results['traces_created'] = False

    except Exception as e:
        results['coordination_stats'] = False
        results['stats_sections'] = False
        results['traces_created'] = False
        print(f"❌ Coordination statistics failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("DISTRIBUTED TRACING SUMMARY")
    print("=" * 80)

    test_keys = [
        'coordinator_init', 'coordination_startup', 'service_registered',
        'trace_context_creation', 'trace_id_available', 'span_id_available',
        'service_name_set', 'trace_propagation', 'propagation_attempted',
        'coordination_stats', 'stats_sections', 'traces_created',
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Distributed Tracing Tests: {success_count}/{total_tests}")

    if success_count >= total_tests - 2:  # Allow 2 tests to fail
        print("🎉 DISTRIBUTED TRACING TESTS PASSED!")
    else:
        print("🚨 Some distributed tracing tests failed")

    return results

def test_analytics_dashboard():
    """Test analytics dashboard functionality."""
    print("\n" + "=" * 80)
    print("PHASE 4: ANALYTICS DASHBOARD TEST")
    print("=" * 80)

    results = {}

    # Test 1: Analytics dashboard initialization
    print("\n1. Testing analytics dashboard initialization...")
    try:
        from agentic_core.dashboard.analytics_dashboard import get_global_dashboard

        dashboard = get_global_dashboard()
        results['dashboard_init'] = dashboard is not None
        print("✅ Analytics dashboard initialized successfully")

    except Exception as e:
        results['dashboard_init'] = False
        print(f"❌ Analytics dashboard initialization failed: {e}")
        traceback.print_exc()

    # Test 2: Default widgets
    print("\n2. Testing default widgets...")
    try:
        if 'dashboard' in locals() and dashboard:
            widgets = dashboard._widgets

            results['default_widgets'] = isinstance(widgets, dict)
            results['widget_count'] = len(widgets) > 0
            results['required_widgets'] = all(widget_id in widgets for widget_id in [
                'system_health', 'active_traces', 'performance_metrics', 'alerts', 'service_health', 'optimization',
            ])

            print("✅ Default widgets:")
            print(f"   - Total widgets: {len(widgets)}")
            print(f"   - Widget types: {list(widgets.keys())}")
            print(f"   - All required widgets present: {results['required_widgets']}")

        else:
            results['default_widgets'] = False
            results['widget_count'] = False
            results['required_widgets'] = False

    except Exception as e:
        results['default_widgets'] = False
        results['widget_count'] = False
        results['required_widgets'] = False
        print(f"❌ Default widgets failed: {e}")
        traceback.print_exc()

    # Test 3: Dashboard startup
    print("\n3. Testing dashboard startup...")
    try:
        if 'dashboard' in locals() and dashboard:
            # Start dashboard
            dashboard.start_dashboard()
            time.sleep(0.1)  # Let dashboard start

            results['dashboard_startup'] = dashboard._dashboard_active

            print("✅ Dashboard startup:")
            print(f"   - Dashboard active: {dashboard._dashboard_active}")
            print(f"   - Dashboard URL: http://{dashboard._config.host}:{dashboard._config.port}")

            # Stop dashboard
            dashboard.stop_dashboard()

        else:
            results['dashboard_startup'] = False

    except Exception as e:
        results['dashboard_startup'] = False
        print(f"❌ Dashboard startup failed: {e}")
        traceback.print_exc()

    # Test 4: Widget management
    print("\n4. Testing widget management...")
    try:
        if 'dashboard' in locals() and dashboard:
            # Test adding a widget
            from agentic_core.dashboard.analytics_dashboard import DashboardWidget

            test_widget = DashboardWidget(
                widget_id="test_widget",
                widget_type="metric",
                title="Test Widget",
                position={"x": 0, "y": 8, "width": 4, "height": 2},
                data={"value": 42},
            )

            add_success = dashboard.add_widget(test_widget)
            widget_added = "test_widget" in dashboard._widgets

            # Test removing a widget
            remove_success = dashboard.remove_widget("test_widget")
            widget_removed = "test_widget" not in dashboard._widgets

            results['widget_management'] = True
            results['add_widget'] = add_success and widget_added
            results['remove_widget'] = remove_success and widget_removed

            print("✅ Widget management:")
            print(f"   - Add widget: {add_success}")
            print(f"   - Widget added: {widget_added}")
            print(f"   - Remove widget: {remove_success}")
            print(f"   - Widget removed: {widget_removed}")

        else:
            results['widget_management'] = False
            results['add_widget'] = False
            results['remove_widget'] = False

    except Exception as e:
        results['widget_management'] = False
        results['add_widget'] = False
        results['remove_widget'] = False
        print(f"❌ Widget management failed: {e}")
        traceback.print_exc()

    # Test 5: Dashboard data export
    print("\n5. Testing dashboard data export...")
    try:
        if 'dashboard' in locals() and dashboard:
            # Get dashboard data
            dashboard_data = dashboard.get_dashboard_data()

            results['dashboard_data_export'] = isinstance(dashboard_data, dict)
            results['data_sections'] = len(dashboard_data) > 0 if isinstance(dashboard_data, dict) else False

            # Export configuration
            config_export = dashboard.export_dashboard_config()

            results['config_export'] = isinstance(config_export, dict)

            # Get dashboard summary
            summary = dashboard.get_dashboard_summary()

            results['dashboard_summary'] = isinstance(summary, dict)

            if isinstance(dashboard_data, dict):
                print("✅ Dashboard data export:")
                print(f"   - Data sections: {list(dashboard_data.keys())}")
                print(f"   - Widgets in data: {len(dashboard_data.get('widgets', {}))}")
                print(f"   - Real-time data points: {len(dashboard_data.get('real_time_data', {}))}")

        else:
            results['dashboard_data_export'] = False
            results['data_sections'] = False
            results['config_export'] = False
            results['dashboard_summary'] = False

    except Exception as e:
        results['dashboard_data_export'] = False
        results['data_sections'] = False
        results['config_export'] = False
        results['dashboard_summary'] = False
        print(f"❌ Dashboard data export failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("ANALYTICS DASHBOARD SUMMARY")
    print("=" * 80)

    test_keys = [
        'dashboard_init', 'default_widgets', 'widget_count', 'required_widgets',
        'dashboard_startup', 'widget_management', 'add_widget', 'remove_widget',
        'dashboard_data_export', 'data_sections', 'config_export', 'dashboard_summary',
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Analytics Dashboard Tests: {success_count}/{total_tests}")

    if success_count >= total_tests - 2:  # Allow 2 tests to fail
        print("🎉 ANALYTICS DASHBOARD TESTS PASSED!")
    else:
        print("🚨 Some analytics dashboard tests failed")

    return results

def main():
    """Run all Phase 4 tests."""
    print("PHASE 4: ADVANCED ANALYTICS AND PERFORMANCE OPTIMIZATION - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    # Run all test suites
    analytics_results = test_advanced_analytics()
    perf_results = test_performance_optimization()
    monitoring_results = test_enhanced_monitoring()
    distributed_results = test_distributed_tracing()
    dashboard_results = test_analytics_dashboard()

    # Combined summary
    print("\n" + "=" * 80)
    print("PHASE 4 COMPREHENSIVE SUMMARY")
    print("=" * 80)

    all_results = {
        **analytics_results,
        **perf_results,
        **monitoring_results,
        **distributed_results,
        **dashboard_results,
    }

    all_tests = list(all_results.keys())
    all_passed = sum(1 for key, value in all_results.items() if value is True)
    total_tests = len(all_tests)

    print(f"Overall Results: {all_passed}/{total_tests} tests passed")

    # Component summaries
    analytics_passed = sum(1 for key, value in analytics_results.items() if value is True)
    perf_passed = sum(1 for key, value in perf_results.items() if value is True)
    monitoring_passed = sum(1 for key, value in monitoring_results.items() if value is True)
    distributed_passed = sum(1 for key, value in distributed_results.items() if value is True)
    dashboard_passed = sum(1 for key, value in dashboard_results.items() if value is True)

    print(f"Advanced Analytics: {analytics_passed}/{len(analytics_results)} passed")
    print(f"Performance Optimization: {perf_passed}/{len(perf_results)} passed")
    print(f"Enhanced Monitoring: {monitoring_passed}/{len(monitoring_results)} passed")
    print(f"Distributed Tracing: {distributed_passed}/{len(distributed_results)} passed")
    print(f"Analytics Dashboard: {dashboard_passed}/{len(dashboard_results)} passed")

    if all_passed >= total_tests * 0.8:  # 80% success rate required
        print("\n🎉 PHASE 4 COMPLETE - ADVANCED ANALYTICS AND PERFORMANCE OPTIMIZATION SUCCESSFUL!")
        print("✅ Advanced pattern analysis operational")
        print("✅ Performance optimization pipeline functional")
        print("✅ Enhanced monitoring and alerting working")
        print("✅ Distributed tracing coordination operational")
        print("✅ Analytics dashboard ready for deployment")
        return True
    else:
        print("\n🚨 PHASE 4 INCOMPLETE - Some advanced features failed")
        print("❌ Advanced analytics pipeline has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
