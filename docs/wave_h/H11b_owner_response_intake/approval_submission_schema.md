# H11b — Approval Submission Schema

wave: H11b
adg_snapshot: artifacts/adg/adg_indexed_04182026_2022.sqlite
adg_snapshot_timestamp: "04182026_2022"

Minimum required fields for a ratification artifact to count for true H11 retry:

1. blocker_mapping
   - `blocker_id` (one of 8 mandatory blockers)
2. owner_role
   - storage/config | runtime | architecture | governance | taxonomy | provider/gateway
3. approval_status
   - `approved` | `rejected` | `changes_requested`
4. timestamp
   - UTC ISO-8601 timestamp
5. artifact_paths_reviewed
   - one or more repo paths for reviewed closure artifacts
6. rationale
   - explicit reasoning for approval/rejection/change request
7. co_ratifier_linkage (if required)
   - references peer approval record IDs/paths for co-ratified blockers

Optional but recommended fields:

- owner_identity (name/handle)
- decision_version
- supersedes_record

Validation notes:

- records missing any required field are invalid for true H11 retry
- `approved` status without artifact paths reviewed is invalid
- co-ratified blockers require linkage to all required co-ratifier approvals before counting as accepted
