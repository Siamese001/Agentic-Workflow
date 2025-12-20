"""
Canon Validator Utilities
Helper functions for file scanning and decorators.
"""

import asyncio
import os
from functools import wraps
from typing import List

from config.canon_validator_config import EXCLUDED_DIRS, EXCLUDED_FILES, is_excluded


def rate_limited_retry(max_retries: int = 5, base_delay: float = 2.0, backoff_factor: float = 2.0):
    """Decorator to handle Gemini 429 errors with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait = base_delay * (backoff_factor ** attempt)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(wait)
                        else:
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator


def get_python_files(root: str = '.') -> List[str]:
    """Get all Python files excluding specified directories and files."""
    print(f"   📂 Scanning Python files in {root}...", flush=True)
    python_files = []
    dir_count = 0
    
    for root_dir, dirs, files in os.walk(root):
        # Filter excluded directories IN-PLACE to prevent os.walk from descending
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        dir_count += 1
        if dir_count % 50 == 0:
            print(f"      Scanned {dir_count} directories, found {len(python_files)} files...", flush=True)
        
        for file in files:
            if file.endswith('.py') and file not in EXCLUDED_FILES:
                file_path = os.path.join(root_dir, file)
                if not is_excluded(file_path):
                    python_files.append(file_path)
    
    print(f"   ✅ Found {len(python_files)} Python files in {dir_count} directories", flush=True)
    return python_files
