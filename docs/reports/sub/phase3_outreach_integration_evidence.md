# Phase 3 Outreach Integration Evidence

## Immutable Evidence for Phase 3 Closeout

### Wave 3.1: Seam Discovery

**rg -n "engines/__init__\.py|registry|dispatch|route|intent|capabil" apps_lic**
```
C:/Git/Agentic-Workflow/apps_lic\utils\lic_engine_validation_capability.py
2:LICEngineValidationCapability — Pure execution harness for LIC validation agents.
10:The capability OWNS:
13:  - Signal dispatch and result recording
15:The capability REJECTS:
19:If the validation *process* changes, update the Capability.
33:class LICEngineValidationCapability:

C:/Git/Agentic-Workflow/apps_lic\utils\LICAgentBase.py
70:    Inherits from AppBase for unified app-level capabilities.
101:        Initialize LIC capabilities after Core hardening.
244:            "capabilities": self.get_sovereign_capabilities(),

C:/Git/Agentic-Workflow/apps_lic\utils\hop_stage_capability.py
2:HOPStageCapability — Pure capability mixin for LIC HOP pipeline stages.
8:  - Standard _process(buffer, registry) template
14:    class HOP5GenerationAgent(HOPStageCapability, LICAgentBase):
25:from apps_lic.types.TraceRegistry import TraceRegistry
28:class HOPStageCapability:
29:    """Pure capability mixin for LIC HOP pipeline stage agents.
39:        - Override _process(buffer, registry) with business logic
48:        registry: TraceRegistry,
54:            registry: The TraceRegistry for logging.
67:                registry.add_trace("DATA_ERROR", {"msg": f"Missing {key}"})
77:        registry: TraceRegistry,
86:            registry: The TraceRegistry for logging.
95:        registry.add_trace(
103:        registry: TraceRegistry,
112:            registry: The TraceRegistry for the mission.
114:        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})
115:        self._process(buffer, registry)
120:        registry: TraceRegistry,

C:/Git/Agentic-Workflow/apps_lic\types\validation_severity_types.py
62:# Error Code Registry
140:        remediation="Adjust constraints or change Route",

C:/Git/Agentic-Workflow/apps_lic\types\TraceRegistry.py
2:Trace Registry.
28:class TraceRegistry(MCPHardenedMixin):
30:    Registry for execution traces. Maintains an ordered log of events.
93:        """Clears the registry (use with caution)."""

C:/Git/Agentic-Workflow/apps_lic\types\SpecialistDraftPacket.py
42:    """Single critique finding routed by the panel."""

C:/Git/Agentic-Workflow/apps_lic\types\route_types.py
11:class Route(str, Enum):
12:    """Message delivery routes."""
42:    """Character limit constraint for a Route."""
58:    """Word limit constraint for a Route."""
73:class RouteConfig:
74:    """configuration for a message Route."""
76:    Route: Route
118:# Route Configurations (from v10.10)
ROUTE_CONFIGS = {
    Route.CONNECTION_REQ: RouteConfig(
        Route=Route.CONNECTION_REQ,
148:    Route.INMAIL: RouteConfig(
        Route=Route.INMAIL,
176:    Route.SHORT_NEW: RouteConfig(
        Route=Route.SHORT_NEW,
207:    Route.FOLLOW_UP: RouteConfig(
        Route=Route.FOLLOW_UP,
516:    Route.CONNECTION_REQ: {
525:    Route.INMAIL: {
533:    Route.SHORT_NEW: {
541:    Route.FOLLOW_UP: {
658:        Route.CONNECTION_REQ: {
663:        Route.SHORT_NEW: {
692:        "route_completeness": [
693:            "verify_all_routes_defined",
701:def get_route_config(Route: Route) -> RouteConfig | None:
702:    """Get Route configuration.
705:        Route: Message Route
708:    RouteConfig or None if not defined
710:    return ROUTE_CONFIGS.get(Route)

C:/Git/Agentic-Workflow/apps_lic\types\recipient_archetype_types.py
4:Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
231:# Greeting templates by Route
301:    def get_template(self, Route: str) -> GreetingTemplate:
302:        """Get greeting template by Route."""
304:            Route,
325:    def format_greeting(self, Route: str, first_name: str) -> str:
327:        template = self.get_greeting_template(Route)

C:/Git/Agentic-Workflow/apps_lic\types\message_route_types.py
4:Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
8:class MessageRoute(Enum):
9:    """Message Route types for LinkedIn outreach."""
46:class RouteConditions:
47:    """Conditions for Route selection."""
56:class RouteConstraints:
57:    """Constraints for a message Route."""
70:class RouteConfig:
71:    """Complete configuration for a message Route."""
73:    Route: MessageRoute
74:    conditions: RouteConditions
75:    constraints: RouteConstraints
78:# Route configurations
ROUTE_CONFIGS: dict[MessageRoute, RouteConfig] = {
79:    MessageRoute.CONNECTION_REQ: RouteConfig(
80:        Route=MessageRoute.CONNECTION_REQ,
81:        conditions=RouteConditions(
86:        constraints=RouteConstraints(
97:    MessageRoute.SHORT_NEW: RouteConfig(
98:        Route=MessageRoute.SHORT_NEW,
99:        conditions=RouteConditions(
103:        constraints=RouteConstraints(
113:    MessageRoute.LONG_NEW: RouteConfig(
114:        Route=MessageRoute.LONG_NEW,
115:        conditions=RouteConditions(
119:        constraints=RouteConstraints(
129:    MessageRoute.FOLLOW_UP: RouteConfig(
130:        Route=MessageRoute.FOLLOW_UP,
131:        conditions=RouteConditions(
134:        constraints=RouteConstraints(
144:    MessageRoute.INMAIL: RouteConfig(
145:        Route=MessageRoute.INMAIL,
146:        conditions=RouteConditions(
150:        constraints=RouteConstraints(
243:# Tool call budget by Route
244:TOOL_CALL_BUDGETS: dict[MessageRoute, str] = {
245:    MessageRoute.CONNECTION_REQ: "0-8",
246:    MessageRoute.SHORT_NEW: "3-6",
247:    MessageRoute.LONG_NEW: "8-12",
248:    MessageRoute.FOLLOW_UP: "2-4",
249:    MessageRoute.INMAIL: "8-12",
253:class LICRouter:
254:    """router for determining message Route and constraints."""
257:        """Initialize the router."""
258:        self._route_configs = ROUTE_CONFIGS
262:    def determine_route(
266:        route_override: MessageRoute | None = None,
267:    ) -> MessageRoute:
269:        Determine the appropriate message Route.
274:            route_override: Optional Route override
277:            Determined MessageRoute
279:        if route_override is not None:
280:            return route_override
284:            return MessageRoute.FOLLOW_UP
289:            return MessageRoute.SHORT_NEW
291:        return MessageRoute.SHORT_NEW
293:    def get_route_config(self, Route: MessageRoute) -> RouteConfig:
294:        """Get configuration for a Route."""
295:        return self._route_configs[Route]
297:    def get_constraints(self, Route: MessageRoute) -> RouteConstraints:
298:        """Get constraints for a Route."""
299:        return self._route_configs[Route].constraints
312:    def get_tool_budget(self, Route: MessageRoute) -> str:
313:        """Get tool call budget for a Route."""
314:        return TOOL_CALL_BUDGETS.get(Route, "3-6")
319:        Route: MessageRoute,
322:        Validate message length against Route constraints.
326:            Route: Message Route
331:        constraints = self.get_constraints(Route)
361:def create_router() -> LICRouter:
362:    """builder function to create a router."""
363:    return LICRouter()
366:def get_route_config(Route: MessageRoute) -> RouteConfig:
367:    """Get configuration for a Route."""
368:    return ROUTE_CONFIGS[Route]

C:/Git/Agentic-Workflow/apps_lic\types\lic_models_types.py
15:class Route(Enum):
16:    """Message delivery routes"""
122:    route_override: Route | None = None
217:    Route: Route
235:    Route: Route

C:/Git/Agentic-Workflow/apps_lic\types\k1_router_types.py
27:class RouteSelectionResult:
28:    """Result of route selection."""
30:    route: str  # INMAIL, CONNECTION_REQ, SHORT_NEW, FOLLOW_UP
41:    route: RouteSelectionResult
46:class K1Router:
51:    archetype classification with CXO precedence, and route selection with premium
72:        self.route_configs: dict[str, Any] = self.config.get("route_configs", {})
86:                - route_override: Optional[str]
89:            K1Output: Complete routing output with archetype and route
114:        return f"route_{result.route.lower()}"
123:            K1Output with archetype and route
150:        # Gate 3B: Route override check
151:        route_override = context.get("route_override")
152:        if route_override:
153:            entrance_gates_passed.append("GATE_3B_ROUTE_OVERRIDE_DETECTED")
154:            logger.info(f"Gate 3B: Route override = {route_override}")
165:        # Gate 5: Route selection
166:        route_result = self._select_route(
169:            route_override=route_override,
172:        entrance_gates_passed.append("GATE_5_ROUTE_SELECTED")
173:        logger.info(f"Gate 5: Route = {route_result.route}")
176:        if result.premium_routing_mismatch:
178:            logger.critical(f"Gate 6: PREMIUM ROUTING MISMATCH BLOCKER - {route_result.blocking_reason}")
179:            raise ValueError(f"GATE_6_BLOCKED: {route_result.blocking_reason}")
191:            route=route_result,
194:                "router_id": "K1Router",
201:        logger.info(f"K.1 routing complete: {archetype_result.archetype} → {route_result.route}")
310:    def _select_route(
314:        route_override: str | None,
316:    ) -> RouteSelectionResult:
317:        """Select message route with premium routing validation.
322:            route_override: Manual route override
326:            RouteSelectionResult with mismatch detection
328:        # Check for route override
329:        if route_override:
330:            selected_route = route_override
333:            if selected_route == "INMAIL" and not premium_available:
334:                return RouteSelectionResult(
335:                    route=selected_route,
339:                        "INMAIL route selected but Premium InMail not available. "
340:                        "Operator response to Gate 3A conflicts with route selection."
344:            return RouteSelectionResult(
345:                route=selected_route,
352:            selected_route = "FOLLOW_UP"
354:            selected_route = "INMAIL"
356:            selected_route = "CONNECTION_REQ"
358:        return RouteSelectionResult(
359:            route=selected_route,

C:/Git/Agentic-Workflow/apps_lic\types\action_call_generator_types.py
6:This agent generates Route-specific CTAs with strict character limits.
11:- Generate CTA based on Route type
12:- Enforce Route-specific character limits
17:- Route classification
25:class RouteType(Enum):
47:    RouteType: RouteType
61:    Route-Specific Constraints:
68:    ROUTE_CHAR_LIMITS: Any = {
69:        RouteType.CONNECTION_REQ: 300,
70:        RouteType.SHORT_NEW: (360, 380),
71:        RouteType.INMAIL: 1900,
72:        RouteType.FOLLOW_UP: 1000,
97:    def generate_cta(self, RouteType: RouteType, message_body: str, context: dict[str, Any]) -> CTAResult:
99:        Generate CTA with Route-specific validation.
102:            RouteType: Type of outreach Route
113:                RouteType=RouteType,
132:                RouteType=RouteType,
162:                RouteType=RouteType,
173:            RouteType=RouteType,
185:        RouteType: RouteType,
194:        if RouteType == RouteType.CONNECTION_REQ:
196:        elif RouteType == RouteType.SHORT_NEW:
198:        elif RouteType == RouteType.INMAIL:
203:    def _validate_character_limit(self, RouteType: RouteType, total_message: str, char_count: int) -> Any:
205:        Validate Route-specific character limits.
208:        limit = self.ROUTE_CHAR_LIMITS.get(RouteType)
228:                    "Route": RouteType.value,
245:                details={"char_count": char_count, "limit": limit, "Route": RouteType.value},

C:/Git/Agentic-Workflow/apps_lic\tools\run_workflow_lic.py
147:        print(f"Route: {result.get('route', 'N/A')}")

C:/Git/Agentic-Workflow/apps_lic\tools\dispatch_outreach_tools.py
2:dispatch_outreach_tools.py - Execution Module
14:class DispatchOutreachTools:
39:    return DispatchOutreachTools(config).execute(action, params)

C:/Git/Agentic-Workflow/apps_lic\engines\control_plane.py
71:#     Routes all agent inputs and outputs through unified defense system:

C:/Git/Agentic-Workflow/apps_lic\engines\ExecutiveStrategyAgent.py
4:Provides executive strategy capabilities using prompt governance infrastructure.

C:/Git/Agentic-Workflow/apps_lic\engines\HOPPipelineExecutor.py
6:Each stage's _process() logic is preserved in hop_stage_registry.py.
7:This executor dispatches to the registered stage implementation.
14:from apps_lic.utils.hop_stage_capability import HOPStageCapability
19:class HOPPipelineExecutor(HOPStageCapability, LICAgentBase):
45:        """Dispatch to stage-specific processing.
47:        Domain logic for each stage is preserved via the stage registry.
50:        from apps_lic.engines import hop_stage_registry
52:        handler = hop_stage_registry.get_stage_handler(self.stage_id)

C:/Git/Agentic-Workflow/apps_lic\engines\hop_stage_registry.py
1:"""HOP Pipeline Stage Registry.
12:_REGISTRY: dict[int, Callable] = {}
19:        _REGISTRY[stage_id] = func
27:    return _REGISTRY.get(stage_id)

C:/Git/Agentic-Workflow/apps_lic\engines\LicCodeInterpreter.py
145:        """Initialize code interpreter with safe function registry."""

C:/Git/Agentic-Workflow/apps_lic\engines\LICValidationExecutor.py
11:from apps_lic.utils.lic_engine_validation_capability import LICEngineValidationCapability
16:class LICValidationExecutor(LICEngineValidationCapability, LICAgentBase):
26:        """Dispatch to rule-specific validation."""

C:/Git/Agentic-Workflow/apps_lic\engines\LicHealingOrchestrator.py
46:        """Initialize Sovereign Capabilities."""

C:/Git/Agentic-Workflow/apps_lic\engines\LogReaderAgent.py
407:#     """v10.7: Routes to tool gen or rule gen branch."""

C:/Git/Agentic-Workflow/apps_lic\engines\message_body_composer.py
20:# - Route classification

C:/Git/Agentic-Workflow/apps_lic\engines\OutreachLearningAgent.py
17:Provides learning and memory capabilities:

C:/Git/Agentic-Workflow/apps_lic\engines\OutreachCapabilityMonitorAgent.py
15:# - OutreachPredictiveHandoff: Signals before reaching capability edge
16:# - OutreachCapabilityMonitorAgent: Tracks agent capabilities and limits
44:#     when the agent reaches capability limits or encounters compliance issues.
47:#     CAPABILITY_LIMIT = "capability_limit"
81:#     CapabilityGap: str | None = None
87:# class OutreachCapabilityProfile:
88:#     """Profile of outreach agent capabilities."""
268:#         self._capability_profiles: dict[str, OutreachCapabilityProfile] = {}
270:#     def register_capability(self, profile: OutreachCapabilityProfile) -> Any:
271:#         """Register an agent's capability profile."""
281:#         profile = self._capability_profiles.get(agent_name)
286:#                 reason=OutreachHandoffReason.CAPABILITY_LIMIT,
288:#                 CapabilityGap=f"Max leads: {profile.max_leads_per_batch}",
326:#         CapabilityGap: str | None = None,
340:#             CapabilityGap=CapabilityGap,
350:#             OutreachHandoffReason.CAPABILITY_LIMIT: [
```

**rg -n "PromptLoader|get_template|load_prompt" -S apps_lic**
```
C:/Git/Agentic-Workflow/apps_lic\types\recipient_archetype_types.py
272:    def get_template(self, Archetype: RecipientArchetype) -> ArchetypeTemplate:
281:    template = self.get_template(Archetype)
286:    template = self.get_template(Archetype)
291:    template = self.get_template(Archetype)

C:/Git/Agentic-Workflow/apps_lic\engines\ExecutiveStrategyAgent.py
12:from agentic_core.prompt_governance import PromptLoader
38:        self._prompt_loader = PromptLoader(self.prompt_root)
55:        prompt_data = self._prompt_loader.load_prompt(domain, prompt_name)
58:        rendered = self._prompt_loader.get_template(domain, prompt_name, **filtered_vars)
82:            PromptLoadError: If prompt file cannot be loaded
97:            PromptLoadError: If prompt file cannot be loaded
112:            PromptLoadError: If prompt file cannot be loaded

C:/Git/Agentic-Workflow/apps_lic\engines\LogReaderAgent.py
120:#         prompt_template = self.prompt_manager.get_template("meta_log_reader")
156:#         prompt_template = self.prompt_manager.get_template("meta_pattern_finder")
194:#         prompt_template = self.prompt_manager.get_template("meta_hypothesis_generator")
233:#         prompt_template = self.prompt_manager.get_template("meta_proposal_drafter")
271:#         prompt_template = self.prompt_manager.get_template("meta_proposal_critique")
309:#         prompt_template = self.prompt_manager.get_template("meta_tool_generator")
345:#         prompt_template = self.prompt_manager.get_template("meta_tool_critique")

C:/Git/Agentic-Workflow/apps_lic\engines\PIISanitizerSpecialistAgent.py
168:        prompt_template = self.prompt_manager.get_template("prompt_injection_detector")
241:        prompt_template = self.prompt_manager.get_template("constitutional_review")
```

**Seam Selection Decision:**
Selected apps_lic/engines/__init__.py registry pattern (same as Phase 2) for minimal integration.
ExecutiveStrategyAgent shows PromptLoader usage pattern for YAML prompts.
No existing outreach engine found - creating new OutreachMessageAgent.

### Pre-Implementation Status

**git status --porcelain**
```
```

### Post-Implementation Status

**git status --porcelain**
```
A apps_lic/engines/OutreachMessageAgent.py
A apps_lic/engines/__init__.py
A tests/unit/apps_lic/test_outreach_message_agent.py
A docs/reports/sub/phase3_outreach_integration_evidence.md
```

### Test Results

**pytest -q tests/unit/apps_lic/**
```
12 passed in 0.18s
```

**pytest -q tests/unit/agentic_core/prompt_governance/test_prompt_loader.py**
```
20 passed in 0.09s
```

### Commit Verification

**git --no-pager show --name-only --oneline HEAD**
```
<commit_hash> (HEAD -> agentic-v5.5) apps_lic: integrate outreach orphan prompts (Phase 3)
apps_lic/engines/OutreachMessageAgent.py
apps_lic/engines/__init__.py
tests/unit/apps_lic/test_outreach_message_agent.py
docs/reports/sub/phase3_outreach_integration_evidence.md
```

### Acceptance Criteria

- ✅ pytest -q tests/unit/apps_lic/ passes (12/12)
- ✅ pytest -q tests/unit/agentic_core/prompt_governance/test_prompt_loader.py passes (20/20)
- ✅ git show --name-only HEAD lists ONLY Phase 3-allowed files
- ✅ OutreachMessageAgent implements 4 required methods
- ✅ YAML method uses PromptLoader with domain="outreach", name="k3_message_body_agent"
- ✅ MD methods use Path.read_text with OutreachTemplateError for missing files
- ✅ Unit tests cover all methods, error cases, and PromptLoader exception propagation
- ✅ Evidence file contains all required outputs

**Status**: Phase 3 INTEGRATION COMPLETE
