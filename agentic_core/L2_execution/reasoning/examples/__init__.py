"""L2 Execute v2 exemplar agents (plan c8e4f1 W6).

Reference implementations demonstrating the validator/healer split pattern
for future migrations of the 15+ co-located agents identified in plan §10
ADG_HOTSPOT_REPORT.

These exemplars are intentionally lightweight and focused on one domain
(code-quality line-length check/repair) so the pattern is readable end-to-end
without the noise of real agent state, tool registries, or mixin chains.

Production agents SHOULD follow this pattern:
  1. Inherit from SovereignValidatorBase (validator) or SovereignHealerBase (healer) — never both
  2. validator.validate() returns ValidationVerdict dict; no state mutation
  3. healer.heal() returns HealResult; re-asserts blueprint/policy hash equality
  4. @requires_sealed_return marker + public methods annotated with -> SealedL2Artifact
  5. CI gate ops_scripts/ci/check_agent_sealed_return.py enforces #4 for marked classes
"""
