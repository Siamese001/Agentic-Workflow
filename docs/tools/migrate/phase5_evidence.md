# Phase 5 Evidence: Pre-commit Clean + Seam-level Test Restoration

## WAVE 5.1 — Reset to clean baseline

### Current state capture:
- git rev-parse HEAD:
6a01fcf00420ca267f658b4602352e4f063f6313

### git status --porcelain=v1 (before pre-commit):
M  artifacts/evidence/phase11_isolated_branch_verification.md
 M tests/unit/test_embedding_sovereign_agent_uses_wrappers.py
?? artifacts/migration/phase5_evidence.md

### pre-commit run -a:
T0: Trailing Whitespace..................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing tests/unit/test_embedding_sovereign_agent_uses_wrappers.py


### git status --porcelain=v1 (after pre-commit):
M  artifacts/evidence/phase11_isolated_branch_verification.md
 M tests/unit/test_embedding_sovereign_agent_uses_wrappers.py
?? artifacts/migration/phase5_evidence.md

### pytest unit test:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 3 items

tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_no_direct_sdk_imports_in_embedding_sovereign_agent [32mPASSED[0m[32m [ 33%][0m
tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_embedding_sovereign_agent_uses_wrapper_factories [32mPASSED[0m[32m [ 66%][0m
tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_embedding_sovereign_agent_no_direct_sdk_instantiation [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================
0.10s call     tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_no_direct_sdk_imports_in_embedding_sovereign_agent

(8 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m3 passed[0m[32m in 0.14s[0m[32m ==============================[0m

### pytest guardian test:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

tests/guardian/test_no_direct_llm_sdk_imports.py::test_no_direct_llm_sdk_imports_in_agentic_core [32mPASSED[0m[32m [ 50%][0m
tests/guardian/test_no_direct_llm_sdk_imports.py::test_only_allowed_direct_imports_in_sdks_mcps [32mPASSED[0m[32m [100%][0m

============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================

=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 2
Passed: 2
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
1.06s call     tests/guardian/test_no_direct_llm_sdk_imports.py::test_no_direct_llm_sdk_imports_in_agentic_core
0.01s call     tests/guardian/test_no_direct_llm_sdk_imports.py::test_only_allowed_direct_imports_in_sdks_mcps

(4 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m2 passed[0m[32m in 1.11s[0m[32m ==============================[0m

### git --no-pager diff:
diff --git a/tests/unit/test_embedding_sovereign_agent_uses_wrappers.py b/tests/unit/test_embedding_sovereign_agent_uses_wrappers.py
index 994596f8c..6ef7e90bb 100644
--- a/tests/unit/test_embedding_sovereign_agent_uses_wrappers.py
+++ b/tests/unit/test_embedding_sovereign_agent_uses_wrappers.py
@@ -4,12 +4,12 @@ Tests that EmbeddingSovereignAgent instantiates wrapper clients via factory func
 """

 import ast
+import sys
+import types
 from unittest.mock import MagicMock

 import pytest

-from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import EmbeddingSovereignAgent
-

 def test_no_direct_sdk_imports_in_embedding_sovereign_agent():
     """AST-based test that EmbeddingSovereignAgent has no direct SDK imports."""
@@ -38,53 +38,95 @@ def test_no_direct_sdk_imports_in_embedding_sovereign_agent():
     assert not found_imports, f"Found direct SDK imports: {found_imports}"


-def test_embedding_sovereign_agent_uses_wrapper_factories(monkeypatch):
-    """Test that EmbeddingSovereignAgent uses client wrapper factories."""
-    # Verify that the module imports the wrapper factories
-    import agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent as module
-
-    # Parse the module AST to verify wrapper factory imports
-    with open(module.__file__, encoding="utf-8") as f:
-        source = f.read()
-
-    tree = ast.parse(source)
-
-    # Check for wrapper factory imports
-    wrapper_imports = []
-    for node in ast.walk(tree):
-        if isinstance(node, ast.ImportFrom):
-            if node.module == "data.sdks_mcps.client_wrappers":
-                for alias in node.names:
-                    if alias.name in ["create_openai_client", "create_vertex_client"]:
-                        wrapper_imports.append(alias.name)
-
-    assert "create_openai_client" in wrapper_imports, "Should import create_openai_client"
-    assert "create_vertex_client" in wrapper_imports, "Should import create_vertex_client"
-
-    # Verify the wrapper factories are callable (they exist in the module)
-    from data.sdks_mcps.client_wrappers import create_openai_client, create_vertex_client
-    assert callable(create_openai_client), "create_openai_client should be callable"
-    assert callable(create_vertex_client), "create_vertex_client should be callable"
-
-    # Verify that the embedding methods reference the wrapper factories
-    # by checking the source code for factory function calls
-    assert "create_vertex_client()" in source, "Should call create_vertex_client"
-    assert "create_openai_client()" in source, "Should call create_openai_client"
-
-    # Verify no direct SDK imports in the embedding methods
-    forbidden_imports = {"openai", "anthropic", "google.generativeai"}
-    direct_sdk_imports = []
-
-    for node in ast.walk(tree):
-        if isinstance(node, ast.Import):
-            for alias in node.names:
-                if any(alias.name.startswith(module_name) for module_name in forbidden_imports):
-                    direct_sdk_imports.append(f"import {alias.name}")
-        elif isinstance(node, ast.ImportFrom):
-            if node.module and any(node.module.startswith(module_name) for module_name in forbidden_imports):
-                direct_sdk_imports.append(f"from {node.module} import *")
-
-    assert not direct_sdk_imports, f"Found direct SDK imports: {direct_sdk_imports}"
+def test_embedding_sovereign_agent_uses_wrapper_factories():
+    """Test that EmbeddingSovereignAgent uses client wrapper factories via sys.modules injection."""
+
+    # Create sentinel objects to track factory calls
+    sentinel_vertex = MagicMock()
+    sentinel_openai = MagicMock()
+    sentinel_anthropic = MagicMock()
+
+    # Track factory function calls
+    vertex_calls = []
+    openai_calls = []
+    anthropic_calls = []
+
+    def mock_vertex_factory():
+        vertex_calls.append(1)
+        return sentinel_vertex
+
+    def mock_openai_factory():
+        openai_calls.append(1)
+        return sentinel_openai
+
+    def mock_anthropic_factory():
+        anthropic_calls.append(1)
+        return sentinel_anthropic
+
+    # Create shim module
+    wrapper_shim = types.ModuleType("data.sdks_mcps.client_wrappers")
+    wrapper_shim.create_vertex_client = mock_vertex_factory
+    wrapper_shim.create_openai_client = mock_openai_factory
+    wrapper_shim.create_anthropic_client = mock_anthropic_factory
+    wrapper_shim.__all__ = ["create_vertex_client", "create_openai_client", "create_anthropic_client"]
+
+    # Inject shim into sys.modules BEFORE importing the target module
+    sys.modules["data.sdks_mcps.client_wrappers"] = wrapper_shim
+
+    try:
+        # Now import and reload the module to ensure it uses our shim
+        import importlib
+        import agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent as module
+        importlib.reload(module)
+
+        # Test that we can import the class without errors
+        EmbeddingSovereignAgent = module.EmbeddingSovereignAgent
+        assert EmbeddingSovereignAgent is not None, "Should be able to import EmbeddingSovereignAgent"
+
+        # Create a minimal mock instance to test the embedding methods
+        # We'll create a mock object and bind the methods to it
+        mock_agent = MagicMock()
+        mock_agent._get_gemini_embedding = EmbeddingSovereignAgent._get_gemini_embedding.__get__(mock_agent)
+        mock_agent._get_openai_embedding = EmbeddingSovereignAgent._get_openai_embedding.__get__(mock_agent)
+
+        # Test the embedding methods to trigger factory calls
+        import asyncio
+
+        async def test_embeddings():
+            # Mock the return values for the embedding methods
+            sentinel_vertex.embed_content.return_value = {"embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}
+            sentinel_openai.embeddings.create.return_value = MagicMock(data=[MagicMock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])])
+
+            # Test Gemini embedding method
+            gemini_result = await mock_agent._get_gemini_embedding("test content")
+            assert gemini_result == [0.1, 0.2, 0.3, 0.4, 0.5], "Gemini embedding should work"
+
+            # Test OpenAI embedding method
+            openai_result = await mock_agent._get_openai_embedding("test content")
+            assert openai_result == [0.1, 0.2, 0.3, 0.4, 0.5], "OpenAI embedding should work"
+
+        # Run the async test
+        asyncio.run(test_embeddings())
+
+        # Verify factory functions were called
+        assert len(vertex_calls) >= 1, f"create_vertex_client should be called at least once, was called {len(vertex_calls)} times"
+        assert len(openai_calls) >= 1, f"create_openai_client should be called at least once, was called {len(openai_calls)} times"
+
+        # Verify the mock clients were used
+        sentinel_vertex.embed_content.assert_called()
+        sentinel_openai.embeddings.create.assert_called()
+
+    finally:
+        # Clean up sys.modules
+        if "data.sdks_mcps.client_wrappers" in sys.modules:
+            del sys.modules["data.sdks_mcps.client_wrappers"]
+        # Also clean up any cached imports
+        modules_to_clean = [
+            "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent",
+        ]
+        for mod_name in modules_to_clean:
+            if mod_name in sys.modules:
+                del sys.modules[mod_name]


 def test_embedding_sovereign_agent_no_direct_sdk_instantiation():
@@ -104,6 +146,6 @@ def test_embedding_sovereign_agent_no_direct_sdk_instantiation():

 if __name__ == "__main__":
     test_no_direct_sdk_imports_in_embedding_sovereign_agent()
-    test_embedding_sovereign_agent_uses_wrapper_factories(pytest.MonkeyPatch())
+    test_embedding_sovereign_agent_uses_wrapper_factories()
     test_embedding_sovereign_agent_no_direct_sdk_instantiation()
     print("All EmbeddingSovereignAgent wrapper tests passed!")
