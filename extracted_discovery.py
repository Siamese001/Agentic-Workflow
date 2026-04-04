def execute_phase1_discovery(agents, territory, decision_engine, state_mgr, ctx: "HealContext" = None):
    """PHASE 1: TERRITORIAL DISCOVERY (Retriable)"""
    return execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, ctx)



def execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, ctx: "HealContext" = None):
    """PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration"""
    logger.info(f"=== PHASE 1: DISCOVERY - {territory} ===")
    state_mgr.update_agent("FilesystemSSOTReconcilerAgent", "L5 - Safety (Validator)")
    from agentic_core.L5_safety.reasoning.filesystem_ssot_validator import (
        FilesystemSSOTValidatorAgent as _FilesystemSSOTValidatorAgent,
    )

    _fs_validator = _FilesystemSSOTValidatorAgent(project_root=REPO_ROOT)
    _fs_check = _fs_validator.to_check_dict()
    drift_report = _fs_check["evidence"]
    if drift_report is None:
        state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", False, "Returned None")
        return (None, None)
    heal_result = {"skipped": 1}
    if ctx is not None and getattr(ctx, "heal", False):
        _fs_healer_cls = agents.get("reconciler")
        if _fs_healer_cls is not None:
            _fs_healer_instance = _fs_healer_cls(project_root=REPO_ROOT)
            # force=True required: without it heal_repository() short-circuits to skipped=1
            heal_result = _fs_healer_instance.heal_repository(dry_run=False, execute=True, force=True)
            # run_with_cleanup covers full SSOT blueprint drift (the 29-item scan)
            cleanup_result = _fs_healer_instance.run_with_cleanup(dry_run=False)
            heal_result["cleanup"] = cleanup_result
            logger.info(
                f"[FilesystemSSOTReconcilerAgent] root_heal={heal_result}, "
                f"cleanup_applied={cleanup_result.get('actions_applied', 0)}"
            )
    violations_count = _fs_check.get("violations_count", 0)
    _heal_applied = heal_result.get("applied", 0) or heal_result.get("cleanup", {}).get("actions_applied", 0)
    _was_skipped = heal_result.get("skipped", 0) and not heal_result.get("cleanup")
    _outcome = "SKIPPED" if _was_skipped else "SUCCESS"
    state_mgr.complete_agent(
        "FilesystemSSOTReconcilerAgent",
        True,
        f"Drift violations: {violations_count}, healed: {_heal_applied}",
    )
    _record_healing_action(
        state_mgr,
        agent="FilesystemSSOTReconcilerAgent",
        territory=territory,
        routing_tier="DETERMINISTIC",
        confidence=1.0,
        fix_summary=f"SSOT drift scan: {violations_count} violation(s), applied: {_heal_applied}",
        outcome=_outcome,
    )
    state_mgr.update_agent("LocationHealerAgent", "L5 - Safety")
    location_validator = _get_location_validator_agent()(project_root=REPO_ROOT)
    repo_root_resolved = REPO_ROOT.resolve()
    territory_path = (repo_root_resolved / territory).resolve()
    # Canonicalize L-layer territories: L0_routing ΓåÆ agentic_core/L0_routing
    if not territory_path.exists() and territory.startswith(
        ("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")
    ):
        territory_path = (repo_root_resolved / AGENTIC_CORE_DIR / territory).resolve()
    if not territory_path.is_relative_to(repo_root_resolved):
        logger.critical(f"SECURITY ALERT: Path traversal attempt detected for territory '{territory}'")
        state_mgr.add_event("security", "Path traversal blocked")
        state_mgr.complete_agent("LocationHealerAgent", False, "Traversal blocked")
        return (drift_report, [])
    violations = []
    location_scan_result = {}
    if territory_path.exists():
        location_scan_result = location_validator.run(target_territory=territory) or {}
        violations = location_scan_result.get("violations", [])
    else:
        logger.warning(f"Territory path does not exist: {territory_path}")
    # --- ADG Behavioral enrichment ---
    # Load behavioral profiles for all violation targets in one bulk query.
    # Gracefully degrades to neutral (score=0.5) when ADG SQLite is unavailable.
    _adg_territory_score = 0.5
    try:
        from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex as _ADGIdx

        _adg_idx = _ADGIdx.from_latest(REPO_ROOT)
        if _adg_idx is not None and violations:
            _violation_paths = [
                str(Path(v.get("file", "")).resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
                for v in violations
                if v.get("file")
            ]
            _profiles = _adg_idx.profiles_for(_violation_paths) if _violation_paths else {}
            # Enrich each violation dict with its ADG behavioral score + signal summary
            for v in violations:
                fpath = v.get("file", "")
                if fpath:
                    try:
                        rel = str(Path(fpath).resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
                    except ValueError:
                        rel = fpath
                    prof = _profiles.get(rel)
                    if prof is not None:
                        v["adg_behavioral_score"] = prof.behavioral_score
                        v["adg_is_agent_like"] = prof.is_agent_like
                        v["adg_is_script_like"] = prof.is_script_like
                        v["adg_signals"] = sorted(prof.all_signals)
            # Territory-level score: mean across all profiled violations
            profiled_scores = [v["adg_behavioral_score"] for v in violations if "adg_behavioral_score" in v]
            if profiled_scores:
                _adg_territory_score = round(sum(profiled_scores) / len(profiled_scores), 4)
            logger.debug(
                "[ADG] territory=%s violations=%d adg_territory_score=%.3f",
                territory,
                len(violations),
                _adg_territory_score,
            )
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as _adg_err:
        logger.debug("[ADG] Behavioral enrichment skipped (non-fatal): %s", _adg_err)
    state_mgr.state["adg_territory_score"] = _adg_territory_score
    # --- end ADG enrichment ---
    if violations:
        logger.info("≡ƒºá Using CognitiveDispositionAgent for enhanced violation analysis...")
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        cognitive_dispositions, enhanced_confidence = loop.run_until_complete(
            decision_engine.analyze_violations_with_cognitive_disposition(violations, territory, state_mgr)
        )
        state_mgr.state["cognitive_dispositions"] = [d.__dict__ for d in cognitive_dispositions]
        confidence = enhanced_confidence
        logger.info(f"≡ƒºá Enhanced confidence with cognitive analysis: {confidence.value:.2f}")
    else:
        confidence = decision_engine.calculate_healing_confidence(
            len(violations),
            [str(v) for v in violations[:10]],
            territory,
            agent_name="location",
            adg_behavioral_score=_adg_territory_score,
        )
    state_mgr.state["compliance_scores"][territory] = confidence.value
    state_mgr.state["location_violations"] = violations
    state_mgr.state["location_scan_result"] = location_scan_result
    if len(violations) > 0:
        proceed, reason = decision_engine.should_proceed_with_healing(
            confidence,
            "LocationHealerAgent",    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling
            territory=territory,
            adg_behavioral_score=_adg_territory_score,
        )
        state_mgr.add_event("decision", f"Location Healing: {reason}")
        logger.info(f"Location Decision: {reason}")
        if proceed and ctx is not None and ctx.heal:
            logger.info(f"Triggering LocationAgent auto-heal for {len(violations)} violations")
            import sys as _sys

            def _w6_hitl_archive_gate(file_path, msg):
                if ctx is not None and getattr(ctx, "auto_approve", False):
                    return (True, "HITL-AUTO-APPROVED (--heal active)")
                if not _sys.stdin.isatty():
                    return (False, "HITL-DEFER (non-interactive)")
                if os.environ.get("ARCHIVE_BATCH_ACCEPT") == "1":
                    return (True, "HITL-APPROVED (batch)")
                border = "=" * 56
                print(f"\n{border}")
                print("  HITL GATE  [FILE DELETION / ARCHIVE]")
                # guardian: allow-silent-swallow - acceptable exception handling
                print(border)
                print(f"  File  : {file_path}")
                print(f"  Reason: {str(msg)[:100]}")
                print(border)
                print("  [A] Archive (reversible)  [S] Skip  [D] Delete permanently")
                print(border)
                try:
                    raw = input("  Choice [A/S/D]: ").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    raw = "S"
                if raw == "A":
                    return (True, "HITL-APPROVED (archive)")
                elif raw == "D":
                    return (True, "HITL-APPROVED (delete)")
                else:
                    return (False, "HITL-SKIPPED")

            location_validator._hitl_approval_fn = _w6_hitl_archive_gate
            if hasattr(location_validator, "heal_violations"):
                heal_result = location_validator.heal_violations(
                    violations, auto_approve=ctx.auto_approve if ctx else False
                )
                healed_count = heal_result.get("healed", 0) if isinstance(heal_result, dict) else 0
                state_mgr.state["location_fixed"] = healed_count
                _record_healing_action(
                    state_mgr,
                    agent="LocationHealerAgent",
                    territory=territory,
                    routing_score=confidence.value,
                    routing_tier="DETERMINISTIC",
                    confidence=confidence.value,
                    fix_summary=f"Healed {healed_count} of {len(violations)} location violations"
                    if healed_count > 0
                    else f"Location scan: {len(violations)} violation(s), 0 healed in {territory}",
                    outcome="SUCCESS" if healed_count > 0 else "PARTIAL",
                )
                state_mgr.complete_agent(
                    "LocationHealerAgent",
                    True,
                    f"Violations: {len(violations)} | Healed: {healed_count} | Conf: {confidence.value:.2f}",
                )
            else:
                logger.warning(
                    "LocationHealerAgent has no heal_violations method - violations detected but not healed"
                )
                _record_healing_action(
                    state_mgr,
                    agent="LocationHealerAgent",
                    territory=territory,
                    routing_score=confidence.value,
                    routing_tier="DETERMINISTIC",
                    confidence=confidence.value,
                    fix_summary=f"Location scan: {len(violations)} violation(s), no heal method in {territory}",
                    outcome="SKIPPED",
                )
                state_mgr.complete_agent(
                    "LocationHealerAgent",
                    True,
                    f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (no heal method)",
                )
        else:
            _record_healing_action(
                state_mgr,
                agent="LocationHealerAgent",
                territory=territory,
                routing_score=confidence.value,
                routing_tier="DETERMINISTIC",
                confidence=confidence.value,
                fix_summary=f"Location scan: {len(violations)} violation(s), healing skipped in {territory}",
                outcome="SKIPPED",
            )
            state_mgr.complete_agent(
                "LocationHealerAgent",
                True,
                f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (healing skipped)",
            )
    else:
        _record_healing_action(
            state_mgr,
            agent="LocationHealerAgent",
            territory=territory,
            routing_score=confidence.value,
            routing_tier="DETERMINISTIC",
            confidence=confidence.value,
            fix_summary=f"Location scan: 0 violations in {territory}",
            outcome="SUCCESS",
        )
        state_mgr.complete_agent("LocationHealerAgent", True, f"Violations: 0 | Conf: {confidence.value:.2f}")
    # PHASE 1 ENHANCEMENT: Early File Classification Detection
    classification_violations = []
    classification_scan_result = {}
    try:
        state_mgr.update_agent("FileClassificationHealerAgent", "L5 - Safety (Validator)")
        from agentic_core.L5_safety.reasoning.file_classification_validator import (
            FileClassificationValidatorAgent as _FileClassificationValidatorAgent,
        )

        _fc_validator = _FileClassificationValidatorAgent(project_root=REPO_ROOT)
        _fc_check = _fc_validator.to_check_dict(target_territory=territory)
        _fc_evidence = _fc_check.get("evidence", {})
        classification_scan_result = _fc_evidence.get("scan_result", {})
        classification_violations = _fc_evidence.get("violations", [])
        classification_count = len(classification_violations)
        state_mgr.complete_agent(
            "FileClassificationHealerAgent",
            True,
            f"Early detection: {classification_count} classification issues",
        )
        _record_healing_action(
            state_mgr,
            agent="FileClassificationHealerAgent",
            territory=territory,
            routing_tier="DETERMINISTIC",
            routing_score=1.0,
            confidence=1.0,
            fix_summary=f"Scanned {territory}: {classification_count} classification issue(s) detected",
            outcome="SUCCESS",
        )
        state_mgr.state["classification_violations"] = classification_violations
        state_mgr.state["classification_scan_result"] = classification_scan_result
        state_mgr.state["classification_check_dict"] = _fc_check
        state_mgr.state["classification_file_registry"] = _fc_evidence.get("file_registry", [])
        logger.info(f"FileClassificationAgent early detection: {classification_count} issues found")
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        logger.error(f"FileClassificationHealerAgent early detection FAILED: {e}\n{traceback.format_exc()}")
        state_mgr.complete_agent("FileClassificationHealerAgent", False, f"Early detection error: {e}")
        _record_healing_action(
            state_mgr,
            agent="FileClassificationHealerAgent",
            territory=territory,
            routing_tier="DETERMINISTIC",
            routing_score=0.0,
            confidence=0.0,
            fix_summary=f"FileClassificationHealerAgent failed: {str(e)[:120]}",
            outcome="FAILED",
        )
        state_mgr.add_event("error", f"FileClassificationHealerAgent early detection failed: {e}")
        state_mgr.state["classification_violations"] = []
        state_mgr.state["classification_scan_result"] = {}
        state_mgr.state["classification_check_dict"] = {}
    return (drift_report, violations, location_scan_result)


@with_retry(max_retries=MAX_RETRIES)
