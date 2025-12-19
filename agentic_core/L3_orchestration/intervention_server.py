"""
L5 Human-in-the-Loop Intervention Server

Provides a FastAPI-based web UI for human approval/veto of high-risk
autonomous actions during validation missions.
"""

import asyncio
import threading
from typing import Any, Optional

# Global event for pausing execution pending human approval
approval_event = asyncio.Event()
_intervention_server_started = False
_intervention_context = None  # Will hold reference to ValidationContext

# Check for FastAPI availability
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    uvicorn = None
    FastAPI = None
    HTMLResponse = None


def create_intervention_app():
    """Create and configure the FastAPI intervention application."""
    if not FASTAPI_AVAILABLE:
        return None
    
    app = FastAPI(title="L5 Intervention UI", description="Human-in-the-Loop approval system")
    
    @app.get("/", response_class=HTMLResponse)
    def get_dashboard():
        """Returns HTML dashboard with current plan and signals."""
        ctx = _intervention_context
        signals = list(ctx.signals) if ctx else []
        plan = getattr(ctx, 'strategic_plan', 'No plan available') if ctx else 'No context'
        modified = list(ctx.modified_files) if ctx else []
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>L5 Intervention Required</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 8px; }}
                .signals {{ background: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0; }}
                .plan {{ background: #d1ecf1; padding: 10px; border-radius: 4px; margin: 10px 0; }}
                .files {{ background: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0; }}
                button {{ padding: 15px 30px; margin: 10px; font-size: 18px; cursor: pointer; border: none; border-radius: 4px; }}
                .approve {{ background: #28a745; color: white; }}
                .veto {{ background: #dc3545; color: white; }}
                h1 {{ color: #856404; }}
            </style>
        </head>
        <body>
            <div class="warning">
                <h1>🚨 L5 INTERVENTION REQUIRED</h1>
                <p>The autonomous system has detected a <strong>HIGH RISK</strong> action and is awaiting human approval.</p>
                
                <div class="signals">
                    <h3>Active Signals:</h3>
                    <ul>{"".join(f"<li>{s}</li>" for s in signals) or "<li>None</li>"}</ul>
                </div>
                
                <div class="plan">
                    <h3>Strategic Plan:</h3>
                    <pre>{plan}</pre>
                </div>
                
                <div class="files">
                    <h3>Modified Files ({len(modified)}):</h3>
                    <ul>{"".join(f"<li>{f}</li>" for f in modified[:10]) or "<li>None</li>"}</ul>
                    {f"<p>...and {len(modified) - 10} more</p>" if len(modified) > 10 else ""}
                </div>
                
                <div>
                    <button class="approve" onclick="approve()">✅ APPROVE</button>
                    <button class="veto" onclick="veto()">🛑 VETO</button>
                </div>
            </div>
            
            <script>
                async function approve() {{
                    await fetch('/approve', {{method: 'POST'}});
                    document.body.innerHTML = '<h1 style="color: green;">✅ APPROVED - Resuming execution...</h1>';
                }}
                async function veto() {{
                    await fetch('/veto', {{method: 'POST'}});
                    document.body.innerHTML = '<h1 style="color: red;">🛑 VETOED - Aborting execution...</h1>';
                }}
            </script>
        </body>
        </html>
        """
        return html
    
    @app.post("/approve")
    def approve_action():
        """Approves the pending action and resumes execution."""
        approval_event.set()
        return {"status": "APPROVED", "message": "Execution will resume."}
    
    @app.post("/veto")
    def veto_action():
        """Vetoes the pending action and signals abort."""
        global _intervention_context
        if _intervention_context:
            _intervention_context.signals.add("VETOED")
        approval_event.set()
        return {"status": "VETOED", "message": "Execution will abort."}
    
    @app.get("/status")
    def get_status():
        """Returns current status as JSON."""
        ctx = _intervention_context
        return {
            "waiting": not approval_event.is_set(),
            "signals": list(ctx.signals) if ctx else [],
            "modified_files_count": len(ctx.modified_files) if ctx else 0
        }
    
    return app


# Create the app instance
intervention_app = create_intervention_app() if FASTAPI_AVAILABLE else None


def _run_intervention_server():
    """Runs the uvicorn server (blocking, for thread)."""
    if FASTAPI_AVAILABLE and intervention_app:
        uvicorn.run(intervention_app, host="127.0.0.1", port=8080, log_level="error")


def start_intervention_server(ctx: Optional[Any] = None):
    """Starts the intervention server in a daemon thread if not already running."""
    global _intervention_server_started, _intervention_context
    
    if not FASTAPI_AVAILABLE:
        print("   ⚠️  FastAPI not available - skipping intervention server")
        return
    
    _intervention_context = ctx
    
    if not _intervention_server_started:
        t = threading.Thread(target=_run_intervention_server, daemon=True)
        t.start()
        _intervention_server_started = True
        print("   🌐 Intervention server started at http://127.0.0.1:8080")


def set_intervention_context(ctx: Any):
    """Update the intervention context."""
    global _intervention_context
    _intervention_context = ctx


def reset_approval_event():
    """Reset the approval event for a new intervention cycle."""
    approval_event.clear()


async def wait_for_approval(timeout: Optional[float] = None) -> bool:
    """
    Wait for human approval.
    
    Args:
        timeout: Optional timeout in seconds
        
    Returns:
        True if approved, False if vetoed or timed out
    """
    try:
        if timeout:
            await asyncio.wait_for(approval_event.wait(), timeout=timeout)
        else:
            await approval_event.wait()
        
        # Check if vetoed
        if _intervention_context and "VETOED" in _intervention_context.signals:
            return False
        return True
    except asyncio.TimeoutError:
        return False
