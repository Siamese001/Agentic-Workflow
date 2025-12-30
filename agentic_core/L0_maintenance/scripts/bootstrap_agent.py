"""
BootstrapAgent: Sovereign Boot Integrity & Neural Link Verifier

Verifies critical boot dependencies:
- .env presence and loading (Gravity Anchor)
- Redis/Langcache connectivity (State Pulse)
- Mandatory model authorization keys (Gemini Link)

Placed in L0_maintenance/scripts per SSOT:
  L0_maintenance -> maintenance territory
  scripts -> approved L2 for boot scripts

Depth: agentic_core/L0_maintenance/scripts/bootstrap_agent.py -> 4 parts -> compliant
"""
import os
import urllib.parse
import redis
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class bootstrap_agent:
    """
    Autonomous boot integrity agent.
    Runs before any validation mission to anchor the environment.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def verify_neural_link(self) -> bool:
        """
        Full neural link verification.
        Checks the physical presence of the .env 'Soul' and Redis state.
        Returns True if all critical systems are active.
        """
        success = True

        # 1. .env gravity anchor
        env_path = self.project_root / ".env"
        if not env_path.exists():
            print(f"\n[!] [L6 ERROR] GRAVITY LOSS: .env missing at {env_path}")
            success = False
        else:
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"   [OK] Sovereign .env loaded from {env_path}")

        # 2. Redis/Langcache state check
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            parsed = urllib.parse.urlparse(redis_url)
            conn_kwargs = {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 6379,
                "password": parsed.password,
                "username": parsed.username,
                "socket_timeout": 3,
            }
            if parsed.scheme == "rediss":
                # Handle SSL for sovereign remote connections
                conn_kwargs.update({"ssl": True, "ssl_cert_reqs": None})

            r = redis.Redis(**conn_kwargs)
            r.ping()
            print(f"   [OK] Redis State Active: Langcache connected.")
        except Exception as e:
            print(f"   [!] [L4 STATE WARNING] Redis offline: {e}")
            # Non-fatal for structural check, but logged
            success = False

        # 3. Model neural authorization check
        mandatory_keys = ["GOOGLE_API_KEY", "GEMINI_MODEL"]
        missing = [k for k in mandatory_keys if not os.getenv(k)]
        if missing:
            print(f"\n[!] [NEURAL LINK ERROR] Missing mandatory keys: {', '.join(missing)}")
            success = False
        else:
            model = os.getenv("GEMINI_MODEL")
            print(f"   [OK] Neural authorization complete: {model}")

        return success

    def run_bootstrap(self) -> bool:
        """Execute full bootstrap sequence with L6 telemetry logging."""
        print("\n[BOOTSTRAP PHASE] Verifying Sovereign Neural Link...")
        result = self.verify_neural_link()
        if result:
            print("   [BOOTSTRAP COMPLETE] All critical links active.")
        else:
            print("   [BOOTSTRAP FAILED] Neural link compromised - check .env and Redis.")
        return result


# Uppercase alias for backward compatibility
BootstrapAgent = bootstrap_agent
