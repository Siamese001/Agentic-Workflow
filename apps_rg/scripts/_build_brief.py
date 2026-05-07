"""One-shot: build a CompanyBrief-shaped JSON from the extracted PDF text."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PDF_BRIEF = Path("apps_rg/scripts/_interactive_brief.json")


def main() -> int:
    raw = json.loads(PDF_BRIEF.read_text(encoding="utf-8"))
    text = raw.get("freeform_text", "")

    brief = {
        "company": "Brown & Brown",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "user_uploaded",
        "freshness_ttl_days": 30,
        "overview": {
            "tagline": "One of the largest publicly traded independent insurance brokerages in the United States, built on a meritocratic, decentralized culture.",
            "founded": 1939,
            "size_band": "Fortune 500; ~17,000+ teammates; >$5B annual revenue",
            "ownership": "NYSE: BRO",
            "headquarters": "Daytona Beach, Florida",
            "core_offerings": [
                "Retail insurance brokerage (commercial and personal lines)",
                "National wholesale brokerage and underwriting",
                "Programs and specialty MGA/MGU operations",
                "Services, claims administration, and risk management",
            ],
        },
        "strategic_priorities": [
            "Multi-year IT strategy tightly aligned with corporate growth objectives",
            "AI, automation, and data-driven capabilities at enterprise scale",
            "Modern enterprise architecture: interoperability, scalability, security, modernization",
            "Innovation incubation: labs, pilots, and emerging-tech evaluation",
            "M&A integration playbook for technology and platform consolidation",
        ],
        "customer_profile": {
            "verticals": [
                "Commercial insurance buyers (mid-market and enterprise)",
                "Public entities, healthcare, construction, energy, marine, transportation",
                "High-net-worth and personal lines clients",
            ],
            "buyer_titles": [
                "CFO",
                "CIO/CITO",
                "Chief Risk Officer",
                "VP Risk Management",
                "Director of Insurance / Treasury",
            ],
            "typical_engagement_size": "Multi-line commercial programs and specialty placements",
        },
        "tech_stack_signals": [
            "Cloud platforms (AWS / Azure)",
            "Modern data platforms; lakehouse / streaming",
            "Enterprise integration / iPaaS",
            "AI/ML and generative AI tooling",
            "Salesforce, ServiceNow, modern policy admin systems",
            "Identity, security, and zero-trust frameworks",
        ],
        "cultural_cues": [
            "Meritocracy — outcome-focused; rewards self-starters",
            "Decentralized P&L with strong central technology backbone",
            "Pragmatic, action-oriented; bias for delivery",
            "Builder mindset; entrepreneurial; teammates not employees",
            "Continuous improvement and disciplined execution",
        ],
        "leadership": [
            {
                "name": "J. Powell Brown",
                "title": "President & CEO",
                "background": "Long-tenured leader steering Brown & Brown's growth and acquisition strategy.",
            },
            {
                "name": "CITO (role context)",
                "title": "Chief Information & Technology Officer",
                "background": "SVP IT Strategy & Innovation reports directly to the CITO; partners on enterprise architecture, AI, and innovation.",
            },
        ],
        "competitive_set": [
            "Marsh McLennan",
            "Aon",
            "Arthur J. Gallagher",
            "Willis Towers Watson",
            "Hub International",
            "Lockton",
            "Acrisure",
        ],
        "pain_points_inferred": [
            "Integrating technology stacks across many acquired agencies",
            "Modernizing legacy policy/claims systems while preserving M&A velocity",
            "Scaling AI responsibly across a decentralized federation",
            "Data interoperability across heterogeneous brokerage platforms",
            "Talent: building durable AI/data engineering capability",
        ],
        "recent_moves": [
            {
                "date": "2024-2026",
                "event": "Continued M&A pace and platform consolidation",
                "signal": "Technology integration is a strategic differentiator; need scalable architecture and innovation incubation.",
            },
            {
                "date": "2025-2026",
                "event": "Public emphasis on AI, data, and interoperability in IT strategy",
                "signal": "Senior leadership investing in long-term technology direction with near-term innovation outcomes.",
            },
        ],
        "language_to_mirror": [
            "meritocracy",
            "teammates",
            "decentralized",
            "discipline and accountability",
            "long-term technology direction",
            "innovation and incubation",
            "enterprise architecture",
            "AI, data, and interoperability",
            "scalable, forward-thinking solutions",
            "operational excellence",
            "competitive differentiation",
            "responsible innovation",
            "bias for action",
            "measurable outcomes",
            "translate complex technology into compelling narratives",
        ],
        "language_to_avoid": [
            "buzzword-heavy abstractions without delivery proof",
            "framework-speak detached from business outcomes",
            "centralized command-and-control posture",
        ],
        "_pdf_source": raw.get("_source"),
        "_pdf_text": text,
    }

    PDF_BRIEF.write_text(json.dumps(brief, indent=2), encoding="utf-8")
    print(f"wrote {PDF_BRIEF} (CompanyBrief shape, {len(text)} chars freeform retained)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
