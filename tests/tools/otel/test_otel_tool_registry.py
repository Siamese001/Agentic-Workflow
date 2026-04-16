from tools.otel.otel_tool_registry import register_tools


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class FakeLifecycle:
    def __init__(self):
        self.ensure_started_calls = 0

    def status(self):
        return {
            "available": True,
            "started": False,
            "registered": False,
            "loading": False,
            "last_error": None,
        }

    def ensure_started(self):
        self.ensure_started_calls += 1


class FakeOpsService:
    def status(self, lifecycle_status=None):
        return {"surface": "status", "lifecycle": lifecycle_status}

    def server_info(self, lifecycle_status=None):
        return {"surface": "server_info", "lifecycle": lifecycle_status}


class FakeQueryService:
    def trace(self, trace_id):
        return {"surface": "trace", "trace_id": trace_id}

    def spans_by_agent(self, agent_class, limit=50):
        return {"surface": "spans_by_agent", "agent_class": agent_class, "limit": limit}

    def healing_chain(self, trace_id):
        return {"surface": "healing_chain", "trace_id": trace_id}

    def policy_decisions(self, time_window_hours=24):
        return {"surface": "policy_decisions", "time_window_hours": time_window_hours}

    def metrics_summary(self):
        return {"surface": "metrics_summary"}

    def anomalies(self, severity="any"):
        return {"surface": "anomalies", "severity": severity}


class FakeIngestService:
    def ingest_to_runtime_adg(self, trace_data):
        return {"surface": "ingest", "trace_data": trace_data}


def test_health_tools_do_not_trigger_lifecycle_start():
    mcp = FakeMCP()
    lifecycle = FakeLifecycle()
    register_tools(mcp, lifecycle, FakeOpsService(), FakeQueryService(), FakeIngestService())

    assert mcp.tools["otel_status"]()["surface"] == "status"
    assert mcp.tools["otel_server_info"]()["surface"] == "server_info"
    assert lifecycle.ensure_started_calls == 0


def test_non_health_tools_trigger_lifecycle_start_nonblocking():
    mcp = FakeMCP()
    lifecycle = FakeLifecycle()
    register_tools(mcp, lifecycle, FakeOpsService(), FakeQueryService(), FakeIngestService())

    assert mcp.tools["otel_trace"]("trace_12345678")["surface"] == "trace"
    assert lifecycle.ensure_started_calls == 1
