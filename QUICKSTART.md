# 🚀 Quick Start Guide - Magnificent Seven

## TL;DR - Get Running in 5 Minutes

### 1. Verify Your Setup

```bash
cd c:\Git\Agentic-Workflow\scripts
python verify_setup.py
```

### 2. Fix Any Issues

Based on the verification output, you have these options:

#### Option A: Use Existing Infrastructure (Recommended)

Your `.env` file already has:
- ✅ Google API Key (as `GOOGLE_API_KEY`)
- ✅ Pinecone API Key
- ✅ Redis configuration

**Quick fixes needed:**

1. **Map Gemini API Key:**
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY = $env:GOOGLE_API_KEY
   
   # Mac/Linux
   export GEMINI_API_KEY=$GOOGLE_API_KEY
   ```

2. **Use Existing Pinecone Index:**
   
   Edit `canon_validator_agentic.py` line 235:
   ```python
   # Change from:
   index_name = "subatomic-codebase"
   
   # To one of your existing indexes:
   index_name = "canon-memory-l2"  # or "agentic-memory"
   ```

3. **Fix Redis URL for Local Testing:**
   ```bash
   # Windows PowerShell
   $env:REDIS_URL = "redis://localhost:6379"
   
   # Mac/Linux
   export REDIS_URL="redis://localhost:6379"
   ```
   
   Then start Redis:
   ```bash
   # Mac
   brew services start redis
   
   # Linux
   sudo systemctl start redis-server
   
   # Windows (if installed) or use Docker:
   docker run -d -p 6379:6379 redis:latest
   ```

#### Option B: Create New Pinecone Index

1. Go to https://app.pinecone.io/
2. Create new index:
   - Name: `subatomic-codebase`
   - Dimensions: 768 or 1536
   - Metric: Cosine

### 3. Run the Validator

```bash
python canon_validator_agentic.py
```

### Expected Output

```
   [CTX] 🧠 INITIALIZING TRI-BRAIN (STRICT MODE)...
      ✅ Gemini Connected: gemini-2.0-flash-exp
      ✅ Redis Configured: redis://localhost:6379
      ✅ Pinecone Connected: Index 'canon-memory-l2'
   [CTX] 🚀 TRI-BRAIN ONLINE. System Integrity Verified.

🚀 STARTING MAGNIFICENT SEVEN MISSION
```

## Troubleshooting

### "GEMINI_API_KEY not set"
Your `.env` has `GOOGLE_API_KEY` instead. Either:
- Set `GEMINI_API_KEY=$GOOGLE_API_KEY` in your shell
- Or add to `.env`: `GEMINI_API_KEY=${GOOGLE_API_KEY}`

### "Redis connection failed"
Your `.env` uses `redis-stack` (Docker hostname). For local testing:
- Change to `redis://localhost:6379`
- Or start Docker: `docker-compose up redis-stack`

### "Pinecone index not found"
You have `canon-memory-l2` and `agentic-memory`. Either:
- Use one of those (edit line 235 in `canon_validator_agentic.py`)
- Or create `subatomic-codebase` in Pinecone dashboard

## What the Magnificent Seven Does

1. **Historian** - Skips unchanged files (saves time & money)
2. **ArchitectureGovernor** - Enforces file size, depth, complexity limits
3. **HygieneGuardian** - Removes generated noise files
4. **CodeStyleGuardian** - Checks formatting, docs, naming
5. **DependencySentinel** - Optimizes imports
6. **SafetyInspector** - Detects security issues
7. **ConcurrencyGuardian** - Prevents race conditions

All powered by the **Tri-Brain**:
- 🧠 Smart Brain (Gemini) - AI analysis
- 🔥 Hot Brain (Redis) - Distributed locking
- 🧊 Deep Brain (Pinecone) - Semantic search

## Full Documentation

See `SETUP.md` for complete installation and configuration details.
