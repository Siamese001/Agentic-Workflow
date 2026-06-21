#!/bin/bash
# SessionStart hook — replicate the local dependency surface on Claude Code on the web.
#
# Runs ONLY in the remote (web) environment. Installs the pip dependency set declared in
# pyproject.toml (main + dev + infra MINUS the GPU-only `vllm`) plus the `mcp` SDK that the
# local Python MCP servers (adg_sqlite / memory / vector_db) import but which is not listed in
# pyproject.toml. It also exports the env vars that .mcp.json substitutes into the MCP server
# definitions (AGENTIC_REPO_ROOT, ADG_REDIS_URL, PYTHONPATH) and starts a local Redis daemon so
# the memory + adg_sqlite servers have their hot-cache backend.
#
# Design notes:
#   * Synchronous (no async block) so deps are guaranteed present before the agent loop starts.
#   * Idempotent — a sentinel import check skips the (slow) install when the container is cached.
#   * Verbose pip output is redirected to a log to avoid flooding session context.
#   * vllm is intentionally excluded: it requires a CUDA GPU, which the web container lacks.

set -uo pipefail

PROJECT_DIR="${AGENTIC_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR" || exit 0

REDIS_URL="redis://localhost:6379/0"
MEMORY_DB="${MEMORY_DB:-$PROJECT_DIR/artifacts/memory/knowledge_graph.sqlite}"
LOG="/tmp/agentic_session_start.log"
: > "$LOG"

export PYTHONPATH="${PYTHONPATH:-$PROJECT_DIR}"
export AGENTIC_REPO_ROOT="$PROJECT_DIR"
export ADG_REDIS_URL="${ADG_REDIS_URL:-$REDIS_URL}"
export MEMORY_DB="$MEMORY_DB"

if [ -z "${GITKRAKEN_GK_PATH:-}" ]; then
  for candidate in \
    "${LOCALAPPDATA:-}/GitKrakenCLI/gk.exe" \
    "$HOME/AppData/Local/GitKrakenCLI/gk.exe" \
    "/c/Users/amita/AppData/Local/GitKrakenCLI/gk.exe" \
    "/mnt/c/Users/amita/AppData/Local/GitKrakenCLI/gk.exe"
  do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      export GITKRAKEN_GK_PATH="$candidate"
      break
    fi
  done
fi

# Lightweight local+remote visibility check: config sync alone does not prove
# Codex mounted major MCPs into the deferred tool registry.
if [ -f "$PROJECT_DIR/.codex/governance/scripts/mcp_tool_exposure_audit.py" ]; then
  python "$PROJECT_DIR/.codex/governance/scripts/mcp_tool_exposure_audit.py" --advisory \
    >> "$LOG" 2>&1
  audit_rc=$?
  echo "[session-start] mcp tool exposure audit complete (advisory rc=$audit_rc; log=$LOG)"
fi

# Web-only from this point: on local machines the developer already has their
# dependency surface. Keep the exposure audit above active locally.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# --- Persist env vars for the session (consumed by .mcp.json ${...} substitution) ----------
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export PYTHONPATH=\"$PROJECT_DIR\""
    echo "export AGENTIC_REPO_ROOT=\"$PROJECT_DIR\""
    echo "export ADG_REDIS_URL=\"$REDIS_URL\""
    echo "export MEMORY_DB=\"$MEMORY_DB\""
    if [ -n "${GITKRAKEN_GK_PATH:-}" ]; then
      echo "export GITKRAKEN_GK_PATH=\"$GITKRAKEN_GK_PATH\""
    fi
  } >> "$CLAUDE_ENV_FILE"
fi
export PYTHONPATH="$PROJECT_DIR"
export AGENTIC_REPO_ROOT="$PROJECT_DIR"
export ADG_REDIS_URL="$REDIS_URL"
export MEMORY_DB="$MEMORY_DB"

# --- Python dependencies (idempotent) ------------------------------------------------------
# Sentinel: one import each from main / infra / mcp-SDK groups. If all present, skip install.
if python -c "import pydantic, chromadb, mcp.server.fastmcp" >/dev/null 2>&1; then
  echo "[session-start] python deps already present — skipping install"
else
  echo "[session-start] installing python deps (logging to $LOG) ..."
  # --ignore-installed: the web base image ships Debian-managed packages (PyYAML, PyJWT) that
  # lack pip RECORD files; without this flag pip aborts trying to uninstall them.
  python -m pip install --ignore-installed -e ".[dev]" >> "$LOG" 2>&1
  rc1=$?
  python -m pip install --ignore-installed \
    "anthropic>=0.5.0" "torch>=2.0.0" "pdfplumber>=0.10.0" "pdf2image>=1.16.0" \
    "pytesseract>=0.3.10" "waitress>=2.1.0" "rich>=13.0.0" "plotly>=5.18.0" \
    "dash>=2.14.0" "livereload>=2.6.0" "matplotlib>=3.8.0" "seaborn>=0.13.0" \
    "pyvis>=0.3.2" "graphviz>=0.20.0" "mcp" >> "$LOG" 2>&1
  rc2=$?
  echo "[session-start] pip install done (main/dev rc=$rc1, infra/mcp rc=$rc2)"
fi

# --- Redis (hot-cache backend for memory + adg_sqlite MCP servers) -------------------------
if command -v redis-server >/dev/null 2>&1; then
  if redis-cli ping >/dev/null 2>&1; then
    echo "[session-start] redis already running"
  else
    redis-server --daemonize yes --save "" --appendonly no --port 6379 >> "$LOG" 2>&1 \
      && echo "[session-start] redis started" \
      || echo "[session-start] WARNING: redis failed to start (see $LOG)"
  fi
else
  echo "[session-start] NOTE: redis-server not installed — memory/adg_sqlite MCP need it"
fi

# Note: the ADG SQLite snapshot (artifacts/adg/*.sqlite) that adg_sqlite serves is NOT built
# here — generation is minutes-long. Build it on demand with:
#   PYTHONPATH=. python tools/adg/generate_full_adg.py
exit 0
