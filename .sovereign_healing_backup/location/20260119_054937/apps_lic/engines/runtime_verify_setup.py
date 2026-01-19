from __future__ import annotations
"""
Tri-Brain Dependency Verification Script
Checks all requirements before running the Magnificent Seven validator
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

def load_env_file() -> Any:
    """Load environment variables from agentic_core.env file if it exists"""
    env_path: Any = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        print(f'📄 Loading environment from: {env_path}')
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line: Any = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key: Any = key.strip()
                    value: Any = value.strip()
                    if key and value and (not os.environ.get(key)):
                        os.environ[key] = value
        print(f'✅ Environment variables loaded from agentic_core.env\n')
    else:
        print(f'⚠️  No .env file found at {env_path}')
        print(f'   Using system environment variables only\n')

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.10+"""
    version: Any = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        return (True, f'✅ Python {version.major}.{version.minor}.{version.micro}')
    return (False, f'❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)')

def check_library(lib_name: str, import_name: str=None) -> Tuple[bool, str]:
    """Check if a Python library is installed"""
    if import_name is None:
        import_name: Any = lib_name
    try:
        __import__(import_name)
        return (True, f'✅ {lib_name} installed')
    except ImportError:
        return (False, f'❌ {lib_name} Missing - install with: pip install {lib_name}')

def check_env_var(var_name: str, optional: bool=False) -> Tuple[bool, str]:
    """Check if environment variable is set"""
    value: Any = os.environ.get(var_name)
    if value:
        if 'KEY' in var_name or 'PASSWORD' in var_name:
            masked: Any = value[:8] + '...' if len(value) > 8 else '***'
            return (True, f'✅ {var_name} set ({masked})')
        return (True, f'✅ {var_name} set ({value})')
    if optional:
        return (True, f'⚠️  {var_name} not set (optional)')
    return (False, f'❌ {var_name} not set')

def check_redis_connection() -> Tuple[bool, str]:
    """Check if Redis is accessible"""
    try:
        import redis
        redis_url: Any = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        client: Any = redis.from_url(redis_url, decode_responses=True)
        client.ping()
        return (True, f'✅ Redis connection successful ({redis_url})')
    except ImportError:
        return (False, '❌ Redis library not installed')
    except Exception as e:
        return (False, f'❌ Redis connection failed: {e}')

def check_pinecone_connection() -> Tuple[bool, str]:
    """Check if Pinecone is accessible"""
    try:
        from pinecone import Pinecone
        api_key: Any = os.environ.get('PINECONE_API_KEY')
        if not api_key:
            return (False, '❌ PINECONE_API_KEY not set')
        pc: Any = Pinecone(api_key=api_key)
        indexes: Any = pc.list_indexes().names()
        if 'canon-memory-l2' in indexes:
            return (True, f"✅ Pinecone connected - index 'canon-memory-l2' exists")
        else:
            return (False, f"❌ Pinecone index 'canon-memory-l2' not found. Available: {indexes}")
    except ImportError:
        return (False, '❌ Pinecone library not installed')
    except Exception as e:
        return (False, f'❌ Pinecone connection failed: {e}')

def check_gemini_connection() -> Tuple[bool, str]:
    """Check if Gemini API is accessible"""
    try:
        import google.generativeai as genai
        api_key: Any = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return (False, '❌ GEMINI_API_KEY not set')
        genai.configure(api_key=api_key)
        return (True, '✅ Gemini API key valid')
    except ImportError:
        return (False, '❌ google-genai library not installed')
    except Exception as e:
        return (False, f'❌ Gemini API connection failed: {e}')

def main() -> Any:
    """Run all verification checks"""
    print('=' * 60)
    print('🧠 TRI-BRAIN DEPENDENCY VERIFICATION')
    print('=' * 60)
    print()
    load_env_file()
    checks: List[Tuple[str, Tuple[bool, str]]] = []
    print('\n📦 SYSTEM REQUIREMENTS')
    print('-' * 60)
    checks.append(('Python Version', check_python_version()))
    print('\n📚 PYTHON LIBRARIES')
    print('-' * 60)
    checks.append(('google-genai', check_library('google-genai', 'google.generativeai')))
    checks.append(('redis', check_library('redis')))
    checks.append(('pinecone-client', check_library('pinecone-client', 'pinecone')))
    checks.append(('isort', check_library('isort')))
    checks.append(('autoflake', check_library('autoflake')))
    checks.append(('pytest', check_library('pytest')))
    print('\n🔐 ENVIRONMENT VARIABLES')
    print('-' * 60)
    checks.append(('GEMINI_API_KEY', check_env_var('GEMINI_API_KEY')))
    checks.append(('REDIS_URL', check_env_var('REDIS_URL')))
    checks.append(('PINECONE_API_KEY', check_env_var('PINECONE_API_KEY')))
    checks.append(('ENABLE_FUZZ', check_env_var('ENABLE_FUZZ', optional=True)))
    print('\n🌐 CONNECTION TESTS')
    print('-' * 60)
    checks.append(('Redis Connection', check_redis_connection()))
    checks.append(('Pinecone Connection', check_pinecone_connection()))
    checks.append(('Gemini API', check_gemini_connection()))
    for name, (success, message) in checks:
        print(f'{message}')
    print('\n' + '=' * 60)
    total: Any = len(checks)
    passed: Any = sum((1 for _, (success, _) in checks if success))
    failed: Any = total - passed
    if failed == 0:
        print(f'✅ ALL CHECKS PASSED ({passed}/{total})')
        print('=' * 60)
        print('\n🚀 System ready to run Magnificent Seven validator!')
        print('\nRun with:')
        print('  python canon_validator_agentic.py')
        return 0
    else:
        print(f'❌ SOME CHECKS FAILED ({passed}/{total} passed, {failed} failed)')
        print('=' * 60)
        print('\n⚠️  System NOT ready. Fix the issues above before running.')
        print('\nFor help, see: SETUP.md')
        return 1
if __name__ == '__main__':
    sys.exit(main())
