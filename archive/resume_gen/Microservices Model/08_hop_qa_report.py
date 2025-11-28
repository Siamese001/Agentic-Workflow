# hops/hop_8_qa_report.py
"""
Hop 8: QA Report Generation - HIGH-SIGNAL OVERWRITE

This is a comprehensive diagnostic report generator.
1. It reads outputs from HOP-0, 1, 3, 4, 5, 6, and 7 to build
   a complete picture of the pipeline run.
2. It generates an Executive Summary with the final gate decision,
   RAG signal quality, and final thematic alignment score.
3. It includes a "RAG Deep Dive" that surfaces the agentic
   evidence_log and critique_history from HOP-0.
4. It shows the "Content Funnel" (bullets in HOP-1 -> selected
   in HOP-3 -> sanitized in HOP-4).
5. It provides a "Validation Deep Dive" from HOP-5.
6. It includes a preview of the final rendered file from HOP-7.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ThematicAnalysis, HopCheckpoint, HopStatus
)

class QAReportBuilder:
    """Generates a comprehensive markdown QA report."""
    
    def __init__(self, workflow_id: str, run_dir: Path, metadata: Dict):
        self.logger = logging.getLogger(__name__)
        self.workflow_id = workflow_id
        self.run_dir = run_dir
        self.metadata = metadata
        self.report_lines = []
        
        # Data loaders
        self.data: Dict[str, Any] = {
            "hop_0": self._load_json(run_dir / "hop_0_thematic_analysis.json"),
            "hop_1": self._load_json(run_dir / "hop_1_clerk_output.json"),
            "hop_3": self._load_json(run_dir / "hop_3_artist_output.json"),
            "hop_4": self._load_json(run_dir / "hop_4_staging_buffer.json"),
            "hop_5": self._load_json(run_dir / "hop_5_validation_results.json"),
            "hop_6": self._load_json(run_dir / "hop_6_gate_decision.json"),
            "hop_7_md": self._load_text(run_dir / "hop_7_resume.md"),
            "checkpoints": self._load_json(run_dir / "hop_checkpoints.json")
        }

    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            self.logger.warning(f"File not found, skipping: {path}")
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {"error": str(e)}

    def _load_text(self, path: Path) -> str:
        if not path.exists():
            self.logger.warning(f"File not found, skipping: {path}")
            return ""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return f"Error loading text: {e}"

    def _add(self, line: str = ""):
        self.report_lines.append(line)

    def _get_validation_rule(self, rule_id: str) -> Dict:
        """Helper to find a specific rule from HOP-5 data."""
        for vr in self.data["hop_5"].get("validation_results", []):
            if vr.get("rule_id") == rule_id:
                return vr
        return {}
        
    def _format_table(self, headers: List[str], rows: List[List[str]]) -> None:
        """Adds a markdown table."""
        self._add(f"| {' | '.join(headers)} |")
        self._add(f"| {' | '.join(['---'] * len(headers))} |")
        for row in rows:
            self._add(f"| {' | '.join(str(cell) for cell in row)} |")

    def build_executive_summary(self):
        self._add(f"# QA Report: {self.metadata.get('company_name', 'Unknown')}")
        self._add(f"**Job Title:** {self.metadata.get('job_title', 'Unknown')}")
        self._add(f"**Workflow ID:** {self.workflow_id}")
        self._add(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._add("\n---\n")
        
        gate_meta = self.data["hop_6"].get("decision_metadata", {})
        rag_signal = self.data["hop_0"].get("signal_quality_score", 0.0)
        alignment_vr = self._get_validation_rule("THEMATIC_ALIGNMENT_SUMMARY")
        alignment_score = alignment_vr.get("details", {}).get("actual_similarity", 0.0)
        
        self._add("## Executive Summary")
        self._add(f"| Metric | Value |")
        self._add(f"| :--- | :--- |")
        self._add(f"| **Final Gate Decision** | **{self.data['hop_6'].get('gate_decision', 'UNKNOWN')}** |")
        self._add(f"| **Gate Reason** | {gate_meta.get('reason', 'N/A')} |")
        self._add(f"| **Input RAG Signal** | {rag_signal:.2%} |")
        self._add(f"| **Thematic Alignment** | {alignment_score:.2%} |")
        self._add(f"| **Validation Risk Score** | {gate_meta.get('total_risk_score', 'N/A')} (Threshold: {gate_meta.get('adjusted_risk_threshold', 'N/A')}) |")
        self._add(f"| **Total API Calls** | {sum(h.get('api_calls', 0) for h in self.data['checkpoints'].get('hops', []))} |")
        self._add(f"| **Failed Validations** | {gate_meta.get('summary', {}).get('failed_validations', 'N/A')} / {gate_meta.get('summary', {}).get('total_validations', 'N/A')} |")

    def build_rag_deep_dive(self):
        self._add("\n## HOP-0: RAG Analysis Deep Dive")
        self._add(f"**Primary Theme:** {self.data['hop_0'].get('primary_theme', {}).get('name', 'N/A')}")
        self._add(f"**Keywords:** `{'`, `'.join(self.data['hop_0'].get('primary_theme', {}).get('keywords', []))}`")
        self.logger.info("Building RAG evidence log...")
        
        evidence_log = self.data['hop_0'].get('evidence_log', [])
        if evidence_log:
            self._add("\n### Agentic Evidence Log (Execute-Critique-Replan)")
            headers = ["Phase", "Timestamp", "Result Snippet"]
            rows = [
                [
                    e.get('phase'), e.get('timestamp', ''), 
                    json.dumps(e.get('result_snippet', ''))
                ] 
                for e in evidence_log[-5:] # Show last 5
            ]
            self._format_table(headers, rows)
            if len(evidence_log) > 5:
                self._add(f"*(Showing last 5 of {len(evidence_log)} evidence entries)*")
        
        critiques = self.data['hop_0'].get('critique_history', [])
        if critiques:
            self._add("\n### Agentic Critique History")
            for i, c in enumerate(critiques):
                self._add(f"**Critique {i+1}:** {c.get('critique_text')}")
                self._add(f"- **Sufficient:** {c.get('is_sufficient')} | **Confidence:** {c.get('confidence_score', 0.0):.1%}")
                self._add(f"- **Refinement Tasks:** `{', '.join(c.get('refinement_tasks', []))}`")

    def build_content_funnel_analysis(self):
        self._add("\n## HOP 1-4: Content Generation Funnel")
        self.logger.info("Building content funnel...")
        
        total_bullets = sum(
            len(exp.get("bullets", [])) 
            for exp in self.data["hop_1"].get("extracted_content", {}).get("experience_sections", [])
        )
        selected_bullets = len(self.data["hop_3"].get("metadata", {}).get("selected_bullet_map_keys", []))
        sections_generated = len(self.data["hop_3"].get("metadata", {}).get("sections_generated", []))
        structural_corrections = self.data["hop_4"].get("staging_metadata", {}).get("structural_corrections", 0)
        placeholders_found = self.data["hop_4"].get("staging_metadata", {}).get("placeholders_found", 0)
        
        self._add("| Stage | Metric | Value |")
        self._add("| :--- | :--- | :--- |")
        self._add(f"| **HOP-1 (Clerk)** | Total bullets in master resume | {total_bullets} |")
        self._add(f"| **HOP-3 (Artist)** | Experience sections selected | {selected_bullets} |")
        self._add(f"| **HOP-3 (Artist)** | Total sections synthesized (LLM) | {sections_generated} |")
        self._add(f"| **HOP-3 (Artist)** | LLM API Calls | {self.data['hop_3'].get('metadata', {}).get('api_calls', 0)} |")
        self._add(f"| **HOP-4 (Staging)** | Structural corrections (e.g., str->list) | {structural_corrections} |")
        self._add(f"| **HOP-4 (Staging)** | Placeholders found pre-validation | {placeholders_found} |")

    def build_validation_report(self):
        self._add("\n## HOP-5: Validation Deep Dive")
        self.logger.info("Building validation report...")
        
        failures = [
            vr for vr in self.data["hop_5"].get("validation_results", [])
            if not vr.get("passed", True)
        ]
        
        if not failures:
            self.logger.info("No validation failures found.")
            self._add("✅ **All validation rules passed.**")
            return
            
        self._add(f"**Found {len(failures)} validation failures:**")
        
        # Highlight Critical/High failures
        self._add("\n### 
        Failed Critical/High Severity Rules")
        crit_high_failures = [f for f in failures if f.get("severity") in ["CRITICAL", "HIGH"]]
        if crit_high_failures:
            headers = ["Rule ID", "Severity", "Message"]
            rows = [[f.get('rule_id'), f.get('severity'), f.get('message')] for f in crit_high_failures]
            self._format_table(headers, rows)
        else:
            self._add("No CRITICAL or HIGH severity failures found.")
            
        # Full report in a collapsible block
        self._add("\n<details>")
        self._add("<summary>Click to view full validation log</summary>\n")
        headers = ["Rule ID", "Passed", "Severity", "Message"]
        rows = [[
            f.get('rule_id'), 
            f.get('passed'), 
            f.get('severity'), 
            f.get('message')
        ] for f in self.data["hop_5"].get("validation_results", [])]
        self._format_table(headers, rows)
        self._add("</details>")

    def build_hop_execution_log(self):
        self._add("\n## Pipeline Execution Log")
        self.logger.info("Building hop execution log...")
        
        headers = ["Status", "Hop Name", "Hop ID", "Duration (s)", "API Calls", "Error"]
        rows = []
        for checkpoint in self.data["checkpoints"].get("hops", []):
            status_emoji = "✅" if checkpoint.get("status") == HopStatus.PASS.value else "❌"
            rows.append([
                status_emoji,
                checkpoint.get("hop_name"),
                checkpoint.get("hop_id"),
                f"{checkpoint.get('duration_sec', 0.0):.2f}",
                checkpoint.get("api_calls", 0),
                checkpoint.get("error_message", "N/A")
            ])
        self._format_table(headers, rows)

    def build_output_preview(self):
        self._add("\n## HOP-7: Rendered Output Preview")
        self.logger.info("Building output preview...")
        
        if not self.data["hop_7_md"]:
            self._add("*(No resume rendered, likely due to HALT)*")
            return
            
        preview = "\n".join(self.data["hop_7_md"].splitlines()[:15])
        self._add(f"```markdown\n{preview}\n...\n```")

    def generate_report(self) -> str:
        """Assembles all components into the final report string."""
        self.logger.info(f"Assembling QA report for {self.workflow_id}...")
        self.build_executive_summary()
        self.build_rag_deep_dive()
        self.build_content_funnel_analysis()
        self.build_validation_report()
        self.build_output_preview()
        self.build_hop_execution_log()
        self.logger.info("QA report assembly complete.")
        return "\n".join(self.report_lines)

def run_hop_8(args: argparse.Namespace):
    """Executes the HOP-8 QA report generation logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-8: QA Report Generation [v-HighSignal] ---")
    start_time = datetime.now()

    try:
        # Prepare metadata
        metadata = {
            "workflow_id": args.workflow_id,
            "company_name": args.company_name,
            "job_title": args.job_title,
            "jd_url": args.jd_url
        }

        # Instantiate QA report builder
        # The builder handles loading all necessary files
        generator = QAReportBuilder(
            workflow_id=args.workflow_id,
            run_dir=Path(args.run_dir),
            metadata=metadata
        )

        # Generate report
        qa_report = generator.generate_report()
        
        logger.info(f"QA report generated ({len(qa_report)} chars)")

        # Write output
        try:
            output_path = Path(args.output_path_qa_report)
            output_path.write_text(qa_report, encoding='utf-8')
            logger.info(f"Successfully wrote QA report to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write QA report: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-8 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0")

    except HopExecutionError as he:
        logger.error(f"HOP-8 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-8 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-8 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-8 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-8: QA Report Generation [v-HighSignal]")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    # Note: A real impl would just pass --run-dir and the builder
    # would infer all input paths based on the file naming convention.
    # The args below are for compatibility with the user's provided files.
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--company-name", required=True, help="Target company name")
    parser.add_argument("--job-title", required=True, help="Target job title")
    parser.add_argument("--jd-url", required=True, help="Job description URL")
    parser.add_argument("--output-path-qa-report", required=True, help="Path to write the QA report markdown file")

    args = parser.parse_args()
    run_hop_8(args)