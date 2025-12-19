"""
Agentic TUI Dashboard - Real-Time Orchestrator Visualization

Provides live visualization of:
- L1-L5 Tri-Brain layer status
- Healing progress and token usage
- Fission mode detection (>40K tokens)
- Signal stream with rolling logs
"""

from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Group, Console
from rich.layout import Layout
from rich.text import Text
from datetime import datetime


class AgenticTUI:
    """
    Real-time TUI dashboard for orchestrator monitoring.
    
    Features:
    - L1-L5 layer status visualization
    - Healing progress tracking
    - Token usage monitoring
    - Fission mode detection
    - Rolling signal stream
    """
    
    def __init__(self, target_dir="agentic_core/", total_violations=233):
        """
        Initialize TUI dashboard.
        
        Args:
            target_dir: Target directory being healed
            total_violations: Total violations detected
        """
        self.target_dir = target_dir
        self.total_violations = total_violations
        self.current_file = "Initializing..."
        self.current_key = "Scanning"
        self.round = 0
        self.tokens = 0
        self.max_tokens = 50000
        self.logs = []
        self.console = Console()

    def update_state(self, file, key, round_num, tokens, log_msg=None):
        """
        Update dashboard state.
        
        Args:
            file: Current file being processed
            key: Current canon key being validated
            round_num: Current healing round
            tokens: Token usage
            log_msg: Optional log message to add to stream
        """
        self.current_file = file
        self.current_key = key
        self.round = round_num
        self.tokens = tokens
        
        if log_msg:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.logs.append(f"[[dim]{timestamp}[/]] {log_msg}")
            if len(self.logs) > 8:
                self.logs.pop(0)

    def generate_layout(self) -> Layout:
        """
        Generate Rich layout for dashboard.
        
        Returns:
            Layout object with all dashboard components
        """
        # Header with L1-L5 Context Window Box
        header = Panel(
            Text("🔗 DEPENDENCY DIPLOMAT - ZERO-LOSS CONTEXT WINDOW", 
                 justify="center", 
                 style="bold white on blue")
        )

        # L1-L5 Layer Status
        l_table = Table(title="Tri-Brain Layer Status", border_style="cyan", expand=True)
        l_table.add_column("Layer", style="bold cyan")
        l_table.add_column("Status", style="magenta")
        l_table.add_row("L5: Safety", "[green]✅ ACTIVE (Guard: 110L)")
        l_table.add_row("L4: State", f"[yellow]📂 {self.target_dir}")
        l_table.add_row("L3: Orchestration", "[bold green]⚙️ HEALING")
        l_table.add_row("L2: Execution", "[orange1]⚡ HIGH LATENCY")
        l_table.add_row("L1: Cognition", f"[bold reverse]🧠 {self.tokens}/{self.max_tokens} Reasoning")

        # Progress Panel with Fission Trigger Awareness
        token_pct = (self.tokens / self.max_tokens) * 100 if self.max_tokens > 0 else 0
        mode = "[bold red]ATOMIC FISSION[/]" if self.tokens > 40000 else "[bold green]HEALING[/]"
        color = "green" if token_pct < 70 else "yellow" if token_pct < 90 else "red"
        
        progress_content = Text.assemble(
            ("\nMode:   ", "bold"), (f"{mode}\n", ""),
            ("Target: ", "bold"), (f"{self.current_file}\n", "yellow"),
            ("Key:    ", "bold"), (f"{self.current_key}\n", "magenta"),
            ("Round:  ", "bold"), (f"{self.round}/5\n", "cyan"),
            ("\nL1 Cognitive Load: ", "bold"), (f"{int(token_pct)}%", color)
        )
        p_panel = Panel(progress_content, title="Mission Progress", border_style="green")

        # Signal Stream (Rolling Logs)
        log_panel = Panel("\n".join(self.logs), title="Signal Stream", border_style="dim")

        # Build layout
        layout = Layout()
        layout.split_column(
            Layout(header, size=3),
            Layout(name="main"),
            Layout(log_panel, size=11)
        )
        layout["main"].split_row(Layout(l_table, ratio=1), Layout(p_panel, ratio=1))
        
        return layout


# Integration Hook Example (Add to orchestrator_main.py)
"""
from agentic_core.infra.tui_dashboard import AgenticTUI
from rich.live import Live

# Initialize TUI
tui = AgenticTUI(target_dir="agentic_core/", total_violations=233)

# Start live display
with Live(tui.generate_layout(), refresh_per_second=4) as live:
    # Inside your healing loop:
    for file in files_to_heal:
        for round_num in range(1, 6):
            # ... healing logic ...
            
            # Update TUI state
            tui.update_state(
                file=file_path,
                key="Key 42",
                round_num=round_num,
                tokens=token_count,
                log_msg=f"✅ Fixed {file_path}"
            )
            
            # Refresh display
            live.update(tui.generate_layout())
"""
