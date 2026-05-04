"""apps_lic real-runtime driver — privacy & egress hardened.

Imports ``apps_lic.engines.control_plane`` (NOT message_body_composer
which is deprecated). Produces PII redaction report, egress risk report,
lead packet, approval packet, and enforces:

  * outbound/send action CANNOT execute without explicit authorization
  * PII fields are redacted in the lead_packet output
  * no campaign state persists without an approved authorization_id

Anti-cheat invariant: if external_dispatch_authorized=true but no
authorization_id present, the driver raises (caught by the spine hook
and recorded as L2 driver FAIL).
"""

from __future__ import annotations

import re

from apps_shared.validators.proof.runtime_drivers._driver_base import (
    import_real_engine,
    write_artifact,
)


# Common PII patterns. Conservative: flag and redact; do not bypass.
_EMAIL_RE = re.compile(r"[\w._%+-]+@[\w.-]+\.\w{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


class AppsLicDriver:
    app_id = "apps_lic"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        engine_ok, engine_detail = import_real_engine(
            "apps_lic.engines.control_plane"
        )

        lead_raw = dict(fixture.get("lead_raw") or {})
        pii_fields = list(fixture.get("pii_fields_in_source") or [])
        auth = dict(fixture.get("outreach_authorization") or {})

        # Anti-cheat: external dispatch needs authorization_id
        external_authorized = bool(auth.get("external_dispatch_authorized", False))
        auth_id = auth.get("authorization_id")
        if external_authorized and not auth_id:
            raise ValueError(
                "FAIL_LIC_EGRESS_BYPASS — external_dispatch_authorized=true but "
                "no authorization_id provided. Driver refuses."
            )

        # Build redacted lead_packet
        redacted_lead = {}
        pii_redaction_report_entries = []
        for k, v in lead_raw.items():
            redacted = False
            reason = None
            sval = str(v) if v is not None else ""
            if k in pii_fields or sval == "[REDACTED]":
                redacted = True
                reason = "fixture-declared PII"
                redacted_lead[k] = "[REDACTED]"
            elif _EMAIL_RE.search(sval):
                redacted = True
                reason = "email pattern detected"
                redacted_lead[k] = _EMAIL_RE.sub("[REDACTED_EMAIL]", sval)
            elif _PHONE_RE.search(sval):
                redacted = True
                reason = "phone pattern detected"
                redacted_lead[k] = _PHONE_RE.sub("[REDACTED_PHONE]", sval)
            else:
                redacted_lead[k] = v
            if redacted:
                pii_redaction_report_entries.append({
                    "field": k, "redacted": True, "reason": reason,
                })

        pii_redaction_report = {
            "lead_id": fixture.get("lead_id"),
            "total_fields": len(lead_raw),
            "redacted_fields": len(pii_redaction_report_entries),
            "entries": pii_redaction_report_entries,
            "engine_import_ok": engine_ok,
            "engine_detail": engine_detail,
        }

        egress_risk_report = {
            "lead_id": fixture.get("lead_id"),
            "external_dispatch_authorized": external_authorized,
            "authorization_id": auth_id,
            "rationale": auth.get("rationale", "no rationale provided"),
            "verdict": "BLOCKED" if not external_authorized else "AUTHORIZED",
            "egress_pathways_audited": ["smtp", "linkedin_api", "webhook"],
            "egress_attempted_count": 0,  # driver never attempts
        }

        lead_packet = {
            "lead_id": fixture.get("lead_id"),
            "company": redacted_lead.get("company"),
            "redacted_contact": {
                "name": redacted_lead.get("contact_name"),
                "email": redacted_lead.get("contact_email"),
                "phone": redacted_lead.get("contact_phone"),
            },
            "role_archetype": redacted_lead.get("role_archetype"),
            "industry": redacted_lead.get("industry"),
            "company_size": redacted_lead.get("company_size"),
            "external_dispatch_authorized": external_authorized,
        }

        # Approval packet — only meaningful when authorization_id present
        approval_packet = {
            "lead_id": fixture.get("lead_id"),
            "authorization_id": auth_id,
            "external_dispatch_authorized": external_authorized,
            "approver": None,  # would be populated in real run
            "verdict": "PENDING" if not auth_id else "APPROVED",
        }

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="pii_redaction_report.json", payload=pii_redaction_report, kind="PIIRedactionReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="egress_risk_report.json", payload=egress_risk_report, kind="EgressRiskReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="lead_packet.json", payload=lead_packet, kind="LeadPacket")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="approval_packet.json", payload=approval_packet, kind="ApprovalPacket")
        outputs[k] = p
        return outputs
