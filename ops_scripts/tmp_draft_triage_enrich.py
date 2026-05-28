"""Enrich DRAFT skills for triage recommendations."""
import json
from pathlib import Path

ledger = json.loads(Path("apps_rg/fact_inventory/master_skills_arsenal_ledger.json").read_text())
cand_path = Path("artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json")
cand = json.loads(cand_path.read_text()) if cand_path.exists() else {}
facts = [f for f in cand.get("facts", []) if isinstance(f, dict)]

drafts = [r for r in ledger.get("skill_rows", []) if r.get("activation_status") == "DRAFT"]

# Brown & Brown JD keywords from gap report context
jd_terms = [
    "insurance", "brokerage", "strategy", "innovation", "enterprise",
    "architecture", "ai", "cloud", "partner", "gtm", "executive", "portfolio",
    "governance", "digital", "transformation", "stakeholder", "revenue",
]

def jd_relevance(row: dict) -> int:
    text = " ".join(
        str(x).lower()
        for x in (
            list(row.get("allowed_phrases") or [])
            + list(row.get("source_snippets") or [])
            + [row.get("pillar", ""), row.get("skill_id", "")]
        )
    )
    return sum(1 for t in jd_terms if t in text)

def suggest_fact(row: dict) -> str:
    allowed = [str(p).lower() for p in (row.get("allowed_phrases") or [])[:5]]
    best_id, best_score = "", 0
    for cf in facts:
        claim = str(cf.get("claim_text", "")).lower()
        tags = " ".join(str(t).lower() for t in (cf.get("capability_tags") or []))
        domain = str(cf.get("domain_family", "")).lower()
        blob = f"{claim} {tags} {domain}"
        score = sum(1 for p in allowed if p and len(p) > 4 and p in blob)
        if score > best_score:
            best_score = score
            best_id = str(cf.get("candidate_fact_id", ""))
    return best_id if best_score >= 1 else ""

for i, row in enumerate(drafts, 1):
    sid = row["skill_id"]
    pillar = (row.get("pillar") or "").replace("pillar_", "")
    support = row.get("support_level", "?")
    facts_links = row.get("fact_id_links") or []
    snippets = row.get("source_snippets") or []
    phrases = (row.get("allowed_phrases") or [])[:2]
    jd = jd_relevance(row)
    sug = suggest_fact(row) if not facts_links else (facts_links[0] if facts_links else "")
    print(f"{i:2}|{sid}|{pillar[:28]}|{support[:28]}|facts={len(facts_links)}|snip={len(snippets)}|jd={jd}|sug={sug}|phrases={phrases}")
