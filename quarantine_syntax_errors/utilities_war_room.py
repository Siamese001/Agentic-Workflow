import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)
# Import your new subatomic architecture modules
try:
    # Import directly to bypass broken __init__.py
    sys.path.append(os.path.join(os.path.dirname(
        __file__), 'runtime', 'shared', 'workflow'))
    from executive_orchestrator import ExecutiveAgentOrchestrator
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from schema_definitions import InterviewerProfile, StrategyRoadmap, TechnicalSWOT
except ImportError as e:
    pass
LOGGER.info(f"CRITICAL: Missing dependencies. {e}")
    LOGGER.info("Run: pip install rich instructor openai anthropic pydantic")
    sys.exit(1)

# Initialize Rich Console for beautiful output
CONSOLE = Console()


class WarRoom:
    def __init__(self, config_path: str = "Job_Workflow_v24.9.json"):
        self.console = CONSOLE
        self.orchestrator = ExecutiveAgentOrchestrator()
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get("4.reasoning", {})
        except FileNotFoundError:
self.console.logger.error(
                f"[bold red]Error:[/bold red] Config file {path} not found.")
            sys.exit(1)

    async def run_k11_shadow_audit(self):
        """Execute K.11: Technical Due Diligence"""
        self.console.rule("[bold blue]K.11 SHADOW AUDIT PROTOCOL")

        company_name = Prompt.ask("Target Company Name")

        self.console.logger.info(f"[green]🕵️  Using autonomous deep search for {company_name}....[/green]")

        with self.console.status(f"[bold green]Running Shadow Audit on {company_name}..."):
            swot = await self.orchestrator.execute_k11_shadow_audit(
                company_name=company_name,
                search_context=None,  # Always use autonomous search now
                config=self.config.get("K.11_shadow_audit", {})
            )

        # Display Results
        self.console.logger.info(Panel(f"[bold]Technical SWOT Analysis for {company_name}[/bold]",
                                       style="blue"))

        self.console.logger.info("[bold]Inferred Tech Stack:[/bold]")
        for item in swot.current_stack:
            self.console.logger.info(f" - [cyan]{item.tool_name}[/cyan]({item.category}): {item.confidence_score*100:.0f}% confidence")

        self.console.logger.info(
            "\n[bold red]Suspected Bottlenecks:[/bold red]")
        for b in swot.suspected_bottlenecks:
            self.console.logger.info(f" - {b}")

        self.console.logger.info(f"\n[bold green]Strategic Opportunity: [/bold green] {swot.strategic_opportunity}")

        return swot

    async def run_k12_strategy(self, technical_swot: TechnicalSWOT):
        """Execute K.12: 30-60-90 Day Strategy"""
        self.console.rule("[bold blue]K.12 STRATEGY GENERATOR")

        self.console.logger.info("[yellow]Paste the full Job Description. Press Ctrl+D(Linux/Mac) or Ctrl+Z(Windows) when done: [/yellow]")
        # Clear stdin buffer if needed or re-open (simplified for script flow)
        # Using input() loop for simpler copy-paste handling in basic terminals
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
pass
        jd_text = "\n".join(lines)

        with self.console.status("[bold green]Synthesizing 90-Day Plan..."):
            roadmap = await self.orchestrator.execute_k12_strategy(
                job_description=jd_text,
                technical_swot=technical_swot,
                config=self.config.get("K.12_strategy_roadmap", {})
            )

        self.console.logger.info(Panel(Markdown(f"# {roadmap.executive_summary}"),
                                       title="Executive Vision",
                                       style="green"))

        for milestone in roadmap.milestones:
            self.console.logger.info(f"[bold]{milestone.timeframe}[/bold]({milestone.focus_area}): {milestone.initiative}")
            self.console.logger.info(f"   [italic]Success Metric: {milestone.success_metric}[/italic]")

        self.console.logger.info(
            "\n[bold yellow]Immediate Wins (Week 1):[/bold yellow]")
        for win in roadmap.immediate_wins:
            self.console.logger.info(f" - {win}")

    async def run_k13_simulation(self):
        """Execute K.13: Interviewer Simulation"""
        self.console.rule("[bold blue]K.13 INTERVIEWER SIMULATION")

        interviewer_linkedin = Prompt.ask("Interviewer LinkedIn URL")

        self.console.logger.info(
            "[yellow]Paste your resume text. Press Ctrl+D when done:[/yellow]")
        resume_text = sys.stdin.read()

        with self.console.status(f"[bold green]Analyzing interviewer profile..."):
            profile = await self.orchestrator.execute_k13_simulation(
                interviewer_linkedin=interviewer_linkedin,
                resume_text=resume_text,
                config=self.config.get("K.13_interviewer_simulation", {})
            )

        # Display Results
        self.console.logger.info(Panel(f"[bold]Interviewer Analysis for {profile.role} at {profile.company_name}[/bold]",
                                       style="purple"))

        self.console.logger.info("[bold]Likely Interviewer Archetypes:[/bold]")
        for interviewer in profile.interviewers:
            self.console.logger.info(f" - [cyan]{interviewer.name}[/cyan]({interviewer.archetype}): {interviewer.background}")
            self.console.logger.info(f"   [italic]Focus Areas: {', '.join(interviewer.focus_areas)}[/italic]")

        self.console.logger.info(
            "\n[bold yellow]Predicted Questions:[/bold yellow]")
        for question in profile.predicted_questions[:5]:  # Show first 5
            self.console.logger.info(f" - {question.question}")
            self.console.logger.info(
                f"   [italic]Asked by: {question.interviewer_type}[/italic]")

        return profile

    async def main_menu(self):
        """Interactive War Room Menu with MCP lifecycle"""
        # Initialize MCP connections
        if self.orchestrator.mcp:
            try:
                await self.orchestrator.mcp.connect_all()
                self.console.logger.info(
                    "[green]✅ MCP servers connected[/green]")
            except Exception as e:
self.console.logger.error(
                    f"[yellow]⚠️ MCP connection failed: {e}[/yellow]")

        try:
            while True:
                self.console.rule(
                    "[bold red]EXECUTIVE WAR ROOM v2.0 (MCP-Enhanced)")
                self.console.logger.info(
                    "1. [bold]Full Audit & Strategy[/bold] (Run K.11 + K.12)")
                self.console.logger.info(
                    "2. [bold]Shadow Audit Only[/bold] (K.11)")
                self.console.logger.info(
                    "3. [bold]Interviewer Sim[/bold] (K.13)")
                self.console.logger.info("4. Exit")

                choice = Prompt.ask("Select Operation", choices=[
                                    "1", "2", "3", "4"])

                if choice == "1":
                    swot = await self.run_k11_shadow_audit()
                    await self.run_k12_strategy(swot)
                elif choice == "2":
                    await self.run_k11_shadow_audit()
                elif choice == "3":
                    await self.run_k13_simulation()
                elif choice == "4":
                    break
        finally:
            # Cleanup MCP connections
            if self.orchestrator.mcp:
                await self.orchestrator.mcp.cleanup()
                self.console.logger.info(
                    "[green]✅ MCP connections closed[/green]")


async def main():
    """Async main entry point"""
    war_room = WarRoom()
    await war_room.main_menu()

if __name__ == "__main__":
    asyncio.run(main())

