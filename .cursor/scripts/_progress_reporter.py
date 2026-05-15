"""
_progress_reporter.py
Pure extraction: Progress bar and colored output for long-running operations.

This module centralizes progress display logic extracted from existing
scripts that perform scans, builds, and queries. It provides the colored
progress bar pattern required by query-progress-bar.md.

W1 SCOPE: Pure extraction only. No new output formats. No policy changes.
"""

import sys
import time
from typing import Optional, Callable, Any


# ============================================================================
# COLOR CODES (ANSI)
# ============================================================================

COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
}


def colorize(text: str, color: str) -> str:
    """Apply ANSI color to text."""
    code = COLORS.get(color.upper(), "")
    if code and sys.stderr.isatty():
        return f"{code}{text}{COLORS['RESET']}"
    return text


# ============================================================================
# PROGRESS BAR (extracted pattern)
# ============================================================================

class ProgressBar:
    """
    Colored progress bar with ETA for long-running operations.
    
    Pure extraction of pattern required for:
    - Operations >5s
    - Loops >10 items
    - Heavy-named functions (scan_*/build_*/query_*) >12 lines
    
    Does NOT introduce new output formats. Pure extraction only.
    """
    
    def __init__(
        self,
        total: int,
        desc: str = "Processing",
        width: int = 40,
        show_eta: bool = True,
        output=sys.stderr
    ):
        self.total = max(total, 1)
        self.current = 0
        self.desc = desc
        self.width = width
        self.show_eta = show_eta
        self.output = output
        self.start_time = time.time()
        self.last_update = 0
    
    def _format_eta(self) -> str:
        """Calculate and format ETA."""
        if self.current == 0:
            return "ETA: --:--"
        
        elapsed = time.time() - self.start_time
        rate = elapsed / self.current
        remaining = (self.total - self.current) * rate
        
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        return f"ETA: {mins:02d}:{secs:02d}"
    
    def _render(self, force: bool = False):
        """Render the progress bar."""
        now = time.time()
        # Throttle updates to 10Hz unless forced
        if not force and now - self.last_update < 0.1:
            return
        self.last_update = now
        
        pct = min(100.0, 100.0 * self.current / self.total)
        filled = int(self.width * self.current / self.total)
        
        # Color based on progress
        if pct < 30:
            bar_color = "RED"
        elif pct < 70:
            bar_color = "YELLOW"
        else:
            bar_color = "GREEN"
        
        bar = "█" * filled + "░" * (self.width - filled)
        bar = colorize(bar, bar_color)
        
        eta_str = f" {self._format_eta()}" if self.show_eta else ""
        line = f"\r{self.desc}: [{bar}] {pct:5.1f}%{eta_str}"
        
        self.output.write(line)
        self.output.flush()
    
    def update(self, n: int = 1):
        """Update progress by n items."""
        self.current = min(self.current + n, self.total)
        self._render()
    
    def set(self, n: int):
        """Set progress to n items."""
        self.current = max(0, min(n, self.total))
        self._render()
    
    def finish(self, message: Optional[str] = None):
        """Complete the progress bar."""
        self.current = self.total
        self._render(force=True)
        
        if message:
            self.output.write(f" {colorize(message, 'GREEN')}\n")
        else:
            self.output.write("\n")
        self.output.flush()
    
    def __enter__(self):
        self._render()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.finish("Done")
        else:
            self.output.write(f" {colorize('FAILED', 'RED')}\n")
            self.output.flush()


def progress_iter(iterable, desc: str = "Processing", show_eta: bool = True):
    """
    Wrap an iterable with progress bar.
    
    Usage:
        for item in progress_iter(long_list, "Scanning files"):
            process(item)
    """
    items = list(iterable)
    with ProgressBar(len(items), desc, show_eta=show_eta) as bar:
        for item in items:
            yield item
            bar.update(1)


# ============================================================================
# SPINNER (for indeterminate operations)
# ============================================================================

class Spinner:
    """Indeterminate progress indicator for operations without known count."""
    
    CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, desc: str = "Working", output=sys.stderr):
        self.desc = desc
        self.output = output
        self._running = False
        self._idx = 0
    
    def _render(self):
        char = self.CHARS[self._idx % len(self.CHARS)]
        char = colorize(char, "CYAN")
        self.output.write(f"\r{char} {self.desc}...")
        self.output.flush()
        self._idx += 1
    
    def tick(self):
        """Advance spinner one frame."""
        self._render()
    
    def finish(self, message: str = "Done"):
        """Stop spinner with completion message."""
        self.output.write(f"\r{colorize('✓', 'GREEN')} {self.desc}: {message}\n")
        self.output.flush()
    
    def fail(self, message: str = "Failed"):
        """Stop spinner with failure message."""
        self.output.write(f"\r{colorize('✗', 'RED')} {self.desc}: {message}\n")
        self.output.flush()


# ============================================================================
# STATUS MESSAGES
# ============================================================================

def success(msg: str):
    """Print success message."""
    print(colorize(f"✓ {msg}", "GREEN"), file=sys.stderr)

def warning(msg: str):
    """Print warning message."""
    print(colorize(f"⚠ {msg}", "YELLOW"), file=sys.stderr)

def error(msg: str):
    """Print error message."""
    print(colorize(f"✗ {msg}", "RED"), file=sys.stderr)

def info(msg: str):
    """Print info message."""
    print(colorize(f"ℹ {msg}", "BLUE"), file=sys.stderr)


# ============================================================================
# PURE EXTRACTION SUMMARY
# ============================================================================

# This module extracts patterns from existing scripts including:
# - ops_scripts/ci/*.py (colored output patterns)
# - tools/analysis/*.py (progress indicators)
# - .cursor/scripts/*.py (scan/build/query progress)

# NO NEW POLICIES. NO NEW OUTPUT FORMATS.


if __name__ == "__main__":
    # Self-test
    print("Testing progress bar...", file=sys.stderr)
    with ProgressBar(10, "Test") as bar:
        for i in range(10):
            time.sleep(0.05)
            bar.update(1)
    
    print("Testing spinner...", file=sys.stderr)
    spinner = Spinner("Test")
    for i in range(10):
        time.sleep(0.05)
        spinner.tick()
    spinner.finish()
    
    success("Self-test completed")
    print("_progress_reporter: All self-tests passed")
