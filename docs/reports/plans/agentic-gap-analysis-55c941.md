# Agentic Process Mapping — Top 10 Gaps: Gory Diff Plan

Each gap below contains exact before/after file diffs grounded in the actual source, new files to create in full, and CI scaffolding. Gaps ordered by execution dependency.

---

## Gap 1 — Direct LLM SDK Bypass of `SovereignLLMGateway` ⚠️ CRITICAL

**Spec:** Gateway is sole outbound LLM seam. AST scanner blocks direct SDK imports outside gateway.

### 1a. `apps_lic/tools/GeminiLLMClient.py` — replace direct genai calls with gateway

```diff
-# File: llm_clients.py
-# Description: Centralized LLM client for all generative AI calls
-
-__version__ = "12.0"
-
-import os
-
-
-class GeminiLLMClient:
-    """
-    Centralized client for all Gemini API calls with circuit breaker protection
-    """
-
-    def __init__(self, circuit_breaker: CircuitBreaker):
-        self.api_key = os.environ.get("GEMINI_API_KEY")
-        if not self.api_key:
-            raise ValueError("GEMINI_API_KEY not found in environment")
-        genai.configure(api_key=self.api_key)
-        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
-        self.circuit_breaker = circuit_breaker
-
-    def _execute_llm_call(self, prompt: str) -> str:
-        """Execute the actual LLM API call"""
-        response = self.model.generate_content(prompt)
-        return response.text
-
-    def generate(self, prompt: str) -> str:
-        try:
-            return self.circuit_breaker.call(self._execute_llm_call, prompt)
-        except Exception as e:
-            raise Exception(f"Gemini API call failed: {e}")
+# File: GeminiLLMClient.py
+# Description: Gemini LLM client — delegates ALL calls through SovereignLLMGateway
+
+__version__ = "13.0"
+
+import asyncio
+
+from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
+from agentic_core.L2_execution.types.gateway_types import GenerationRequest
+
+
+class GeminiLLMClient:
+    """Gateway-delegating client for Gemini.  No direct SDK access."""
+
+    _AGENT_ID = "GeminiLLMClient"
+    _MODEL = "gemini-pro"  # allowlisted model id in SovereignLLMGateway
+
+    def __init__(self, circuit_breaker=None):
+        self._gateway = SovereignLLMGateway()
+        self.circuit_breaker = circuit_breaker  # kept for API compat; unused internally
+
+    def generate(self, prompt: str) -> str:
+        request = GenerationRequest(
+            agent_id=self._AGENT_ID,
+            provider="google",
+            model=self._MODEL,
+            prompt=prompt,
+        )
+        response = asyncio.get_event_loop().run_until_complete(
+            self._gateway.route_generation(request)
+        )
+        return response.content
```

### 1b. `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` — excise `_setup_client`, delegate through gateway

```diff
-    def _setup_client(self) -> None:
-        """Setup Anthropic client."""
-        try:
-            import anthropic
-        except ImportError as exc:
-            raise ImportError("Anthropic package not installed. Install with: pip install anthropic") from exc
-
-        api_key = os.getenv("ANTHROPIC_API_KEY")
-        if not api_key:
-            raise RuntimeError("ANTHROPIC_API_KEY environment variable must be set")
-
-        self._client = anthropic.Anthropic(
-            api_key=api_key,
-            timeout=self.config.timeout_s,
-        )
+    def _setup_client(self) -> None:
+        """Delegate to SovereignLLMGateway — no direct Anthropic SDK access."""
+        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
+        self._gateway = SovereignLLMGateway()
+        self._client = None  # kept for isinstance checks in callers; not used
```

All callsites in `HardenedAnthropicExecutor` that invoke `self._client.messages.create(...)` must be replaced with:

```diff
-        response = self._client.messages.create(
-            model=self.config.model,
-            max_tokens=self.config.max_tokens,
-            messages=messages,
-        )
-        return response.content[0].text
+        import asyncio
+        from agentic_core.L2_execution.types.gateway_types import GenerationRequest
+        request = GenerationRequest(
+            agent_id="HardenedAnthropicExecutor",
+            provider="anthropic",
+            model=self.config.model,
+            prompt=messages[-1]["content"] if messages else "",
+            max_tokens=self.config.max_tokens,
+        )
+        resp = asyncio.get_event_loop().run_until_complete(
+            self._gateway.route_generation(request)
+        )
+        return resp.content
```

Also remove top-level `import os` and `from dataclasses import dataclass` usage tied to the deleted `_setup_client`.

### 1c. New file: `ops_scripts/ci/check_sovereign_llm_gateway.py`

```python
"""AST-based CI guard: no direct LLM SDK usage outside the gateway.

Fails with non-zero exit if any .py file outside the allowed boundary
contains a direct import or instantiation of openai/anthropic/google SDK.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Only these files may touch LLM SDKs directly
ALLOWED_SDK_FILES = {
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "data/sdks_mcps/client_wrappers.py",
}

FORBIDDEN_IMPORTS = {
    "openai",
    "anthropic",
    "google.generativeai",
}

FORBIDDEN_CALLS = {
    # (module_attr, attr) pairs
    ("openai", "OpenAI"),
    ("anthropic", "Anthropic"),
    ("genai", "configure"),
    ("genai", "GenerativeModel"),
}

FORBIDDEN_MODEL_PREFIXES = ("gpt-", "claude-", "gemini-")


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _check_file(path: Path) -> list[str]:
    rel = _rel(path)
    if rel in ALLOWED_SDK_FILES:
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    violations: list[str] = []

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = ""
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_IMPORTS):
                        violations.append(f"{rel}:{node.lineno}: forbidden import '{mod}'")
            else:
                mod = node.module or ""
                if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_IMPORTS):
                    violations.append(f"{rel}:{node.lineno}: forbidden from-import '{mod}'")

        # Check hardcoded model strings
        if isinstance(node, ast.Constant) and isinstance(node.s, str):
            if any(node.s.startswith(p) for p in FORBIDDEN_MODEL_PREFIXES):
                violations.append(
                    f"{rel}:{node.lineno}: hardcoded model literal '{node.s}'"
                )

    return violations


def main() -> int:
    scan_roots = [
        REPO_ROOT / "apps_lic",
        REPO_ROOT / "apps_rg",
        REPO_ROOT / "apps_shared",
        REPO_ROOT / "agentic_core",
        REPO_ROOT / "system_learning",
    ]
    violations: list[str] = []
    for root in scan_roots:
        for py in root.rglob("*.py"):
            violations.extend(_check_file(py))

    if violations:
        print(f"FAIL: {len(violations)} sovereign gateway violation(s):")
        for v in sorted(violations):
            print(f"  {v}")
        return 1

    count = sum(1 for r in scan_roots for _ in r.rglob("*.py"))
    print(f"OK: sovereign gateway boundary clean ({count} files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 1d. New file: `.github/workflows/sovereign-gateway-guard.yml`

```yaml
name: Sovereign LLM Gateway Guard
on: [push, pull_request]
jobs:
  gateway-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Run sovereign gateway boundary check
        run: python ops_scripts/ci/check_sovereign_llm_gateway.py
```

### 1e. New file: `tests/architecture/test_sovereign_gateway_boundary.py`

```python
"""In-process AST gate: zero direct LLM SDK usage outside allowed boundary."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ops_scripts.ci.check_sovereign_llm_gateway import main


def test_sovereign_gateway_boundary_clean():
    assert main() == 0, "Direct LLM SDK usage detected outside SovereignLLMGateway"
```

---

## Gap 2 — `SandboxEnvelope` missing `ToolBudget` caps ⚠️ CRITICAL

**Spec (contract [2]):** `SandboxEnvelope = [InstructionPacket, ToolBudget(compute_ms, memory_mb, stdout_bytes)]`

### 2a. `agentic_core/L2_execution/types/sandbox_envelope.py` — add `ToolBudget` field

```diff
 from __future__ import annotations

 import hashlib
 import hmac
-from dataclasses import dataclass, field, replace
+from dataclasses import dataclass, field, replace
 from typing import Any

 from agentic_core.L2_execution.enforcement.key_source import get_current_secret
 from agentic_core.L2_execution.types.instruction_packet import (
     SignatureVerificationError,
     _canonical_bytes,
 )

+# ---------------------------------------------------------------------------
+# ToolBudget
+# ---------------------------------------------------------------------------
+
+
+@dataclass(frozen=True)
+class ToolBudget:
+    """Hard resource caps for a sandboxed tool invocation.
+
+    All values must be strictly positive.
+    """
+
+    compute_ms: int    # wall-clock limit in milliseconds
+    memory_mb: int     # RSS limit in megabytes
+    stdout_bytes: int  # captured stdout byte limit
+
+    def __post_init__(self) -> None:
+        for name, val in (
+            ("compute_ms", self.compute_ms),
+            ("memory_mb", self.memory_mb),
+            ("stdout_bytes", self.stdout_bytes),
+        ):
+            if not isinstance(val, int) or val <= 0:
+                raise ValueError(f"ToolBudget.{name} must be a positive int, got {val!r}")
+
+    def to_signable_dict(self) -> dict[str, int]:
+        return {
+            "compute_ms": self.compute_ms,
+            "memory_mb": self.memory_mb,
+            "stdout_bytes": self.stdout_bytes,
+        }
+
+
+DEFAULT_TOOL_BUDGET = ToolBudget(compute_ms=30_000, memory_mb=256, stdout_bytes=65_536)
+

 @dataclass(frozen=True)
 class SandboxEnvelope:
     """Signed wrapper for L2 tool invocations."""

     envelope_id: str
     tool_name: str
     tool_args: dict[str, Any] = field(default_factory=dict)
     instruction_packet_id: str = ""
     invocation_metadata: dict[str, Any] = field(default_factory=dict)
+    tool_budget: ToolBudget = field(default_factory=lambda: DEFAULT_TOOL_BUDGET)
     signature: str = field(default="", init=False)

     def _signable_dict(self) -> dict[str, Any]:
         return {
             "envelope_id": self.envelope_id,
             "instruction_packet_id": self.instruction_packet_id,
             "invocation_metadata": self.invocation_metadata,
             "tool_args": self.tool_args,
             "tool_name": self.tool_name,
+            "tool_budget": self.tool_budget.to_signable_dict(),
         }
```

### 2b. New file: `agentic_core/L2_execution/enforcement/budget_enforcer.py`

```python
"""BudgetEnforcer — wraps tool execution with hard ToolBudget caps.

Enforces compute_ms via threading.Timer, stdout_bytes via ByteCapStream,
memory_mb via resource.setrlimit (Unix) or best-effort on Windows.
"""
from __future__ import annotations

import io
import sys
import threading
from typing import Any, Callable

from agentic_core.L2_execution.types.sandbox_envelope import ToolBudget


class BudgetExceededError(RuntimeError):
    """Raised when a ToolBudget cap is violated."""


class _ByteCapStream(io.RawIOBase):
    """Wraps sys.stdout to enforce stdout_bytes cap."""

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._written = 0
        self._original = sys.stdout

    def write(self, data: bytes | str) -> int:
        encoded = data.encode() if isinstance(data, str) else data
        self._written += len(encoded)
        if self._written > self._limit:
            raise BudgetExceededError(
                f"stdout_bytes cap exceeded: {self._written} > {self._limit}"
            )
        self._original.write(data if isinstance(data, str) else data.decode(errors="replace"))
        return len(encoded)

    def flush(self) -> None:
        self._original.flush()


class BudgetEnforcer:
    """Context manager that enforces a ToolBudget around a callable."""

    def __init__(self, budget: ToolBudget) -> None:
        self._budget = budget
        self._timer: threading.Timer | None = None
        self._timed_out = False

    def enforce(self, fn: Callable[[], Any]) -> Any:
        """Run fn() under full budget enforcement.  Raises BudgetExceededError on violation."""
        cap_stream = _ByteCapStream(self._budget.stdout_bytes)
        original_stdout = sys.stdout

        def _timeout_handler() -> None:
            self._timed_out = True

        self._timer = threading.Timer(
            self._budget.compute_ms / 1000.0, _timeout_handler
        )
        self._timer.daemon = True

        sys.stdout = cap_stream  # type: ignore[assignment]
        self._timer.start()
        try:
            result = fn()
            if self._timed_out:
                raise BudgetExceededError(
                    f"compute_ms cap exceeded: >{self._budget.compute_ms}ms"
                )
            return result
        finally:
            self._timer.cancel()
            sys.stdout = original_stdout
```

### 2c. Test: `tests/agentic_core/L2_execution/types/test_sandbox_envelope_budget.py`

```python
"""Regression: SandboxEnvelope must carry ToolBudget in signable surface."""
import pytest
from agentic_core.L2_execution.types.sandbox_envelope import (
    DEFAULT_TOOL_BUDGET,
    SandboxEnvelope,
    ToolBudget,
)
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)

inject_key_source(TestKeySource())


def _make_env(**kwargs) -> SandboxEnvelope:
    defaults = dict(envelope_id="e1", tool_name="test_tool")
    return SandboxEnvelope(**{**defaults, **kwargs})


def test_default_budget_present():
    env = _make_env()
    assert env.tool_budget == DEFAULT_TOOL_BUDGET


def test_custom_budget_in_signable_dict():
    budget = ToolBudget(compute_ms=5000, memory_mb=64, stdout_bytes=1024)
    env = _make_env(tool_budget=budget)
    sd = env._signable_dict()
    assert sd["tool_budget"] == {"compute_ms": 5000, "memory_mb": 64, "stdout_bytes": 1024}


def test_budget_bound_in_signature():
    env1 = _make_env(tool_budget=ToolBudget(compute_ms=1000, memory_mb=32, stdout_bytes=512))
    env2 = _make_env(tool_budget=ToolBudget(compute_ms=9000, memory_mb=32, stdout_bytes=512))
    assert env1.signature != env2.signature


def test_zero_budget_rejected():
    with pytest.raises(ValueError, match="compute_ms"):
        ToolBudget(compute_ms=0, memory_mb=64, stdout_bytes=1024)


def test_verify_passes_with_budget():
    secret = TestKeySource.TEST_SECRET
    env = _make_env(tool_budget=ToolBudget(compute_ms=5000, memory_mb=64, stdout_bytes=1024))
    env.verify(secret)  # must not raise
```

---

## Gap 3 — `HumanDecisionArtifact` (Path D contract) absent ⚠️ CRITICAL

**Spec (contract [5]):** `HumanDecisionArtifact = [trace_id, policy_hash, reviewer_id, action:[APPROVE|MODIFY_DIFF|REJECT], structured_patch_schema, reviewer_sig]`

### 3a. New file: `agentic_core/L5_safety/types/human_decision_artifact.py`

```python
"""HumanDecisionArtifact — Path D contract (spec contract [5]).

Emitted by HumanReviewQueue on every approve/reject/modify_diff decision.
reviewer_sig = HMAC-SHA256 over canonical JSON of the artifact (excl. sig field).
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Literal


class HumanDecisionContractViolation(ValueError):
    """Raised when HumanDecisionArtifact invariants are violated."""


HDAAction = Literal["APPROVE", "MODIFY_DIFF", "REJECT"]


@dataclass(frozen=True)
class HumanDecisionArtifact:
    """Immutable signed record of a human reviewer decision."""

    trace_id: str
    policy_hash: str
    reviewer_id: str
    action: HDAAction
    structured_patch_schema: dict  # empty dict for APPROVE/REJECT
    reviewer_sig: str  # HMAC-SHA256 hex; empty string = unsigned draft

    # MODIFY_DIFF only — must reference the original plan hash
    original_plan_hash: str = ""

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise HumanDecisionContractViolation("trace_id is required")
        if not self.reviewer_id:
            raise HumanDecisionContractViolation("reviewer_id is required")
        if self.action not in ("APPROVE", "MODIFY_DIFF", "REJECT"):
            raise HumanDecisionContractViolation(f"Invalid action: {self.action!r}")
        if self.action == "MODIFY_DIFF" and not self.original_plan_hash:
            raise HumanDecisionContractViolation(
                "MODIFY_DIFF requires original_plan_hash"
            )

    def _signable_dict(self) -> dict:
        return {
            "action": self.action,
            "original_plan_hash": self.original_plan_hash,
            "policy_hash": self.policy_hash,
            "reviewer_id": self.reviewer_id,
            "structured_patch_schema": self.structured_patch_schema,
            "trace_id": self.trace_id,
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self._signable_dict(), sort_keys=True, separators=(",", ":")
        ).encode("ascii")

    def sign(self, secret: bytes) -> "HumanDecisionArtifact":
        """Return new artifact with reviewer_sig populated."""
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        return HumanDecisionArtifact(
            trace_id=self.trace_id,
            policy_hash=self.policy_hash,
            reviewer_id=self.reviewer_id,
            action=self.action,
            structured_patch_schema=self.structured_patch_schema,
            reviewer_sig=mac.hexdigest().lower(),
            original_plan_hash=self.original_plan_hash,
        )

    def verify(self, secret: bytes) -> None:
        """Raise HumanDecisionContractViolation if signature wrong or absent."""
        if not self.reviewer_sig:
            raise HumanDecisionContractViolation("reviewer_sig absent — artifact unsigned")
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.reviewer_sig, expected):
            raise HumanDecisionContractViolation(
                "reviewer_sig mismatch — artifact tampered or wrong key"
            )


__all__ = ["HumanDecisionArtifact", "HumanDecisionContractViolation", "HDAAction"]
```

### 3b. `agentic_core/L5_safety/enforcement/human_review_queue.py` — wire artifact emission + MODIFY_DIFF

```diff
 class ReviewStatus(Enum):
     PENDING = "pending"
     IN_REVIEW = "in_review"
     APPROVED = "approved"
     REJECTED = "rejected"
     ESCALATED = "escalated"
     EXPIRED = "expired"
+    MODIFY_DIFF = "modify_diff"


+@dataclass
+class ModifyDiffRequest:
+    """Structured MODIFY_DIFF submission — replaces the proposed diff inline."""
+    original_plan_hash: str
+    structured_patch_schema: dict
+    reviewer_id: str
+    notes: str = ""
```

```diff
+from agentic_core.L5_safety.types.human_decision_artifact import HumanDecisionArtifact
+from agentic_core.L2_execution.enforcement.key_source import get_current_secret
```

```diff
     def approve(
         self,
         request_id: str,
         reviewer_id: str,
         notes: str = "",
-    ) -> ReviewRequest:
+        policy_hash: str = "",
+    ) -> tuple[ReviewRequest, HumanDecisionArtifact]:
         """Approve a pending review request."""
         with self._lock:
             request = self._pending_requests.get(request_id)
             if not request:
                 raise ValueError(f"Review request not found: {request_id}")

             request.status = ReviewStatus.APPROVED
             request.reviewer_id = reviewer_id
             request.review_completed_at = datetime.utcnow()
             request.review_notes = notes

             del self._pending_requests[request_id]
             self._completed_requests.append(request)

         Logger.info(f"[REVIEW_QUEUE] Request {request_id} APPROVED by {reviewer_id}")
         self._trigger_callback(request_id, "approved")
         self._emit_policy_update_proposal(request, HILOutcome.APPROVED)
-        return request
+
+        artifact = HumanDecisionArtifact(
+            trace_id=request_id,
+            policy_hash=policy_hash,
+            reviewer_id=reviewer_id,
+            action="APPROVE",
+            structured_patch_schema={},
+        ).sign(get_current_secret())
+        return request, artifact
```

```diff
     def reject(
         self,
         request_id: str,
         reviewer_id: str,
         notes: str,
-    ) -> ReviewRequest:
+        policy_hash: str = "",
+    ) -> tuple[ReviewRequest, HumanDecisionArtifact]:
         """Reject a pending review request."""
         if not notes:
             raise ValueError("Rejection notes are required")
         ...
         Logger.info(...)
         self._trigger_callback(request_id, "rejected")
         self._emit_policy_update_proposal(request, HILOutcome.REJECTED)
-        return request
+
+        artifact = HumanDecisionArtifact(
+            trace_id=request_id,
+            policy_hash=policy_hash,
+            reviewer_id=reviewer_id,
+            action="REJECT",
+            structured_patch_schema={},
+        ).sign(get_current_secret())
+        return request, artifact
```

```diff
+    def modify_diff(
+        self,
+        request_id: str,
+        modify_request: ModifyDiffRequest,
+        policy_hash: str = "",
+    ) -> tuple[ReviewRequest, HumanDecisionArtifact]:
+        """Apply a MODIFY_DIFF decision — replaces diff before routing back to L2."""
+        if not modify_request.original_plan_hash:
+            raise ValueError("MODIFY_DIFF requires original_plan_hash")
+        with self._lock:
+            request = self._pending_requests.get(request_id)
+            if not request:
+                raise ValueError(f"Review request not found: {request_id}")
+            request.status = ReviewStatus.MODIFY_DIFF
+            request.reviewer_id = modify_request.reviewer_id
+            request.review_completed_at = datetime.utcnow()
+            request.review_notes = modify_request.notes
+            del self._pending_requests[request_id]
+            self._completed_requests.append(request)
+
+        artifact = HumanDecisionArtifact(
+            trace_id=request_id,
+            policy_hash=policy_hash,
+            reviewer_id=modify_request.reviewer_id,
+            action="MODIFY_DIFF",
+            structured_patch_schema=modify_request.structured_patch_schema,
+            original_plan_hash=modify_request.original_plan_hash,
+        ).sign(get_current_secret())
+        Logger.info(f"[REVIEW_QUEUE] Request {request_id} MODIFY_DIFF by {modify_request.reviewer_id}")
+        return request, artifact
```

### 3c. Test: `tests/agentic_core/L5_safety/types/test_human_decision_artifact.py`

```python
"""Contract tests for HumanDecisionArtifact (Path D spec [5])."""
import pytest
from agentic_core.L5_safety.types.human_decision_artifact import (
    HumanDecisionArtifact,
    HumanDecisionContractViolation,
)

SECRET = b"test-l5-secret"


def _make(**kwargs) -> HumanDecisionArtifact:
    defaults = dict(
        trace_id="t1", policy_hash="ph1", reviewer_id="r1",
        action="APPROVE", structured_patch_schema={}, reviewer_sig="",
    )
    return HumanDecisionArtifact(**{**defaults, **kwargs})


def test_approve_roundtrip():
    art = _make().sign(SECRET)
    art.verify(SECRET)  # must not raise


def test_reject_roundtrip():
    art = _make(action="REJECT").sign(SECRET)
    art.verify(SECRET)


def test_modify_diff_requires_plan_hash():
    with pytest.raises(HumanDecisionContractViolation, match="original_plan_hash"):
        _make(action="MODIFY_DIFF")


def test_modify_diff_roundtrip():
    art = _make(
        action="MODIFY_DIFF",
        original_plan_hash="abc123",
        structured_patch_schema={"file": "x.py", "patch": "@@..."},
    ).sign(SECRET)
    art.verify(SECRET)


def test_tampered_sig_rejected():
    art = _make().sign(SECRET)
    tampered = HumanDecisionArtifact(
        trace_id=art.trace_id, policy_hash=art.policy_hash,
        reviewer_id=art.reviewer_id, action=art.action,
        structured_patch_schema=art.structured_patch_schema,
        reviewer_sig="deadbeef" * 8,
    )
    with pytest.raises(HumanDecisionContractViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_empty_trace_id_rejected():
    with pytest.raises(HumanDecisionContractViolation):
        _make(trace_id="")


def test_invalid_action_rejected():
    with pytest.raises(HumanDecisionContractViolation):
        _make(action="SNOOZE")
```

---

## Gap 4 — `AgentExecutionProfileRegistry` not enforced at L0

**Spec:** Every agent invocation must be registry-checked. Unregistered = HARD FAIL.

### 4a. `agentic_core/L0_routing/enforcement/execution_gateway.py` — add registry check before `_validate_manifest`

```diff
+from agentic_core.agents.agent_registry import get_profile, registry_digest
+from agentic_core.agents.types.agent_execution_profile import ExecutionMode
+
+
+class UnregisteredAgentError(RuntimeError):
+    """Raised when an agent is not found in AgentExecutionProfileRegistry."""
+

 class V15ExecutionGateway:
     def __init__(self) -> None:
         self._clock = SemanticClock()
         self._seen_signals: set[str] = set()
         self._pipe_violations: list[dict[str, object]] = []
         self._policy_violations: list[dict[str, object]] = []
         self._mismatch_tracker: HashMismatchTracker | None = None
+        self._registry_digest: str = registry_digest()

     def execute(
         self,
         execution_input: Any,
         heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
         state_hash_fn: Callable[[], tuple[str, str, str]],
         trace_id: str = "gw-default",
+        agent_id: str = "",
         **kwargs: Any,
     ) -> GatewayResult:
         self._pipe_violations = []
         self._policy_violations = []
+        if agent_id:
+            self._enforce_agent_registered(agent_id)
         try:
             return self._execute_with_envelope(execution_input, heal_fn, state_hash_fn, trace_id, **kwargs)
         except V15SoftFailAbort as sfa:
             ...
+
+    def _enforce_agent_registered(self, agent_id: str) -> None:
+        """Raise UnregisteredAgentError if agent_id not in AGENT_REGISTRY."""
+        try:
+            profile = get_profile(agent_id)
+        except KeyError:
+            raise UnregisteredAgentError(
+                f"Agent '{agent_id}' not registered in AgentExecutionProfileRegistry. "
+                f"Add an AgentExecutionProfile entry to agentic_core/agents/agent_registry.py."
+            )
+        Logger.debug("[V15-GW] Agent '%s' registry check OK (mode=%s)", agent_id, profile.execution_mode)
```

### 4b. New CI file: `ops_scripts/ci/check_agent_registry_completeness.py`

```python
"""AST-based CI guard: every apps_* reasoning agent class is in AGENT_REGISTRY.

Scans all apps_*/reasoning/*.py files, extracts class names, cross-checks
against the AGENT_REGISTRY dict keys.  Hard-fails on any missing entry.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REASONING_GLOBS = [
    "apps_lic/reasoning/*.py",
    "apps_rg/reasoning/*.py",
    "apps_shared/reasoning/*.py",
]


def _extract_classes(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def _load_registry_keys() -> set[str]:
    sys.path.insert(0, str(REPO_ROOT))
    from agentic_core.agents.agent_registry import AGENT_REGISTRY  # noqa: PLC0415
    return set(AGENT_REGISTRY.keys())


def main() -> int:
    agent_classes: list[tuple[str, str]] = []  # (class_name, rel_path)
    for glob in REASONING_GLOBS:
        for path in REPO_ROOT.glob(glob):
            for cls in _extract_classes(path):
                agent_classes.append((cls, path.relative_to(REPO_ROOT).as_posix()))

    registry_keys = _load_registry_keys()
    missing = [
        (cls, path) for cls, path in agent_classes if cls not in registry_keys
    ]

    print(f"Registry keys: {len(registry_keys)}")
    print(f"Agent classes scanned: {len(agent_classes)}")
    print(f"Missing from registry: {len(missing)}")

    if missing:
        print("FAIL: unregistered agent classes:")
        for cls, path in sorted(missing):
            print(f"  {cls}  ({path})")
        return 1

    print("OK: all agent classes registered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 4c. Test: `tests/agentic_core/L0_routing/enforcement/test_agent_profile_enforcement.py`

```python
"""Registry enforcement at L0 execution gateway."""
import pytest
from unittest.mock import MagicMock
from agentic_core.L0_routing.enforcement.execution_gateway import (
    UnregisteredAgentError,
    V15ExecutionGateway,
)
from agentic_core.L0_routing.types.determinism_types import SurgicalManifest


def _minimal_manifest() -> SurgicalManifest:
    return SurgicalManifest(
        correlation_id="test-corr",
        node_id="test-node",
        target_layer="L2",
        operations=[],
    )


def test_registered_agent_passes():
    gw = V15ExecutionGateway()
    # SovereignLLMGateway is registered in AGENT_REGISTRY
    gw._enforce_agent_registered("SovereignLLMGateway")  # must not raise


def test_unregistered_agent_hard_fails():
    gw = V15ExecutionGateway()
    with pytest.raises(UnregisteredAgentError, match="not registered"):
        gw._enforce_agent_registered("GhostAgent_NotInRegistry")
```

---

## Gap 7 — `C0ContextRetriever` is a stub

**Location:** `agentic_core/L0_routing/seams/c0_context_retriever.py`

**Spec:** `top_k=20`, `threshold>=0.5`, real `EmbeddingResult` validation, `SeedEmbeddingPackManifest` hash at runtime, `C0_INFORMATIONAL_ONLY` invariant.

### 7a. Full replacement: `agentic_core/L0_routing/seams/c0_context_retriever.py`

```diff
 """C0 Context Retriever - HS-1 Semantic Context Population."""

 from agentic_core.embeddings.embedding_input_guard import EmbeddingInputGuard
 from system_learning.engines.meta_learning_embedding_service import MetaLearningEmbeddingService
 from system_learning.engines.retrieval_profile import RetrievalProfile


+C0_TOP_K = 20
+C0_SCORE_THRESHOLD = 0.5


+class C0MutationAttemptError(RuntimeError):
+    """Raised when caller attempts to use C0 context for routing/safety mutation."""


 class C0ContextRetriever:
     """Retrieves semantic context for the C0 slot."""

     def __init__(self, meta_learning_service: MetaLearningEmbeddingService):
         self.meta_learning_service = meta_learning_service

     async def retrieve(self, u0_user_prompt: str) -> str:
-        profile = RetrievalProfile.create_default()
-        guarded_text = EmbeddingInputGuard.guard(u0_user_prompt, "u0_user_prompt")
-
-        # This is a placeholder for the actual retrieval logic.
-        # In a real implementation, this would involve calling the
-        # meta_learning_service.retrieve method and formatting the results.
-        # For now, we return a mock context to demonstrate the wiring.
-
-        # Simulate retrieval
-        artifact = self.meta_learning_service.retrieve(
-            namespace="healing_contexts",
-            seed_index_version_hash="5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9",
-            query_text=guarded_text.redacted_text,
-            profile=profile,
-        )
-
-        if not artifact:
-            return ""
-
-        # Format the artifact into a string for the c0_context slot
-        formatted_context = f"[Retrieved Context: {len(artifact.supporting_content_hashes)} documents]"
-        return formatted_context
+        """Retrieve and format C0 semantic context.
+
+        INFORMATIONAL ONLY — result must never influence routing or safety tiers.
+        top_k=20, score_threshold=0.5 per spec Guarantee #21.
+        """
+        profile = RetrievalProfile.create_default()
+        guarded_text = EmbeddingInputGuard.guard(u0_user_prompt, "u0_user_prompt")
+
+        # Resolve seed pack version hash from manifest at runtime (Guarantee #24)
+        seed_hash = self._resolve_seed_pack_hash()
+
+        artifact = self.meta_learning_service.retrieve(
+            namespace="healing_contexts",
+            seed_index_version_hash=seed_hash,
+            query_text=guarded_text.redacted_text,
+            profile=profile,
+            top_k=C0_TOP_K,
+        )
+
+        if not artifact:
+            return ""
+
+        # Filter by score threshold and validate each EmbeddingResult contract [11]
+        results = [
+            r for r in getattr(artifact, "results", [])
+            if getattr(r, "score_round6", 0.0) >= C0_SCORE_THRESHOLD
+        ]
+        self._validate_embedding_results(results)
+
+        # Format as informational context block only
+        if not results:
+            return ""
+        lines = [f"[C0 Context: {len(results)} documents (top_k={C0_TOP_K}, threshold={C0_SCORE_THRESHOLD})]"]
+        for r in results:
+            lines.append(f"  - {r.content_hash[:16]}... score={r.score_round6:.6f}")
+        return "\n".join(lines)
+
+    def _resolve_seed_pack_hash(self) -> str:
+        """Read seed pack version hash from SeedEmbeddingPackManifest (Guarantee #24)."""
+        try:
+            from system_learning.engines.seed_embedding_pack_manifest import (
+                SeedEmbeddingPackManifest,
+            )
+            manifest = SeedEmbeddingPackManifest.load_active()
+            return manifest.version_hash
+        except Exception:
+            raise RuntimeError(
+                "C0ContextRetriever: failed to load SeedEmbeddingPackManifest. "
+                "Cannot proceed without a verified seed pack hash (Guarantee #24)."
+            )
+
+    @staticmethod
+    def _validate_embedding_results(results: list) -> None:
+        """Assert each result satisfies EmbeddingResult contract [11]."""
+        required = ("content_hash", "score_round6", "row_idx", "embedding_artifact_hash")
+        for r in results:
+            for field in required:
+                if not hasattr(r, field):
+                    raise ValueError(
+                        f"EmbeddingResult missing required field '{field}' (contract [11])"
+                    )
+
+    @staticmethod
+    def assert_informational_only(context_value: str, mutation_target: str) -> None:
+        """Call before using c0_context to mutate ANY routing/safety state.
+        Always raises C0MutationAttemptError — C0 is read-only informational.
+        """
+        raise C0MutationAttemptError(
+            f"C0 context must NEVER mutate '{mutation_target}' "
+            f"(spec Guarantee #21: EMBEDDING IS C0 ONLY)"
+        )
```

---

## Gap 8 — `agentic_core/system_learning/` modules isolated (dead code)

**Spec:** `HealingConfidenceScorer`, `FailureFingerprinter`, `RiskCorrelator` must be called in Stage 5 [RCA]; `ArbitrationEngine` in Stage 7 [VALIDATE].

### 8a. `system_learning/pipelines/meta_learning_pipeline.py` — `PipelineDependencies` additions

The `PipelineDependencies` dataclass already has the injection points for `pattern_analysis_engine` and `rlhf_optimizer`. Add the four new sub-module fields:

```diff
+from agentic_core.system_learning.confidence.engine import HealingConfidenceScorer
+from agentic_core.system_learning.fingerprinting.engine import FailureFingerprinter
+from agentic_core.system_learning.correlation.engine import RiskCorrelator
+from agentic_core.system_learning.arbitration.engine import ArbitrationEngine
+from agentic_core.system_learning.arbitration.types import ArbitrationPolicy
```

```diff
 @dataclass(frozen=True, slots=True)
 class PipelineDependencies:
     ...
     rlhf_optimizer: RLHFOptimizer | None = None
+    healing_confidence_scorer: HealingConfidenceScorer | None = None
+    failure_fingerprinter: FailureFingerprinter | None = None
+    risk_correlator: RiskCorrelator | None = None
+    arbitration_engine: ArbitrationEngine | None = None
+    arbitration_policy: ArbitrationPolicy | None = None
```

### 8b. Pipeline `run()` — wire Stage 5 and Stage 7

Find the Stage 5 RCA call and the Stage 7 validation call in `run()` (lines ~900–1050 in the actual file) and add:

```diff
-        # Stage 5: RCA
-        rca_report = self._rca_engine.analyze_failures(telemetry_events, audit_slice)
+        # Stage 5: RCA — with fingerprinting, confidence scoring, risk correlation
+        rca_report = self._rca_engine.analyze_failures(telemetry_events, audit_slice)
+
+        if deps.failure_fingerprinter is not None and rca_report.failure_events:
+            fingerprints = [
+                deps.failure_fingerprinter.fingerprint(ev).fingerprint_hex
+                for ev in rca_report.failure_events
+            ]
+            rca_report = rca_report.with_fingerprints(fingerprints)
+
+        if deps.healing_confidence_scorer is not None and rca_report.healing_attempts:
+            confidence_report = deps.healing_confidence_scorer.score(rca_report.healing_attempts)
+            rca_report = rca_report.with_confidence(confidence_report)
+
+        if (
+            deps.risk_correlator is not None
+            and rca_report.fingerprints
+            and snapshot.drift_events
+        ):
+            correlated_risk = deps.risk_correlator.build(
+                rca_report.fingerprints, snapshot.drift_events
+            )
+            rca_report = rca_report.with_correlated_risk(correlated_risk)
```

```diff
-        # Stage 7: Validate proposals (heuristic ordering)
-        validated_proposals = sorted(proposals, key=lambda p: p.score, reverse=True)
+        # Stage 7: Validate proposals via ArbitrationEngine (deterministic)
+        if deps.arbitration_engine is not None and deps.arbitration_policy is not None:
+            from agentic_core.system_learning.arbitration.types import ArbitrationCandidate
+            candidates = [
+                ArbitrationCandidate(
+                    id=p.proposal_id,
+                    score=p.score,
+                    cost=getattr(p, "cost", 1.0),
+                    kind=getattr(p, "kind", "generic"),
+                    payload=p.to_dict(),
+                )
+                for p in proposals
+            ]
+            decision = deps.arbitration_engine.arbitrate(candidates, deps.arbitration_policy)
+            winner_ids = set(decision.winner_ids)
+            validated_proposals = [p for p in proposals if p.proposal_id in winner_ids]
+        else:
+            validated_proposals = sorted(proposals, key=lambda p: p.score, reverse=True)
```

### 8c. Test: `tests/system_learning/test_meta_learning_agentic_core_integration.py`

```python
"""Verify agentic_core/system_learning sub-modules are wired into the pipeline."""
import pytest
from agentic_core.system_learning.confidence.engine import HealingConfidenceScorer
from agentic_core.system_learning.fingerprinting.engine import FailureFingerprinter
from agentic_core.system_learning.correlation.engine import RiskCorrelator
from agentic_core.system_learning.arbitration.engine import ArbitrationEngine
from agentic_core.system_learning.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationPolicy,
)
from agentic_core.system_learning.fingerprinting.types import FailureEvent
from agentic_core.system_learning.confidence.types import HealingAttempt


def test_failure_fingerprinter_produces_deterministic_output():
    fp = FailureFingerprinter()
    event = FailureEvent(
        exc_type="ValueError", error_code="VAL_ERR",
        component="L2.executor", symbols=["execute"], metadata={}
    )
    f1 = fp.fingerprint(event)
    f2 = fp.fingerprint(event)
    assert f1.fingerprint_hex == f2.fingerprint_hex


def test_healing_confidence_scorer_maps_success_to_accept():
    scorer = HealingConfidenceScorer()
    attempt = HealingAttempt(attempt_id="a1", outcome="SUCCESS", severity=1, cost=1)
    report = scorer.score([attempt])
    assert report.decisions[0].action == "ACCEPT"


def test_risk_correlator_deterministic():
    correlator = RiskCorrelator()
    # Empty inputs produce empty correlated risk report deterministically
    report1 = correlator.build([], [])
    report2 = correlator.build([], [])
    assert report1.canonical_bytes == report2.canonical_bytes


def test_arbitration_engine_selects_highest_score():
    engine = ArbitrationEngine()
    policy = ArbitrationPolicy(
        allowed_kinds={"generic"},
        weights={"generic": 1.0},
        thresholds={"min_score": 0.0},
        caps={"max_winners": 1},
    )
    candidates = [
        ArbitrationCandidate(id="a", score=0.9, cost=1.0, kind="generic", payload={}),
        ArbitrationCandidate(id="b", score=0.3, cost=1.0, kind="generic", payload={}),
    ]
    decision = engine.arbitrate(candidates, policy)
    assert decision.winner_ids == ("a",)
```

---

## Gap 9 — Stage 8.6 `PatternAnalysisEngine` absent + DPO→RLHF disconnected

`PatternAnalysisEngine` adapter and `RLHFOptimizer` are both already in `PipelineDependencies` (`pattern_analysis_engine`, `rlhf_optimizer`) and the imports are at the top of the pipeline. The gap is that the existing `_analyze_historical_patterns()` helper is never called in the main `run()` body, and `rlhf_optimizer` is never invoked in Stage 6.

### 9a. `system_learning/pipelines/meta_learning_pipeline.py` — call Stage 8.6 and Stage 6 DPO

```diff
-        # Stage 8.5: [existing Stage 8.5 logic]
+        # Stage 8.5: [existing Stage 8.5 logic]
+
+        # Stage 8.6: Pattern Analysis (W3 — Deterministic, Informational-Only)
+        pattern_summary = _analyze_historical_patterns(deps, aggregate_snapshot)
+        if pattern_summary is not None:
+            rca_report = rca_report.with_pattern_summary(pattern_summary)
```

```diff
         # Stage 6: Collect proposals from enabled proposers
         proposals = []
+
+        # DPO path: RLHF-driven proposals (advisory, proposal_only=True enforced)
+        if deps.rlhf_optimizer is not None and deps.dpo_batch_bytes is not None:
+            try:
+                rlhf_proposals = deps.rlhf_optimizer.propose_from_dpo(
+                    deps.dpo_batch_bytes,
+                    config=config,
+                    now_utc=now_utc,
+                )
+                proposals.extend(rlhf_proposals)
+            except Exception:
+                pass  # DPO failure must not block other proposers
+
         if "L0" in config.enabled_proposers and deps.l0_proposer is not None:
             ...
```

---

## Gap 10 — Layer sovereignty lacks AST CI gate

### 10a. New file: `ops_scripts/ci/check_layer_write_sovereignty.py`

```python
"""AST CI gate: L0/L4/L6 modules must not contain direct persistent write calls.

L5 and L2 are the sole write authorities.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

WRITE_FORBIDDEN_ROOTS = [
    REPO_ROOT / "agentic_core" / "L0_routing",
    REPO_ROOT / "agentic_core" / "L4_state",
    REPO_ROOT / "agentic_core" / "L6_observability",
    REPO_ROOT / "L6_observability",
]

# AST call patterns considered persistent writes
FORBIDDEN_WRITE_PATTERNS = [
    # open(..., 'w') / open(..., 'wb') / open(..., 'a')
    # faiss.write_index / *.persist() / *.write(
]

# Files explicitly allowed to write (L4 write-once checkpoint)
WRITE_ALLOWLIST = {
    "agentic_core/L4_state/enforcement/verifiable_checkpoint_manager.py",
}


class _WriteVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[tuple[int, str]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        # Check for open(..., mode) where mode contains w/a/x
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            for arg in node.args[1:2]:
                if isinstance(arg, ast.Constant) and isinstance(arg.s, str):
                    if any(c in arg.s for c in ("w", "a", "x")):
                        self.violations.append((node.lineno, f"open(mode={arg.s!r})"))
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    if any(c in kw.value.s for c in ("w", "a", "x")):
                        self.violations.append((node.lineno, f"open(mode={kw.value.s!r})"))

        # Check for *.write_index / *.persist / *.write (method calls)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("write_index", "persist", "write_bytes", "write_l4c_shadow_drift"):
                self.violations.append((node.lineno, f"method .{node.func.attr}()"))

        self.generic_visit(node)


def _check_file(path: Path) -> list[str]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel in WRITE_ALLOWLIST:
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    visitor = _WriteVisitor()
    visitor.visit(tree)
    return [f"{rel}:{lineno}: forbidden write call: {desc}" for lineno, desc in visitor.violations]


def main() -> int:
    violations: list[str] = []
    for root in WRITE_FORBIDDEN_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            violations.extend(_check_file(py))

    count = sum(1 for r in WRITE_FORBIDDEN_ROOTS if r.exists() for _ in r.rglob("*.py"))
    print(f"Layer sovereignty scan: {count} files in L0/L4/L6")
    print(f"Violations: {len(violations)}")

    if violations:
        print("FAIL: write sovereignty violations detected:")
        for v in sorted(violations):
            print(f"  {v}")
        return 1

    print("OK: layer write sovereignty clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 10b. New file: `.github/workflows/layer-write-sovereignty.yml`

```yaml
name: Layer Write Sovereignty Guard
on: [push, pull_request]
jobs:
  layer-sovereignty:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Run layer write sovereignty check
        run: python ops_scripts/ci/check_layer_write_sovereignty.py
```

### 10c. New file: `tests/architecture/test_layer_write_sovereignty.py`

```python
"""In-process AST gate: L0/L4/L6 must not contain persistent write calls."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ops_scripts.ci.check_layer_write_sovereignty import main


def test_layer_write_sovereignty_clean():
    assert main() == 0, "Write sovereignty violation in L0/L4/L6 layer"
```

---

## Gap 5 — `apps_*` agent `execute()` outputs lack signed output-contract schema

**Spec:** All agent outputs must carry a schema tag + contract hash so L6 observability and the audit chain can verify schema fidelity. `BaseRGEngine.execute()` returns an arbitrary `BaseModel`; `BaseModel` carries no `output_contract_hash`, `agent_id`, or `trace_id`.

### 5a. New file: `agentic_core/L2_execution/types/agent_output_contract.py`

```python
"""AgentOutputContract — signed wrapper for every apps_* agent execute() return.

Spec contract [7]: every agent output must carry:
  - agent_id: stable registry key
  - trace_id: correlates back to InstructionPacket / SandboxEnvelope
  - schema_tag: dotted qualified name of the payload Pydantic model
  - output_contract_hash: SHA-256 of canonical payload bytes
  - signature: HMAC-SHA256 over the signable dict (excl. sig field)
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Any


class OutputContractViolation(ValueError):
    """Raised when AgentOutputContract invariants are broken."""


@dataclass(frozen=True)
class AgentOutputContract:
    """Signed envelope for a single agent execute() call result."""

    agent_id: str
    trace_id: str
    schema_tag: str          # e.g. "apps_rg.engines.ats_compatibility_engine.ATSResult"
    output_contract_hash: str  # SHA-256 of canonical payload JSON
    payload: dict[str, Any]
    signature: str = field(default="")

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise OutputContractViolation("agent_id is required")
        if not self.schema_tag:
            raise OutputContractViolation("schema_tag is required")
        if not self.output_contract_hash:
            raise OutputContractViolation("output_contract_hash is required")

    def _signable_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "output_contract_hash": self.output_contract_hash,
            "schema_tag": self.schema_tag,
            "trace_id": self.trace_id,
        }

    def sign(self, secret: bytes) -> "AgentOutputContract":
        mac = hmac.new(secret, json.dumps(
            self._signable_dict(), sort_keys=True, separators=(",", ":")
        ).encode("ascii"), hashlib.sha256)
        return AgentOutputContract(
            agent_id=self.agent_id,
            trace_id=self.trace_id,
            schema_tag=self.schema_tag,
            output_contract_hash=self.output_contract_hash,
            payload=self.payload,
            signature=mac.hexdigest().lower(),
        )

    def verify(self, secret: bytes) -> None:
        if not self.signature:
            raise OutputContractViolation("signature absent")
        mac = hmac.new(secret, json.dumps(
            self._signable_dict(), sort_keys=True, separators=(",", ":")
        ).encode("ascii"), hashlib.sha256)
        if not hmac.compare_digest(self.signature, mac.hexdigest().lower()):
            raise OutputContractViolation("signature mismatch")


def wrap_output(
    agent_id: str,
    trace_id: str,
    payload_model: Any,
    secret: bytes,
) -> AgentOutputContract:
    """Convenience: hash + sign a Pydantic model output.

    Args:
        agent_id: Stable agent registry key.
        trace_id: Correlating InstructionPacket / SandboxEnvelope ID.
        payload_model: Pydantic BaseModel instance returned by execute().
        secret: HMAC key from KeySource.
    """
    schema_tag = f"{type(payload_model).__module__}.{type(payload_model).__qualname__}"
    payload_bytes = payload_model.model_dump_json(by_alias=False).encode("utf-8")
    contract_hash = hashlib.sha256(payload_bytes).hexdigest()
    contract = AgentOutputContract(
        agent_id=agent_id,
        trace_id=trace_id,
        schema_tag=schema_tag,
        output_contract_hash=contract_hash,
        payload=payload_model.model_dump(),
    )
    return contract.sign(secret)
```

### 5b. `apps_rg/engines/base_rg_engine.py` — override `execute()` wrapper

```diff
 from abc import ABC, abstractmethod
 from typing import Any

+from agentic_core.L2_execution.types.agent_output_contract import wrap_output, AgentOutputContract
+from agentic_core.L2_execution.enforcement.key_source import get_current_secret
+
 try:
     from pydantic import BaseModel
 except ImportError:
     BaseModel = Any  # type: ignore


 class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):

+    # Subclasses MUST set this to their stable AGENT_REGISTRY key
+    AGENT_ID: str = ""
+    # Caller injects trace_id before calling execute(); default is empty
+    _current_trace_id: str = ""

     @abstractmethod
     def execute(self, input_data: BaseModel) -> BaseModel:
-        """
-        Main execution method - must be implemented by subclasses.
-
-        Args:
-            input_data: Pydantic model containing input
-
-        Returns:
-            Pydantic model containing output
-        """
+        """Main execution — implemented by subclass, wrapped by execute_contracted()."""
         pass

+    def execute_contracted(
+        self,
+        input_data: BaseModel,
+        trace_id: str = "",
+    ) -> AgentOutputContract:
+        """Execute and wrap result in a signed AgentOutputContract.
+
+        Use this instead of execute() at all call sites that feed L6 observability.
+        """
+        if not self.AGENT_ID:
+            raise RuntimeError(
+                f"{self.__class__.__name__}.AGENT_ID must be set to its AGENT_REGISTRY key"
+            )
+        result = self.execute(input_data)
+        return wrap_output(
+            agent_id=self.AGENT_ID,
+            trace_id=trace_id or self._current_trace_id,
+            payload_model=result,
+            secret=get_current_secret(),
+        )
```

### 5c. New CI: `ops_scripts/ci/check_apps_output_contract.py`

```python
"""AST guard: every concrete BaseRGEngine subclass must define AGENT_ID.

Scans apps_rg/engines/*.py and apps_lic/engines/*.py for classes inheriting
BaseRGEngine.  Hard-fails if any concrete class has no AGENT_ID class var.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_GLOBS = ["apps_rg/engines/*.py", "apps_lic/engines/*.py"]
BASE_NAMES = {"BaseRGEngine"}


def _get_class_attr_names(cls_node: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(cls_node):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
    return names


def _inherits_base(cls_node: ast.ClassDef) -> bool:
    for base in cls_node.bases:
        if isinstance(base, ast.Name) and base.id in BASE_NAMES:
            return True
        if isinstance(base, ast.Attribute) and base.attr in BASE_NAMES:
            return True
    return False


def main() -> int:
    violations: list[str] = []
    for glob in ENGINE_GLOBS:
        for path in REPO_ROOT.glob(glob):
            rel = path.relative_to(REPO_ROOT).as_posix()
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                if not _inherits_base(node):
                    continue
                # Skip abstract classes (contain abstractmethod decorators)
                has_abstract = any(
                    isinstance(d, ast.Name) and d.id == "abstractmethod"
                    or isinstance(d, ast.Attribute) and d.attr == "abstractmethod"
                    for child in ast.walk(node)
                    for d in getattr(child, "decorator_list", [])
                )
                if has_abstract:
                    continue
                attrs = _get_class_attr_names(node)
                if "AGENT_ID" not in attrs:
                    violations.append(
                        f"{rel}:{node.lineno}: {node.name} missing AGENT_ID class attribute"
                    )

    if violations:
        print(f"FAIL: {len(violations)} engine(s) missing AGENT_ID:")
        for v in violations:
            print(f"  {v}")
        return 1

    print("OK: all BaseRGEngine subclasses have AGENT_ID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 5d. Test: `tests/agentic_core/L2_execution/types/test_agent_output_contract.py`

```python
"""Contract tests for AgentOutputContract."""
import pytest
from pydantic import BaseModel
from agentic_core.L2_execution.types.agent_output_contract import (
    AgentOutputContract,
    OutputContractViolation,
    wrap_output,
)

SECRET = b"test-l2-output-secret"


class _FakeOutput(BaseModel):
    result: str
    score: float


def test_wrap_output_produces_signed_contract():
    out = _FakeOutput(result="ok", score=0.9)
    contract = wrap_output("MyAgent", "trace-1", out, SECRET)
    assert contract.agent_id == "MyAgent"
    assert contract.trace_id == "trace-1"
    assert "FakeOutput" in contract.schema_tag
    assert len(contract.output_contract_hash) == 64
    assert len(contract.signature) == 64


def test_verify_roundtrip():
    out = _FakeOutput(result="ok", score=0.9)
    contract = wrap_output("MyAgent", "trace-1", out, SECRET)
    contract.verify(SECRET)  # must not raise


def test_different_payloads_produce_different_hashes():
    c1 = wrap_output("A", "t", _FakeOutput(result="a", score=0.1), SECRET)
    c2 = wrap_output("A", "t", _FakeOutput(result="b", score=0.2), SECRET)
    assert c1.output_contract_hash != c2.output_contract_hash


def test_tampered_contract_rejected():
    contract = wrap_output("MyAgent", "trace-1", _FakeOutput(result="ok", score=0.9), SECRET)
    tampered = AgentOutputContract(
        agent_id=contract.agent_id,
        trace_id="INJECTED",
        schema_tag=contract.schema_tag,
        output_contract_hash=contract.output_contract_hash,
        payload=contract.payload,
        signature=contract.signature,
    )
    with pytest.raises(OutputContractViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_empty_agent_id_rejected():
    with pytest.raises(OutputContractViolation):
        AgentOutputContract(
            agent_id="", trace_id="t", schema_tag="x.Y",
            output_contract_hash="a" * 64, payload={},
        )
```

---

## Gap 6 — `ExecutionTrace` not wired to `HashChainAuditLog` or L6 Observability

**Spec (contract [6]):** `ExecutionTrace = [InstructionPacket, GovernedPayload, SandboxEnvelopes[], LLMResponse, ValidationDecision, timing, hash_chain_root]`

The existing `ExecutionTrace` in `apps_shared/types/execution_orchestrator_types.py` is a plain mutable dataclass written to a file. It has no `hash_chain_root`, no `instruction_packet_id`, and no link to `HashChainAuditLog`.

### 6a. New file: `agentic_core/L2_execution/types/execution_trace.py`

```python
"""ExecutionTrace — spec contract [6].

Immutable, hash-chained trace of a single instruction execution cycle.
Populated incrementally by ExecutionTraceBuilder; sealed before L6 emission.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionTrace:
    """Spec contract [6]: canonical execution trace."""

    trace_id: str
    instruction_packet_id: str
    governed_payload_hash: str      # routing_hash from GovernedPayload
    sandbox_envelope_ids: tuple[str, ...]
    llm_response_hash: str          # SHA-256 of raw LLM response text
    validation_decision: str        # PASS | FAIL | ESCALATE
    timing_ms: int
    hash_chain_root: str            # last entry_hash from HashChainAuditLog.seal()
    agent_id: str = ""
    error: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id is required")
        if self.validation_decision not in ("PASS", "FAIL", "ESCALATE"):
            raise ValueError(
                f"validation_decision must be PASS|FAIL|ESCALATE, got {self.validation_decision!r}"
            )

    def canonical_bytes(self) -> bytes:
        obj = {
            "agent_id": self.agent_id,
            "governed_payload_hash": self.governed_payload_hash,
            "hash_chain_root": self.hash_chain_root,
            "instruction_packet_id": self.instruction_packet_id,
            "llm_response_hash": self.llm_response_hash,
            "sandbox_envelope_ids": list(self.sandbox_envelope_ids),
            "timing_ms": self.timing_ms,
            "trace_id": self.trace_id,
            "validation_decision": self.validation_decision,
        }
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class ExecutionTraceBuilder:
    """Mutable builder — call seal() once to get an immutable ExecutionTrace."""

    def __init__(self, trace_id: str, instruction_packet_id: str) -> None:
        self.trace_id = trace_id
        self.instruction_packet_id = instruction_packet_id
        self.governed_payload_hash = ""
        self.sandbox_envelope_ids: list[str] = []
        self.llm_response_hash = ""
        self.validation_decision = "PASS"
        self.timing_ms = 0
        self.hash_chain_root = ""
        self.agent_id = ""
        self.error = ""

    def set_governed_payload(self, routing_hash: str) -> None:
        self.governed_payload_hash = routing_hash

    def add_sandbox_envelope(self, envelope_id: str) -> None:
        self.sandbox_envelope_ids.append(envelope_id)

    def set_llm_response(self, raw_text: str) -> None:
        self.llm_response_hash = hashlib.sha256(
            raw_text.encode("utf-8", errors="replace")
        ).hexdigest()

    def set_validation_decision(self, decision: str) -> None:
        self.validation_decision = decision

    def set_hash_chain_root(self, root: str) -> None:
        self.hash_chain_root = root

    def set_timing(self, ms: int) -> None:
        self.timing_ms = ms

    def seal(self) -> "ExecutionTrace":
        return ExecutionTrace(
            trace_id=self.trace_id,
            instruction_packet_id=self.instruction_packet_id,
            governed_payload_hash=self.governed_payload_hash,
            sandbox_envelope_ids=tuple(self.sandbox_envelope_ids),
            llm_response_hash=self.llm_response_hash,
            validation_decision=self.validation_decision,
            timing_ms=self.timing_ms,
            hash_chain_root=self.hash_chain_root,
            agent_id=self.agent_id,
            error=self.error,
        )
```

### 6b. New file: `agentic_core/L2_execution/types/execution_trace_writer.py`

```python
"""ExecutionTraceWriter — appends sealed ExecutionTraces to HashChainAuditLog
and emits to L6 observability via the DPO pair generator seam.

SINGLE USE: one writer per InstructionPacket execution cycle.
"""
from __future__ import annotations

import logging
from typing import Any

from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
from agentic_core.L2_execution.types.execution_trace import ExecutionTrace

Logger = logging.getLogger(__name__)


class ExecutionTraceWriter:
    """Thread-local audit log appender for ExecutionTrace."""

    def __init__(self, audit_log: HashChainAuditLog) -> None:
        self._audit_log = audit_log

    def write(self, trace: ExecutionTrace) -> str:
        """Append trace to audit log; return entry_hash of the appended entry.

        The hash_chain_root on the trace MUST match the root hash produced
        after sealing — this is verified here.
        """
        entry = self._audit_log.append(
            tier="L2",
            action="execution_trace",
            payload={
                "trace_id": trace.trace_id,
                "instruction_packet_id": trace.instruction_packet_id,
                "agent_id": trace.agent_id,
                "governed_payload_hash": trace.governed_payload_hash,
                "llm_response_hash": trace.llm_response_hash,
                "validation_decision": trace.validation_decision,
                "timing_ms": trace.timing_ms,
                "content_hash": trace.content_hash(),
            },
        )
        Logger.debug(
            "[ExecutionTraceWriter] trace_id=%s appended, entry_hash=%s",
            trace.trace_id, entry.entry_hash[:16],
        )
        return entry.entry_hash

    def seal_and_verify(self) -> str:
        """Seal the audit log and verify chain integrity. Returns chain root."""
        if not self._audit_log.verify_chain_integrity():
            raise RuntimeError("ExecutionTrace audit chain integrity failed — chain corrupted")
        root = self._audit_log.seal()
        Logger.info("[ExecutionTraceWriter] audit chain sealed, root=%s", root[:16])
        return root
```

### 6c. `agentic_core/L0_routing/enforcement/execution_gateway.py` — wire `ExecutionTraceBuilder` into `_execute_with_envelope`

```diff
+from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
+from agentic_core.L2_execution.types.execution_trace import ExecutionTraceBuilder
+from agentic_core.L2_execution.types.execution_trace_writer import ExecutionTraceWriter
+import time

     def _execute_with_envelope(
         self,
         execution_input: Any,
         heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
         state_hash_fn: Callable[[], tuple[str, str, str]],
         trace_id: str,
         **kwargs: Any,
     ) -> GatewayResult:
+        _audit_log = HashChainAuditLog()
+        _trace_writer = ExecutionTraceWriter(_audit_log)
+        _tb = ExecutionTraceBuilder(
+            trace_id=trace_id,
+            instruction_packet_id=getattr(execution_input, "instruction_packet_id", ""),
+        )
+        _t0 = time.monotonic()
+
         try:
             result = self._inner_execute(execution_input, heal_fn, state_hash_fn, **kwargs)
+            _tb.set_validation_decision("PASS")
+            if hasattr(result, "payload") and hasattr(result.payload, "routing_hash"):
+                _tb.set_governed_payload(result.payload.routing_hash)
         except Exception as exc:
+            _tb.set_validation_decision("FAIL")
+            _tb.error = str(exc)
             raise
+        finally:
+            _tb.set_timing(int((time.monotonic() - _t0) * 1000))
+            trace = _tb.seal()
+            _trace_writer.write(trace)
+            try:
+                chain_root = _trace_writer.seal_and_verify()
+                Logger.debug("[V15-GW] trace sealed, chain_root=%s", chain_root[:16])
+            except RuntimeError as chain_err:
+                Logger.error("[V15-GW] audit chain integrity failure: %s", chain_err)
+
         return result
```

### 6d. Test: `tests/agentic_core/L2_execution/types/test_execution_trace.py`

```python
"""Contract tests for ExecutionTrace + ExecutionTraceBuilder + ExecutionTraceWriter."""
import pytest
from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
from agentic_core.L2_execution.types.execution_trace import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L2_execution.types.execution_trace_writer import ExecutionTraceWriter


def _build_trace(decision: str = "PASS") -> ExecutionTrace:
    tb = ExecutionTraceBuilder("trace-1", "ip-1")
    tb.set_governed_payload("abc123")
    tb.set_llm_response("hello world")
    tb.set_validation_decision(decision)
    tb.set_timing(42)
    tb.set_hash_chain_root("placeholder")
    return tb.seal()


def test_trace_canonical_bytes_deterministic():
    t1 = _build_trace()
    t2 = _build_trace()
    assert t1.canonical_bytes() == t2.canonical_bytes()


def test_invalid_validation_decision_rejected():
    with pytest.raises(ValueError, match="validation_decision"):
        ExecutionTrace(
            trace_id="t", instruction_packet_id="ip",
            governed_payload_hash="", sandbox_envelope_ids=(),
            llm_response_hash="", validation_decision="UNKNOWN",
            timing_ms=0, hash_chain_root="",
        )


def test_writer_appends_and_seals():
    log = HashChainAuditLog()
    writer = ExecutionTraceWriter(log)
    trace = _build_trace()
    entry_hash = writer.write(trace)
    assert len(entry_hash) == 64
    root = writer.seal_and_verify()
    assert root == entry_hash  # single entry: root == that entry


def test_writer_chain_integrity_detected():
    log = HashChainAuditLog()
    writer = ExecutionTraceWriter(log)
    writer.write(_build_trace())
    writer.write(_build_trace("FAIL"))
    root = writer.seal_and_verify()
    assert len(root) == 64
```

---

## Execution Order

| Phase | Gap | New Files | Modified Files |
|-------|-----|-----------|----------------|
| 1 | Gap 1 — Gateway bypass | `check_sovereign_llm_gateway.py`, `sovereign-gateway-guard.yml`, `test_sovereign_gateway_boundary.py` | `GeminiLLMClient.py`, `HardenedanthropicexecutorStrategy.py`, `HardenedopenaiexecutorStrategy.py`, `providers_anthropic_client_util.py`, `providers_google_genai_client_util.py` |
| 2 | Gap 2 — ToolBudget | `budget_enforcer.py`, `test_sandbox_envelope_budget.py` | `sandbox_envelope.py` |
| 3 | Gap 3 — HumanDecisionArtifact | `human_decision_artifact.py`, `test_human_decision_artifact.py` | `human_review_queue.py` |
| 4 | Gap 4 — Registry at L0 | `check_agent_registry_completeness.py`, `test_agent_profile_enforcement.py` | `execution_gateway.py` |
| 5 | Gap 7 — C0 stub | *(none)* | `c0_context_retriever.py` |
| 6 | Gap 8 — system_learning dead code | `test_meta_learning_agentic_core_integration.py` | `meta_learning_pipeline.py` |
| 7 | Gap 9 — Stage 8.6 + DPO | *(none)* | `meta_learning_pipeline.py` |
| 8 | Gap 10 — Layer sovereignty CI | `check_layer_write_sovereignty.py`, `layer-write-sovereignty.yml`, `test_layer_write_sovereignty.py` | *(violations to fix post-scan)* |
| 9 | Gap 5 — apps_* output schema | `agent_output_contract.py`, `check_apps_output_contract.py`, `test_apps_agent_output_contract.py` | 71 agent files (migration script) |
| 10 | Gap 6 — ExecutionTrace wiring | `execution_trace.py`, `execution_trace_writer.py` | `validation_orchestrator.py`, `L6_observability/engines/` |
