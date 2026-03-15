"""
Compare UI components between monolithic and modular dashboards
Catalogs: tabs, cards, tables, footnotes, filters, modals, KPIs
"""

import re
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def extract_components(html_content, name):
    """Extract UI components from HTML content"""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_components", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_components", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "extract_components")
    components = {
        "tabs": [],
        "kpi_boxes": [],
        "chart_cards": [],
        "tables": [],
        "filters": [],
        "modals": [],
        "footnotes": [],
        "functions": [],
        "data_files": [],
    }
    tab_matches = re.findall('data-target="([^"]+)"[^>]*>([^<]+)</a>', html_content)
    for target, label in tab_matches:
        components["tabs"].append({"target": target, "label": label.strip()})
    kpi_matches = re.findall(
        'class="kpi-box[^"]*"[^>]*>.*?<div class="kpi-label">([^<]+)</div>', html_content, re.DOTALL
    )
    components["kpi_boxes"] = list(set(kpi_matches))
    card_matches = re.findall('<div class="chart-title"[^>]*>([^<]+)</div>', html_content)
    components["chart_cards"] = list(set(card_matches))
    filter_matches = re.findall(
        "checkbox[^>]*>([^<]+)</label>|checkbox[^>]*>\\s*<[^>]*>([^<]+)<", html_content, re.DOTALL
    )
    for match in filter_matches:
        label = match[0] or match[1]
        if label and label.strip():
            components["filters"].append(label.strip())
    modal_matches = re.findall('id="([^"]*[Mm]odal[^"]*)"', html_content)
    components["modals"] = list(set(modal_matches))
    data_matches = re.findall('src="([^"]*\\.js)"', html_content)
    components["data_files"] = [f for f in data_matches if "data/" in f or "js/" in f]
    func_matches = re.findall("function\\s+(\\w+)\\s*\\(", html_content)
    components["functions"] = list(set(func_matches))
    if "Factory analogy" in html_content:
        components["footnotes"].append("Factory analogies present")
    if "Icon Legend" in html_content:
        components["footnotes"].append("Icon legend present")
    if "Health Score:" in html_content or "Heal Capability %:" in html_content:
        components["footnotes"].append("Metric definitions present")
    return components


def compare_components():
    """Compare monolithic vs modular UI components"""
    print("\n" + "=" * 70)
    print("UI COMPONENT COMPARISON: Monolithic vs Modular")
    print("=" * 70 + "\n")
    mono_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard_backup.html")
    if not mono_path.exists():
        print(f"❌ Monolithic backup not found: {mono_path}")
        return
    with open(mono_path, encoding="utf-8") as f:
        mono_html = f.read()
    mod_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    if not mod_path.exists():
        print(f"❌ Modular dashboard not found: {mod_path}")
        return
    with open(mod_path, encoding="utf-8") as f:
        mod_html = f.read()
    js_content = ""
    js_files = [
        "agentic_core/L6_observability/dashboards/js/renderers/table-renderer.js",
        "agentic_core/L6_observability/dashboards/js/main.js",
    ]
    for js_file in js_files:
        js_path = Path(js_file)
        if js_path.exists():
            with open(js_path, encoding="utf-8") as f:
                js_content += f.read()
    mod_html += js_content
    mono_components = extract_components(mono_html, "Monolithic")
    mod_components = extract_components(mod_html, "Modular")
    categories = [
        ("tabs", "Navigation Tabs"),
        ("kpi_boxes", "KPI Boxes"),
        ("chart_cards", "Chart Cards"),
        ("filters", "Filter Controls"),
        ("modals", "Modals"),
        ("footnotes", "Footnotes & Legends"),
        ("data_files", "Data Files"),
        ("functions", "JavaScript Functions"),
    ]
    all_issues = []
    for key, label in categories:
        set(mono_components[key]) if isinstance(
            mono_components[key][0] if mono_components[key] else "", str
        ) else {str(x) for x in mono_components[key]}
        set(mod_components[key]) if isinstance(
            mod_components[key][0] if mod_components[key] else "", str
        ) else {str(x) for x in mod_components[key]}
        print(f"\n{'=' * 50}")
        print(f"📦 {label}")
        print(f"{'=' * 50}")
        print(f"  Monolithic: {len(mono_components[key])} items")
        print(f"  Modular:    {len(mod_components[key])} items")
        if isinstance(mono_components[key], list) and mono_components[key]:
            if isinstance(mono_components[key][0], dict):
                mono_set = {str(x) for x in mono_components[key]}
                mod_set = {str(x) for x in mod_components[key]}
            else:
                mono_set = set(mono_components[key])
                mod_set = set(mod_components[key])
            missing = mono_set - mod_set
            if missing:
                print("  ❌ Missing in modular:")
                for item in list(missing)[:10]:
                    print(f"     - {item}")
                    all_issues.append(f"{label}: {item}")
            else:
                print("  ✅ All items present")
    print(f"\n{'=' * 50}")
    print("📑 DETAILED TAB COMPARISON")
    print(f"{'=' * 50}")
    mono_tabs = mono_components["tabs"]
    mod_tabs = mod_components["tabs"]
    print("\nMonolithic tabs:")
    for tab in mono_tabs:
        print(f"  - {tab['label']} → #{tab['target']}")
    print("\nModular tabs:")
    for tab in mod_tabs:
        print(f"  - {tab['label']} → #{tab['target']}")
    print(f"\n{'=' * 50}")
    print("🔍 CRITICAL FEATURE CHECK")
    print(f"{'=' * 50}")
    critical_features = [
        ("renderTerritorySummaryTable", "Territory Summary Table Renderer"),
        ("renderCodeQualityTable", "Code Quality Table Renderer"),
        ("openDrillModal", "Drill-down Modal"),
        ("toggleFilter", "Filter Toggle Function"),
        ("toggleToxicityFilter", "Toxicity Filter"),
        ("toggleZombieFilter", "Zombie Filter"),
        ("toggleOutlierFilter", "Outlier Filter"),
        ("loadData", "Data Loading Function"),
        ("openTab", "Tab Navigation"),
        ("manualRefresh", "Manual Refresh"),
        ("Factory analogy", "Factory Analogies in Footnotes"),
        ("Icon Legend", "Icon Legend"),
        ("Heal Capability %:", "Heal Capability Definition"),
        ("Health Score:", "Health Score Formula"),
        ("drillModal", "Drill-down Modal Element"),
    ]
    for feature, description in critical_features:
        mono_has = feature in mono_html
        mod_has = feature in mod_html
        if mono_has and mod_has:
            status = "✅"
        elif mono_has and (not mod_has):
            status = "❌ MISSING"
            all_issues.append(f"Missing: {description}")
        elif not mono_has and mod_has:
            status = "➕ NEW"
        else:
            status = "⚪ N/A"
        print(f"  {status} {description}")
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    if all_issues:
        print(f"\n❌ {len(all_issues)} issues found:\n")
        for issue in all_issues[:20]:
            print(f"  - {issue}")
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more")
    else:
        print("\n✅ All critical features present in modular dashboard!")
    return all_issues


if __name__ == "__main__":
    issues = compare_components()
    exit(1 if issues else 0)
