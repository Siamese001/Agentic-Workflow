# Safety Incident Response Runbook

## SLA: 5-Minute Initial Response

### Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| P0 | Active harm, data breach | Immediate | VP + Legal |
| P1 | Safety bypass, PII exposure | 5 minutes | Director |
| P2 | Policy violation, edge case | 30 minutes | Manager |
| P3 | Minor issue, false positive | 4 hours | On-call |

---

## Phase 1: Isolate (0-2 minutes)

### Immediate Actions

1. **Identify the scope**
   - Which model/endpoint is affected?
   - How many users impacted?
   - Is the issue ongoing or historical?

2. **Contain the incident**
   ```bash
   # Disable affected endpoint
   kubectl scale deployment llm-api --replicas=0

   # Or enable circuit breaker
   curl -X POST https://api.internal/safety/circuit-breaker/open
   ```

3. **Preserve evidence**
   - Screenshot the incident
   - Export relevant logs
   - Note exact timestamps

---

## Phase 2: Preserve (2-5 minutes)

### Evidence Collection

```python
# Export incident logs
from datetime import datetime, timedelta

incident_time = datetime.utcnow()
start = incident_time - timedelta(hours=1)
end = incident_time + timedelta(minutes=5)

logs = export_logs(
    service="llm-api",
    start_time=start,
    end_time=end,
    include_request_body=True,
    include_response_body=True,
)

# Store in incident bucket
upload_to_s3(
    bucket="safety-incidents",
    key=f"incident-{incident_time.isoformat()}/logs.json",
    data=logs,
)
```

### Documentation Template

```markdown
## Incident Report: [ID]

**Time Detected**: YYYY-MM-DD HH:MM UTC
**Severity**: P0/P1/P2/P3
**Status**: Active/Contained/Resolved

### Summary
[One paragraph description]

### Impact
- Users affected: N
- Requests affected: N
- Data exposed: Yes/No

### Timeline
- HH:MM - Incident detected
- HH:MM - Containment initiated
- HH:MM - [Additional actions]
```

---

## Phase 3: Notify (5-15 minutes)

### Notification Matrix

| Severity | Slack Channel | Email | PagerDuty |
|----------|---------------|-------|-----------|
| P0 | #incident-war-room | all-hands | Yes |
| P1 | #safety-incidents | safety-team | Yes |
| P2 | #safety-incidents | safety-team | No |
| P3 | #safety-triage | - | No |

### Communication Template

```
🚨 SAFETY INCIDENT - [SEVERITY]

What: [Brief description]
When: [Timestamp]
Impact: [Scope]
Status: [Contained/Investigating]
Lead: [Name]

Updates in: #[channel]
```

---

## Phase 4: Post-Mortem (24-48 hours)

### Required Sections

1. **Executive Summary**
2. **Timeline of Events**
3. **Root Cause Analysis**
4. **Impact Assessment**
5. **Remediation Actions**
6. **Prevention Measures**

### Blameless Culture

- Focus on systems, not individuals
- Ask "what" and "how", not "who"
- Identify process gaps
- Implement systemic fixes
