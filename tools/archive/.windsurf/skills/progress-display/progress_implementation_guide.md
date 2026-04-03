# Progress Implementation Guide

**Technical implementation details** for integrating progress displays into existing Windsurf tools and scripts.

## Core Progress Class

### BaseProgressTracker
```python
import time
import sys
from typing import Optional, Callable
from enum import Enum

class OperationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class BaseProgressTracker:
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.operation_name = operation_name
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.status = OperationStatus.PENDING
        self.eta_calculator = ETACalculator()
        
    def start(self):
        """Initialize progress tracking"""
        self.status = OperationStatus.IN_PROGRESS
        self.start_time = time.time()
        self._display_header()
        
    def update(self, increment: int = 1, message: str = ""):
        """Update progress by increment"""
        self.current_item += increment
        self.last_update_time = time.time()
        
        if self._should_update_display():
            self._display_progress(message)
            
    def set_status(self, status: OperationStatus, message: str = ""):
        """Set operation status"""
        self.status = status
        if message:
            self._display_status_message(message)
            
    def complete(self, message: str = "Complete"):
        """Mark operation as complete"""
        self.current_item = self.total_items
        self.status = OperationStatus.SUCCESS
        self._display_completion(message)
        
    def fail(self, error_message: str):
        """Mark operation as failed"""
        self.status = OperationStatus.ERROR
        self._display_error(error_message)
        
    def _should_update_display(self) -> bool:
        """Determine if display should be updated"""
        # Update every 5 seconds minimum, or every 10% progress
        time_since_last = time.time() - self.last_update_time
        progress_percent = (self.current_item / self.total_items) * 100
        
        return (time_since_last >= 5.0 or 
                self.current_item % max(1, self.total_items // 10) == 0 or
                self.current_item == self.total_items)
    
    def _display_progress(self, message: str = ""):
        """Display current progress"""
        progress_bar = colored_progress_bar(self.current_item, self.total_items)
        eta = self.eta_calculator.get_eta(self.current_item, self.total_items)
        
        line = f"\r\033[K{progress_bar} - ETA: {eta}"
        if message:
            line += f" - {message}"
            
        print(line, end='', flush=True)
```

### ETACalculator Implementation
```python
class ETACalculator:
    def __init__(self):
        self.start_time = time.time()
        self.samples = []  # Store recent samples for smoothing
        self.max_samples = 10
        
    def add_sample(self, current: int, total: int):
        """Add a progress sample for ETA calculation"""
        now = time.time()
        elapsed = now - self.start_time
        
        if current > 0:
            rate = current / elapsed
            self.samples.append(rate)
            
            # Keep only recent samples
            if len(self.samples) > self.max_samples:
                self.samples.pop(0)
                
    def get_eta(self, current: int, total: int) -> str:
        """Calculate estimated time remaining"""
        self.add_sample(current, total)
        
        if current == 0 or not self.samples:
            return "∞"
            
        # Use average of recent samples for stability
        avg_rate = sum(self.samples) / len(self.samples)
        remaining = total - current
        eta_seconds = remaining / avg_rate if avg_rate > 0 else float('inf')
        
        return self._format_duration(eta_seconds)
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
```

## Integration Patterns

### 1. File System Operations
```python
class FileSystemProgressTracker(BaseProgressTracker):
    def __init__(self, file_list: list, operation_name: str = "Scanning files"):
        super().__init__(len(file_list), operation_name)
        self.file_list = file_list
        
    def scan_files(self, processor_func: Callable):
        """Scan files with progress display"""
        self.start()
        
        try:
            for i, file_path in enumerate(self.file_list):
                processor_func(file_path)
                self.update(1, f"Processing {os.path.basename(file_path)}")
                
            self.complete(f"Scanned {self.total_items} files")
            
        except Exception as e:
            self.fail(f"Failed to scan files: {e}")
            raise

# Usage
def scan_repository_with_progress(repo_path: str):
    file_list = get_all_python_files(repo_path)
    tracker = FileSystemProgressTracker(file_list, "Scanning repository")
    
    def process_file(file_path):
        # Your file processing logic here
        analyze_file(file_path)
    
    tracker.scan_files(process_file)
```

### 2. Test Execution Progress
```python
class TestProgressTracker(BaseProgressTracker):
    def __init__(self, test_nodes: list):
        super().__init__(len(test_nodes), "Running tests")
        self.test_nodes = test_nodes
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        
    def run_tests(self, test_runner: Callable):
        """Run tests with detailed progress"""
        self.start()
        
        try:
            for i, test_id in enumerate(self.test_nodes):
                result = test_runner(test_id)
                
                if result.passed:
                    self.passed += 1
                elif result.failed:
                    self.failed += 1
                else:
                    self.skipped += 1
                    
                status_msg = f"✅ {self.passed} ❌ {self.failed} ⏸ {self.skipped}"
                self.update(1, status_msg)
                
            # Final summary
            self._display_test_summary()
            
        except Exception as e:
            self.fail(f"Test execution failed: {e}")
            raise
            
    def _display_test_summary(self):
        """Display final test summary"""
        print()  # New line after progress bar
        
        if self.failed > 0:
            color = '\033[91m'
            icon = "❌"
        elif self.skipped > 0:
            color = '\033[93m'
            icon = "⚠️"
        else:
            color = '\033[92m'
            icon = "✅"
            
        reset = '\033[0m'
        summary = f"{icon} Results: {self.passed} passed, {self.failed} failed, {self.skipped} skipped"
        print(f"{color}{summary}{reset}")
```

### 3. ADG Operations Progress
```python
class ADGProgressTracker(BaseProgressTracker):
    def __init__(self, operation_type: str, total_items: int):
        super().__init__(total_items, f"ADG {operation_type}")
        self.operation_type = operation_type
        
    def scan_modules(self, scanner, module_list):
        """Scan modules for ADG generation"""
        self.start()
        
        try:
            for i, module in enumerate(module_list):
                scanner.scan_module(module)
                self.update(1, f"Scanning {module}")
                
            self.complete(f"Scanned {self.total_items} modules")
            
        except Exception as e:
            self.fail(f"Module scanning failed: {e}")
            raise
            
    def build_edges(self, builder, edge_list):
        """Build dependency edges"""
        self.start()
        
        try:
            for i, edge in enumerate(edge_list):
                builder.add_edge(edge)
                self.update(1, f"Building edges")
                
            self.complete(f"Built {self.total_items} edges")
            
        except Exception as e:
            self.fail(f"Edge building failed: {e}")
            raise
```

## Context Manager Pattern

### Progress Context Manager
```python
class ProgressContext:
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.tracker = BaseProgressTracker(total_items, operation_name)
        
    def __enter__(self):
        self.tracker.start()
        return self.tracker
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.tracker.complete()
        else:
            self.tracker.fail(str(exc_val))
        return False  # Don't suppress exceptions

# Usage
with ProgressContext(len(file_list), "Processing files") as progress:
    for i, file_path in enumerate(file_list):
        process_file(file_path)
        progress.update(1, f"Processed {os.path.basename(file_path)}")
```

## Decorator Pattern

### Progress Decorator
```python
def with_progress(operation_name: str = None):
    """Decorator to add progress to any iterable operation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to extract iterable from result
            result = func(*args, **kwargs)
            
            if hasattr(result, '__len__') and hasattr(result, '__iter__'):
                total_items = len(result)
                name = operation_name or func.__name__
                
                with ProgressContext(total_items, name) as progress:
                    processed_items = []
                    for item in result:
                        processed_items.append(item)
                        progress.update(1, f"Processing item {len(processed_items)}")
                    
                    return processed_items
            else:
                return result
                
        return wrapper
    return decorator

# Usage
@with_progress("Loading data")
def load_large_dataset():
    return list(range(1000))

# Automatically shows progress when iterated
data = load_large_dataset()
```

## Integration with Existing Tools

### 1. Modifying generate_full_adg.py
```python
# Add to imports
from .progress_display import ADGProgressTracker

# In main function
def generate_adg_with_progress():
    print("🔍 Starting ADG generation...")
    
    # Module scanning
    modules = discover_modules()
    module_tracker = ADGProgressTracker("module scan", len(modules))
    module_tracker.scan_modules(scanner, modules)
    
    # Edge building
    edges = discover_edges()
    edge_tracker = ADGProgressTracker("edge building", len(edges))
    edge_tracker.build_edges(builder, edges)
    
    # Validation
    print("✅ ADG generation complete!")
```

### 2. Modifying test runners
```python
# In pytest wrapper
def run_pytest_with_progress(test_args):
    test_nodes = collect_test_nodes(test_args)
    tracker = TestProgressTracker(test_nodes)
    
    def test_runner(test_id):
        return run_single_test(test_id)
    
    tracker.run_tests(test_runner)
    return tracker.get_results()
```

### 3. Modifying file system tools
```python
# In file search tools
def search_files_with_progress(pattern, search_path):
    matching_files = []
    
    for root, dirs, files in os.walk(search_path):
        file_list = [os.path.join(root, f) for f in files if f.endswith('.py')]
        
        if file_list:
            tracker = FileSystemProgressTracker(file_list, f"Searching {root}")
            
            def check_file(file_path):
                if pattern in file_path or pattern_in_file(file_path, pattern):
                    matching_files.append(file_path)
            
            tracker.scan_files(check_file)
    
    return matching_files
```

## Error Handling and Recovery

### Checkpoint Support
```python
class CheckpointProgressTracker(BaseProgressTracker):
    def __init__(self, total_items: int, checkpoint_file: str, operation_name: str = "Processing"):
        super().__init__(total_items, operation_name)
        self.checkpoint_file = checkpoint_file
        self.current_item = self._load_checkpoint()
        
    def _load_checkpoint(self) -> int:
        """Load progress from checkpoint file"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return int(f.read().strip())
            except:
                return 0
        return 0
        
    def _save_checkpoint(self):
        """Save current progress to checkpoint file"""
        with open(self.checkpoint_file, 'w') as f:
            f.write(str(self.current_item))
            
    def update(self, increment: int = 1, message: str = ""):
        """Update with checkpoint saving"""
        super().update(increment, message)
        self._save_checkpoint()
        
    def complete(self, message: str = "Complete"):
        """Complete and remove checkpoint file"""
        super().complete(message)
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
```

## Performance Considerations

### 1. Update Frequency Optimization
```python
class SmartProgressTracker(BaseProgressTracker):
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        super().__init__(total_items, operation_name)
        self.update_interval = self._calculate_optimal_interval()
        
    def _calculate_optimal_interval(self) -> float:
        """Calculate optimal update interval based on total items"""
        if self.total_items < 100:
            return 1.0  # Update every item for small sets
        elif self.total_items < 1000:
            return 2.0  # Update every 2 seconds
        else:
            return 5.0  # Standard 5-second interval
```

### 2. Memory Efficiency
```python
def memory_efficient_progress(large_iterable, operation_name: str = "Processing"):
    """Progress tracker for very large iterables that don't fit in memory"""
    # First pass: count items
    print(f"🔍 Counting items for {operation_name}...")
    total_count = sum(1 for _ in large_iterable)
    
    # Second pass: process with progress
    tracker = BaseProgressTracker(total_count, operation_name)
    tracker.start()
    
    for item in large_iterable:
        yield item
        tracker.update(1)
    
    tracker.complete()
```

## Testing Progress Display

### Unit Test Example
```python
import io
import sys
from unittest.mock import patch

def test_progress_tracker():
    """Test progress tracker output"""
    
    # Capture stdout
    captured_output = io.StringIO()
    
    with patch('sys.stdout', captured_output):
        tracker = BaseProgressTracker(100, "Test operation")
        tracker.start()
        
        # Simulate progress
        for i in range(0, 101, 10):
            tracker.update(10, f"Processing item {i}")
            time.sleep(0.1)  # Simulate work
            
        tracker.complete("Test complete")
    
    output = captured_output.getvalue()
    
    # Verify progress bar format
    assert "[████" in output
    assert "100%" in output
    assert "Test complete" in output
    assert "\033[92m" in output  # Green color for success
```

This implementation guide provides the foundation for adding consistent, colored progress displays across all Windsurf operations.
