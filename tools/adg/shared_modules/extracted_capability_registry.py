r"""
Extracted capability module: extracted_capability_registry
Source: agentic_core\L3_orchestration\registry\capability_registry.py
Extracted: 2026-03-27T06:50:34.188517
"""

class CapabilityNotFoundError(LookupError):
    """Raised when no registered agent has the requested capability.

    Gate A enforcement: dispatch without registry resolution fails.
    """

class CapabilityPermissionError(PermissionError):
    """Raised when caller is not in allowed_callers for the capability.

    Gate B enforcement: capability token must have resolved_agent_id.
    """

class UnregisteredAgentError(RuntimeError):
    """Raised when selected agent is not in CapabilityRegistry.

    Gate C enforcement: unregistered agents must not do production work.
    """

class ExclusiveCapabilityConflictError(RuntimeError):
    """Raised when multiple agents claim exclusive ownership without shared policy.

    Gate D enforcement: exclusive capability conflicts must be explicit.
    """

class RegistryVersionError(RuntimeError):
    """Raised on illegal registry mutation without version increment.

    Gate E enforcement: capability changes must be versioned.
    """

class UnregisteredDispatchError(RuntimeError):
    """Raised when dispatch bypasses registry resolution.

    Gate A enforcement: all dispatches must go through resolve_agent_for_capability().
    """

class CapabilityOwnership(str, Enum):
    """How execution ownership is held for a capability."""

    SINGLETON = "SINGLETON"  # Only one agent may hold this capability
    DELEGATED = "DELEGATED"  # One owner; may delegate to others
    PARALLELIZABLE = "PARALLELIZABLE"  # Multiple agents may run concurrently
    SHARED = "SHARED"  # Multiple agents share with explicit policy

class CapabilityRegistryEntry:
    """Registry entry for one versioned agent capability declaration.

    Spec §2 fields (10 required):
        agent_id, agent_version, layer, capability_set,
        allowed_callers, action_classes, policy_requirements,
        human_review_requirement, owner_team, active_status
    """

    agent_id: str
    agent_version: str
    layer: str
    capability_set: list[str]
    allowed_callers: list[str]
    action_classes: list[str]
    policy_requirements: list[str]
    human_review_requirement: bool
    owner_team: str
    active_status: bool

    ownership: CapabilityOwnership = CapabilityOwnership.SINGLETON
    shared_policy_hash: str = ""
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.entry_hash = _sha256(f"{self.agent_id}:{self.agent_version}:{sorted(self.capability_set)}")

    def allows_caller(self, caller_agent_id: str) -> bool:
        """Wildcard '*' allows all callers."""
        return "*" in self.allowed_callers or caller_agent_id in self.allowed_callers

    def has_capability(self, capability_name: str) -> bool:
        return capability_name in self.capability_set

    def meets_policy(self, policy_hash: str) -> bool:
        return not self.policy_requirements or bool(policy_hash)

class CapabilityToken:
    """Typed token issued on every successful capability resolution.

    Spec §4 fields: capability_name, capability_token, resolved_agent_id.
    Also carries trace_id for ADG binding.
    """

    capability_name: str
    capability_token: str
    resolved_agent_id: str
    caller_agent_id: str
    run_id: str
    trace_id: str
    registry_version: int

    @classmethod
    def create(
        cls,
        *,
        capability_name: str,
        resolved_agent_id: str,
        caller_agent_id: str,
        run_id: str,
        trace_id: str,
        registry_version: int,
    ) -> CapabilityToken:
        token = _sha256(
            f"{capability_name}:{resolved_agent_id}:{caller_agent_id}:{run_id}:{uuid.uuid4().hex[:8]}",
        )
        return cls(
            capability_name=capability_name,
            capability_token=token,
            resolved_agent_id=resolved_agent_id,
            caller_agent_id=caller_agent_id,
            run_id=run_id,
            trace_id=trace_id,
            registry_version=registry_version,
        )

class CapabilityDecision:
    """Result of resolve_agent_for_capability() — bound to trace."""

    capability_name: str
    caller_agent_id: str
    eligible_agents: list[str]
    selected_agent_id: str
    capability_token: CapabilityToken
    run_id: str
    trace_id: str
    registry_version: int

class RunContext:
    """Minimal run context for capability resolution."""

    run_id: str
    trace_id: str
    policy_hash: str = ""

    @classmethod
    def create(cls, run_id: str = "", trace_id: str = "", policy_hash: str = "") -> RunContext:
        return cls(
            run_id=run_id or f"run-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id or f"trace-{uuid.uuid4().hex[:8]}",
            policy_hash=policy_hash,
        )

class CapabilityRegistry:
    """Thread-safe agent capability registry.

    Spec §1: the central directory mapping agents to capabilities.
    Spec §5: exposes ownership, sharing, and parallelizability.
    Spec §6: every mutation increments registry_version.

    Only registered agents may execute. Dispatch must go through
    resolve_agent_for_capability() — no direct agent lookup allowed.
    """

    def __init__(self) -> None:
        self._entries: dict[str, CapabilityRegistryEntry] = {}  # keyed by agent_id
        self._registry_version: int = 0
        self._version_history: list[tuple[int, str]] = []  # (version, reason)
        self._lock = threading.RLock()

    # -----------------------------------------------------------------------
    # Registration — spec §6: every mutation increments version
    # -----------------------------------------------------------------------

    def register(self, entry: CapabilityRegistryEntry, reason: str = "register") -> int:
        """Register or update an agent entry. Returns new registry_version."""
        with self._lock:
            if entry.ownership == CapabilityOwnership.SINGLETON:
                # Check for exclusive conflicts
                for cap in entry.capability_set:
                    existing = self._exclusive_owners(cap)
                    existing_non_self = [a for a in existing if a != entry.agent_id]
                    if existing_non_self and not entry.shared_policy_hash:
                        raise ExclusiveCapabilityConflictError(
                            f"CapabilityRegistry: capability '{cap}' already has exclusive "
                            f"owners {existing_non_self}. Set shared_policy_hash or use "
                            f"CapabilityOwnership.SHARED to allow multiple agents.",
                        )
            self._entries[entry.agent_id] = entry
            self._registry_version += 1
            self._version_history.append((self._registry_version, reason))
            logger.debug(
                "CAPABILITY_REGISTRY register agent=%s caps=%s version=%d",
                entry.agent_id,
                entry.capability_set,
                self._registry_version,
            )
            return self._registry_version

    def deactivate(self, agent_id: str, reason: str = "deactivate") -> int:
        """Mark agent inactive. Returns new registry_version."""
        with self._lock:
            if agent_id not in self._entries:
                raise UnregisteredAgentError(
                    f"CapabilityRegistry.deactivate: agent '{agent_id}' not registered.",
                )
            entry = self._entries[agent_id]
            # Re-register with active_status=False
            updated = CapabilityRegistryEntry(
                agent_id=entry.agent_id,
                agent_version=entry.agent_version,
                layer=entry.layer,
                capability_set=entry.capability_set,
                allowed_callers=entry.allowed_callers,
                action_classes=entry.action_classes,
                policy_requirements=entry.policy_requirements,
                human_review_requirement=entry.human_review_requirement,
                owner_team=entry.owner_team,
                active_status=False,
                ownership=entry.ownership,
                shared_policy_hash=entry.shared_policy_hash,
            )
            self._entries[agent_id] = updated
            self._registry_version += 1
            self._version_history.append((self._registry_version, reason))
            return self._registry_version

    # -----------------------------------------------------------------------
    # Query interface — spec §5
    # -----------------------------------------------------------------------

    def is_registered(self, agent_id: str) -> bool:
        with self._lock:
            return agent_id in self._entries

    def get_entry(self, agent_id: str) -> CapabilityRegistryEntry | None:
        with self._lock:
            return self._entries.get(agent_id)

    def agents_for_capability(self, capability_name: str) -> list[CapabilityRegistryEntry]:
        """Return all active entries that declare this capability."""
        with self._lock:
            return [
                e for e in self._entries.values() if e.active_status and e.has_capability(capability_name)
            ]

    def capability_owner(self, capability_name: str) -> CapabilityRegistryEntry | None:
        """Return the SINGLETON owner of a capability, or None if shared/absent."""
        with self._lock:
            owners = [
                e
                for e in self._entries.values()
                if e.active_status
                and e.has_capability(capability_name)
                and e.ownership == CapabilityOwnership.SINGLETON
            ]
            return owners[0] if len(owners) == 1 else None

    def all_capabilities(self) -> list[str]:
        """Return sorted list of all declared capabilities."""
        with self._lock:
            caps: set[str] = set()
            for e in self._entries.values():
                caps.update(e.capability_set)
            return sorted(caps)

    def all_agents(self) -> list[str]:
        with self._lock:
            return sorted(self._entries.keys())

    @property
    def registry_version(self) -> int:
        with self._lock:
            return self._registry_version

    @property
    def version_history(self) -> list[tuple[int, str]]:
        with self._lock:
            return list(self._version_history)

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _exclusive_owners(self, capability_name: str) -> list[str]:
        return [
            e.agent_id
            for e in self._entries.values()
            if e.active_status
            and e.has_capability(capability_name)
            and e.ownership == CapabilityOwnership.SINGLETON
        ]

def resolve_agent_for_capability(
    capability_name: str,
    caller_agent_id: str,
    run_context: RunContext,
    *,
    registry: CapabilityRegistry | None = None,
    preferred_agent_id: str = "",
) -> CapabilityDecision:
    """Mandatory capability resolution entrypoint — P2/L3 spec §3.

    Steps (in order, all mandatory):
      1. query CapabilityRegistry for capability_name
      2. validate caller permission (allowed_callers check)
      3. return eligible target agents
      4. bind capability decision to trace (issues_capability_token ADG edge)
      5. reject unregistered or unauthorized matches

    Args:
        capability_name:   The capability being requested.
        caller_agent_id:   Agent making the dispatch request.
        run_context:       RunContext carrying run_id, trace_id, policy_hash.
        registry:          CapabilityRegistry to consult (uses global if None).
        preferred_agent_id: Optional hint for which agent to select.

    Returns:
        CapabilityDecision with CapabilityToken and resolved_agent_id.

    Raises:
        CapabilityNotFoundError:     No registered agent has this capability.
        CapabilityPermissionError:   Caller not in allowed_callers.
        UnregisteredAgentError:      preferred_agent_id not in registry.
    """
    _registry = registry or get_capability_registry()
    _gw = get_routing_gateway(run_context.trace_id if hasattr(run_context, "trace_id") else "")

    _emit_records_execution_trace(
        run_context.trace_id,
        LayerSegment.L3_ORCHESTRATION,
        f"resolve_agent_for_capability:{capability_name}",
    )
    _TRACE_LOG.debug(
        "records_execution_trace CAPABILITY_RESOLVE cap=%s caller=%s run=%s trace=%s",
        capability_name,
        caller_agent_id,
        run_context.run_id,
        run_context.trace_id,
    )

    # --- Step 1: Query CapabilityRegistry for capability_name ---
    candidates = _registry.agents_for_capability(capability_name)

    if not candidates:
        raise CapabilityNotFoundError(
            f"resolve_agent_for_capability: no active registered agent declares "
            f"capability '{capability_name}'. Register an agent with this capability "
            f"before dispatching (spec §4: only registered agents may execute).",
        )

    # --- Step 2: Validate caller permission ---
    permitted = [e for e in candidates if e.allows_caller(caller_agent_id)]

    if not permitted:
        agent_ids = [e.agent_id for e in candidates]
        raise CapabilityPermissionError(
            f"resolve_agent_for_capability: caller '{caller_agent_id}' is not in "
            f"allowed_callers for capability '{capability_name}'. "
            f"Candidates: {agent_ids}. Add caller to allowed_callers or use '*'.",
        )

    # --- Step 3: Return eligible target agents ---
    eligible_agent_ids = [e.agent_id for e in permitted]

    # Select target: preferred_agent_id if specified and eligible, else first permitted
    if preferred_agent_id:
        if not _registry.is_registered(preferred_agent_id):
            raise UnregisteredAgentError(
                f"resolve_agent_for_capability: preferred_agent_id '{preferred_agent_id}' "
                f"is not registered in CapabilityRegistry. "
                f"Unregistered agents must not do production work (spec §12.3).",
            )
        selected = preferred_agent_id if preferred_agent_id in eligible_agent_ids else eligible_agent_ids[0]
    else:
        selected = eligible_agent_ids[0]

    # --- Step 4: Bind capability decision to trace ---
    token = CapabilityToken.create(
        capability_name=capability_name,
        resolved_agent_id=selected,
        caller_agent_id=caller_agent_id,
        run_id=run_context.run_id,
        trace_id=run_context.trace_id,
        registry_version=_registry.registry_version,
    )

    _CAPABILITY_LOG.debug(
        "issues_capability_token cap=%s resolved=%s caller=%s token=%s run=%s trace=%s version=%d",
        capability_name,
        selected,
        caller_agent_id,
        token.capability_token[:12],
        run_context.run_id,
        run_context.trace_id,
        _registry.registry_version,
    )

    _DISPATCH_LOG.debug(
        "agent_executes_agent CAPABILITY_RESOLVED parent=%s child=%s cap=%s token=%s",
        caller_agent_id,
        selected,
        capability_name,
        token.capability_token[:12],
    )

    # --- Step 5: Return decision (unregistered/unauthorized already raised above) ---
    decision = CapabilityDecision(
        capability_name=capability_name,
        caller_agent_id=caller_agent_id,
        eligible_agents=eligible_agent_ids,
        selected_agent_id=selected,
        capability_token=token,
        run_id=run_context.run_id,
        trace_id=run_context.trace_id,
        registry_version=_registry.registry_version,
    )

    logger.debug(
        "CAPABILITY_RESOLVED cap=%s selected=%s eligible=%s version=%d",
        capability_name,
        selected,
        eligible_agent_ids,
        _registry.registry_version,
    )
    return decision

class CapabilityDecisionStore:
    """In-memory queryable store for all issued CapabilityDecision records."""

    def __init__(self) -> None:
        self._decisions: list[CapabilityDecision] = []
        self._lock = threading.RLock()

    def ingest(self, decision: CapabilityDecision) -> None:
        with self._lock:
            self._decisions.append(decision)

    def by_run_id(self, run_id: str) -> list[CapabilityDecision]:
        with self._lock:
            return [d for d in self._decisions if d.run_id == run_id]

    def by_capability(self, capability_name: str) -> list[CapabilityDecision]:
        with self._lock:
            return [d for d in self._decisions if d.capability_name == capability_name]

    def by_agent(self, agent_id: str) -> list[CapabilityDecision]:
        with self._lock:
            return [d for d in self._decisions if d.selected_agent_id == agent_id]

    def all_decisions(self) -> list[CapabilityDecision]:
        with self._lock:
            return list(self._decisions)

    def unresolved_dispatches(self) -> list[CapabilityDecision]:
        """Decisions where resolved_agent_id is empty (Gate B violation)."""
        with self._lock:
            return [d for d in self._decisions if not d.selected_agent_id]

def get_capability_registry() -> CapabilityRegistry:
    """Return the process-level CapabilityRegistry singleton."""
    global _global_registry
    if _global_registry is None:
        with _global_registry_lock:
            if _global_registry is None:
                _global_registry = CapabilityRegistry()
    return _global_registry

def get_capability_decision_store() -> CapabilityDecisionStore:
    """Return the process-level CapabilityDecisionStore singleton."""
    global _global_store
    if _global_store is None:
        with _global_store_lock:
            if _global_store is None:
                _global_store = CapabilityDecisionStore()
    return _global_store

def reset_capability_registry() -> None:
    """Reset global registry (for testing)."""
    global _global_registry
    _global_registry = None

def reset_capability_decision_store() -> None:
    """Reset global store (for testing)."""
    global _global_store
    _global_store = None

    def allows_caller(self, caller_agent_id: str) -> bool:
        """Wildcard '*' allows all callers."""
        return "*" in self.allowed_callers or caller_agent_id in self.allowed_callers

    def has_capability(self, capability_name: str) -> bool:
        return capability_name in self.capability_set

    def meets_policy(self, policy_hash: str) -> bool:
        return not self.policy_requirements or bool(policy_hash)

    def create(
        cls,
        *,
        capability_name: str,
        resolved_agent_id: str,
        caller_agent_id: str,
        run_id: str,
        trace_id: str,
        registry_version: int,
    ) -> CapabilityToken:
        token = _sha256(
            f"{capability_name}:{resolved_agent_id}:{caller_agent_id}:{run_id}:{uuid.uuid4().hex[:8]}",
        )
        return cls(
            capability_name=capability_name,
            capability_token=token,
            resolved_agent_id=resolved_agent_id,
            caller_agent_id=caller_agent_id,
            run_id=run_id,
            trace_id=trace_id,
            registry_version=registry_version,
        )

    def create(cls, run_id: str = "", trace_id: str = "", policy_hash: str = "") -> RunContext:
        return cls(
            run_id=run_id or f"run-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id or f"trace-{uuid.uuid4().hex[:8]}",
            policy_hash=policy_hash,
        )

    def register(self, entry: CapabilityRegistryEntry, reason: str = "register") -> int:
        """Register or update an agent entry. Returns new registry_version."""
        with self._lock:
            if entry.ownership == CapabilityOwnership.SINGLETON:
                # Check for exclusive conflicts
                for cap in entry.capability_set:
                    existing = self._exclusive_owners(cap)
                    existing_non_self = [a for a in existing if a != entry.agent_id]
                    if existing_non_self and not entry.shared_policy_hash:
                        raise ExclusiveCapabilityConflictError(
                            f"CapabilityRegistry: capability '{cap}' already has exclusive "
                            f"owners {existing_non_self}. Set shared_policy_hash or use "
                            f"CapabilityOwnership.SHARED to allow multiple agents.",
                        )
            self._entries[entry.agent_id] = entry
            self._registry_version += 1
            self._version_history.append((self._registry_version, reason))
            logger.debug(
                "CAPABILITY_REGISTRY register agent=%s caps=%s version=%d",
                entry.agent_id,
                entry.capability_set,
                self._registry_version,
            )
            return self._registry_version

    def deactivate(self, agent_id: str, reason: str = "deactivate") -> int:
        """Mark agent inactive. Returns new registry_version."""
        with self._lock:
            if agent_id not in self._entries:
                raise UnregisteredAgentError(
                    f"CapabilityRegistry.deactivate: agent '{agent_id}' not registered.",
                )
            entry = self._entries[agent_id]
            # Re-register with active_status=False
            updated = CapabilityRegistryEntry(
                agent_id=entry.agent_id,
                agent_version=entry.agent_version,
                layer=entry.layer,
                capability_set=entry.capability_set,
                allowed_callers=entry.allowed_callers,
                action_classes=entry.action_classes,
                policy_requirements=entry.policy_requirements,
                human_review_requirement=entry.human_review_requirement,
                owner_team=entry.owner_team,
                active_status=False,
                ownership=entry.ownership,
                shared_policy_hash=entry.shared_policy_hash,
            )
            self._entries[agent_id] = updated
            self._registry_version += 1
            self._version_history.append((self._registry_version, reason))
            return self._registry_version

    def is_registered(self, agent_id: str) -> bool:
        with self._lock:
            return agent_id in self._entries

    def get_entry(self, agent_id: str) -> CapabilityRegistryEntry | None:
        with self._lock:
            return self._entries.get(agent_id)

    def agents_for_capability(self, capability_name: str) -> list[CapabilityRegistryEntry]:
        """Return all active entries that declare this capability."""
        with self._lock:
            return [
                e for e in self._entries.values() if e.active_status and e.has_capability(capability_name)
            ]

    def capability_owner(self, capability_name: str) -> CapabilityRegistryEntry | None:
        """Return the SINGLETON owner of a capability, or None if shared/absent."""
        with self._lock:
            owners = [
                e
                for e in self._entries.values()
                if e.active_status
                and e.has_capability(capability_name)
                and e.ownership == CapabilityOwnership.SINGLETON
            ]
            return owners[0] if len(owners) == 1 else None

    def all_capabilities(self) -> list[str]:
        """Return sorted list of all declared capabilities."""
        with self._lock:
            caps: set[str] = set()
            for e in self._entries.values():
                caps.update(e.capability_set)
            return sorted(caps)

    def all_agents(self) -> list[str]:
        with self._lock:
            return sorted(self._entries.keys())

    def registry_version(self) -> int:
        with self._lock:
            return self._registry_version

    def version_history(self) -> list[tuple[int, str]]:
        with self._lock:
            return list(self._version_history)

    def ingest(self, decision: CapabilityDecision) -> None:
        with self._lock:
            self._decisions.append(decision)

    def by_run_id(self, run_id: str) -> list[CapabilityDecision]:
        with self._lock:
            return [d for d in self._decisions if d.run_id == run_id]

    def by_capability(self, capability_name: str) -> list[CapabilityDecision]:
        with self._lock:
            return [d for d in self._decisions if d.capability_name == capability_name]

    def by_agent(self, agent_id: str) -> list[CapabilityDecision]:
        with self._lock:
            return [d for d in self._decisions if d.selected_agent_id == agent_id]

    def all_decisions(self) -> list[CapabilityDecision]:
        with self._lock:
            return list(self._decisions)

    def unresolved_dispatches(self) -> list[CapabilityDecision]:
        """Decisions where resolved_agent_id is empty (Gate B violation)."""
        with self._lock:
            return [d for d in self._decisions if not d.selected_agent_id]
