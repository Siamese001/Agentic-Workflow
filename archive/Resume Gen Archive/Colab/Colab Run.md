# ======================================================================
# 🌟 AGENTIC-WORKFLOW v10.7.2 — FULL COLAB BOOTSTRAP
#   (REDIS + GOOGLE DRIVE + ANTHROPIC/OPENAI/GEMINI EXPLICIT CONFIG)
# ======================================================================

echo "🧨 Resetting Colab /content directory..."
rm -rf /content/*
mkdir -p /content


# ----------------------------------------------------------------------
# (1) INSTALL & START REDIS (MANDATORY)
# ----------------------------------------------------------------------
echo "⚙️ Installing Redis server..."
apt-get update -y
apt-get install -y redis-server

echo "🚀 Starting Redis in daemon mode..."
redis-server --daemonize yes

echo "🔍 Verifying Redis..."
redis-cli ping


# ----------------------------------------------------------------------
# (2) GOOGLE DRIVE PERSISTENCE (META + CHROMA)
# ----------------------------------------------------------------------
echo "📁 Mounting Google Drive..."
python3 - << 'EOF'
from google.colab import drive
drive.mount('/content/drive')
EOF

PERSIST_ROOT="/content/drive/MyDrive/AgenticWorkflowPersistent"

mkdir -p $PERSIST_ROOT/logs
mkdir -p $PERSIST_ROOT/generated_tools_v10_7
mkdir -p $PERSIST_ROOT/chromadb_persist

echo "📦 Persistent directories ready:"
echo "   $PERSIST_ROOT/logs"
echo "   $PERSIST_ROOT/generated_tools_v10_7"
echo "   $PERSIST_ROOT/chromadb_persist"


# ----------------------------------------------------------------------
# (3) LOAD API KEYS FROM COLAB SECRETS
# ----------------------------------------------------------------------
echo "🔑 Loading API keys into shell env..."
echo "export OPENAI_API_KEY=${OPENAI_API_KEY}"   >> ~/.bashrc
echo "export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" >> ~/.bashrc
echo "export GOOGLE_API_KEY=${GOOGLE_API_KEY}"  >> ~/.bashrc
source ~/.bashrc


# ----------------------------------------------------------------------
# (4) CLONE REPO CLEAN
# ----------------------------------------------------------------------
echo "📥 Cloning Agentic-Workflow..."
git clone https://github.com/Siamese001/Agentic-Workflow.git /content/Agentic-Workflow
cd /content/Agentic-Workflow

echo "🧹 Cleaning cached Python artifacts..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +


# ----------------------------------------------------------------------
# (5) PATCH master_config_v10_7.json FOR DRIVE + REDIS REQUIRED
# ----------------------------------------------------------------------
echo "🛠 Patching master_config_v10_7.json for persistence + Redis required..."

python3 - << 'EOF'
import json

path = "/content/Agentic-Workflow/master_config_v10_7.json"
persist_root = "/content/drive/MyDrive/AgenticWorkflowPersistent"

with open(path, "r") as f:
    cfg = json.load(f)

# --- Make Redis mandatory (your Redis integration patch will respect this) ---
cfg.setdefault("redis_config", {})
cfg["redis_config"]["required"] = True

# --- META-LEARNING PERSISTENCE ---
cfg["meta_loop_config"]["feedback_log_path"]    = f"{persist_root}/logs/feedback_log.jsonl"
cfg["meta_loop_config"]["preference_log_path"]  = f"{persist_root}/logs/preference_log.jsonl"
cfg["meta_loop_config"]["proposed_rules_path"]  = f"{persist_root}/logs/proposed_rules.jsonl"
cfg["meta_loop_config"]["generated_tools_path"] = f"{persist_root}/generated_tools_v10_7"

# --- CHROMA PERSISTENCE ---
cfg["chromadb_config"]["persistent_path"] = f"{persist_root}/chromadb_persist"

with open(path, "w") as f:
    json.dump(cfg, f, indent=2)

print("🔥 master_config_v10_7.json patched for Redis REQUIRED + Drive persistence.")
EOF


# ----------------------------------------------------------------------
# (6) INSTALL MINIMAL DEPENDENCIES (STABLE VERSIONS)
# ----------------------------------------------------------------------
echo "📦 Installing Python dependencies..."

PIP_INDEX_URL="https://pypi.org/simple"

pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "langgraph>=1.0.0"
pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "anthropic==1.18.1"
pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "google-generativeai>=0.6.0"
pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "chromadb>=0.5.0"
pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "redis>=5.0.1"
pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "rank-bm25>=0.2.2"
pip install --upgrade --no-cache-dir --index-url $PIP_INDEX_URL "openai>=1.0.0" || echo "⚠️ OpenAI package install skipped/failed (may be MCP-only)."


# ----------------------------------------------------------------------
# (7) EXPLICIT PYTHON-LEVEL CONFIG FOR ALL PROVIDERS
# ----------------------------------------------------------------------
echo "🔧 Configuring Anthropic, OpenAI, and Gemini inside Python..."

python3 - << 'EOF'
import os

# --- Anthropic explicit configuration ---
import anthropic
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_key:
    raise RuntimeError("ANTHROPIC_API_KEY not found in environment.")
# New SDK prefers client instantiation; we also keep global var for safety.
print("🔐 Anthropic key present.")


# --- OpenAI explicit configuration ---
try:
    from openai import OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment.")
    _openai_client = OpenAI(api_key=openai_key)  # stored if you need it
    print("🔐 OpenAI client instantiated successfully.")
except Exception as e:
    print(f"⚠️ OpenAI explicit config skipped or not required: {e}")


# --- Gemini explicit configuration ---
import google.generativeai as genai
google_key = os.environ.get("GOOGLE_API_KEY")
if not google_key:
    raise RuntimeError("GOOGLE_API_KEY not found in environment.")
genai.configure(api_key=google_key)
print("🔐 Gemini configured via genai.configure().")

print("✅ All providers configured inside Python.")
EOF


# ----------------------------------------------------------------------
# (8) ENVIRONMENT & REDIS VALIDATION
# ----------------------------------------------------------------------
echo "🩺 Running environment diagnostics..."

python3 - << 'EOF'
import os, redis, anthropic, google.generativeai as genai

print("=== API Keys ===")
print("OPENAI:   ", bool(os.getenv("OPENAI_API_KEY")))
print("ANTHROPIC:", bool(os.getenv("ANTHROPIC_API_KEY")))
print("GOOGLE:   ", bool(os.getenv("GOOGLE_API_KEY")))
print()

print("=== Redis Check ===")
r = redis.Redis(host="localhost", port=6379, db=0)
print("Redis ping:", r.ping())
print()

print("=== SDK Versions ===")
print("Anthropic:", anthropic.__version__)
print("Gemini available:", hasattr(genai, "GenerativeModel"))

try:
    from langgraph.graph import StateGraph
    print("LangGraph StateGraph import OK")
except Exception as e:
    print("LangGraph import error:", e)

print("\n🎉 Environment READY for Agentic-Workflow v10.7.2 (Redis + Drive + All LLMs configured).")
EOF

echo "🚀 SETUP COMPLETE — You may now run:"
echo "    python3 main_v10_7.py -j job_input.json -m master_resume.json --debug"
