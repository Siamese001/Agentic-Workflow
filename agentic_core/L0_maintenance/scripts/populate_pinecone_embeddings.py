#!/usr/bin/env python3
"""
Pinecone Semantic Knowledge Ingestion Script
=============================================

Populates the 'agentic-semantic-search' Pinecone index with 6 namespaces:
1. agents - All 272 agents from agent_discovery_full.json
2. mixins - Core extension mixins from agentic_core/utils/core_extensions
3. architecture-docs - Active markdown documentation
4. healing-patterns - RCA docs and healing patterns
5. api-contracts - Method signatures from agentic_core
6. config-blueprints - SSOT configuration files

Uses Pinecone's integrated inference (multilingual-e5-large) - no OpenAI needed.

Usage:
    python scripts/populate_pinecone_embeddings.py
    
Environment:
    PINECONE_API_KEY - Required for Pinecone access
"""

import os
import json
import ast
import glob
import time
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from pinecone import Pinecone
except ImportError:
    print("Error: pinecone-client not installed. Run: pip install pinecone-client")
    sys.exit(1)

# Configuration
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "agentic-semantic-search")
BATCH_SIZE = 50  # Records per batch for upsert

# Paths
AGENT_DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"
CORE_EXTENSIONS_DIR = PROJECT_ROOT / "agentic_core" / "utils" / "core_extensions"
BLUEPRINT_DIR = PROJECT_ROOT / "agentic_core" / "config" / "blueprint_sovereign"
DOCS_DIR = PROJECT_ROOT / "docs"
AGENTIC_CORE_DIR = PROJECT_ROOT / "agentic_core"


class PineconePopulator:
    """
    Orchestrates the extraction and upsertion of codebase metadata 
    into 6 distinct semantic namespaces in Pinecone.
    
    Uses Pinecone's integrated inference - embeddings are generated automatically
    when records contain the 'content' field (mapped to 'text' in index config).
    """
    
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        self.stats = {
            "agents": 0,
            "mixins": 0, 
            "architecture-docs": 0,
            "healing-patterns": 0,
            "api-contracts": 0,
            "config-blueprints": 0
        }
        print(f"✅ Initialized PineconePopulator for index: {PINECONE_INDEX_NAME}")

    def batch_upsert(self, records: List[Dict[str, Any]], namespace: str):
        """
        Upserts records to Pinecone in batches.
        
        Records must have 'content' field which will be embedded by Pinecone's
        integrated inference (multilingual-e5-large model).
        """
        total = len(records)
        if total == 0:
            print(f"  ⚠️  No records to upsert for '{namespace}'")
            return
            
        for i in range(0, total, BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            try:
                self.index.upsert_records(namespace=namespace, records=batch)
                print(f"  📤 Upserted batch {i//BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1) // BATCH_SIZE} to '{namespace}'")
            except Exception as e:
                print(f"  ❌ Error upserting batch: {e}")
                # Continue with next batch
        
        self.stats[namespace] = total
        print(f"✅ Completed namespace '{namespace}': {total} records")

    # -------------------------------------------------------------------------
    # 1. Namespace: agents
    # -------------------------------------------------------------------------
    def process_agents(self):
        """Extract all agents from agent_discovery_full.json"""
        print("\n" + "="*60)
        print("📦 Processing Agents...")
        print("="*60)
        
        if not AGENT_DISCOVERY_FILE.exists():
            print(f"  ⚠️  {AGENT_DISCOVERY_FILE} not found. Skipping.")
            return

        with open(AGENT_DISCOVERY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        records = []
        agents_list = data if isinstance(data, list) else data.get("agents", [])
        
        for agent in agents_list:
            class_name = agent.get('class_name', 'Unknown')
            description = agent.get('description', '').strip()
            key_methods = agent.get('key_methods', [])
            inheritance = agent.get('inheritance', [])
            
            # Construct rich semantic content
            content = (
                f"Agent: {class_name}. "
                f"Layer: {agent.get('layer', 'Unknown')}. "
                f"Territory: {agent.get('territory', 'Unknown')}. "
                f"Category: {agent.get('category', 'Uncategorized')}. "
                f"Description: {description}. "
                f"Key methods: {', '.join(key_methods[:5])}. "
                f"Inherits from: {', '.join(inheritance)}."
            )

            records.append({
                "_id": f"agent-{class_name}",
                "content": content,  # This field is embedded by Pinecone
                "class_name": class_name,
                "layer": agent.get("layer", "Unknown"),
                "territory": agent.get("territory", "Unknown"),
                "category": agent.get("category", "Uncategorized"),
                "path": agent.get("path", ""),
                "has_healing": agent.get("has_healing", False),
                "mcp_hardened": agent.get("mcp_hardened", False),
                "has_tests": agent.get("has_tests", False),
                "loc": agent.get("loc", 0),
                "type": "agent_definition"
            })
        
        self.batch_upsert(records, "agents")

    # -------------------------------------------------------------------------
    # 2. Namespace: mixins
    # -------------------------------------------------------------------------
    def process_mixins(self):
        """Extract mixins from core_extensions directory"""
        print("\n" + "="*60)
        print("🔧 Processing Mixins...")
        print("="*60)
        
        records = []
        
        if not CORE_EXTENSIONS_DIR.exists():
            print(f"  ⚠️  {CORE_EXTENSIONS_DIR} not found. Skipping.")
            return
            
        from agentic_core.utils.ssot_discovery import get_python_files
        for file_path in get_python_files(CORE_EXTENSIONS_DIR):
            if file_path.name.startswith("__"):
                continue
                
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError) as e:
                print(f"  ⚠️  Skipping {file_path.name}: {e}")
                continue

            for node in tree.body:
                if isinstance(node, ast.ClassDef) and "Mixin" in node.name:
                    docstring = ast.get_docstring(node) or "No documentation available."
                    methods = [
                        m.name for m in node.body 
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                        and not m.name.startswith("_")
                    ]
                    
                    content = (
                        f"Mixin: {node.name}. "
                        f"Purpose: {docstring[:500]}. "
                        f"Public methods: {', '.join(methods[:10])}."
                    )
                    
                    records.append({
                        "_id": f"mixin-{node.name}",
                        "content": content,
                        "name": node.name,
                        "methods": json.dumps(methods[:20]),  # Store as JSON string
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "layer": "L0",
                        "type": "mixin_definition"
                    })
        
        self.batch_upsert(records, "mixins")

    # -------------------------------------------------------------------------
    # 3. Namespace: architecture-docs
    # -------------------------------------------------------------------------
    def process_docs(self):
        """Extract markdown documentation from docs/ and root"""
        print("\n" + "="*60)
        print("📚 Processing Architecture Docs...")
        print("="*60)
        
        records = []
        
        # Phase 6: Use ssot_discovery instead of rglob for MD files
        from agentic_core.utils.ssot_discovery import get_markdown_files
        all_files = get_markdown_files(PROJECT_ROOT)
            
        for file_path in all_files:
            path_str = str(file_path)
                
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                print(f"  ⚠️  Skipping {file_path.name}: {e}")
                continue
            
            if len(content) < 50:  # Skip very small files
                continue
                
            filename = file_path.name
            # Create summary embedding (first 1500 chars + filename)
            embed_content = (
                f"Document: {filename}. "
                f"Content: {content[:1500]}"
            )
            
            # Determine category from filename
            category = "general"
            if "RCA" in filename.upper():
                category = "rca"
            elif "IMPLEMENTATION" in filename.upper():
                category = "implementation"
            elif "PHASE" in filename.upper():
                category = "phase_report"
            elif "README" in filename.upper():
                category = "readme"
            
            records.append({
                "_id": f"doc-{filename.replace('.', '_').replace(' ', '_')}",
                "content": embed_content,
                "filename": filename,
                "path": str(file_path.relative_to(PROJECT_ROOT)),
                "length": len(content),
                "category": category,
                "type": "documentation"
            })
            
        self.batch_upsert(records, "architecture-docs")

    # -------------------------------------------------------------------------
    # 4. Namespace: healing-patterns
    # -------------------------------------------------------------------------
    def process_healing(self):
        """Extract healing patterns from RCA docs and healing-related files"""
        print("\n" + "="*60)
        print("🩹 Processing Healing Patterns...")
        print("="*60)
        
        records = []
        
        # Find RCA files
        rca_patterns = [
            PROJECT_ROOT / "*.md",
            DOCS_DIR / "**/*.md" if DOCS_DIR.exists() else None,
            PROJECT_ROOT / "agentic_core" / "L6_observability" / "reports" / "*.md"
        ]
        
        rca_files = []
        for pattern in rca_patterns:
            if pattern:
                # Absolute Zero: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery import get_python_files
        if "*" in str(pattern):
            rca_files.extend(list(get_python_files(pattern.parent)))
        else:
            rca_files.append(pattern)
        
        for file_path in rca_files:
            if not file_path.exists() or not file_path.is_file():
                continue
                
            filename = file_path.name
            # Only process RCA and healing-related docs
            if not any(kw in filename.upper() for kw in ["RCA", "FIX", "HEALING", "REPORT", "COMPLETE"]):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue
            
            if len(content) < 100:
                continue
                
            # Extract problem/solution pattern
            embed_content = (
                f"Healing Pattern: {filename}. "
                f"Content: {content[:2000]}"
            )
            
            records.append({
                "_id": f"healing-{filename.replace('.', '_').replace(' ', '_')}",
                "content": embed_content,
                "source": filename,
                "path": str(file_path.relative_to(PROJECT_ROOT)),
                "type": "healing_pattern"
            })
            
        self.batch_upsert(records, "healing-patterns")

    # -------------------------------------------------------------------------
    # 5. Namespace: api-contracts
    # -------------------------------------------------------------------------
    def process_api_contracts(self):
        """Extract method signatures from agentic_core classes"""
        print("\n" + "="*60)
        print("📋 Processing API Contracts...")
        print("="*60)
        
        records = []
        
        if not AGENTIC_CORE_DIR.exists():
            print(f"  ⚠️  {AGENTIC_CORE_DIR} not found. Skipping.")
            return
        
        # Phase 4.1: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files
        for file_path in get_python_files(AGENTIC_CORE_DIR):
            path_str = str(file_path)
                
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):
                continue
                
            # Determine layer from path
            layer = "Unknown"
            for l in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
                if l in path_str:
                    layer = l
                    break
            
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Skip private methods except important ones
                            if item.name.startswith("_") and item.name not in ["__init__", "__call__"]:
                                continue
                            
                            # Build signature
                            args = []
                            for arg in item.args.args:
                                arg_str = arg.arg
                                if arg.annotation:
                                    try:
                                        arg_str += f": {ast.unparse(arg.annotation)}"
                                    except:
                                        pass
                                args.append(arg_str)
                            
                            # Get return type
                            return_type = ""
                            if item.returns:
                                try:
                                    return_type = f" -> {ast.unparse(item.returns)}"
                                except:
                                    pass
                            
                            signature = f"{item.name}({', '.join(args)}){return_type}"
                            docstring = ast.get_docstring(item) or ""
                            
                            content = (
                                f"Method: {item.name}. "
                                f"Class: {class_name}. "
                                f"Signature: {signature}. "
                                f"Documentation: {docstring[:300]}."
                            )
                            
                            records.append({
                                "_id": f"contract-{class_name}-{item.name}",
                                "content": content,
                                "method": item.name,
                                "class_name": class_name,
                                "signature": signature,
                                "layer": layer,
                                "path": str(file_path.relative_to(PROJECT_ROOT)),
                                "type": "api_contract"
                            })
        
        # Deduplicate by _id (keep first occurrence)
        seen = set()
        unique_records = []
        for r in records:
            if r["_id"] not in seen:
                seen.add(r["_id"])
                unique_records.append(r)
        
        self.batch_upsert(unique_records, "api-contracts")

    # -------------------------------------------------------------------------
    # 6. Namespace: config-blueprints
    # -------------------------------------------------------------------------
    def process_configs(self):
        """Extract SSOT configuration blueprints"""
        print("\n" + "="*60)
        print("⚙️  Processing Config Blueprints...")
        print("="*60)
        
        records = []
        
        if not BLUEPRINT_DIR.exists():
            print(f"  ⚠️  {BLUEPRINT_DIR} not found. Skipping.")
            return
            
        from agentic_core.utils.ssot_discovery import get_python_files
        for file_path in get_python_files(BLUEPRINT_DIR):
            if file_path.name.startswith("__"):
                continue
                
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            filename = file_path.name
            
            # Extract key definitions (constants, classes)
            definitions = []
            try:
                tree = ast.parse(content)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id.isupper():
                                definitions.append(target.id)
                    elif isinstance(node, ast.ClassDef):
                        definitions.append(f"class {node.name}")
            except:
                pass
            
            embed_content = (
                f"Configuration Blueprint: {filename}. "
                f"Defines: {', '.join(definitions[:20])}. "
                f"Content preview: {content[:1000]}"
            )
            
            records.append({
                "_id": f"config-{filename.replace('.', '_')}",
                "content": embed_content,
                "filename": filename,
                "definitions": json.dumps(definitions[:30]),
                "path": str(file_path.relative_to(PROJECT_ROOT)),
                "type": "ssot_blueprint"
            })
                
        self.batch_upsert(records, "config-blueprints")

    def run_all(self):
        """Execute all processing steps."""
        start_time = time.time()
        print("\n" + "="*60)
        print("🚀 STARTING SEMANTIC KNOWLEDGE INGESTION")
        print("="*60)
        print(f"Index: {PINECONE_INDEX_NAME}")
        print(f"Project Root: {PROJECT_ROOT}")
        
        self.process_agents()
        self.process_mixins()
        self.process_docs()
        self.process_healing()
        self.process_configs()
        self.process_api_contracts()  # Largest, do last
        
        duration = time.time() - start_time
        
        print("\n" + "="*60)
        print("✅ INGESTION COMPLETE")
        print("="*60)
        print(f"Duration: {duration:.2f} seconds")
        print("\nRecords per namespace:")
        total = 0
        for ns, count in self.stats.items():
            print(f"  📁 {ns}: {count} records")
            total += count
        print(f"\n  📊 TOTAL: {total} records")
        print("="*60)
        
        return self.stats


def main():
    """Main entry point."""
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ Error: PINECONE_API_KEY environment variable not set.")
        print("   Set it with: $env:PINECONE_API_KEY='your-key'")
        sys.exit(1)
        
    try:
        populator = PineconePopulator()
        populator.run_all()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
