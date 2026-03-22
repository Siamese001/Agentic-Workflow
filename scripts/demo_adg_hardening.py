#!/usr/bin/env python3
"""
ADG Hardening Demo - Verification Suite Showcase

Demonstrates the ADG hardening verification suite with sample data and reporting.
This script shows how the verification suite works and what kind of issues it can detect.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_demo_database(db_path: Path) -> None:
    """Create a demo SQLite database with sample ADG data for testing."""
    
    print("🏗️  Creating demo ADG database...")
    
    # Remove existing demo database
    if db_path.exists():
        db_path.unlink()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create nodes table
        cursor.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                layer TEXT NOT NULL,
                confidence TEXT NOT NULL,
                resolved_path TEXT,
                identity_origin TEXT,
                domain TEXT,
                owner_surface TEXT,
                canonical_symbol TEXT,
                source_hash TEXT,
                identity_kind TEXT
            )
        """)
        
        # Create edges table
        cursor.execute("""
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER NOT NULL,
                dst_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                edge_kind TEXT NOT NULL,
                source_file TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                symbol TEXT,
                confidence TEXT,
                extraction_rule TEXT,
                authority_level TEXT,
                policy_scope TEXT,
                replay_relevance TEXT,
                learning_relevance TEXT,
                FOREIGN KEY (src_id) REFERENCES nodes (id),
                FOREIGN KEY (dst_id) REFERENCES nodes (id)
            )
        """)
        
        # Create meta table for provenance
        cursor.execute("""
            CREATE TABLE meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Insert sample nodes
        nodes_data = [
            # First-party modules
            (1, "ADG::Module::agentic_core/L0_routing/router.py", "module", "L0", "HIGH", 
             "agentic_core/L0_routing/router.py", "first_party", "runtime", "core", 
             "agentic_core.L0_routing.router", "abc123", "repo_module"),
            (2, "ADG::Module::agentic_core/L5_safety/guardian.py", "module", "L5", "HIGH",
             "agentic_core/L5_safety/guardian.py", "first_party", "runtime", "safety",
             "agentic_core.L5_safety.guardian", "def456", "repo_module"),
            (3, "ADG::Module::agentic_core/L4_persistence/store.py", "module", "L4", "HIGH",
             "agentic_core/L4_persistence/store.py", "first_party", "runtime", "persistence",
             "agentic_core.L4_persistence.store", "ghi789", "repo_module"),
            # External module
            (4, "ADG::Module::requests/api.py", "module", "L_RUNTIME", "HIGH",
             "requests/api.py", "external", "runtime", "core",
             "requests.api", "external123", "external_module"),
            # Unresolved import
            (5, "ADG::Module::unknown_module", "module", "UNKNOWN", "LOW",
             None, "unknown", "runtime", "core",
             None, None, "unresolved_import"),
        ]
        
        cursor.executemany("""
            INSERT INTO nodes (id, adg_name, entity_type, layer, confidence, resolved_path,
                             identity_origin, domain, owner_surface, canonical_symbol, 
                             source_hash, identity_kind)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, nodes_data)
        
        # Insert sample edges
        edges_data = [
            # Normal calls
            (1, 1, 2, "calls", "static", "agentic_core/L0_routing/router.py", 10, "route_request"),
            (2, 2, 3, "writes_to", "dynamic", "agentic_core/L5_safety/guardian.py", 25, "write_state"),
            # Trace coverage
            (3, 1, 1, "records_execution_trace", "runtime", "agentic_core/L0_routing/router.py", 15, "trace"),
            (4, 1, 1, "emits_replay_key", "runtime", "agentic_core/L0_routing/router.py", 16, "replay"),
            (5, 2, 2, "signs_execution_trace", "runtime", "agentic_core/L5_safety/guardian.py", 30, "signature"),
            # UWG termination
            (6, 2, 2, "execution_terminates_at_uwg", "runtime", "agentic_core/L5_safety/guardian.py", 31, "uwg_term"),
            # Layer violation (L0 -> L_RUNTIME direct)
            (7, 1, 4, "invokes_provider", "external", "agentic_core/L0_routing/router.py", 20, "api_call"),
            # Hard failure without transcript
            (8, 3, 3, "hard_fails_untranscripted", "runtime", "agentic_core/L4_persistence/store.py", 40, "hard_fail"),
            # Policy validation
            (9, 2, 2, "validated_by_safety_plane", "runtime", "agentic_core/L5_safety/guardian.py", 32, "policy_check"),
        ]
        
        cursor.executemany("""
            INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol,
                             confidence, extraction_rule, authority_level, policy_scope, replay_relevance, learning_relevance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL)
        """, edges_data)
        
        # Insert provenance metadata
        meta_data = [
            ("commit_sha", "abc123def456789012345678901234567890abcd"),
            ("artifact_digest", "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"),
            ("scan_timestamp_utc", datetime.now(timezone.utc).isoformat()),
            ("scanner_version", "1.0.0"),
            ("ruleset_version", "1.0.0"),
            ("repo_root", str(Path.cwd())),
            ("extractor_build_id", "build-20250321-001"),
            ("schema_version", "adg-schema-2.0"),
            ("generation_mode", "full"),
            ("source_snapshot_digest", "sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"),
        ]
        
        cursor.executemany("INSERT INTO meta (key, value) VALUES (?, ?)", meta_data)
        
        conn.commit()
        print(f"   ✅ Demo database created: {db_path}")
        print(f"   📊 Nodes: {len(nodes_data)}, Edges: {len(edges_data)}")

def run_demo_verification(adg_dir: Path) -> Dict[str, Any]:
    """Run verification suite on demo data."""
    
    print(f"\n🚀 Running ADG Verification Suite Demo")
    print(f"📁 ADG Directory: {adg_dir}")
    
    # Import and run the verification suite
    try:
        from scripts.run_adg_mandatory_verification import ADGMandatoryVerificationSuite
        
        suite = ADGMandatoryVerificationSuite(adg_dir)
        
        # Run only completed phases for demo
        completed_phases = {
            "provenance": suite.VERIFICATION_PHASES["provenance"],
            "consistency": suite.VERIFICATION_PHASES["consistency"], 
            "identity_completeness": suite.VERIFICATION_PHASES["identity_completeness"],
            "trace_replay_coverage": suite.VERIFICATION_PHASES["trace_replay_coverage"],
            "layer_authority": suite.VERIFICATION_PHASES["layer_authority"],
            "l4_normalization": suite.VERIFICATION_PHASES["l4_normalization"]
        }
        
        suite.VERIFICATION_PHASES = completed_phases
        
        # Run verification
        results = suite.run_verification_suite()
        
        return results
        
    except ImportError as e:
        print(f"❌ Could not import verification suite: {e}")
        return {"status": "ERROR", "error": str(e)}

def analyze_demo_results(results: Dict[str, Any]) -> None:
    """Analyze and present demo results."""
    
    print(f"\n📊 DEMO RESULTS ANALYSIS")
    print(f"{'='*60}")
    
    if results.get("status") == "ERROR":
        print(f"❌ Demo failed with error: {results.get('error')}")
        return
    
    summary = results.get("summary", {})
    
    print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
    print(f"Total Phases: {summary.get('total_phases', 0)}")
    print(f"Passed: {summary.get('passed_phases', 0)}")
    print(f"Failed: {summary.get('failed_phases', 0)}")
    print(f"Errors: {summary.get('error_phases', 0)}")
    print(f"Blocking Failures: {summary.get('blocking_failures', 0)}")
    
    # Phase-by-phase breakdown
    print(f"\n📋 PHASE BREAKDOWN:")
    phase_results = results.get("phase_results", {})
    
    for phase_name, result in phase_results.items():
        status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "💥"
        blocking_mark = " 🔒" if result["blocking"] else ""
        exec_time = result.get("execution_time", 0)
        
        print(f"   {status_icon} {phase_name}: {result['status']}{blocking_mark} ({exec_time:.2f}s)")
        
        # Show specific issues for failed phases
        if result["status"] in ["FAIL", "ERROR"]:
            if "errors" in result and result["errors"]:
                for error in result["errors"][:2]:  # Show first 2 errors
                    print(f"      • {error}")
    
    # Recommendations
    recommendations = results.get("recommendations", [])
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations[:5]:  # Show first 5
            print(f"   • {rec}")
    
    # Key metrics from completed phases
    print(f"\n📈 KEY METRICS:")
    
    # Trace coverage
    trace_coverage = results.get("phase_results", {}).get("trace_replay_coverage", {})
    if "summary" in trace_coverage:
        tc_summary = trace_coverage["summary"]
        print(f"   Trace Coverage: {tc_summary.get('trace_coverage_percentage', 0):.1f}%")
        print(f"   Complete Coverage: {tc_summary.get('complete_coverage', 0)} modules")
    
    # Layer authority
    layer_auth = results.get("phase_results", {}).get("layer_authority", {})
    if "summary" in layer_auth:
        la_summary = layer_auth["summary"]
        print(f"   Layer Violations: {la_summary.get('layer_violations', 0)}")
        print(f"   UWG Violations: {la_summary.get('uwg_violations', 0)}")
    
    # Identity completeness
    identity_comp = results.get("phase_results", {}).get("identity_completeness", {})
    if "summary" in identity_comp:
        ic_summary = identity_comp["summary"]
        print(f"   Identity Issues: {ic_summary.get('identity_issues', 0)}")

def main():
    """Main demo execution."""
    print("🎯 ADG Hardening Verification Suite Demo")
    print("=" * 60)
    
    # Setup demo environment
    demo_dir = Path("artifacts/demo_adg")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    demo_db = demo_dir / "adg_indexed_demo.sqlite"
    
    try:
        # Create demo database
        create_demo_database(demo_db)
        
        # Run verification suite
        results = run_demo_verification(demo_dir)
        
        # Analyze results
        analyze_demo_results(results)
        
        # Save results
        results_file = demo_dir / "demo_verification_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Demo results saved to: {results_file}")
        print(f"\n🎉 Demo completed! Check the results above to see how the verification suite works.")
        
        return 0 if results.get("summary", {}).get("overall_status") == "PASS" else 1
        
    except Exception as e:
        print(f"💥 Demo failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
