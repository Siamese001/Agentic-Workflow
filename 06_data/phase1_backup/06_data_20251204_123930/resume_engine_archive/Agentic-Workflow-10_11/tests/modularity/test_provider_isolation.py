from pathlib import Path
import re

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_only_providers_contain_provider_sdks() -> None:
    """Verify that only providers/ directory contains external SDK imports.
    
    This enforces architectural separation where concrete SDK dependencies
    (openai, anthropic, redis, chromadb, pinecone, etc.) are isolated
    to the providers layer only.
    """
    
    # External SDKs that should be isolated to providers/ only
    external_sdks = {
        'openai', 'anthropic', 'redis', 'chromadb', 'pinecone',
        'google.generativeai', 'transformers', 'torch', 'numpy',
        'pandas', 'sklearn', 'matplotlib', 'seaborn'
    }
    
    # Find all Python files and check for SDK imports
    violations = []
    
    # Check non-provider directories for SDK imports
    exclude_dirs = {'providers', 'tests', '__pycache__', '.venv', '.pytest_cache'}
    
    for py_file in PROJECT_ROOT.rglob('*.py'):
        # Skip files in excluded directories or test files
        if any(exclude_dir in py_file.parts for exclude_dir in exclude_dirs):
            continue
        
        # Skip test files that validate SDK functionality
        if 'test' in py_file.name or 'tests' in py_file.parts:
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Check for direct imports of external SDKs
            for sdk in external_sdks:
                # Match patterns like: import openai, from openai import, etc.
                import_patterns = [
                    rf'^\s*import\s+{re.escape(sdk)}\b',
                    rf'^\s*from\s+{re.escape(sdk)}\s+import',
                ]
                
                for pattern in import_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        violations.append({
                            'file': str(py_file.relative_to(PROJECT_ROOT)),
                            'sdk': sdk,
                            'line': next((i+1 for i, line in enumerate(content.split('\n')) 
                                       if re.search(pattern, line)), None)
                        })
        except (UnicodeDecodeError, PermissionError):
            continue
    
    # Report violations
    if violations:
        violation_details = []
        for violation in violations:
            violation_details.append(
                f"  {violation['file']}:{violation['line']} - {violation['sdk']}"
            )
        
        pytest.fail(
            f"Found {len(violations)} provider SDK isolation violations:\n" +
            "\n".join(violation_details) +
            "\n\nExternal SDKs should only be imported in providers/ directory"
        )






