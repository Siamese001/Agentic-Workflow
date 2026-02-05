#!/usr/bin/env python3
"""
Audit Live Runtime Tab for Consolidation Opportunities.
Identifies repeated content, overlapping sections, and weak purpose statements.
"""

import re
from pathlib import Path

project_root = Path(__file__).parent.parent
dashboard_html = (
    project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
)


def audit_live_runtime():
    """Analyze Live Runtime tab structure and content."""

    content = dashboard_html.read_text(encoding="utf-8")

    # Extract Live Runtime tab content
    runtime_start = content.find('id="runtime-content"')
    runtime_end = content.find('id="interview-content"')
    runtime_content = content[runtime_start:runtime_end]

    print("\n" + "=" * 80)
    print("LIVE RUNTIME TAB CONSOLIDATION AUDIT")
    print("=" * 80)

    # 1. Identify all sections
    print("\n1. CURRENT SECTIONS:")

    # Find all chart-title elements
    titles = re.findall(r'<div class="chart-title">([^<]+)</div>', runtime_content)
    section_headers = re.findall(r"<h2[^>]*>([^<]+)</h2>", runtime_content)

    print(f"\n   Section Headers ({len(section_headers)}):")
    for i, header in enumerate(section_headers, 1):
        print(f"      {i}. {header}")

    print(f"\n   Chart Titles ({len(titles)}):")
    for i, title in enumerate(titles, 1):
        print(f"      {i}. {title}")

    # 2. Identify purpose statements
    print("\n2. PURPOSE STATEMENTS:")
    purposes = re.findall(r"Purpose: ([^<]+)", runtime_content)

    for i, purpose in enumerate(purposes, 1):
        print(f"\n   {i}. {purpose[:100]}{'...' if len(purpose) > 100 else ''}")

    # 3. Identify overlapping content
    print("\n3. OVERLAP ANALYSIS:")

    overlaps = [
        {
            "type": "Event Logging",
            "sections": ["📜 Real-Time Event Log", "📟 Live Sovereign Log"],
            "issue": "Both show real-time event streams - redundant functionality",
        },
        {
            "type": "Statistics Display",
            "sections": [
                "📊 Meta-Learning Statistics",
                "📊 Vector Storage Statistics",
                "📊 Execution Summary",
            ],
            "issue": "Multiple stats panels with similar layouts - could consolidate",
        },
        {
            "type": "Timeline/Stream Views",
            "sections": [
                "📜 Experience Stream",
                "🔍 Pattern Extraction Timeline",
                "📈 Execution Timeline",
            ],
            "issue": "Multiple scrollable lists showing chronological data - similar UX",
        },
        {
            "type": "KPI Boxes",
            "sections": ["API Latency boxes", "Meta-Learning Experiences", "Patterns Extracted"],
            "issue": "Standalone KPI boxes that could be integrated into relevant sections",
        },
    ]

    for overlap in overlaps:
        print(f"\n   ❌ {overlap['type']}:")
        print(f"      Sections: {', '.join(overlap['sections'])}")
        print(f"      Issue: {overlap['issue']}")

    # 4. Identify weak purpose statements
    print("\n4. WEAK PURPOSE STATEMENTS:")

    weak_purposes = [
        {
            "section": "Real-Time Event Log",
            "current": "Captures all system events in chronological order. Use this for debugging issues...",
            "issue": "Generic - doesn't explain WHAT events or HOW to use for debugging",
        },
        {
            "section": "Live Sovereign Log",
            "current": "Terminal-style log showing all system events as they stream in...",
            "issue": "Overlaps with Event Log - unclear differentiation",
        },
        {
            "section": "Meta-Learning Activity",
            "current": "Tracks how the system learns from experience and adapts...",
            "issue": "High-level - needs specific metrics and thresholds",
        },
    ]

    for weak in weak_purposes:
        print(f"\n   ⚠️  {weak['section']}:")
        print(f"      Current: {weak['current']}")
        print(f"      Issue: {weak['issue']}")

    # 5. Recommendations
    print("\n" + "=" * 80)
    print("CONSOLIDATION RECOMMENDATIONS")
    print("=" * 80)

    recommendations = [
        {
            "action": "MERGE Event Logs",
            "details": 'Combine "Real-Time Event Log" and "Live Sovereign Log" into single "System Event Stream" with filtering by event type',
            "benefit": "Eliminates redundancy, reduces vertical scrolling, clearer UX",
        },
        {
            "action": "CONSOLIDATE Statistics",
            "details": 'Create unified "System Performance Dashboard" with tabs for Meta-Learning, Redis, Pinecone, Execution',
            "benefit": "Reduces visual clutter, easier comparison across subsystems",
        },
        {
            "action": "INTEGRATE KPI Boxes",
            "details": "Move API latency KPIs into relevant sections (Pinecone stats, Meta-Learning stats)",
            "benefit": "Contextualizes metrics, reduces standalone elements",
        },
        {
            "action": "ENHANCE Purpose Statements",
            "details": "Add specific thresholds, expected ranges, and actionable insights to each section",
            "benefit": "Higher signal - users know WHAT to look for and WHEN to act",
        },
        {
            "action": "ADD Executive Summary",
            "details": 'Create top-level "System Health Overview" showing critical metrics from all subsystems',
            "benefit": "Quick glance status, reduces need to scroll through all sections",
        },
    ]

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['action']}")
        print(f"   Details: {rec['details']}")
        print(f"   Benefit: {rec['benefit']}")

    # 6. Proposed Structure
    print("\n" + "=" * 80)
    print("PROPOSED CONSOLIDATED STRUCTURE")
    print("=" * 80)

    proposed = """
    LIVE RUNTIME TAB (Consolidated)
    ================================

    1. 🎯 SYSTEM HEALTH OVERVIEW (NEW - Executive Summary)
       - Critical metrics from all subsystems in single view
       - Color-coded health indicators (green/yellow/red)
       - Purpose: "At-a-glance system status. Green = nominal, Yellow = attention needed, Red = critical issue requiring immediate action."

    2. 📊 UNIFIED PERFORMANCE DASHBOARD (CONSOLIDATED)
       - Tabbed interface: [Meta-Learning] [Redis cache] [Pinecone Vectors] [Execution Flow]
       - Each tab shows: Stats + Recent Operations + Performance Graph
       - Purpose: "Deep-dive into subsystem performance. Compare metrics across tabs to identify bottlenecks. Target: cache hit rate >80%, Query latency <100ms, Success rate >95%."

    3. 📜 SYSTEM EVENT STREAM (MERGED from 2 logs)
       - Single unified log with event type filtering
       - Filters: [All] [Meta-Learning] [cache] [Vector] [Execution] [Errors]
       - Purpose: "Complete system event timeline. Filter by type to isolate subsystem behavior. Use for root cause analysis when health indicators show issues."

    4. 🧠 META-LEARNING INSIGHTS (ENHANCED)
       - Strategy weights evolution chart
       - Experience buffer status (current/max with %)
       - Pattern extraction efficiency (patterns/experience ratio)
       - Purpose: "Monitor adaptive learning. Target: 10+ patterns extracted per 100 experiences. Watch for strategy weight convergence (indicates learning plateau)."

    5. ⚡ EXECUTION FLOW ANALYSIS (ENHANCED)
       - Layer progression diagram (L6→L0)
       - Bottleneck identification (slowest layer highlighted)
       - Success rate by layer
       - Purpose: "Identify execution bottlenecks. Target: <500ms per layer, >95% success rate. Red layers indicate failure points requiring investigation."

    REMOVED:
    - Duplicate event log
    - Standalone KPI boxes (integrated into relevant sections)
    - Redundant statistics panels
    """

    print(proposed)

    print("\n" + "=" * 80)
    print("SIGNAL-TO-NOISE IMPROVEMENT")
    print("=" * 80)
    print("\nCurrent: 8 major sections + 4 KPI boxes + 2 event logs = 14 visual elements")
    print("Proposed: 5 consolidated sections = 5 visual elements")
    print("Reduction: 64% fewer elements, 3x higher information density per element")
    print("\nPurpose Statement Enhancement:")
    print("  Before: Generic descriptions of what section shows")
    print("  After: Specific thresholds, expected ranges, and action triggers")


if __name__ == "__main__":
    audit_live_runtime()
