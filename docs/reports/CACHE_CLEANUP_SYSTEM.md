# Repository Cache Cleanup System

A comprehensive cache cleanup system for Python repositories with Git integration and cross-platform compatibility.

## Components

### 1. Core Cleanup Utility
**File**: `scripts/purge_cache.py`

Recursively removes all Python cache artifacts:
- `__pycache__/` directories
- `*.pyc` and `*.pyo` files
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `temp_*` directories
- `.sovereign_healing_backup/`

**Usage**:
```bash
python scripts/purge_cache.py
```

### 2. Git Integration

#### Post-Checkout Hook
**Files**: 
- `.git/hooks/post-checkout` (Unix/Linux)
- `.git/hooks/post-checkout.ps1` (Windows)

Automatically purges cache after branch switches to prevent stale bytecode issues.

#### Pre-Commit Hook
**File**: `.pre-commit-config.yaml`

Ensures no cache files are staged for commit:
```yaml
-   id: purge-cache
    name: Purge Python Cache
    entry: python scripts/purge_cache.py
    language: python
    pass_filenames: false
    always_run: true
```

### 3. Bytecode Control Utility
**File**: `scripts/bytecode_control.py`

Provides environment-based control over Python bytecode generation.

**Commands**:
```bash
# Disable bytecode generation
python scripts/bytecode_control.py --disable

# Enable bytecode generation
python scripts/bytecode_control.py --enable

# Show current status
python scripts/bytecode_control.py --status

# Create no-bytecode launcher
python scripts/bytecode_control.py --create-launcher
```

### 4. Environment Variable Control

Set `PYTHONDONTWRITEBYTECODE=1` to disable bytecode generation:
```bash
# Windows
set PYTHONDONTWRITEBYTECODE=1

# Unix/Linux/macOS
export PYTHONDONTWRITEBYTECODE=1
```

## Installation

1. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

2. **Make Git Hooks Executable** (Unix/Linux):
   ```bash
   chmod +x .git/hooks/post-checkout
   ```

3. **Verify Installation**:
   ```bash
   python scripts/validate_cache_system.py
   ```

## Usage Patterns

### Development Workflow
1. Switch branches → Cache automatically purged by post-checkout hook
2. Make changes → Pre-commit hook prevents cache commits
3. Run tests → Clean environment without stale bytecode

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Purge Cache
  run: python scripts/purge_cache.py
```

### Manual Cleanup
```bash
# Quick cleanup
python scripts/purge_cache.py

# Disable future bytecode generation
python scripts/bytecode_control.py --disable
```

## Testing

### Validation Script
```bash
python scripts/validate_cache_system.py
```

### Test Suite
```bash
# Windows-compatible tests
python tests/test_cache_purge_windows.py

# Original comprehensive tests (Unix/Linux)
python tests/test_cache_purge.py
```

## Cross-Platform Compatibility

- **Windows**: PowerShell hooks, `python` command
- **Unix/Linux**: Bash hooks, `python3` command
- **macOS**: Bash hooks, `python3` command
- **Encoding**: UTF-8 with fallback handling

## Configuration

### Custom Patterns
Edit `scripts/purge_cache.py` to add/remove patterns:
```python
patterns = [
    "**/__pycache__",
    "**/*.py[co]",
    # Add your custom patterns here
]
```

### Pre-commit Configuration
Add to `.pre-commit-config.yaml`:
```yaml
repos:
-   repo: local
    hooks:
    -   id: purge-cache
        name: Purge Python Cache
        entry: python scripts/purge_cache.py
        language: python
        pass_filenames: false
        always_run: true
```

## Troubleshooting

### Unicode Issues on Windows
If you encounter encoding errors, the system includes fallback handling for Windows codepages.

### Git Hooks Not Running
1. Verify hook files exist in `.git/hooks/`
2. Check file permissions (Unix/Linux: `chmod +x`)
3. Ensure Git is configured to run hooks

### Cache Files Persisting
1. Check file permissions
2. Verify patterns match your cache files
3. Run with elevated privileges if needed

## Benefits

1. **Clean Repository**: No cache artifacts in version control
2. **Branch Safety**: No stale bytecode after switches
3. **CI/CD Reliability**: Consistent environments
4. **Storage Efficiency**: Reduced repository size
5. **Cross-Platform**: Works on Windows, Linux, macOS

## Integration with Existing Workflows

The cache cleanup system is designed to be non-intrusive:
- Runs automatically during Git operations
- Preserves all source files
- No configuration required for basic usage
- Optional fine-tuning available

## Security Considerations

- Scripts only remove cache-related patterns
- Source files are never touched
- Temporary files are safely handled
- No network access required
