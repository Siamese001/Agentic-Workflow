# 🚀 Magnificent Seven Setup Guide

## Overview

The **Magnificent Seven** validator is a production-grade agentic code validation system powered by the **Tri-Brain architecture** (Gemini + Redis + Pinecone). All three components are **mandatory** — the system will refuse to start if any are missing.

## Prerequisites

### System Requirements
- Python 3.10+
- Redis server (local or remote)
- Pinecone account with API access
- Google Gemini API access

## Installation

### 1. Install Hard Dependencies

All dependencies are **required** for the Tri-Brain to function:

```bash
pip install google-genai redis pinecone-client isort autoflake pytest pytest-asyncio
```

**What each does:**
- `google-genai` - Smart Brain (Gemini AI for intelligent code mutations)
- `redis` - Hot Brain (distributed locking, rate limiting, caching)
- `pinecone-client` - Deep Brain (vector embeddings for semantic code search)
- `isort`, `autoflake` - Code formatting utilities
- `pytest`, `pytest-asyncio` - Testing framework

### 2. Set Up Redis

**Option A: Local Redis (Recommended for Development)**

**Mac (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis:latest`

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Option B: Remote Redis (Production)**
- Use Redis Cloud, AWS ElastiCache, or similar
- Get your connection URL (format: `redis://user:password@host:port`)

### 3. Set Up Pinecone

1. **Create Account:** https://www.pinecone.io/
2. **Get API Key:** From your Pinecone dashboard
3. **Create Index:**
   - Name: `subatomic-codebase`
   - Dimensions: 768 (for text-embedding-ada-002) or 1536 (for newer models)
   - Metric: Cosine similarity

### 4. Get Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Create a new API key
3. Ensure access to `gemini-2.0-flash-exp` or similar model

## Environment Configuration

### Mac/Linux

Create a `.env` file or export directly:

```bash
export GEMINI_API_KEY="your_actual_gemini_key_here"
export REDIS_URL="redis://localhost:6379"
export PINECONE_API_KEY="your_actual_pinecone_key_here"
export ENABLE_FUZZ="true"  # Optional: Enables RedSentinel active defense
```

**Permanent setup (add to `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export GEMINI_API_KEY="your_key"' >> ~/.bashrc
echo 'export REDIS_URL="redis://localhost:6379"' >> ~/.bashrc
echo 'export PINECONE_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell)

```powershell
$env:GEMINI_API_KEY="your_actual_gemini_key_here"
$env:REDIS_URL="redis://localhost:6379"
$env:PINECONE_API_KEY="your_actual_pinecone_key_here"
$env:ENABLE_FUZZ="true"
```

**Permanent setup (add to PowerShell profile):**
```powershell
notepad $PROFILE
# Add the lines above, save, then:
. $PROFILE
```

### Windows (Command Prompt)

```cmd
set GEMINI_API_KEY=your_actual_gemini_key_here
set REDIS_URL=redis://localhost:6379
set PINECONE_API_KEY=your_actual_pinecone_key_here
set ENABLE_FUZZ=true
```

## Running the Validator

### Basic Usage

```bash
cd c:\Git\Agentic-Workflow\scripts
python canon_validator_agentic.py
```

### Expected Output

If all dependencies are configured correctly:

```
   [CTX] 🧠 INITIALIZING TRI-BRAIN (STRICT MODE)...
      ✅ Gemini Connected: gemini-2.0-flash-exp
      ✅ Redis Configured: redis://localhost:6379
      ✅ Pinecone Connected: Index 'subatomic-codebase'
   [CTX] 🚀 TRI-BRAIN ONLINE. System Integrity Verified.
   [CTX] Blackboard initialized with X valid source files.

🚀 STARTING MAGNIFICENT SEVEN MISSION

[>>>] Historian ACTIVATED: Loading Memory...
[>>>] ArchitectureGovernor ACTIVATED: Enforcing Architectural Laws...
[>>>] HygieneGuardian ACTIVATED: Enforcing Project Hygiene...
[>>>] CodeStyleGuardian ACTIVATED: Enforcing Code Style & Hygiene...
[>>>] DependencySentinel ACTIVATED: Enforcing Import Hygiene...
[>>>] SafetyInspector ACTIVATED: Enforcing Security Standards...
[>>>] ConcurrencyGuardian ACTIVATED: Enforcing comprehensive concurrency safety...

==================================================
MISSION COMPLETE
==================================================
```

## Troubleshooting

### Error: "CRITICAL: 'google-genai' library missing"
**Solution:** `pip install google-genai`

### Error: "CRITICAL: GEMINI_API_KEY environment variable is missing"
**Solution:** Set the environment variable as shown above

### Error: "CRITICAL: 'redis' library missing"
**Solution:** `pip install redis`

### Error: "CRITICAL: REDIS_URL environment variable is missing"
**Solution:** Set `REDIS_URL` or ensure Redis is running on default port

### Error: "CRITICAL: Failed to configure Redis: Connection refused"
**Solution:** 
- Check if Redis is running: `redis-cli ping`
- Start Redis: `brew services start redis` (Mac) or `sudo systemctl start redis-server` (Linux)
- For Windows, ensure Redis service is running

### Error: "CRITICAL: 'pinecone-client' library missing"
**Solution:** `pip install pinecone-client`

### Error: "CRITICAL: Pinecone index 'subatomic-codebase' does not exist"
**Solution:** Create the index in your Pinecone dashboard with name `subatomic-codebase`

## Verification Checklist

Before running, verify:

- [ ] **Python 3.10+** installed: `python --version`
- [ ] **All packages** installed: `pip list | grep -E "google-genai|redis|pinecone"`
- [ ] **Redis running**: `redis-cli ping` returns `PONG`
- [ ] **Environment variables** set: `echo $GEMINI_API_KEY` (Mac/Linux) or `echo %GEMINI_API_KEY%` (Windows)
- [ ] **Pinecone index** exists: Check dashboard at https://app.pinecone.io/
- [ ] **Gemini API** accessible: Test at https://aistudio.google.com/

## Architecture Overview

### The Magnificent Seven Agents

1. **Historian** - Memory/Skip logic (prevents redundant work)
2. **ArchitectureGovernor** - Enforces depth, atomicity, complexity budgets
3. **HygieneGuardian** - File system cleanup and organization
4. **CodeStyleGuardian** - Code formatting, docs, naming conventions
5. **DependencySentinel** - Import management and optimization
6. **SafetyInspector** - Security pattern detection
7. **ConcurrencyGuardian** - Race condition, livelock, starvation prevention

### The Tri-Brain System

- **Smart Brain (Gemini)** - AI-powered code analysis and mutations
- **Hot Brain (Redis)** - Distributed locking, rate limiting, caching
- **Deep Brain (Pinecone)** - Vector embeddings for semantic code search

All three brains are **mandatory** and work together to provide intelligent, scalable code validation.

## Advanced Configuration

### Custom Redis Configuration

```bash
# Remote Redis with authentication
export REDIS_URL="redis://username:password@redis.example.com:6379/0"

# Redis with SSL
export REDIS_URL="rediss://username:password@redis.example.com:6380/0"
```

### Custom Pinecone Index

Edit `canon_validator_agentic.py` line 235 to change the index name:
```python
index_name = "your-custom-index-name"
```

### Disable Fuzzing (Optional)

```bash
unset ENABLE_FUZZ  # Mac/Linux
Remove-Item Env:\ENABLE_FUZZ  # Windows PowerShell
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed and configured
3. Check Redis and Pinecone service status
4. Review error messages for specific guidance

## License

This project is part of the Agentic-Workflow system.
