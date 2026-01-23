from __future__ import annotations

"""
L5 Human-in-the-Loop Intervention Server

Provides a FastAPI-based web UI for human approval/veto of high-risk
autonomous actions during validation missions.
"""
import asyncio
import threading
from typing import Any

approval_event: Any = asyncio.Event()
_intervention_server_started = False
_intervention_context = None
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    FASTAPI_AVAILABLE: Any = True
except ImportError:
    FASTAPI_AVAILABLE: Any = False
    uvicorn: Any = None
    FastAPI: Any = None
    HTMLResponse: Any = None


def create_intervention_app() -> Any:
    """Create and configure the FastAPI intervention application."""
    if not FASTAPI_AVAILABLE:
        return None
    app: Any = FastAPI(title="L5 Intervention UI", description="Human-in-the-Loop approval system")

    @app.get("/", response_class=HTMLResponse)
    def get_dashboard() -> Any:
        """Returns HTML dashboard with current plan and signals."""
        ctx: Any = _intervention_context
        signals: Any = list(ctx.signals) if ctx else []
        plan: Any = getattr(ctx, "strategic_plan", "No plan available") if ctx else "No context"
        modified: Any = list(ctx.modified_files) if ctx else []
        html: Any = f"""\n        <!DOCTYPE html>\n        <html>\n        <head>\n            <title>L5 Intervention Required</title>\n            <style>\n                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}\n                .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 8px; }}\n                .signals {{ background: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0; }}\n                .plan {{ background: #d1ecf1; padding: 10px; border-radius: 4px; margin: 10px 0; }}\n                .files {{ background: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0; }}\n                button {{ padding: 15px 30px; margin: 10px; font-size: 18px; cursor: pointer; border: none; border-radius: 4px; }}\n                .approve {{ background: #28a745; color: white; }}\n                .veto {{ background: #dc3545; color: white; }}\n                h1 {{ color: #856404; }}\n            </style>\n        </head>\n        <body>\n            <div class="warning">\n                <h1>[ALERT] L5 INTERVENTION REQUIRED</h1>\n                <p>The autonomous system has detected a <strong>HIGH RISK</strong> action and is awaiting human approval.</p>\n\n                <div class="signals">\n                    <h3>Active Signals:</h3>\n                    <ul>{"".join(f"<li>{s}</li>" for s in signals) or "<li>None</li>"}</ul>\n                </div>\n\n                <div class="plan">\n                    <h3>Strategic Plan:</h3>\n                    <pre>{plan}</pre>\n                </div>\n\n                <div class="files">\n                    <h3>Modified Files ({len(modified)}):</h3>\n                    <ul>{"".join(f"<li>{f}</li>" for f in modified[:10]) or "<li>None</li>"}</ul>\n                    {(f"<p>...and {len(modified) - 10} more</p>" if len(modified) > 10 else "")}\n                </div>\n\n                <div>\n                    <button class="approve" onclick="approve()">[OK] APPROVE</button>\n                    <button class="veto" onclick="veto()">🛑 VETO</button>\n                </div>\n            </div>\n\n            <script>\n                async function approve() {{\n                    await fetch('/approve', {{method: 'POST'}});\n                    document.body.innerHTML = '<h1 style="color: green;">[OK] APPROVED - Resuming execution...</h1>';\n                }}\n                async function veto() {{\n                    await fetch('/veto', {{method: 'POST'}});\n                    document.body.innerHTML = '<h1 style="color: red;">🛑 VETOED - Aborting execution...</h1>';\n                }}\n            </script>\n        </body>\n        </html>\n        """
        return html

    @app.post("/approve")
    def approve_action() -> Any:
        """Approves the pending action and resumes execution."""
        approval_event.set()
        return {"status": "APPROVED", "message": "Execution will resume."}

    @app.post("/veto")
    def veto_action() -> Any:
        """Vetoes the pending action and signals abort."""
        global _intervention_context
        if _intervention_context:
            _intervention_context.signals.add("VETOED")
        approval_event.set()
        return {"status": "VETOED", "message": "Execution will abort."}

    @app.get("/status")
    def get_status() -> Any:
        """Returns current status as JSON."""
        ctx: Any = _intervention_context
        return {
            "waiting": not approval_event.is_set(),
            "signals": list(ctx.signals) if ctx else [],
            "modified_files_count": len(ctx.modified_files) if ctx else 0,
        }

    return app


intervention_app: Any = create_intervention_app() if FASTAPI_AVAILABLE else None


def _run_intervention_server():
    """Runs the uvicorn server (blocking, for thread)."""
    if FASTAPI_AVAILABLE and intervention_app:
        uvicorn.run(intervention_app, host="127.0.0.1", port=8080, log_level="error")


def start_intervention_server(ctx: Any | None = None) -> Any:
    """Starts the intervention server in a daemon thread if not already running."""
    global _intervention_server_started, _intervention_context
    if not FASTAPI_AVAILABLE:
        print("   [!]  FastAPI not available - skipping intervention server")
        return
    _intervention_context = ctx
    if not _intervention_server_started:
        t: Any = threading.Thread(target=_run_intervention_server, daemon=True)
        t.start()
        _intervention_server_started = True
        print("   🌐 Intervention server started at http://127.0.0.1:8080")


def set_intervention_context(ctx: Any) -> Any:
    """Update the intervention context."""
    global _intervention_context
    _intervention_context = ctx


def reset_approval_event() -> Any:
    """Reset the approval event for a new intervention cycle."""
    approval_event.clear()


async def wait_for_approval(timeout: float | None = None) -> bool:
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
        if _intervention_context and "VETOED" in _intervention_context.signals:
            return False
        return True
    except asyncio.TimeoutError:
        return False
