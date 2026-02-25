ORIGINAL (single location)                 TEMP SHIM (remove later)                    PERMANENT FACADE (keep)
───────────────────────────               ────────────────────────────                 ────────────────────────────

callers                                   callers                                     many subsystems
import L5_safety.decorators_util           import L5_safety.decorators_util            import safety.api
        │                                           │                                           │
        ▼                                           ▼                                           ▼
L5_safety.decorators_util                  L5_safety.decorators_util                    safety/api.py
(real implementation)                      (SHIM: re-export only)                      (stable public interface)
                                           from base_agents.decorators                  defines approved surface
                                                    │                                           │
                                                    ▼                                           ▼
                                           base_agents.decorators                        internal implementations
                                           (real implementation)                         base_agents.decorators
                                                                                         utils.decorators
                                                                                         other internals


END STATE:                                 END STATE:                                   END STATE:
Single module holds logic                  Migrate callers → delete shim                Keep facade stable
                                                                                         Swap internals safely
