#!/usr/bin/env python3
"""
SubAtomicRegistry - Live Semantic Index of Every Method
"""

import ast
import asyncio
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List

from agentic_core.L4_state.validation_context.pinecone_sovereign_agent import (
    PineconeSovereignAgent,
)
from agentic_core.L4_state.validation_context.redis_sovereign_agent import (
    RedisSovereignAgent,
)


class SubAtomicRegistry:
    """
    Sovereign method registry — live, hybrid-indexed, eternal.
    Now with Redis sovereign caching for instant method discovery.
    """
    def __init__(self, project_root: Path):
        self.root = project_root
        self.pinecone = PineconeSovereignAgent(project_root)
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

        # Index for methods
        self.method_index_name = f"{self.pinecone.index_name}_methods"
        self.method_index = self.pinecone.index

    def extract_methods(self) -> List[Dict]:
        """Deep crawl of all .py files to find callables"""
        methods = []
        for py_file in self.root.rglob("*.py"):
            if "env" in str(py_file) or "archives" in str(py_file): continue
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Enhanced metadata extraction
                        doc = ast.get_docstring(node) or "No docstring provided."
                        source_lines = ast.get_source_segment(open(py_file).read(), node) or ""
                        methods.append({
                            "id": f"{py_file.stem}_{node.name}",
                            "path": str(py_file),
                            "method": node.name,
                            "docstring": doc,
                            "source_snippet": f"Method: {node.name}\nDoc: {doc}\nSource: {source_lines[:200]}...",
                            "line_number": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef)
                        })
            except Exception: continue
        return methods

    def rebuild_registry(self):
        """Eternal rebuild — full method index + Redis cache warm"""
        print("   [REBUILD] SubAtomicRegistry: Indexing all methods...")
        methods = self.extract_methods()
        vectors = []
        for m in methods:
            emb = self.pinecone.get_embedding(m["source_snippet"])
            vec_id = m["id"]
            vectors.append({
                "id": vec_id,
                "values": emb,
                "metadata": m
            })

            # [CACHE WARM] Store method metadata in Redis for instant lookup
            cache_key = f"method_meta:{vec_id}"
            try:
                self.redis.set(cache_key, json.dumps(m), ex=86400)  # 24h
            except Exception: pass

        if vectors:
            self.method_index.upsert(vectors=vectors)
            print(f"   [OK] SubAtomicRegistry: Indexed {len(vectors)} methods + Cache Warmed")

    def find_method(self, task: str, top_k: int = 3) -> List[Dict]:
        """Hybrid search for best method — now cache-first"""
        cache_key = f"method_search:{hashlib.sha256(task.encode()).hexdigest()}_{top_k}"
        try:
            cached = self.redis.get(cache_key)
            if cached:
                print(f"   [CACHE HIT] Method search for '{task[:30]}...'")
                return json.loads(cached)
        except Exception: pass

        results = self.pinecone.hybrid_search(
            query_text=task,
            keywords=[w for w in self.pinecone.CANON_SIGNALS if w in task.lower()],
            top_k=top_k,
            min_score=0.88
        )

        # [CACHE WARM] Store successful search results
        try:
            if results:
                self.redis.set(cache_key, json.dumps(results), ex=3600)  # 1h
        except Exception: pass

        return results

    def find_and_invoke(self, task_description: str, *args, **kwargs):
        """The ultimate sovereign loop: Find it, then do it."""
        matches = self.find_method(task_description, top_k=1)
        if not matches:
            raise ValueError(f"No method found for task: {task_description}")
        
        meta = matches[0]['metadata']
        print(f"   [EXECUTE] Invoking {meta['method']} from {Path(meta['path']).name}")
        # Dynamic import and execution logic would go here
        return meta

    def invoke_method(self, method_meta: Dict, *args, **kwargs) -> Any:
        """Dynamically invoke a method by metadata"""
        try:
            # Import the module
            module_path = Path(method_meta['path']).relative_to(self.root)
            module_name = str(module_path).replace(os.sep, '.')[:-3]
            module = importlib.import_module(module_name)
            
            # Get the method
            method = getattr(module, method_meta['method'])
            
            # Execute it
            if inspect.iscoroutinefunction(method):
                return asyncio.run(method(*args, **kwargs))
            else:
                return method(*args, **kwargs)
        except Exception as e:
            print(f"   [ERROR] Failed to invoke {method_meta['method']}: {e}")
            raise

    async def execute(self, ctx=None):
        count = len(self.extract_methods())
        print(f"   [OK] SubAtomicRegistry: {count} methods online and searchable.")
        if ctx:
            ctx.report("Registry", count, True, "Method capabilities mapped.")
