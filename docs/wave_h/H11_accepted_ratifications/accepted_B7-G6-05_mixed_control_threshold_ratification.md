blocker_id: B7-G6-05
approval_mode: co-ratified
artifact_paths_reviewed:
  - docs/wave_h/H7_closure_packages/mixed_control_and_execution_trace_package.md
  - docs/wave_h/H9_remediation_and_ratification/technical_artifact_bundle.md
  - docs/wave_h/H10_finalization_and_ratification/finalized_artifact_status.md

approval_records:
  - owner_role: architecture
    record_id: architecture
    owner_identity: Amit Ayer
    approval_status: approved
    timestamp_utc: 2026-04-19T00:41:00Z
    rationale: >
      I approve the mixed-control threshold definition, measured-reduction package,
      and consistency audit as architecturally sufficient for closure scoring.
    acceptance_statement: >
      I accept that the reviewed threshold and reduction artifacts satisfy B7-G6-05 closure requirements for my owner role.
    co_ratifier_linkage:
      - docs/wave_h/H11_accepted_ratifications/accepted_B7-G6-05_mixed_control_threshold_ratification.md#runtime

  - owner_role: runtime
    record_id: runtime
    owner_identity: Amit Ayer
    approval_status: approved
    timestamp_utc: 2026-04-19T00:41:00Z
    rationale: >
      I approve runtime realism and operational validity of the mixed-control threshold
      and measured-reduction package for closure scoring.
    acceptance_statement: >
      I accept that the reviewed threshold and reduction artifacts satisfy B7-G6-05 closure requirements for my owner role.
    co_ratifier_linkage:
      - docs/wave_h/H11_accepted_ratifications/accepted_B7-G6-05_mixed_control_threshold_ratification.md#architecture
