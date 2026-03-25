# Color Scheme Reference

**Standard ANSI color codes** for progress displays and terminal output in Windsurf.

## Primary Colors

| Color | ANSI Code | Hex | Use Case | Example |
|-------|-----------|-----|----------|---------|
| **Bright Red** | `\033[91m` | #FF0000 | Error, failure, critical | `❌ Failed` |
| **Bright Green** | `\033[92m` | #00FF00 | Success, complete, healthy | `✅ Complete` |
| **Bright Yellow** | `\033[93m` | #FFFF00 | Warning, slow, caution | `⚠️ Slow` |
| **Bright Blue** | `\033[94m` | #0000FF | In-progress, processing | `🔄 Running` |
| **Bright Magenta** | `\033[95m` | #FF00FF | Debug, info | `🐛 Debug` |
| **Bright Cyan** | `\033[96m` | #00FFFF | Query, search | `🔍 Querying` |
| **Bright White** | `\033[97m` | #FFFFFF | Neutral, default | `⏸ Pending` |

## Background Colors

| Color | ANSI Code | Use Case |
|-------|-----------|----------|
| **Red Background** | `\033[101m` | Critical errors |
| **Green Background** | `\033[102m` | Success highlights |
| **Yellow Background** | `\033[103m` | Warning highlights |
| **Blue Background** | `\033[104m` | Active operation |

## Formatting Codes

| Code | Effect | Example |
|------|--------|---------|
| **Reset** | `\033[0m` | Reset all formatting |
| **Bold** | `\033[1m` | Bold text |
| **Underline** | `\033[4m` | Underlined text |
| **Clear Line** | `\033[K` | Clear to end of line |
| **Save Cursor** | `\033[s` | Save cursor position |
| **Restore Cursor** | `\033[u` | Restore cursor position |

## Status Mapping

### Operation States
```python
STATUS_COLORS = {
    'success': '\033[92m',      # Bright Green
    'error': '\033[91m',        # Bright Red  
    'warning': '\033[93m',      # Bright Yellow
    'in_progress': '\033[94m', # Bright Blue
    'pending': '\033[97m',     # Bright White
    'debug': '\033[95m',        # Bright Magenta
    'query': '\033[96m',        # Bright Cyan
}
```

### Progress Thresholds
```python
def get_progress_color(percentage):
    """Return color based on completion percentage"""
    if percentage >= 90:
        return '\033[92m'  # Green - nearly complete
    elif percentage >= 70:
        return '\033[94m'  # Blue - good progress
    elif percentage >= 40:
        return '\033[93m'  # Yellow - moderate progress
    else:
        return '\033[91m'  # Red - slow progress
```

### Performance Indicators
```python
def get_performance_color(actual_time, expected_time):
    """Return color based on performance vs expectation"""
    ratio = actual_time / expected_time
    if ratio <= 1.0:
        return '\033[92m'  # Green - on time or faster
    elif ratio <= 1.5:
        return '\033[93m'  # Yellow - slower but acceptable
    elif ratio <= 2.0:
        return '\033[95m'  # Magenta - significantly slower
    else:
        return '\033[91m'  # Red - critically slow
```

## Icon Mapping

| Icon | Unicode | Color | Meaning |
|------|---------|-------|---------|
| ✅ | U+2705 | Green | Success/Complete |
| ❌ | U+274C | Red | Error/Failed |
| ⚠️ | U+26A0 | Yellow | Warning/Caution |
| 🔄 | U+1F504 | Blue | In-Progress/Processing |
| ⏸ | U+23F8 | White | Paused/Pending |
| 🔍 | U+1F50D | Cyan | Querying/Searching |
| 🐛 | U+1F41B | Magenta | Debug/Info |
| ⚡ | U+26A1 | Yellow | Fast operation |
| 🐌 | U+1F40C | Red | Slow operation |

## Usage Examples

### Basic Colored Text
```python
def print_status(message, status='neutral'):
    color = STATUS_COLORS.get(status, '\033[97m')
    reset = '\033[0m'
    print(f"{color}{message}{reset}")

# Usage
print_status("✅ Operation completed successfully", "success")
print_status("❌ Operation failed", "error")
print_status("⚠️ Operation slower than expected", "warning")
```

### Progress Bar with Colors
```python
def colored_progress_bar(current, total, width=40):
    percentage = (current / total) * 100
    color = get_progress_color(percentage)
    reset = '\033[0m'
    
    filled = int(width * current // total)
    bar = '█' * filled + '░' * (width - filled)
    
    return f"{color}[{bar}]{reset} {percentage:5.1f}% ({current}/{total})"
```

### Status Line Updates
```python
def update_status_line(message, status='in_progress'):
    """Update current line with colored status"""
    color = STATUS_COLORS.get(status, '\033[97m')
    reset = '\033[0m'
    clear = '\033[K'
    
    print(f"\r{clear}{color}{message}{reset}", end='', flush=True)
```

### Multi-line Status Display
```python
def show_operation_summary(operations):
    """Display summary table with colored status"""
    for op_name, result in operations.items():
        if result['success']:
            status_icon = "✅"
            color = '\033[92m'
        else:
            status_icon = "❌"
            color = '\033[91m'
        
        reset = '\033[0m'
        duration = f"{result['duration']:.2f}s"
        print(f"{color}{status_icon} {op_name:<20} {duration:>8}{reset}")
```

## Terminal Compatibility

### Supported Terminals
- **Windows Terminal** (Windows 11/10)
- **PowerShell** (with ANSI support)
- **CMD** (limited ANSI support)
- **WSL** (full ANSI support)
- **Git Bash** (full ANSI support)
- **VS Code Integrated Terminal** (full ANSI support)

### Detection and Fallback
```python
import sys
import os

def supports_color():
    """Check if terminal supports ANSI colors"""
    # Windows
    if sys.platform == 'win32':
        # Windows 10+ supports ANSI
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            return kernel32.GetConsoleMode(kernel32.GetStdHandle(-11)) != 0
        except:
            return False
    
    # Unix-like systems
    return os.isatty(sys.stdout.fileno())

def safe_print(message, status='neutral'):
    """Print with colors if supported, plain text otherwise"""
    if supports_color():
        color = STATUS_COLORS.get(status, '\033[97m')
        reset = '\033[0m'
        print(f"{color}{message}{reset}")
    else:
        # Fallback to plain text with status prefixes
        prefixes = {
            'success': "[OK] ",
            'error': "[ERROR] ",
            'warning': "[WARN] ",
            'in_progress': "[...] ",
            'pending': "[WAIT] ",
        }
        prefix = prefixes.get(status, "")
        print(f"{prefix}{message}")
```

## Best Practices

1. **Always reset colors** after use to avoid bleeding
2. **Use clear line codes** (`\033[K`) when updating progress
3. **Check terminal compatibility** before using colors
4. **Provide fallbacks** for terminals without color support
5. **Use consistent color mapping** across all operations
6. **Avoid overuse** - color should enhance, not overwhelm
7. **Test in different terminals** to ensure compatibility
