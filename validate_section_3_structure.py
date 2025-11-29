#!/usr/bin/env python3
"""
Section 3 Structure Validation Script
Tests all imports and functionality of the new Section 3 aligned structure
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test all new component imports"""
    print("🔍 Testing Section 3 Structure Imports...")
    print("=" * 60)
    
    results = {
        "passed": [],
        "failed": [],
        "total": 0
    }
    
    # Test L2 Execution Tools (25 tools)
    print("\n📦 Testing L2 Execution Tools...")
    l2_tools = [
        # RETRIEVAL Family
        "agentic_core.l2_execution.tools.create_bm25_tool",
        "agentic_core.l2_execution.tools.create_dense_retrieval_tool",
        "agentic_core.l2_execution.tools.create_hybrid_router_tool",
        "agentic_core.l2_execution.tools.create_reranker_tool",
        "agentic_core.l2_execution.tools.create_snippet_extraction_tool",
        "agentic_core.l2_execution.tools.create_text_cleaning_tool",
        
        # RAG Family
        "agentic_core.l2_execution.tools.create_rrf_fusion_tool",
        "agentic_core.l2_execution.tools.create_rag_filter_tool",
        "agentic_core.l2_execution.tools.create_rag_query_rewriter_tool",
        "agentic_core.l2_execution.tools.create_hyde_tool",
        "agentic_core.l2_execution.tools.create_chunking_tool",
        
        # KG Family
        "agentic_core.l2_execution.tools.create_kg_lookup_tool",
        "agentic_core.l2_execution.tools.create_kg_traversal_tool",
        "agentic_core.l2_execution.tools.create_kg_relation_expand_tool",
        
        # TEMPORAL Family
        "agentic_core.l2_execution.tools.create_temporal_extraction_tool",
        "agentic_core.l2_execution.tools.create_temporal_invalidation_tool",
        "agentic_core.l2_execution.tools.create_temporal_event_builder_tool",
        
        # INFRA Family
        "agentic_core.l2_execution.tools.create_embedding_tool",
        "agentic_core.l2_execution.tools.create_search_tool",
        "agentic_core.l2_execution.tools.create_http_tool",
        "agentic_core.l2_execution.tools.create_sql_tool",
        "agentic_core.l2_execution.tools.create_file_tool",
        "agentic_core.l2_execution.tools.create_serialization_tool",
        "agentic_core.l2_execution.tools.create_crypto_hash_tool",
        "agentic_core.l2_execution.tools.create_diff_tool"
    ]
    
    for import_path in l2_tools:
        results["total"] += 1
        if test_single_import(import_path):
            results["passed"].append(import_path)
        else:
            results["failed"].append(import_path)
    
    # Test L3 Orchestration
    print("\n🎯 Testing L3 Orchestration...")
    l3_components = [
        "agentic_core.l3_orchestration.framework.create_arbitration_engine"
    ]
    
    for import_path in l3_components:
        results["total"] += 1
        if test_single_import(import_path):
            results["passed"].append(import_path)
        else:
            results["failed"].append(import_path)
    
    # Test L4 Memory State
    print("\n💾 Testing L4 Memory State...")
    l4_components = [
        "agentic_core.l4_memory_state.providers.create_redis_provider"
    ]
    
    for import_path in l4_components:
        results["total"] += 1
        if test_single_import(import_path):
            results["passed"].append(import_path)
        else:
            results["failed"].append(import_path)
    
    # Test L5 Safety
    print("\n🛡️ Testing L5 Safety...")
    l5_components = [
        "agentic_core.l5_safety.filters.create_injection_detector",
        "agentic_core.l5_safety.validators.create_content_validator"
    ]
    
    for import_path in l5_components:
        results["total"] += 1
        if test_single_import(import_path):
            results["passed"].append(import_path)
        else:
            results["failed"].append(import_path)
    
    # Test Prompt Governance
    print("\n📋 Testing Prompt Governance...")
    governance_components = [
        "agentic_core.prompt_governance.create_prompt_manifest",
        "agentic_core.prompt_governance.create_prompt_acl",
        "agentic_core.prompt_governance.create_prompt_definition",
        "agentic_core.prompt_governance.create_prompt_metadata",
        "agentic_core.prompt_governance.create_prompt_version",
        "agentic_core.prompt_governance.create_prompt_domain",
        "agentic_core.prompt_governance.create_injection_policy",
        "agentic_core.prompt_governance.PromptManifest",
        "agentic_core.prompt_governance.PromptACL",
        "agentic_core.prompt_governance.PromptDefinition",
        "agentic_core.prompt_governance.PromptMetadata",
        "agentic_core.prompt_governance.PromptVersion",
        "agentic_core.prompt_governance.PromptDomain",
        "agentic_core.prompt_governance.InjectionPolicy"
    ]
    
    for import_path in governance_components:
        results["total"] += 1
        if test_single_import(import_path):
            results["passed"].append(import_path)
        else:
            results["failed"].append(import_path)
    
    return results

def test_single_import(import_path):
    """Test a single import path"""
    try:
        module_path, component_name = import_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[component_name])
        component = getattr(module, component_name)
        print(f"  ✅ {import_path}")
        return True
    except Exception as e:
        print(f"  ❌ {import_path} - ERROR: {str(e)}")
        return False

def test_functionality():
    """Test basic functionality of key components"""
    print("\n🔧 Testing Basic Functionality...")
    print("=" * 60)
    
    functionality_results = {
        "passed": [],
        "failed": []
    }
    
    # Test L2 Tools instantiation
    try:
        from agentic_core.l2_execution.tools import create_bm25_tool
        tool = create_bm25_tool()
        if hasattr(tool, 'search'):
            functionality_results["passed"].append("BM25 Tool instantiation")
        else:
            functionality_results["failed"].append("BM25 Tool missing search method")
    except Exception as e:
        functionality_results["failed"].append(f"BM25 Tool failed: {e}")
    
    # Test L3 Orchestration
    try:
        from agentic_core.l3_orchestration.framework import create_arbitration_engine
        engine = create_arbitration_engine()
        if hasattr(engine, 'arbitrate_decision'):
            functionality_results["passed"].append("Arbitration Engine instantiation")
        else:
            functionality_results["failed"].append("Arbitration Engine missing arbitrate_decision method")
    except Exception as e:
        functionality_results["failed"].append(f"Arbitration Engine failed: {e}")
    
    # Test L5 Safety
    try:
        from agentic_core.l5_safety.filters import create_injection_detector
        detector = create_injection_detector()
        if hasattr(detector, 'detect_injection'):
            functionality_results["passed"].append("Injection Detector instantiation")
        else:
            functionality_results["failed"].append("Injection Detector missing detect_injection method")
    except Exception as e:
        functionality_results["failed"].append(f"Injection Detector failed: {e}")
    
    # Test Prompt Governance
    try:
        from agentic_core.prompt_governance import create_prompt_manifest
        manifest = create_prompt_manifest()
        if hasattr(manifest, 'create_manifest'):
            functionality_results["passed"].append("Prompt Manifest instantiation")
        else:
            functionality_results["failed"].append("Prompt Manifest missing create_manifest method")
    except Exception as e:
        functionality_results["failed"].append(f"Prompt Manifest failed: {e}")
    
    for result in functionality_results["passed"]:
        print(f"  ✅ {result}")
    for result in functionality_results["failed"]:
        print(f"  ❌ {result}")
    
    return functionality_results

def main():
    """Main validation function"""
    print("🚀 Section 3 Structure Validation")
    print("Validating complete alignment with new repository structure...")
    print()
    
    # Test imports
    import_results = test_imports()
    
    # Test functionality
    functionality_results = test_functionality()
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Imports Tested: {import_results['total']}")
    print(f"Passed: {len(import_results['passed'])}")
    print(f"Failed: {len(import_results['failed'])}")
    print(f"Success Rate: {len(import_results['passed']) / import_results['total'] * 100:.1f}%")
    
    print(f"\nFunctionality Tests: {len(functionality_results['passed'])} passed, {len(functionality_results['failed'])} failed")
    
    if import_results['failed']:
        print("\n❌ FAILED IMPORTS:")
        for failed in import_results['failed']:
            print(f"  - {failed}")
    
    if functionality_results['failed']:
        print("\n❌ FAILED FUNCTIONALITY:")
        for failed in functionality_results['failed']:
            print(f"  - {failed}")
    
    # Final verdict
    all_passed = len(import_results['failed']) == 0 and len(functionality_results['failed']) == 0
    
    if all_passed:
        print("\n🎉 VALIDATION SUCCESSFUL!")
        print("✅ Section 3 structure is fully functional and ready for use.")
        return 0
    else:
        print("\n⚠️ VALIDATION FAILED!")
        print("❌ Some components need to be fixed before the structure is fully functional.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
