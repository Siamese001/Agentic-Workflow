"""apps_rg - Declarative ingress-only application (per W5 of plan apps-rg-declarative-ingress-only-spinal-governance-c8b3e1).

Runtime authority lives in agentic_core. apps_rg may only build AppsRgIngressPayload
and submit to AppIngressRunner. The bootstrap_runtime module was quarantined under
AG-RGGOV-8 — there are no runtime shims for ingress-only packages.
"""
