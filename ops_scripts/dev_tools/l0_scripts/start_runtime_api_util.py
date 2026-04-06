"""
Start the Runtime API server for the Live Runtime Dashboard.

This script starts the FastAPI server that provides real-time telemetry
data to the dashboard for meta-learning, Redis, Pinecone, and execution
flow visualization.

Usage:
    python scripts/start_runtime_api_util.py

    # With custom port
    python scripts/start_runtime_api_util.py --port 8081

    # With reload for development
    python scripts/start_runtime_api_util.py --reload

API Endpoints:
    GET /api/health                     - Health check
    GET /api/runtime/state              - Full runtime state
    GET /api/meta-learning/statistics   - Meta-learning stats
    GET /api/meta-learning/activity     - Meta-learning activity
    GET /api/redis/stats                - Redis cache statistics
    GET /api/redis/logs                 - Recent Redis operations
    GET /api/pinecone/stats             - Pinecone vector statistics
    GET /api/execution/timeline         - Agent execution timeline
    GET /api/metrics/latency            - API latency metrics
    POST /api/meta-learning/experience  - Record new experience
"""
import argparse
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

def main():
    """Start the Runtime API server."""
    parser = argparse.ArgumentParser(description='Start Runtime API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8081, help='Port to listen on (default: 8081)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes (default: 1)')
    args = parser.parse_args()
    print('=' * 70)
    print('RUNTIME API SERVER')
    print('=' * 70)
    print(f'Host: {args.host}')
    print(f'Port: {args.port}')
    print(f'Reload: {args.reload}')
    print(f'Workers: {args.workers}')
    print('=' * 70)
    print()
    print('API Endpoints:')
    print(f'  Health:              http://localhost:{args.port}/api/health')
    print(f'  Runtime State:       http://localhost:{args.port}/api/runtime/state')
    print(f'  Meta-Learning Stats: http://localhost:{args.port}/api/meta-learning/statistics')
    print(f'  Redis Stats:         http://localhost:{args.port}/api/redis/stats')
    print(f'  Pinecone Stats:      http://localhost:{args.port}/api/pinecone/stats')
    print(f'  Execution Timeline:  http://localhost:{args.port}/api/execution/timeline')
    print()
    print('Dashboard URL:')
    print('  http://localhost:8765/autonomy_dashboard.html#runtime')
    print()
    print('Press Ctrl+C to stop the server')
    print('=' * 70)
    try:
        import uvicorn
        from agentic_core.L6_observability.api.runtime_api import app  # guardian: allow-layer-violation -- runtime API utility script requires L6 observability layer for server startup
        uvicorn.run('agentic_core.L6_observability.api.runtime_api:app', host=args.host, port=args.port, reload=args.reload, workers=args.workers if not args.reload else 1, log_level='info')
    except ImportError as e:
        print(f'\n❌ Error: Missing dependency - {e}')
        print('\nInstall required packages:')
        print('  pip install fastapi uvicorn')
        sys.exit(1)
    except KeyboardInterrupt:  # guardian: allow-broad-exception -- graceful shutdown on user interrupt
        print('\n\n✅ Server stopped')
        sys.exit(0)
    except Exception as e:
        print(f'\n❌ Error starting server: {e}')
        sys.exit(1)
if __name__ == '__main__':
    main()
