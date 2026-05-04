# apps_research — Threat Model

## Scope

`apps_research` performs autonomous research by harvesting external web content, extracting insights, and synthesizing reports. The web-harvest boundary is the primary attack surface.

## Assets

| Asset | Sensitivity | Integrity requirement |
|---|---|---|
| Research query | Low–Medium | Must not leak via URL parameters to untrusted services |
| Harvested content | Medium | Provenance (URL + timestamp + hash) recorded in evidence packet |
| Credibility scores | Medium | Must be reproducible from harvested content |
| Final synthesis report | Medium | Must cite every claim with source_id + span |

## Threat actors

1. **Malicious web publisher** — serves content designed to poison research output
2. **Compromised search index** — returns attacker-controlled URLs
3. **Prompt-injection via harvested content** — payload embedded in page text
4. **Privacy-invasive tracking** — telemetry correlating queries to identity

## Threats and mitigations

### T1 — Content-based prompt injection

- **Mitigation**: Harvested content passes through `CredibilityScorerService` before reaching `InsightExtractorService`. Content matching injection signatures (jailbreak phrases, role-switching directives) is flagged and excluded.
- **Residual risk**: Novel injection patterns — mitigated by rubric-based QA and `anti_overfitting` constraints ported from apps_rg.

### T2 — Poisoned search results

- **Mitigation**: `SourceDiscoveryService` scores sources by credibility (domain reputation, citation count, freshness). Low-credibility sources are excluded or flagged in the evidence packet.
- **Residual risk**: Sophisticated SEO manipulation — mitigated by human-in-the-loop review on low-credibility high-weight sources.

### T3 — PII / query leakage

- **Mitigation**: Queries to external search APIs are transmitted over HTTPS; no PII (user identifiers, session tokens) is appended to the query string. API keys are scoped read-only.
- **Residual risk**: Upstream search provider may log queries — mitigated by query redaction in `CitationManagerService`.

### T4 — Report fabrication (hallucination)

- **Mitigation**: Every synthesis statement in `ReportCompilerService` must cite a `source_id` with `span_start`/`span_end` pointing into the harvested-content corpus. Uncited statements fail the contract gate.
- **Residual risk**: Citation-span mismatches — mitigated by `ProvenancetrackerStrategy` verification in apps_shared.

### T5 — Harvest-time DoS / rate-limiting

- **Mitigation**: `ContentHarvesterService` uses exponential backoff and respects `robots.txt`. Per-domain rate limits enforced.
- **Residual risk**: Adversarial slowloris — mitigated by per-request timeout (subprocess timeout §14).

### T6 — SSRF via harvested URLs

- **Mitigation**: URL allow-list enforced before harvest. Internal/loopback/metadata-service URLs blocked. No URL rewrites based on harvested content.

## Trust boundaries

```
QUERY ──[SourceDiscovery: credibility]──> EXTERNAL WEB ──[Harvester: timeout+allowlist]──> CONTENT
                                                                                               ↓
                                          [CredibilityScorer → InsightExtractor] ──[Synthesis + cite check]──> REPORT
```

## Non-goals

- Cryptographic authentication of arbitrary web content
- Protecting against compromised network middleboxes
- Long-term integrity guarantees beyond the evidence-packet hash

## References

- ADR-082 — folder taxonomy
- ADR-028 — publisher-boundary
- `tools/cert/` — certification evidence
- `TECHNICAL_SPEC.md` (to be authored)
