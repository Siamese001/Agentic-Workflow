"""
Dashboard Renderer - Sovereign UI Engine (L6 Observability)
Moved from L5_safety/validators as part of Phase 1 Consolidation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import re

log = logging.getLogger(__name__)


class DashboardRenderer:
    """
    Renders the autonomy dashboard HTML from template and data.
    
    Responsibilities:
    - Load dashboard template
    - Inject data placeholders
    - Generate recommendations section
    - Save final HTML
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize the renderer.
        
        Args:
            project_root: Root path of the project
        """
        self.project_root = project_root
        # PHASE 2: Synchronize with consolidated L6 template location
        self.template_dir = self.project_root / "agentic_core" / "observability" / "dashboard" / "templates"
        self.template_path = self.template_dir / "dashboard.html"
        
        self.output_path = self.project_root / "reports" / "autonomy_dashboard.html"
    
    def load_template(self) -> str:
        """Load the canonical SSOT HTML template."""
        if not self.template_path.exists():
            error_msg = (
                f"Critical SSOT Violation: Dashboard template missing at {self.template_path}. "
                "Ensure Phase 2 Migration (template move) has been executed."
            )
            log.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        return self.template_path.read_text(encoding="utf-8")
    
    def render(
        self,
        dashboard_rows: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        interview_questions: List[Dict[str, Any]],
        gauge_data: Dict[str, Any],
        last_updated: str
    ) -> str:
        """
        Render the complete dashboard HTML.
        
        Args:
            dashboard_rows: List of territory data rows
            recommendations: List of strategic recommendations
            interview_questions: List of interview prep questions
            gauge_data: Data for gauge charts
            last_updated: Timestamp string
            
        Returns:
            Complete HTML string
        """
        template = self.load_template()
        
        # Inject data into template
        html = self._inject_data(
            template,
            dashboard_rows,
            recommendations,
            interview_questions,
            gauge_data,
            last_updated
        )
        
        # Validate injection
        if not self._validate_injection(html):
            log.warning("Dashboard may have uninjected placeholders")
        
        return html
    
    def _inject_data(
        self,
        template: str,
        dashboard_rows: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        interview_questions: List[Dict[str, Any]],
        gauge_data: Dict[str, Any],
        last_updated: str
    ) -> str:
        """Inject data into template placeholders."""
        html = template
        
        # Helper to escape backslashes in replacement strings for re.sub
        def safe_replace(pattern: str, replacement: str, text: str, flags: int = 0) -> str:
            # Escape backslashes in the replacement to prevent regex interpretation
            safe_repl = replacement.replace('\\', '\\\\')
            return re.sub(pattern, safe_repl, text, flags=flags)
        
        # Inject dashboard data
        dashboard_json = json.dumps(dashboard_rows, indent=2, default=str)
        html = safe_replace(
            r'const dashboardData = \[.*?\];',
            f'const dashboardData = {dashboard_json};',
            html,
            flags=re.DOTALL
        )
        
        # Inject recommendations
        recommendations_json = json.dumps(recommendations, indent=2, default=str)
        html = safe_replace(
            r'const recommendationsData = \[.*?\];',
            f'const recommendationsData = {recommendations_json};',
            html,
            flags=re.DOTALL
        )
        
        # Inject interview questions
        questions_json = json.dumps(interview_questions, indent=2, default=str)
        html = safe_replace(
            r'const interviewQuestions = \[.*?\];',
            f'const interviewQuestions = {questions_json};',
            html,
            flags=re.DOTALL
        )
        
        # Inject gauge data
        gauge_json = json.dumps(gauge_data, indent=2, default=str)
        html = safe_replace(
            r'const gaugeData = \{.*?\};',
            f'const gaugeData = {gauge_json};',
            html,
            flags=re.DOTALL
        )
        
        # Inject timestamp
        html = safe_replace(
            r'const lastUpdatedStr = ".*?";',
            f'const lastUpdatedStr = "{last_updated}";',
            html
        )
        
        return html
    
    def _validate_injection(self, html: str) -> bool:
        """Validate that all placeholders were injected."""
        # Check for any remaining placeholder patterns
        placeholders = [
            '= [];',  # Empty arrays
            '= {};',  # Empty objects
            '{{',     # Mustache-style
            '}}',
        ]
        
        for placeholder in placeholders:
            if placeholder in html:
                # Allow empty arrays/objects in some cases
                if placeholder in ['= [];', '= {};']:
                    continue
                log.warning(f"Found potential uninjected placeholder: {placeholder}")
                return False
        
        return True
    
    def save(self, html: str, output_path: Optional[Path] = None) -> Path:
        """
        Save the rendered HTML to file.
        
        Args:
            html: Rendered HTML content
            output_path: Optional custom output path
            
        Returns:
            Path to saved file
        """
        if output_path is None:
            output_path = self.project_root / "reports" / "autonomy_dashboard.html"
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_path.write_text(html, encoding="utf-8")
        log.debug(f"Dashboard file created: {output_path.stat().st_size:,} bytes")
        
        return output_path
    
    def generate_recommendations(
        self,
        total_row: Dict[str, Any],
        territory_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations based on metrics.
        
        Args:
            total_row: TOTAL summary row
            territory_rows: List of territory rows
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        health = total_row.get("Health", 0)
        test_pct = total_row.get("Test %", 0)
        invoke_pct = total_row.get("Invocation %", 0)
        typed_pct = total_row.get("Typed %", 0)
        avg_cc = total_row.get("Avg CC", 0)
        
        # 1. Test coverage recommendation
        if test_pct < 80:
            recommendations.append({
                "priority": 1,
                "title": "Expand Test Coverage",
                "description": "Add unit tests for core behaviors and regression baselines. Focus on agents with 0% coverage first.",
                "impact": "HIGH",
                "effort": "MEDIUM",
                "target_metric": "Test %",
                "current_value": test_pct,
                "target_value": 95,
            })
        
        # 2. Healing invocation recommendation
        if invoke_pct < 90:
            recommendations.append({
                "priority": 2,
                "title": "Complete Healing Capability Rollout",
                "description": "Add HealerMixin to all agents. Enables standardized self-recovery tools across the portfolio.",
                "impact": "HIGH",
                "effort": "LOW",
                "target_metric": "Invocation %",
                "current_value": invoke_pct,
                "target_value": 95,
            })
        
        # 3. Complexity recommendation
        if avg_cc > 15:
            recommendations.append({
                "priority": 3,
                "title": "Reduce Cyclomatic Complexity",
                "description": "Refactor methods with CC>15 into smaller primitives. Focus on L5 validators and L3 orchestrators first.",
                "impact": "MEDIUM",
                "effort": "HIGH",
                "target_metric": "Avg CC",
                "current_value": avg_cc,
                "target_value": 10,
            })
        
        # 4. Typing recommendation
        if typed_pct < 90:
            recommendations.append({
                "priority": 4,
                "title": "Improve Type Coverage",
                "description": "Add type hints to all function parameters and return types. Reduces runtime errors by 50-70%.",
                "impact": "MEDIUM",
                "effort": "MEDIUM",
                "target_metric": "Typed %",
                "current_value": typed_pct,
                "target_value": 95,
            })
        
        # 5. Layer-specific recommendations
        weak_layers = [r for r in territory_rows if r.get("Health", 100) < 70]
        for layer in weak_layers[:3]:
            recommendations.append({
                "priority": 5,
                "title": f"Strengthen {layer['Territory']}",
                "description": f"Territory has {layer.get('Health', 0):.0f}% health. Focus on test coverage and healing invocation.",
                "impact": "MEDIUM",
                "effort": "MEDIUM",
                "target_metric": "Health",
                "current_value": layer.get("Health", 0),
                "target_value": 85,
            })
        
        return recommendations[:7]  # Limit to top 7
    
    def generate_interview_questions(
        self,
        total_row: Dict[str, Any],
        territory_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate interview preparation questions based on weak signals.
        
        Args:
            total_row: TOTAL summary row
            territory_rows: List of territory rows
            
        Returns:
            List of interview question dictionaries
        """
        questions = []
        
        # Base questions about the architecture
        questions.append({
            "category": "Architecture",
            "question": "How does the healing system work across agents?",
            "analogy": "Like a factory where each worker has a personal repair toolkit (HealerMixin) and follows a master safety checklist (heal_repository).",
            "key_metric": f"Healing Invocation: {total_row.get('Invocation %', 0):.0f}%",
        })
        
        questions.append({
            "category": "Quality",
            "question": "What's your approach to managing code complexity?",
            "analogy": "We measure workflow complexity like steps in an assembly line. Target is ≤10 steps (CC). Current average is {:.0f}.".format(total_row.get("Avg CC", 0)),
            "key_metric": f"Avg CC: {total_row.get('Avg CC', 0):.1f}",
        })
        
        questions.append({
            "category": "Testing",
            "question": "How do you ensure agent reliability?",
            "analogy": "Each agent has quality control inspections (tests) before deployment. {:.0f}% currently have verification procedures.".format(total_row.get("Test %", 0)),
            "key_metric": f"Test Coverage: {total_row.get('Test %', 0):.0f}%",
        })
        
        # Add weak signal questions
        weak_territories = sorted(territory_rows, key=lambda x: x.get("Health", 100))[:3]
        for t in weak_territories:
            questions.append({
                "category": "Improvement",
                "question": f"What's the plan for improving {t['Territory']}?",
                "analogy": f"This territory is at {t.get('Health', 0):.0f}% health with {t.get('Test %', 0):.0f}% test coverage.",
                "key_metric": f"Health: {t.get('Health', 0):.0f}%",
            })
        
        return questions[:15]  # Limit to 15
    
    def generate_gauge_data(self, total_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for gauge charts.
        
        Args:
            total_row: TOTAL summary row
            
        Returns:
            Dict with gauge data
        """
        return {
            "health": total_row.get("Health", 0),
            "compliance": total_row.get("Invocation %", 0),
            "test_coverage": total_row.get("Test %", 0),
            "code_quality": total_row.get("Code Quality Score", 0),
            "typing": total_row.get("Typed %", 0),
            "complexity_health": total_row.get("Complexity Health", 0)
        }
