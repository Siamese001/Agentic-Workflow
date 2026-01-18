"""
Report Generator - Markdown report generation for analysis results.
Extracted from agent_capability_supplement.py for single responsibility.
"""
from __future__ import annotations
from typing import Dict, List, Set, Counter
from collections import Counter as CounterType
import datetime


class ReportGenerator:
    """Generates markdown reports for capability analysis."""
    
    def generate_capability_report(
        self,
        live_agent_count: int,
        dead_agent_count: int,
        suspect_agent_count: int,
        live_cap_counter: CounterType,
        dead_cap_detail: Dict,
        unique_to_dead: Set,
        underrepresented: Dict,
        recommendations: List
    ) -> str:
        """Generate detailed markdown report for capability analysis.
        
        Args:
            live_agent_count: Number of live agents
            dead_agent_count: Number of dead agents
            suspect_agent_count: Number of suspect agents
            live_cap_counter: Counter of capabilities in live agents
            dead_cap_detail: Detailed capability info for dead agents
            unique_to_dead: Capabilities unique to dead agents
            underrepresented: Underrepresented capabilities
            recommendations: List of supplementation recommendations
            
        Returns:
            Markdown formatted report string
        """
        lines = []
        
        # Header
        lines.append("# ULTRA CAPABILITY SUPPLEMENTATION ANALYSIS REPORT")
        lines.append("")
        lines.append(f"**Generated:** {datetime.datetime.now().isoformat()}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.extend(self._generate_executive_summary(
            live_agent_count, dead_agent_count, suspect_agent_count,
            unique_to_dead, underrepresented
        ))
        
        # Live Agent Capabilities
        lines.extend(self._generate_live_capabilities_section(live_cap_counter))
        
        # Unique to Dead
        lines.extend(self._generate_unique_capabilities_section(
            unique_to_dead, dead_cap_detail
        ))
        
        # Underrepresented
        lines.extend(self._generate_underrepresented_section(
            underrepresented, dead_cap_detail
        ))
        
        # Recommendations
        lines.extend(self._generate_recommendations_section(recommendations))
        
        return "\n".join(lines)
    
    def _generate_executive_summary(
        self,
        live_count: int,
        dead_count: int,
        suspect_count: int,
        unique_to_dead: Set,
        underrepresented: Dict
    ) -> List[str]:
        """Generate executive summary section."""
        lines = []
        lines.append("## Executive Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| **Live Agents** | {live_count} |")
        lines.append(f"| **Dead Agents (to mine)** | {dead_count} |")
        lines.append(f"| **Suspect Agents** | {suspect_count} |")
        lines.append(f"| **Unique Capabilities in Dead** | {len(unique_to_dead)} |")
        lines.append(f"| **Underrepresented Capabilities** | {len(underrepresented)} |")
        lines.append("")
        return lines
    
    def _generate_live_capabilities_section(
        self,
        live_cap_counter: CounterType
    ) -> List[str]:
        """Generate live agent capability coverage section."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## Live Agent Capability Coverage")
        lines.append("")
        lines.append("| Capability | Count in Live Agents |")
        lines.append("|------------|---------------------|")
        for cap, count in sorted(live_cap_counter.items(), key=lambda x: -x[1]):
            lines.append(f"| {cap} | {count} |")
        lines.append("")
        return lines
    
    def _generate_unique_capabilities_section(
        self,
        unique_to_dead: Set,
        dead_cap_detail: Dict
    ) -> List[str]:
        """Generate unique capabilities section."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## Unique Capabilities in DEAD Agents")
        lines.append("")
        
        if unique_to_dead:
            lines.append(f"Found **{len(unique_to_dead)}** capabilities present ONLY in DEAD agents:")
            lines.append("")
            for cap in sorted(unique_to_dead):
                donors = [
                    name for name, detail in dead_cap_detail.items()
                    if cap in detail["caps"]["semantic_tags"] or cap in detail["caps"]["patterns"]
                ]
                lines.append(f"### `{cap.upper()}`")
                lines.append("")
                lines.append("**Donor Agents:**")
                for d in donors:
                    lines.append(f"- `{d}` → `{dead_cap_detail[d]['file']}`")
                lines.append("")
        else:
            lines.append("✅ **No completely unique capabilities** — all logic covered by LIVE agents.")
            lines.append("")
        
        return lines
    
    def _generate_underrepresented_section(
        self,
        underrepresented: Dict,
        dead_cap_detail: Dict
    ) -> List[str]:
        """Generate underrepresented capabilities section."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## Underrepresented Capabilities")
        lines.append("")
        lines.append("Capabilities that appear in fewer than 2 LIVE agents:")
        lines.append("")
        
        if underrepresented:
            lines.append("| Capability | Live Count | Potential Donors |")
            lines.append("|------------|------------|------------------|")
            for cap, count in sorted(underrepresented.items()):
                donors = [
                    name for name, detail in dead_cap_detail.items()
                    if cap in detail["caps"]["semantic_tags"] or cap in detail["caps"]["patterns"]
                ]
                donor_str = ", ".join(donors[:3])
                if len(donors) > 3:
                    donor_str += f" (+{len(donors)-3} more)"
                lines.append(f"| {cap} | {count} | {donor_str} |")
            lines.append("")
        else:
            lines.append("✅ **All capabilities well-represented** in LIVE agents.")
            lines.append("")
        
        return lines
    
    def _generate_recommendations_section(
        self,
        recommendations: List
    ) -> List[str]:
        """Generate recommendations section."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## Supplementation Recommendations")
        lines.append("")
        
        if recommendations:
            lines.append(f"**Total Recommendations:** {len(recommendations)}")
            lines.append("")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"### Recommendation {i}")
                lines.append("")
                lines.append(f"**Target Agent:** `{rec.get('target_agent', 'N/A')}`")
                lines.append(f"**Donor Agent:** `{rec.get('donor_agent', 'N/A')}`")
                lines.append(f"**Capability:** `{rec.get('capability', 'N/A')}`")
                lines.append(f"**Method:** `{rec.get('method', 'N/A')}`")
                lines.append(f"**Priority:** {rec.get('priority', 'Medium')}")
                lines.append("")
        else:
            lines.append("✅ **No supplementation needed** — LIVE agents have comprehensive coverage.")
            lines.append("")
        
        return lines
    
    def generate_summary_table(
        self,
        data: List[Dict[str, any]]
    ) -> str:
        """Generate a markdown table from data.
        
        Args:
            data: List of dictionaries with consistent keys
            
        Returns:
            Markdown table string
        """
        if not data:
            return ""
        
        lines = []
        
        # Header
        keys = list(data[0].keys())
        lines.append("| " + " | ".join(keys) + " |")
        lines.append("|" + "|".join(["---" for _ in keys]) + "|")
        
        # Rows
        for row in data:
            values = [str(row.get(k, "")) for k in keys]
            lines.append("| " + " | ".join(values) + " |")
        
        return "\n".join(lines)
