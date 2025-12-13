import json
import os
import sys
from typing import Dict, Any

# Import your new subatomic architecture modules
try:
    from runtime.shared.workflow.executive_agents import ExecutiveAgentOrchestrator
    from runtime.shared.workflow.schema_definitions import TechnicalSWOT, StrategyRoadmap, InterviewerProfile
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
except ImportError as e:
    print(f"CRITICAL: Missing dependencies. {e}")
    print("Run: pip install rich instructor openai anthropic pydantic")
    sys.exit(1)

# Initialize Rich Console for beautiful output
console = Console()

class WarRoom:
    def __init__(self, config_path: str = "Job_Workflow_v24.9.json"):
        self.console = console
        self.orchestrator = ExecutiveAgentOrchestrator()
        self.config = self._load_config(config_path)
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get("4.reasoning", {})
        except FileNotFoundError:
            self.console.print(f"[bold red]Error:[/bold red] Config file {path} not found.")
            sys.exit(1)

    def run_k11_shadow_audit(self):
        """Execute K.11: Technical Due Diligence"""
        self.console.rule("[bold blue]K.11 SHADOW AUDIT PROTOCOL")
        
        company_name = Prompt.ask("Target Company Name")
        
        self.console.print(f"[green]🕵️  Using autonomous deep search for {company_name}...[/green]")

        with self.console.status(f"[bold green]Running Shadow Audit on {company_name}..."):
            swot = self.orchestrator.execute_k11_shadow_audit(
                company_name=company_name,
                search_context=None,  # Always use autonomous search now
                config=self.config.get("K.11_shadow_audit", {})
            )
        
        # Display Results
        self.console.print(Panel(f"[bold]Technical SWOT Analysis for {company_name}[/bold]", style="blue"))
        
        self.console.print("[bold]Inferred Tech Stack:[/bold]")
        for item in swot.current_stack:
            self.console.print(f" - [cyan]{item.tool_name}[/cyan] ({item.category}): {item.confidence_score*100:.0f}% confidence")
            
        self.console.print("\n[bold red]Suspected Bottlenecks:[/bold red]")
        for b in swot.suspected_bottlenecks:
            self.console.print(f" - {b}")
            
        self.console.print(f"\n[bold green]Strategic Opportunity:[/bold green] {swot.strategic_opportunity}")
        
        return swot

    def run_k12_strategy(self, technical_swot: TechnicalSWOT):
        """Execute K.12: 30-60-90 Day Strategy"""
        self.console.rule("[bold blue]K.12 STRATEGY GENERATOR")
        
        self.console.print("[yellow]Paste the full Job Description. Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done:[/yellow]")
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
            roadmap = self.orchestrator.execute_k12_strategy(
                jd_text=jd_text,
                technical_swot=technical_swot,
                config=self.config.get("K.12_strategy_roadmap", {})
            )

        self.console.print(Panel(Markdown(f"# {roadmap.executive_summary}"), title="Executive Vision", style="green"))
        
        for milestone in roadmap.milestones:
            self.console.print(f"[bold]{milestone.timeframe}[/bold] ({milestone.focus_area}): {milestone.initiative}")
            self.console.print(f"   [italic]Success Metric: {milestone.success_metric}[/italic]")

        self.console.print("\n[bold yellow]Immediate Wins (Week 1):[/bold yellow]")
        for win in roadmap.immediate_wins:
            self.console.print(f" - {win}")

    def run_k13_simulation(self):
        """Execute K.13: Interviewer Simulation"""
        self.console.rule("[bold blue]K.13 INTERVIEWER SIMULATION")
        
        company_name = Prompt.ask("Target Company Name")
        role = Prompt.ask("Target Role")
        
        self.console.print("[yellow]Paste LinkedIn profile context (if available). Press Ctrl+D when done:[/yellow]")
        linkedin_context = sys.stdin.read()
        
        with self.console.status(f"[bold green]Analyzing interview panel at {company_name}..."):
            profile = self.orchestrator.execute_k13_simulation(
                company_name=company_name,
                role=role,
                linkedin_context=linkedin_context,
                config=self.config.get("K.13_interviewer_simulation", {})
            )
        
        # Display Results
        self.console.print(Panel(f"[bold]Interviewer Analysis for {role} at {company_name}[/bold]", style="purple"))
        
        self.console.print("[bold]Likely Interviewer Archetypes:[/bold]")
        for interviewer in profile.interviewers:
            self.console.print(f" - [cyan]{interviewer.name}[/cyan] ({interviewer.archetype}): {interviewer.background}")
            self.console.print(f"   [italic]Focus Areas: {', '.join(interviewer.focus_areas)}[/italic]")
            
        self.console.print("\n[bold yellow]Predicted Questions:[/bold yellow]")
        for question in profile.predicted_questions[:5]:  # Show first 5
            self.console.print(f" - {question.question}")
            self.console.print(f"   [italic]Asked by: {question.interviewer_type}[/italic]")
        
        return profile

    def main_menu(self):
        """Interactive War Room Menu"""
        while True:
            self.console.rule("[bold red]EXECUTIVE WAR ROOM v1.0")
            self.console.print("1. [bold]Full Audit & Strategy[/bold] (Run K.11 + K.12)")
            self.console.print("2. [bold]Shadow Audit Only[/bold] (K.11)")
            self.console.print("3. [bold]Interviewer Sim[/bold] (K.13)")
            self.console.print("4. Exit")
            
            choice = Prompt.ask("Select Operation", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                swot = self.run_k11_shadow_audit()
                self.run_k12_strategy(swot)
            elif choice == "2":
                self.run_k11_shadow_audit()
            elif choice == "3":
                self.run_k13_simulation()
            elif choice == "4":
                sys.exit(0)

if __name__ == "__main__":
    war_room = WarRoom()
    war_room.main_menu()
