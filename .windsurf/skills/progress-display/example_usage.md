#!/usr/bin/env python3
"""
Progress Display Implementation Example

Demonstrates the progress display functionality for Windsurf operations.
This script shows how to integrate colored progress bars and percentage displays
into long-running operations.

Usage:
    python progress_example.py --demo basic
    python progress_example.py --demo files
    python progress_example.py --demo tests
"""

import argparse
import os
import sys
import time
import random
from pathlib import Path
from typing import List, Callable

# ANSI Color codes
COLORS = {
    'reset': '\033[0m',
    'success': '\033[92m',      # Bright Green
    'error': '\033[91m',        # Bright Red  
    'warning': '\033[93m',      # Bright Yellow
    'in_progress': '\033[94m', # Bright Blue
    'pending': '\033[97m',     # Bright White
    'debug': '\033[95m',        # Bright Magenta
    'query': '\033[96m',        # Bright Cyan
}

def get_progress_color(percentage: float) -> str:
    """Return color based on completion percentage"""
    if percentage >= 90:
        return COLORS['success']      # Green - nearly complete
    elif percentage >= 70:
        return COLORS['in_progress'] # Blue - good progress
    elif percentage >= 40:
        return COLORS['warning']      # Yellow - moderate progress
    else:
        return COLORS['error']        # Red - slow progress

def format_progress_bar(current: int, total: int, width: int = 40) -> str:
    """Generate standardized progress bar with colors"""
    percentage = (current / total) * 100
    color = get_progress_color(percentage)
    reset = COLORS['reset']
    
    filled = int(width * current // total)
    bar = '█' * filled + '░' * (width - filled)
    
    return f"{color}[{bar}]{reset} {percentage:5.1f}% ({current}/{total})"

class ETACalculator:
    """Calculate estimated time remaining"""
    def __init__(self):
        self.start_time = time.time()
        self.samples = []
        self.max_samples = 10
        
    def add_sample(self, current: int, total: int):
        """Add a progress sample for ETA calculation"""
        now = time.time()
        elapsed = now - self.start_time
        
        if current > 0:
            rate = current / elapsed
            self.samples.append(rate)
            
            if len(self.samples) > self.max_samples:
                self.samples.pop(0)
                
    def get_eta(self, current: int, total: int) -> str:
        """Calculate estimated time remaining"""
        self.add_sample(current, total)
        
        if current == 0 or not self.samples:
            return "∞"
            
        avg_rate = sum(self.samples) / len(self.samples)
        remaining = total - current
        eta_seconds = remaining / avg_rate if avg_rate > 0 else float('inf')
        
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            return f"{eta_seconds/60:.1f}m"
        else:
            return f"{eta_seconds/3600:.1f}h"

class ProgressTracker:
    """Base progress tracker with standardized display"""
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.operation_name = operation_name
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.eta_calculator = ETACalculator()
        
    def start(self):
        """Initialize progress tracking"""
        print(f"{COLORS['query']}🔍 Starting {self.operation_name}...{COLORS['reset']}")
        self.start_time = time.time()
        
    def update(self, increment: int = 1, message: str = ""):
        """Update progress by increment"""
        self.current_item += increment
        self.last_update_time = time.time()
        
        if self._should_update_display():
            self._display_progress(message)
            
    def complete(self, message: str = "Complete"):
        """Mark operation as complete"""
        self.current_item = self.total_items
        progress_bar = format_progress_bar(self.current_item, self.total_items)
        print(f"\r{COLORS['reset']}\033[K{progress_bar} - {COLORS['success']}✅ {message}{COLORS['reset']}")
        print()
        
    def fail(self, error_message: str):
        """Mark operation as failed"""
        progress_bar = format_progress_bar(self.current_item, self.total_items)
        print(f"\r{COLORS['reset']}\033[K{progress_bar} - {COLORS['error']}❌ {error_message}{COLORS['reset']}")
        print()
        
    def _should_update_display(self) -> bool:
        """Determine if display should be updated"""
        time_since_last = time.time() - self.last_update_time
        progress_percent = (self.current_item / self.total_items) * 100
        
        return (time_since_last >= 1.0 or 
                self.current_item % max(1, self.total_items // 20) == 0 or
                self.current_item == self.total_items)
    
    def _display_progress(self, message: str = ""):
        """Display current progress"""
        progress_bar = format_progress_bar(self.current_item, self.total_items)
        eta = self.eta_calculator.get_eta(self.current_item, self.total_items)
        
        line = f"\r{COLORS['reset']}\033[K{progress_bar} - ETA: {eta}"
        if message:
            line += f" - {COLORS['in_progress']}{message}{COLORS['reset']}"
            
        print(line, end='', flush=True)

def demo_basic_progress():
    """Demonstrate basic progress bar functionality"""
    print(f"{COLORS['debug']}🐛 Basic Progress Demo{COLORS['reset']}")
    print()
    
    tracker = ProgressTracker(100, "Basic Progress Demo")
    tracker.start()
    
    for i in range(100):
        # Simulate work
        time.sleep(0.05)
        
        # Add some randomness to simulate variable processing times
        if i % 10 == 0:
            time.sleep(random.uniform(0.1, 0.3))
        
        tracker.update(1, f"Processing item {i+1}")
    
    tracker.complete("Basic demo completed")

def demo_file_scanning():
    """Demonstrate file scanning progress"""
    print(f"{COLORS['debug']}🐛 File Scanning Demo{COLORS['reset']}")
    print()
    
    # Simulate finding Python files
    repo_path = Path(".")
    python_files = list(repo_path.rglob("*.py"))[:50]  # Limit to 50 for demo
    
    if not python_files:
        print(f"{COLORS['warning']}⚠️ No Python files found for demo{COLORS['reset']}")
        return
    
    tracker = ProgressTracker(len(python_files), "Scanning Python files")
    tracker.start()
    
    for i, file_path in enumerate(python_files):
        # Simulate file processing
        time.sleep(random.uniform(0.1, 0.3))
        
        tracker.update(1, f"Scanning {file_path.name}")
    
    tracker.complete(f"Scanned {len(python_files)} Python files")

def demo_test_execution():
    """Demonstrate test execution progress"""
    print(f"{COLORS['debug']}🐛 Test Execution Demo{COLORS['reset']}")
    print()
    
    # Simulate test nodes
    test_nodes = [f"test_module_{i}" for i in range(30)]
    passed = failed = 0
    
    tracker = ProgressTracker(len(test_nodes), "Running tests")
    tracker.start()
    
    for i, test_id in enumerate(test_nodes):
        # Simulate test execution
        time.sleep(random.uniform(0.2, 0.5))
        
        # Random test results
        if random.random() < 0.85:  # 85% pass rate
            passed += 1
            status = f"✅ {passed} ❌ {failed}"
        else:
            failed += 1
            status = f"✅ {passed} ❌ {failed}"
        
        tracker.update(1, status)
    
    # Final summary
    if failed > 0:
        final_color = COLORS['warning']
        icon = "⚠️"
    else:
        final_color = COLORS['success']
        icon = "✅"
        
    tracker.complete(f"{icon} Results: {passed} passed, {failed} failed")

def demo_adg_operations():
    """Demonstrate ADG operation progress"""
    print(f"{COLORS['debug']}🐛 ADG Operations Demo{COLORS['reset']}")
    print()
    
    # Module scanning phase
    modules = [f"module_{i}" for i in range(40)]
    module_tracker = ProgressTracker(len(modules), "ADG Module Scanning")
    module_tracker.start()
    
    for i, module in enumerate(modules):
        time.sleep(random.uniform(0.1, 0.2))
        module_tracker.update(1, f"Scanning {module}")
    
    module_tracker.complete(f"Scanned {len(modules)} modules")
    
    # Edge building phase
    edges = [f"edge_{i}" for i in range(200)]
    edge_tracker = ProgressTracker(len(edges), "ADG Edge Building")
    edge_tracker.start()
    
    for i, edge in enumerate(edges):
        time.sleep(random.uniform(0.02, 0.05))
        edge_tracker.update(1, f"Building edge {i+1}")
    
    edge_tracker.complete(f"Built {len(edges)} edges")
    
    # Validation phase
    print(f"{COLORS['query']}🔍 Validating ADG structure...{COLORS['reset']}")
    time.sleep(1.0)
    print(f"{COLORS['success']}✅ ADG validation complete{COLORS['reset']}")

def supports_color() -> bool:
    """Check if terminal supports ANSI colors"""
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            return kernel32.GetConsoleMode(kernel32.GetStdHandle(-11)) != 0
        except:
            return False
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def main():
    parser = argparse.ArgumentParser(description="Progress Display Demo")
    parser.add_argument('--demo', choices=['basic', 'files', 'tests', 'adg', 'all'], 
                       default='all', help='Demo to run')
    
    args = parser.parse_args()
    
    if not supports_color():
        print("Warning: Terminal doesn't support ANSI colors. Output will be plain text.")
    
    demos = {
        'basic': demo_basic_progress,
        'files': demo_file_scanning,
        'tests': demo_test_execution,
        'adg': demo_adg_operations,
    }
    
    if args.demo == 'all':
        for demo_name, demo_func in demos.items():
            demo_func()
            print()
    else:
        demos[args.demo]()

if __name__ == "__main__":
    main()
