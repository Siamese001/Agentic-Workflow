# Execute SSOT Mutation Fence Hardening — Evidence
## Commit Chain
```
82942d37cc6f96938428a2356985ab3f04da15ed
```
Wave 1 commit: 9f0d951ae4cb425f4a9fd2cd16eb3587eacc287b
Wave 1 hygiene commit: c5344d5f6d2ae5a5fc435ae64978192c802728e4
Wave 2 baseline commit: f55ac93377048383dfd663fbc9c6ba20e54e53e6
Wave 2 correction commit: bc3d518feebd681f310fc6ca44b774c1d2582dc7
Wave 2 discoverability commit: ddfc9c6c428c15e214a54770dc4858b97a12bf97
Scope-repair revert commit: 82942d37cc6f96938428a2356985ab3f04da15ed

## Wave 1 — Write Surface Audit (raw)
```
agentic_core\interfaces\IBlackboardLeaseVerifier.py:78:    current = Path(__file__).resolve()
agentic_core\interfaces\IBlackboardLeaseVerifier.py:168:    with open(resolved_path, encoding="utf-8") as f:
agentic_core\interfaces\IBlackboardLeaseVerifier.py:201:            with open(resolved_path, encoding="utf-8") as f:
agentic_core\interfaces\IBlackboardLeaseVerifier.py:242:    with open(resolved_path, "w", encoding="utf-8") as f:
agentic_core\interfaces\IBlackboardLeaseVerifier.py:326:                file_path = Path(root) / filename
agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:78:    current = Path(__file__).resolve()
agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:168:    with open(resolved_path, encoding="utf-8") as f:
agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:201:            with open(resolved_path, encoding="utf-8") as f:
agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:242:    with open(resolved_path, "w", encoding="utf-8") as f:
agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:327:                file_path = Path(root) / filename
agentic_core\mixins\atomic_execution_mixin.py:135:            shutil.copy2(file_path, backup_path)
agentic_core\mixins\atomic_execution_mixin.py:161:                    shutil.copy2(backup.backup_path, backup.original_path)
agentic_core\mixins\atomic_execution_mixin.py:187:                shutil.rmtree(backup_dir)
agentic_core\mixins\atomic_execution_mixin.py:285:            file_path.write_text(content, encoding=encoding)
agentic_core\mixins\atomic_execution_mixin.py:362:            shutil.move(str(src_path), str(dst_path))
agentic_core\mixins\audit_trail_mixin.py:172:            "domain": getattr(self, "domain_root", Path("unknown")).name,
agentic_core\mixins\audit_trail_mixin.py:191:        log_entry = json.dumps(payload, separators=(",", ":"), default=json_serializer)
agentic_core\mixins\cst_healer_mixin.py:275:                context.file_path.write_text(modified_code, encoding="utf-8")
agentic_core\mixins\event_emission_mixin.py:13:_SOURCE = Path(__file__).resolve().parent.parent / "runtime" / "types" / "sovereign_events_types.py"
agentic_core\mixins\feature_flagged_agent_mixin.py:453:            f"[AUDIT] {event_id} | {self.__class__.__name__} | {event_type} | {json.dumps(data, default=str)}",
agentic_core\mixins\healing_policy_mixin.py:154:            with open(file_path, encoding="utf-8") as f:
agentic_core\mixins\meta_learning_client_mixin.py:445:            sig_str = json.dumps(
agentic_core\mixins\pinecone_vector_mixin.py:162:            emb_sig = hashlib.sha256(json.dumps(embedding[:5] + embedding[-5:]).encode()).hexdigest()[:16]
agentic_core\mixins\rate_limit_mixin.py:114:            payload = json.dumps(self._bucket_state[key])
agentic_core\mixins\redis_cache_mixin.py:125:                root = Path(__file__).resolve().parents[3]  # Adjusted for utils location
agentic_core\mixins\redis_cache_mixin.py:205:            _ = json.dumps(value)
agentic_core\mixins\runtime_safety_mixin.py:33:    def safe_popen(*args, **kwargs):
agentic_core\mixins\runtime_safety_mixin.py:49:    - safe_popen(): Secure subprocess.Popen wrapper
agentic_core\mixins\runtime_safety_mixin.py:94:    def safe_popen(
agentic_core\mixins\runtime_safety_mixin.py:106:        return safe_popen(command, cwd=cwd, **kwargs)
agentic_core\mixins\state_validation_mixin.py:65:            s = json.dumps(payload, sort_keys=True)
agentic_core\prompt_governance\prompt_loader.py:82:                with open(prompt_file, encoding="utf-8") as f:
agentic_core\utils\ast_fuzzy_util.py:145:    with open(path, "rb") as f:
agentic_core\utils\canonical_serializer_util.py:5:ShiftReport, ReplayBundle) MUST use this serializer.  Direct json.dumps
agentic_core\utils\canonical_serializer_util.py:58:    return json.dumps(
agentic_core\utils\fs_util.py:40:                file_path = Path(root) / file
agentic_core\utils\fs_util.py:61:        with open(file_path, "rb") as f:
agentic_core\utils\fs_util.py:81:    return Path(str(resolved).replace("\\", "/"))
agentic_core\utils\meta_learning_storage_util.py:84:            _ = json.dumps(result)  # serialization guard
agentic_core\utils\project_root_util.py:22:        start_path = Path(__file__).resolve()
agentic_core\utils\project_root_util.py:32:        env_root = Path(os.environ["PROJECT_ROOT"])
agentic_core\utils\project_root_util.py:49:        current = start_path or Path(__file__).resolve()
agentic_core\utils\structural_healing_engine_util.py:58:    shutil.move(str(source_path), str(target_path))
agentic_core\utils\structural_healing_engine_util.py:61:        shutil.move(str(target_path), str(source_path))
agentic_core\config\core\config_loader.py:17:    path_to_check = Path(filename)
agentic_core\config\core\config_loader.py:22:            with open(path_to_check, encoding="utf-8") as f:
agentic_core\config\core\non_conforming_agent_finder_config.py:36:PROJECT_ROOT = Path(__file__).resolve().parents[1]
agentic_core\config\core\reflection_config.py:308:        context_text = f"\nContext: {json.dumps(context, indent=2)}" if context else ""
agentic_core\config\core\reflection_config.py:313:{json.dumps(content, indent=2)}
agentic_core\config\core\reflection_config.py:369:            return json.dumps(
agentic_core\config\core\reflection_config.py:378:            return json.dumps(
agentic_core\config\core\reflection_config.py:387:            return json.dumps(
agentic_core\config\core\reflection_config.py:412:                json.dumps(content)
agentic_core\config\core\yaml_injection_loader.py:65:            yaml_root = Path("data/prompt_governance/injections")
agentic_core\config\core\yaml_injection_loader.py:67:        self.yaml_root = Path(yaml_root)
agentic_core\config\core\yaml_injection_loader.py:159:            with open(yaml_file, encoding="utf-8") as f:
agentic_core\knowledge\document_loaders\html_loader.py:56:        raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
agentic_core\knowledge\document_loaders\pdf_document_loader_config.py:9:        self.file_path = Path(file_path)
agentic_core\knowledge\document_loaders\text_document_loader_config.py:9:        self.file_path = Path(file_path)
agentic_core\knowledge\document_loaders\text_document_loader_config.py:16:        return Path(file_path).read_text(encoding="utf-8", errors="replace")
agentic_core\knowledge\engine\rag_orchestrator.py:181:                    "content": json.dumps(self.static_knowledge["action_verbs"], indent=2),
agentic_core\knowledge\engine\rag_orchestrator.py:190:                    "content": json.dumps(SKILL_TAXONOMY, indent=2),
agentic_core\knowledge\engine\rag_orchestrator.py:245:{json.dumps([{"idx": i, "text": c["content"][:500]} for i, c in enumerate(candidates)], indent=2)}
agentic_core\knowledge\healing\wiki_healer.py:76:            agentic_core_path = Path("agentic_core")
agentic_core\knowledge\reasoning\SovereignRAGManagerAgent.py:25:        self.storage_root = Path(storage_root)
agentic_core\knowledge\reasoning\SovereignRAGManagerAgent.py:64:        suffix = Path(file_path).suffix.lower()
agentic_core\knowledge\reasoning\SovereignRAGManagerAgent.py:68:            loader = TextDocumentLoader(Path(file_path))
agentic_core\knowledge\reasoning\SovereignRAGManagerAgent.py:70:            loader = PDFDocumentLoader(Path(file_path))
agentic_core\knowledge\reasoning\SovereignRAGManagerAgent.py:78:        self.index_document(Path(file_path).name, chunks)
agentic_core\knowledge\research_cache\cache_store_util.py:35:        self.cache_dir = Path(cache_dir)
agentic_core\knowledge\research_cache\cache_store_util.py:52:            with self.cache_file.open("r", encoding="utf-8") as f:
agentic_core\knowledge\research_cache\cache_store_util.py:95:            with self.cache_file.open("r", encoding="utf-8") as f:
agentic_core\knowledge\research_cache\cache_store_util.py:125:            with self.cache_file.open("a", encoding="utf-8") as f:
agentic_core\knowledge\research_cache\cache_store_util.py:127:                    sum(1 for _ in open(self.cache_file, encoding="utf-8")) if self.cache_file.exists() else 0
agentic_core\knowledge\research_cache\cache_store_util.py:129:                json.dump(entry, f)
agentic_core\L0_routing\enforcement\apps_taxonomy_guard.py:37:        repo_path = Path(repo_root)
agentic_core\L0_routing\enforcement\boot_sequence.py:24:sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
agentic_core\L0_routing\enforcement\mutation_prohibition.py:6:Persistent writes include: Path.write_text/write_bytes, json.dump to file,
agentic_core\L0_routing\enforcement\mutation_prohibition.py:7:os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').
agentic_core\L0_routing\enforcement\mutation_prohibition.py:52:        op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
agentic_core\L0_routing\enforcement\mutation_prohibition.py:83:def safe_write_text(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:91:    """Guarded Path.write_text replacement."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:92:    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:93:    Path(filepath).write_text(content, encoding=encoding)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:96:def safe_write_bytes(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:103:    """Guarded Path.write_bytes replacement."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:104:    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:105:    Path(filepath).write_bytes(data)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:118:    """Guarded json.dump-to-file replacement."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:119:    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:120:    with open(filepath, "w", encoding="utf-8") as f:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:121:        json.dump(obj, f, indent=indent, sort_keys=sort_keys, **kwargs)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:131:    """Guarded shutil.move replacement."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:132:    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:133:    shutil.move(str(src), str(dst))
agentic_core\L0_routing\enforcement\mutation_prohibition.py:142:    """Guarded shutil.rmtree replacement."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:143:    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:144:    shutil.rmtree(str(target))
agentic_core\L0_routing\enforcement\mutation_prohibition.py:153:    """Guarded os.remove replacement."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:154:    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:155:    os.remove(filepath)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:178:    """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
agentic_core\L0_routing\enforcement\mutation_prohibition.py:179:    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:180:    return open(filepath, mode, encoding=encoding)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:213:    "safe_write_bytes",
agentic_core\L0_routing\enforcement\mutation_prohibition.py:214:    "safe_write_text",
agentic_core\L0_routing\engines\assembly_stage.py:27:    return json.dumps(
agentic_core\L0_routing\engines\path_router.py:13:class Path(Enum):
agentic_core\L0_routing\meta_control\config_store_types.py:30:    return json.dumps(obj, sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\meta_control\meta_apply.py:110:    spec_json = json.dumps(change_spec, sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\meta_control\meta_apply.py:146:    content = json.dumps(data, sort_keys=True, indent=2, separators=(",", ": "))
agentic_core\L0_routing\meta_control\meta_apply.py:147:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\meta_control\meta_apply.py:148:    tmp.write_text(content, encoding="utf-8")
agentic_core\L0_routing\meta_control\meta_learning_bus.py:39:        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\reasoning\RootCustomsAgent.py:61:            with open(file_path, encoding="utf-8") as f:
agentic_core\L0_routing\reasoning\RootCustomsAgent.py:171:            with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\reasoning\RootCustomsAgent.py:564:            shutil.move(str(source), str(target_file))
agentic_core\L0_routing\reasoning\RootCustomsAgent.py:750:        project_root=Path(args.project_root) if args.project_root else None,
agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py:410:                        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py:411:                        py_file.write_text(new_content, encoding="utf-8")
agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py:497:            dir_path = Path(dirpath)
agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:18:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:118:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:119:            file_path.write_text(source, encoding="utf-8")
agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:136:    with open(discovery_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:15:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:20:with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:127:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:128:            agent_path.write_text(new_content, encoding="utf-8")
agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:14:with open("agent_discovery_full.json") as f:
agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:30:    agent_path = Path(agent["path"])
agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:112:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:113:            agent_path.write_text(content, encoding="utf-8")
agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:13:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:16:with open(discovery_file, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:146:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:147:            agent_path.write_text(content, encoding="utf-8")
agentic_core\L0_routing\scripts\agent_analysis_config.py:299:    project_root = Path(__file__).parents[3]
agentic_core\L0_routing\scripts\agent_analysis_config.py:307:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\agent_analysis_config.py:308:    report_path.write_text(report, encoding="utf-8")
agentic_core\L0_routing\scripts\agent_capability_supplement_util.py:42:with open(REPORT_PATH, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\agent_capability_supplement_util.py:406:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\agent_capability_supplement_util.py:407:    report_path.write_text(md_report, encoding="utf-8")
agentic_core\L0_routing\scripts\agent_validation_util.py:17:project_root = Path(__file__).parent.parent.parent
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:25:        if not Path(d).exists():
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:27:        for py_file in Path(d).rglob("*.py"):
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:48:        if not Path(d).exists():
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:50:        for py_file in Path(d).rglob("*.py"):
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:85:        if not Path(d).exists():
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:87:        for py_file in Path(d).rglob("*.py"):
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:110:        if not Path(d).exists():
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:112:        for py_file in Path(d).rglob("*.py"):
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:192:        folder = Path(f).parent.name
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:193:        by_folder[folder].append(Path(f).name)
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:208:            Path(f).unlink()
agentic_core\L0_routing\scripts\aggressive_dedup_util.py:212:            print(f"  ✗ Failed: {Path(f).name}: {e}")
agentic_core\L0_routing\scripts\align_tests_structure_util.py:42:        with open(init_file, "w") as f:
agentic_core\L0_routing\scripts\align_tests_structure_util.py:49:        with open(gitkeep, "w") as f:
agentic_core\L0_routing\scripts\archive_duplicates_util.py:8:PROJECT_ROOT = Path(__file__).parent.parent.parent
agentic_core\L0_routing\scripts\archive_duplicates_util.py:48:                shutil.move(str(source_path), str(dest_path))
agentic_core\L0_routing\scripts\archive_duplicate_tests_util.py:18:    test_dir = Path(__file__).parent.parent / TESTS_DIR
agentic_core\L0_routing\scripts\archive_duplicate_tests_util.py:44:    archive_dir = Path(__file__).parent.parent / ARCHIVES_DIR / f"duplicate_tests_{timestamp}"
agentic_core\L0_routing\scripts\archive_duplicate_tests_util.py:58:                shutil.move(str(dup), str(archive_target))
agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py:15:TARGET_DIR = Path("agentic_core")
agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py:96:        with open(file_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py:138:    with open(file_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py:157:                path = Path(root) / file
agentic_core\L0_routing\scripts\bloat_analysis_util.py:9:ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:16:current_file: Any = Path(__file__).resolve()
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:54:    with open(audit_log, "a") as f:
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:69:    with open(output_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:102:                    shutil.move(str(file_path), str(dest_path))
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:16:PROJECT_ROOT = Path(__file__).resolve().parents[1]
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:24:    with open(DISCOVERY_PATH) as f:
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:61:                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:62:                file_path.write_text(new_content, encoding="utf-8")
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:79:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:80:        file_path.write_text(new_content, encoding="utf-8")
agentic_core\L0_routing\scripts\check_duplicate_filenames_util.py:8:    project_root = Path(__file__).parent.parent.parent
agentic_core\L0_routing\scripts\check_from_utils_duplicates_util.py:7:project_root = Path(__file__).parent.parent.parent
agentic_core\L0_routing\scripts\check_protected_files_util.py:50:        commit_msg_file = Path(".git/COMMIT_EDITMSG")
agentic_core\L0_routing\scripts\check_protected_files_util.py:66:        protected_path = Path(protected).as_posix()
agentic_core\L0_routing\scripts\check_protected_files_util.py:68:            staged_path = Path(staged).as_posix()
agentic_core\L0_routing\scripts\check_rglob_usage_util.py:119:    script_dir = Path(__file__).parent
agentic_core\L0_routing\scripts\check_sovereign_base_util.py:6:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\check_sovereign_base_util.py:7:with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
agentic_core\L0_routing\scripts\check_syntax_util.py:8:sys.path.insert(0, str(Path(__file__).parent.parent))
agentic_core\L0_routing\scripts\check_syntax_util.py:14:    project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\chunk_type.py:254:    target_path: Any = Path(args.target).resolve()
agentic_core\L0_routing\scripts\class_info.py:22:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\class_info.py:80:        with open(file_path, "rb") as f:
agentic_core\L0_routing\scripts\class_info.py:92:        with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\scripts\class_info.py:101:        with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\scripts\class_info.py:121:        with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\scripts\class_info.py:459:            with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\scripts\class_info.py:507:            file_path = Path(root) / file_name
agentic_core\L0_routing\scripts\class_info.py:699:    with open(report_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\class_info.py:733:    with open(json_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\class_info.py:734:        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\class_info.py:735:        json.dump(json_data, f, indent=2)
agentic_core\L0_routing\scripts\code_entity.py:252:        for py_file in Path(dir_path).rglob("*.py"):
agentic_core\L0_routing\scripts\code_entity.py:339:    archives_root = Path("archives")
agentic_core\L0_routing\scripts\code_entity.py:447:        report.append(f"\n  [{analysis.unique_score:.0f}%] {Path(analysis.path).name}")
agentic_core\L0_routing\scripts\code_entity.py:471:        report.append(f"\n  [{analysis.unique_score:.0f}%] {Path(analysis.path).name}")
agentic_core\L0_routing\scripts\code_entity.py:492:        report.append(f"\n  [{analysis.unique_score:.0f}%] {Path(analysis.path).name}")
agentic_core\L0_routing\scripts\code_entity.py:531:        filename = Path(analysis.path).name
agentic_core\L0_routing\scripts\code_entity.py:539:    report_path = Path("docs/ARCHIVE_ANALYSIS_REPORT.md")
agentic_core\L0_routing\scripts\code_entity.py:540:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\code_entity.py:541:    report_path.write_text(report_text, encoding="utf-8")
agentic_core\L0_routing\scripts\collision_resolver.py:123:            target_path = Path(target)
agentic_core\L0_routing\scripts\collision_resolver.py:165:            target_path = Path(target)
agentic_core\L0_routing\scripts\collision_resolver.py:208:    root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\colors.py:151:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\colors.py:152:        state_path.write_text(_json.dumps(_runtime_state, indent=2, default=str), encoding="utf-8")
agentic_core\L0_routing\scripts\colors.py:294:current_file_path = Path(__file__).resolve()
agentic_core\L0_routing\scripts\compare_archive_to_current_util.py:21:        for f in Path(d).rglob(filename):
agentic_core\L0_routing\scripts\compare_archive_to_current_util.py:85:        archive_file = Path(archive_path)
agentic_core\L0_routing\scripts\compare_archive_to_current_util.py:150:        print(f"\n  [SKIP] {Path(item['archive']).name}")
agentic_core\L0_routing\scripts\compare_autonomy_guardian_files_util.py:6:file1 = Path("agentic_core/L5_safety/validators/AutonomyGuardianAgent.py")
agentic_core\L0_routing\scripts\compare_autonomy_guardian_files_util.py:7:file2 = Path("agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent.py")
agentic_core\L0_routing\scripts\compare_ui_components_util.py:83:    mono_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard_backup.html")
agentic_core\L0_routing\scripts\compare_ui_components_util.py:88:    with open(mono_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\compare_ui_components_util.py:92:    mod_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
agentic_core\L0_routing\scripts\compare_ui_components_util.py:97:    with open(mod_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\compare_ui_components_util.py:107:        js_path = Path(js_file)
agentic_core\L0_routing\scripts\compare_ui_components_util.py:109:            with open(js_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\comprehensive_archive_check_util.py:6:PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\scripts\core_synthesis_executor.py:23:        self.base_path = Path("agentic_core/base_agents")
agentic_core\L0_routing\scripts\core_synthesis_executor.py:24:        self.utils_path = Path("agentic_core/utils")
agentic_core\L0_routing\scripts\core_synthesis_executor.py:25:        self.archives_path = Path("archives/phase20_synthesis")
agentic_core\L0_routing\scripts\core_synthesis_executor.py:31:            with open("core_refinery_analysis_results.json") as f:
agentic_core\L0_routing\scripts\core_synthesis_executor.py:95:                archive_dest = self.archives_path / Path(file_info["file_path"])
agentic_core\L0_routing\scripts\core_synthesis_executor.py:100:                    shutil.move(str(file_path), str(archive_dest))
agentic_core\L0_routing\scripts\core_synthesis_executor.py:246:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\core_synthesis_executor.py:247:            target_path.write_text(target_content, encoding="utf-8")
agentic_core\L0_routing\scripts\core_synthesis_executor.py:281:                shutil.move(str(file_path), str(dest))
agentic_core\L0_routing\scripts\core_synthesis_executor.py:361:        with open("PHASE20_SYNTHESIS_EXECUTION_REPORT.md", "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\count_territories_util.py:8:with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\coverage.py:24:sys.path.insert(0, str(Path(__file__).parent.parent))
agentic_core\L0_routing\scripts\coverage.py:41:        l0_modules = list(get_python_files(Path(L0_MAINTENANCE_DIR)))
agentic_core\L0_routing\scripts\coverage.py:66:        file_path = Path(violation["path"])
agentic_core\L0_routing\scripts\c_c_measurement.py:25:        self.project_root = project_root or Path(__file__).parent.parent.parent
agentic_core\L0_routing\scripts\c_c_measurement.py:179:            with open(output_file, "w") as f:
agentic_core\L0_routing\scripts\c_c_measurement.py:180:                assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\c_c_measurement.py:181:                json.dump(report, f, indent=2)
agentic_core\L0_routing\scripts\debris_hunter.py:54:                            self.debris_found.append(Path(dirpath) / f)
agentic_core\L0_routing\scripts\debris_hunter.py:86:                os.remove(path)
agentic_core\L0_routing\scripts\debris_hunter.py:99:    root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\debug_drilldown_util.py:7:html = Path("reports/autonomy_dashboard.html").read_text(encoding="utf-8")
agentic_core\L0_routing\scripts\debug_invocation_pipeline_util.py:8:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\debug_invocation_pipeline_util.py:11:registry = json.load(open(PROJECT_ROOT / AGENT_DISCOVERY_JSON))
agentic_core\L0_routing\scripts\debug_target_mismatch_util.py:7:dashboard_path = Path("reports/autonomy_dashboard.html")
agentic_core\L0_routing\scripts\delete_duplicates_util.py:17:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\demo_cli_functionality_util.py:11:project_root = Path(__file__).parent
agentic_core\L0_routing\scripts\diagnose_syntax_util.py:45:    root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\disposition.py:48:        self.base_path = Path(base_path)
agentic_core\L0_routing\scripts\disposition.py:437:    with open("CORE_REFINERY_ANALYSIS.md", "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\disposition.py:458:    with open("core_refinery_analysis_results.json", "w") as f:
agentic_core\L0_routing\scripts\disposition.py:459:        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\disposition.py:460:        json.dump(detailed_results, f, indent=2)
agentic_core\L0_routing\scripts\drift.py:120:                with open(full_path, encoding="utf-8") as source:
agentic_core\L0_routing\scripts\emoji_fixer.py:14:    AGENTIC_CORE_DIR = Path("agentic_core")
agentic_core\L0_routing\scripts\emoji_fixer.py:15:    APPS_SHARED_DIR = Path("apps_shared")
agentic_core\L0_routing\scripts\emoji_fixer.py:47:        with open(file_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\emoji_fixer.py:53:            with open(file_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\execute_safe_deletion_util.py:15:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\execute_ssot.py:137:    cur = Path(start or __file__).resolve()
agentic_core\L0_routing\scripts\execute_ssot.py:426:            with open(fp, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\execute_ssot.py:1206:                assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:1207:                json.dump(self.state, tf, indent=2, default=str, ensure_ascii=False)
agentic_core\L0_routing\scripts\execute_ssot.py:1224:                    os.remove(temp_name)
agentic_core\L0_routing\scripts\execute_ssot.py:1273:                            full_path = Path(raw_path)
agentic_core\L0_routing\scripts\execute_ssot.py:1276:                            rel_path = Path(raw_path)
agentic_core\L0_routing\scripts\execute_ssot.py:1320:                            full_path = Path(raw_path)
agentic_core\L0_routing\scripts\execute_ssot.py:1323:                            rel_path = Path(raw_path)
agentic_core\L0_routing\scripts\execute_ssot.py:1357:                    assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:1358:                    json.dump(discovery_data, tf, indent=2, ensure_ascii=False)
agentic_core\L0_routing\scripts\execute_ssot.py:1369:                    os.remove(temp_name)
agentic_core\L0_routing\scripts\execute_ssot.py:1428:        quality_report = validator.check_file_quality(Path(fpath))
agentic_core\L0_routing\scripts\execute_ssot.py:2212:    _safe_print(json.dumps(detailed_cert, indent=2))
agentic_core\L0_routing\scripts\execute_ssot.py:2259:        with open(json_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\execute_ssot.py:2260:            assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:2261:            json.dump(detailed_cert, f, indent=2, default=str, ensure_ascii=False)
agentic_core\L0_routing\scripts\execute_ssot.py:2264:        with open(md_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\execute_ssot.py:3204:                file_path = Path(root) / file
agentic_core\L0_routing\scripts\execute_ssot.py:3206:                    with open(file_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\execute_ssot_entrypoint.py:25:    cur = Path(__file__).resolve()
agentic_core\L0_routing\scripts\extract_agent_duplicates_util.py:65:                "agent_name": Path(canonical).stem,
agentic_core\L0_routing\scripts\extract_net.py:16:    source_dir: Any = Path("archives/legacy_lic")
agentic_core\L0_routing\scripts\extract_net.py:17:    staging_dir: Any = Path("archive_code")
agentic_core\L0_routing\scripts\extract_net.py:20:        shutil.rmtree(staging_dir)
agentic_core\L0_routing\scripts\extract_net.py:32:            shutil.copy2(py_file, dest_path)
agentic_core\L0_routing\scripts\extract_unique_content_util.py:17:        for py_file in Path(dir_path).rglob("*.py"):
agentic_core\L0_routing\scripts\extract_unique_content_util.py:173:        file_path = Path(archive_path)
agentic_core\L0_routing\scripts\extract_unique_content_util.py:233:        print(f"\n  {Path(item['source']).name} -> {item['target']}/")
agentic_core\L0_routing\scripts\extract_unique_content_util.py:240:        print(f"\n  {Path(item['source']).name} -> {item['target']}/")
agentic_core\L0_routing\scripts\extract_unique_content_util.py:246:        print(f"  {Path(item['source']).name} - exists: {item['existing'][:3]}")
agentic_core\L0_routing\scripts\extract_unique_content_util.py:257:        src = Path(item["source"])
agentic_core\L0_routing\scripts\extract_unique_content_util.py:258:        target_dir = Path(item["target"])
agentic_core\L0_routing\scripts\extract_unique_content_util.py:270:            shutil.copy2(str(src), str(dst))
agentic_core\L0_routing\scripts\extract_unique_content_util.py:278:        src = Path(item["source"])
agentic_core\L0_routing\scripts\extract_unique_content_util.py:279:        target_dir = Path(item["target"])
agentic_core\L0_routing\scripts\extract_unique_content_util.py:285:            shutil.copy2(str(src), str(dst))
agentic_core\L0_routing\scripts\file_analysis.py:232:        for py_file in Path(dir_path).rglob("*.py"):
agentic_core\L0_routing\scripts\file_analysis.py:300:        path = Path(archive_path)
agentic_core\L0_routing\scripts\file_analysis.py:391:        print(f"    - {Path(r['path']).name} [{r['analysis'].domain}]")
agentic_core\L0_routing\scripts\file_analysis.py:395:        print(f"    - {Path(r['path']).name} -> {Path(r['similar'][0]['file']).name}")
agentic_core\L0_routing\scripts\file_analysis.py:399:        print(f"    - {Path(r['path']).name} (score: {r['similar'][0]['similarity_score']})")
agentic_core\L0_routing\scripts\find_agents_in_low_heal_territories_util.py:8:with open(
agentic_core\L0_routing\scripts\find_agents_in_low_heal_territories_util.py:37:l1_agents = list(get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core/L1_cognition")))
agentic_core\L0_routing\scripts\find_agents_in_low_heal_territories_util.py:44:l3_agents = list(get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core/L3_orchestration")))
agentic_core\L0_routing\scripts\find_agents_in_low_heal_territories_util.py:51:all_agents = get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core"))
agentic_core\L0_routing\scripts\find_agents_in_low_heal_territories_util.py:57:        print(f"  ❌ {agent.relative_to(Path('C:/Git/Agentic-Workflow'))}")
agentic_core\L0_routing\scripts\find_base_class_agents_util.py:7:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\find_base_class_agents_util.py:10:with open(discovery_file, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\find_corrupted_files_util.py:24:    safe_write_text,
agentic_core\L0_routing\scripts\find_corrupted_files_util.py:60:        root_path = Path(root_dir)
agentic_core\L0_routing\scripts\find_corrupted_files_util.py:87:                                safe_write_text(py_file, clean, layer="L0", encoding="utf-8")
agentic_core\L0_routing\scripts\find_infrastructure_target_issue_util.py:7:dashboard_path = Path("reports/autonomy_dashboard.html")
agentic_core\L0_routing\scripts\find_low_heal_territories_util.py:7:with open(
agentic_core\L0_routing\scripts\find_low_typed_documented_util.py:7:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\find_low_typed_documented_util.py:9:with open(PROJECT_ROOT / "agent_discovery_full.json", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\find_missing_agents_util.py:8:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\find_missing_agents_util.py:11:with open(DISCOVERY_PATH, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\find_missing_invocations_util.py:10:with open("agent_discovery_full.json") as f:
agentic_core\L0_routing\scripts\find_missing_invocation_util.py:7:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\find_non_hardened_l0_util.py:7:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\find_non_hardened_l0_util.py:9:with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\find_open_heal_invocations_util.py:11:with open("agent_discovery_full.json") as f:
agentic_core\L0_routing\scripts\find_real_duplicates_v2_util.py:98:    with open(output_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\find_remaining_missing_heal_util.py:9:sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
agentic_core\L0_routing\scripts\find_remaining_missing_heal_util.py:14:with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\fission_executor_util.py:50:            with open(module_file, "w", encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\scripts\fission_executor_util.py:73:        shutil.copy2(file_path, f"{backup_path}.tmp")
agentic_core\L0_routing\scripts\fission_executor_util.py:75:        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py:21:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py:58:                shutil.move(str(py_file), str(target))
agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py:67:            dir_path: Any = Path(root) / dir_name
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:100:    with path.open("rb") as f:
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:309:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:310:    tmp.write_text(data, encoding="utf-8")
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:475:    payload = json.dumps(output, indent=2)
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:495:        outp = Path(args.out) if args.out else None
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:500:        print(json.dumps({"fatal_error": str(e)}))
agentic_core\L0_routing\scripts\full_agent_discovery.py:122:    with path.open("rb") as f:
agentic_core\L0_routing\scripts\full_agent_discovery.py:638:            path = Path(args.inspect)
agentic_core\L0_routing\scripts\full_agent_discovery.py:645:                json.dumps(
agentic_core\L0_routing\scripts\full_agent_discovery.py:660:            print(json.dumps(agents, indent=2, default=str))
agentic_core\L0_routing\scripts\full_agent_discovery.py:671:            print(json.dumps(summary, indent=2, default=str))
agentic_core\L0_routing\scripts\gatekeeper_lock_util.py:48:    if commit_msg_file and Path(commit_msg_file).exists():
agentic_core\L0_routing\scripts\gatekeeper_lock_util.py:49:        return Path(commit_msg_file).read_text(encoding="utf-8")
agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:35:PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:53:    with open(YAML_CONFIG, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:66:        with open(PYTHON_OUTPUT, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:399:    with open(PYTHON_OUTPUT, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:413:    with open(JS_OUTPUT, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\handler.py:13:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\hardened_anti_pattern_visitor.py:10:PROJECT_ROOT = Path(__file__).resolve().parent.parent
agentic_core\L0_routing\scripts\heal_schema_visitor.py:139:    root = Path(__file__).parent.parent.parent / args.path
agentic_core\L0_routing\scripts\heal_schema_visitor.py:153:                Path(v["file"]).relative_to(root.parent)
agentic_core\L0_routing\scripts\heal_schema_visitor.py:154:                if root.parent in Path(v["file"]).parents
agentic_core\L0_routing\scripts\identify_agents_without_tests_util.py:11:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\identify_agents_without_tests_util.py:14:with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\identify_low_quality_agents_util.py:11:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\identify_low_quality_agents_util.py:30:    with open(DISCOVERY_FILE, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\investigate_overlaps_util.py:5:PROJECT_ROOT = Path(__file__).parent.parent.parent
agentic_core\L0_routing\scripts\investigate_overlaps_util.py:28:                    found_files.append(Path(root) / f)
agentic_core\L0_routing\scripts\investigate_sovereign_base_util.py:6:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\investigate_sovereign_base_util.py:7:with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
agentic_core\L0_routing\scripts\layer_summary_util.py:8:data = json.load(open(AGENT_DISCOVERY_JSON))
agentic_core\L0_routing\scripts\list_layer_agents_util.py:18:data = json.load(open(AGENT_DISCOVERY_JSON))
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:18:    Path(__file__).resolve().parents[3]
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:161:                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:162:                init_path.write_text(generate_init_content(l1, l2), encoding="utf-8")
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:171:                        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:172:                        d3_init.write_text(generate_init_content(l1, l2, depth3.name), encoding="utf-8")
agentic_core\L0_routing\scripts\root_hygiene_util.py:58:                    shutil.move(str(item), str(target))
agentic_core\L0_routing\scripts\root_hygiene_util.py:70:                    shutil.rmtree(target)  # Force overwrite logic for dirs
agentic_core\L0_routing\scripts\root_hygiene_util.py:72:                shutil.move(str(item), str(target))
agentic_core\L0_routing\scripts\root_hygiene_util.py:93:            shutil.rmtree(reports_cov)
agentic_core\L0_routing\scripts\root_hygiene_util.py:97:        shutil.move(str(cov_html), str(reports_cov))
agentic_core\L0_routing\scripts\root_hygiene_util.py:111:        shutil.move(str(purge_script), str(target))
agentic_core\L0_routing\scripts\run_all_guardians.py:304:        return _json.dumps(package.to_dict(), sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\scripts\run_guardian_architecture_governance.py:108:                result.append(Path(dirpath) / fname)
agentic_core\L0_routing\scripts\run_guardian_classification_compliance.py:106:                    result.append(Path(dirpath) / fname)
agentic_core\L0_routing\scripts\run_guardian_contract_integrity.py:7:3. Do not emit raw dict/json.dumps without GuardianResult
agentic_core\L0_routing\scripts\run_guardian_contract_integrity.py:80:    Find json.dumps calls that are NOT on a GuardianResult method.
agentic_core\L0_routing\scripts\run_guardian_contract_integrity.py:86:            # json.dumps(...)
agentic_core\L0_routing\scripts\run_guardian_hygiene.py:99:            current = Path(dirpath_str)
agentic_core\L0_routing\scripts\run_guardian_hygiene.py:123:            current = Path(dirpath_str)
agentic_core\L0_routing\scripts\run_guardian_manifest.py:48:    with open(file_path, "rb") as f:
agentic_core\L0_routing\scripts\run_hierarchy_agent_dry_run_util.py:17:project_root = Path(__file__).resolve().parents[1]
agentic_core\L0_routing\scripts\run_hierarchy_healer_dry_run_util.py:15:project_root = Path(__file__).resolve().parents[1]
agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py:12:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py:48:            current_dir = Path(dirpath)
agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py:77:            current_dir = Path(dirpath)
agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py:115:                shutil.rmtree(path)
agentic_core\L0_routing\scripts\run_hygiene_naming_audit_util.py:11:root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\run_hygiene_naming_audit_util.py:21:    root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\run_naming_law_check_util.py:8:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\run_naming_scan_util.py:10:project_root = Path(__file__).resolve().parents[1]
agentic_core\L0_routing\scripts\run_sovereign_compliance_audit_util.py:13:project_root = Path(__file__).resolve().parents[3]
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:36:PROJECT_ROOT = Path(__file__).resolve().parents[1]
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:150:    with open(DISCOVERY_JSON, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:348:    with open(report_path, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:349:        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:350:        json.dump(report, f, indent=2)
agentic_core\L0_routing\scripts\sovereign_lockdown_check_util.py:36:        project_root = Path(__file__).resolve().parent.parent.parent
agentic_core\L0_routing\scripts\sovereign_precommit_no_hardcoded_util.py:33:    normalized_path: Any = str(Path(filepath)).replace("\\", "/")
agentic_core\L0_routing\scripts\sovereign_precommit_no_hardcoded_util.py:37:        with open(filepath, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\sovereign_precommit_no_raw_prompts_util.py:30:    normalized_path: Any = str(Path(filepath)).replace("\\", "/")
agentic_core\L0_routing\scripts\sovereign_precommit_no_raw_prompts_util.py:34:        with open(filepath, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\ssot_audit_util.py:28:ROOT = Path(".")
agentic_core\L0_routing\scripts\ssot_audit_util.py:146:        print(f"  {v['file_layer']} imports {v['import_layer']}: {Path(v['file']).name}")
agentic_core\L0_routing\scripts\ssot_cli.py:28:REPO = Path(__file__).parent.parent.resolve()
agentic_core\L0_routing\scripts\ssot_cli.py:162:            output_path = Path(args.output)
agentic_core\L0_routing\scripts\ssot_cli.py:167:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\ssot_cli.py:168:        output_path.write_text(report.to_markdown(), encoding="utf-8")
agentic_core\L0_routing\scripts\ssot_cli.py:185:        print("\n" + json.dumps(json_data, indent=2))
agentic_core\L0_routing\scripts\validate_base_agents_util.py:24:data = json.load(open("agent_discovery_full.json"))
agentic_core\L0_routing\scripts\validate_drilldown_util.py:48:    dashboard_path = Path("reports/autonomy_dashboard.html")
agentic_core\L0_routing\scripts\validate_table2_data_util.py:34:    dashboard_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
agentic_core\L0_routing\scripts\validate_table2_data_util.py:127:    gen_script = Path("agentic_core/L6_observability/dashboards/generate_dashboard.py")
agentic_core\L0_routing\scripts\verify_agent_status_util.py:18:PROJECT_ROOT = Path(__file__).resolve().parents[1]
agentic_core\L0_routing\scripts\verify_all_checkpoint_files_util.py:6:PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\scripts\verify_all_checkpoint_files_util.py:38:    filename = Path(file_path).name
agentic_core\L0_routing\scripts\verify_base_agent_names_util.py:7:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\verify_healing_metrics_util.py:9:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\verify_healing_metrics_util.py:21:    with open(DISCOVERY_FILE, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\verify_health_calculation_util.py:10:dashboard_path = Path("reports/autonomy_dashboard.html")
agentic_core\L0_routing\scripts\verify_heal_invocation_util.py:6:data = json.load(open("agent_discovery_full.json"))
agentic_core\L0_routing\scripts\verify_intentional_variants_util.py:18:project_root = Path(__file__).parent.parent
agentic_core\L0_routing\scripts\verify_intentional_variants_util.py:26:        with open(file_path, encoding="utf-8") as f:
agentic_core\L0_routing\scripts\verify_intentional_variants_util.py:343:    with open(output_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\verify_manifest_cleanliness_util.py:24:manifest_path = Path("agent_discovery_full.json")
agentic_core\L0_routing\scripts\verify_manifest_cleanliness_util.py:29:with open(manifest_path) as f:
agentic_core\L0_routing\scripts\verify_manifest_util.py:96:    report_path = Path(args.report)
agentic_core\L0_routing\scripts\verify_manifest_util.py:102:        with open(report_path) as f:
agentic_core\L0_routing\scripts\verify_mro_util.py:14:PROJECT_ROOT = Path(__file__).resolve().parent.parent
agentic_core\L0_routing\scripts\verify_row_order_util.py:7:with open("agentic_core/L6_observability/dashboards/data/dashboard_data.js", encoding="utf-8") as f:
agentic_core\L0_routing\scripts\verify_territory_counts_util.py:10:with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f:
agentic_core\L0_routing\types\guardian_contract.py:583:        payload = json.dumps(result_dict, default=str)
agentic_core\L0_routing\types\guardian_contract.py:622:    s = str(PurePosixPath(s))
agentic_core\L0_routing\types\guardian_contract.py:810:        canonical_bytes = json.dumps(
agentic_core\L0_routing\types\guardian_contract.py:876:        canonical = json.dumps(d, sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\types\guardian_contract.py:883:        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
agentic_core\L0_routing\types\guardian_contract.py:933:    output_dir = Path(output_dir)
agentic_core\L0_routing\types\guardian_contract.py:936:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\guardian_contract.py:937:    out_path.write_text(result.to_json(), encoding="utf-8")
agentic_core\L0_routing\types\guardian_contract.py:943:    with open(path, encoding="utf-8") as f:
agentic_core\L0_routing\types\guardian_contract.py:1045:        payload_seed = json.dumps(
agentic_core\L0_routing\types\guardian_contract_types.py:583:        payload = json.dumps(result_dict, default=str)
agentic_core\L0_routing\types\guardian_contract_types.py:622:    s = str(PurePosixPath(s))
agentic_core\L0_routing\types\guardian_contract_types.py:810:        canonical_bytes = json.dumps(
agentic_core\L0_routing\types\guardian_contract_types.py:876:        canonical = json.dumps(d, sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\types\guardian_contract_types.py:883:        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
agentic_core\L0_routing\types\guardian_contract_types.py:933:    output_dir = Path(output_dir)
agentic_core\L0_routing\types\guardian_contract_types.py:936:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\guardian_contract_types.py:937:    out_path.write_text(result.to_json(), encoding="utf-8")
agentic_core\L0_routing\types\guardian_contract_types.py:943:    with open(path, encoding="utf-8") as f:
agentic_core\L0_routing\types\guardian_contract_types.py:1045:        payload_seed = json.dumps(
agentic_core\L0_routing\types\integration_contract.py:75:        return json.dumps(self.to_ordered_dict(), sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\types\integration_contract.py:80:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\integration_contract.py:81:        path.write_text(self.to_json(), encoding="utf-8")
agentic_core\L0_routing\types\integration_contract_types.py:75:        return json.dumps(self.to_ordered_dict(), sort_keys=True, separators=(",", ":"))
agentic_core\L0_routing\types\integration_contract_types.py:80:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\integration_contract_types.py:81:        path.write_text(self.to_json(), encoding="utf-8")
agentic_core\L0_routing\types\routing_artifact_types.py:44:class RoutePath(str, Enum):
agentic_core\L0_routing\types\routing_contracts.py:606:        out_dir = Path(artifacts_dir)
agentic_core\L0_routing\types\routing_contracts.py:609:        with out_path.open("a", encoding="utf-8") as fh:
agentic_core\L0_routing\types\routing_contracts.py:611:                fh.write(json.dumps(event, sort_keys=True, default=str) + "\n")
agentic_core\L0_routing\types\routing_contracts.py:628:    return json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
agentic_core\L0_routing\utils\add_test_coverage_util.py:70:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\add_test_coverage_util.py:71:    filepath.write_text(new_content, encoding="utf-8")
agentic_core\L0_routing\utils\add_test_coverage_util.py:77:    agents = json.load(open(AGENT_DISCOVERY_JSON))
agentic_core\L0_routing\utils\add_test_coverage_util.py:82:        p = Path(a["path"])
agentic_core\L0_routing\utils\add_test_coverage_util.py:107:        p = Path(a["path"])
agentic_core\L0_routing\utils\add_test_coverage_util.py:432:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\add_test_coverage_util.py:433:    filepath.write_text("\n".join(lines), encoding="utf-8")
agentic_core\L0_routing\utils\add_test_coverage_util.py:456:        filepath = Path(path)
agentic_core\L0_routing\utils\complexity_visitor_util.py:50:sys.path.insert(0, str(Path(__file__).parent))
agentic_core\L0_routing\utils\complexity_visitor_util.py:52:sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core" / "L0_routing" / "scripts"))
agentic_core\L0_routing\utils\complexity_visitor_util.py:143:    Path(__file__).resolve().parents[3]
agentic_core\L0_routing\utils\complexity_visitor_util.py:451:    content_str = json.dumps(agents, sort_keys=True)
agentic_core\L0_routing\utils\complexity_visitor_util.py:768:    project_root = Path(__file__).parent.parent
agentic_core\L0_routing\utils\complexity_visitor_util.py:1289:                    os.remove(stale_path)
agentic_core\L0_routing\utils\complexity_visitor_util.py:1667:        json_text = json.dumps(agents, indent=2)
agentic_core\L0_routing\utils\complexity_visitor_util.py:1668:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\complexity_visitor_util.py:1669:        tmp_json.write_text(json_text, encoding="utf-8")
agentic_core\L0_routing\utils\complexity_visitor_util.py:1689:        manifest_text = json.dumps(manifest, indent=2)
agentic_core\L0_routing\utils\complexity_visitor_util.py:1690:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\complexity_visitor_util.py:1691:        tmp_manifest.write_text(manifest_text, encoding="utf-8")
agentic_core\L0_routing\utils\core_integrity_util.py:30:    CORE_PATH: Final[Path] = Path(__file__).parent.parent.parent.absolute() / "base_agents"
agentic_core\L0_routing\utils\core_integrity_util.py:31:    GOLDEN_SEAL_FILE: Final[Path] = Path(__file__).parent.absolute() / ".core_golden_seal"
agentic_core\L0_routing\utils\core_integrity_util.py:48:            alt_path = Path(__file__).parent.parent.parent / "agentic_core" / "base_agents"
agentic_core\L0_routing\utils\core_integrity_util.py:70:                    shutil.rmtree(pycache)
agentic_core\L0_routing\utils\core_integrity_util.py:92:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\core_integrity_util.py:93:            cls.GOLDEN_SEAL_FILE.write_text(current_hash)
agentic_core\L0_routing\utils\core_integrity_util.py:151:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\core_integrity_util.py:152:        cls.GOLDEN_SEAL_FILE.write_text(current_hash)
agentic_core\L0_routing\utils\file_utils_util.py:9:raw open()/write() calls.
agentic_core\L0_routing\utils\file_utils_util.py:34:        Path(path).mkdir(parents=True, exist_ok=True)
agentic_core\L0_routing\utils\file_utils_util.py:60:        return Path(path).read_text(encoding=encoding, errors=errors)
agentic_core\L0_routing\utils\file_utils_util.py:79:    path = Path(path)
agentic_core\L0_routing\utils\file_utils_util.py:85:            shutil.copy2(path, backup_path)
agentic_core\L0_routing\utils\file_utils_util.py:95:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\file_utils_util.py:96:        temp_path.write_text(content, encoding=encoding)
agentic_core\L0_routing\utils\file_utils_util.py:123:        path = Path(path)
agentic_core\L0_routing\utils\file_utils_util.py:125:        with open(path, "a", encoding=encoding) as f:
agentic_core\L0_routing\utils\file_utils_util.py:144:    path = Path(path)
agentic_core\L0_routing\utils\file_utils_util.py:153:            shutil.copy2(path, backup_path)
agentic_core\L0_routing\utils\file_utils_util.py:177:    src, dst = Path(src), Path(dst)
agentic_core\L0_routing\utils\file_utils_util.py:187:            shutil.copy2(dst, backup_path)
agentic_core\L0_routing\utils\file_utils_util.py:196:        shutil.move(str(src), str(dst))
agentic_core\L0_routing\utils\file_utils_util.py:214:        return Path(path).stat().st_size
agentic_core\L0_routing\utils\file_utils_util.py:248:    return Path(path)
agentic_core\L0_routing\utils\find_misnamed_agents_util.py:33:    AGENTIC_CORE_DIR = Path("agentic_core")
agentic_core\L0_routing\utils\find_misnamed_agents_util.py:34:    APPS_LIC_DIR = Path("apps_lic")
agentic_core\L0_routing\utils\find_misnamed_agents_util.py:35:    APPS_RG_DIR = Path("apps_rg")
agentic_core\L0_routing\utils\find_misnamed_agents_util.py:36:    APPS_SHARED_DIR = Path("apps_shared")
agentic_core\L0_routing\utils\find_misnamed_agents_util.py:43:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L0_routing\utils\fix_all_tunnels_util.py:18:ROOT: Any = Path(__file__).parent.parent.parent.parent
agentic_core\L0_routing\utils\fix_all_tunnels_util.py:44:                shutil.move(str(py_file), str(target_file))
agentic_core\L0_routing\utils\fix_all_tunnels_util.py:55:            dir_path: Any = Path(root) / name
agentic_core\L0_routing\utils\fix_depth_violations_util.py:50:                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_depth_violations_util.py:51:                stage_init.write_text('"""Stage module."""\n')
agentic_core\L0_routing\utils\fix_depth_violations_util.py:55:                shutil.move(str(py_file), str(target))
agentic_core\L0_routing\utils\fix_mission_runner_util.py:11:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\fix_mission_runner_util.py:18:    with open(mission_runner, encoding="utf-8") as f:
agentic_core\L0_routing\utils\fix_mission_runner_util.py:40:    with open(mission_runner, "w", encoding="utf-8") as f:
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:12:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:24:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:25:        (stage / "__init__.py").write_text('"""Stage module."""\n')
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:34:                    shutil.move(str(f), str(target))
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:41:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:42:        (stage / "__init__.py").write_text('"""Stage module."""\n')
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:51:                    shutil.move(str(f), str(target))
agentic_core\L0_routing\utils\force_annexation_util.py:17:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\force_annexation_util.py:53:                shutil.move(str(item), str(target_item))
agentic_core\L0_routing\utils\force_annexation_util.py:60:                shutil.rmtree(old_path)
agentic_core\L0_routing\utils\gravity_audit_util.py:13:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\gravity_audit_util.py:28:            with open(py_file, encoding="utf-8") as f:
agentic_core\L0_routing\utils\json_formatter_util.py:34:        return json.dumps(log_obj)
agentic_core\L0_routing\utils\manifest_guardian_util.py:19:    MANIFEST_PATH = Path("manifest.json")
agentic_core\L0_routing\utils\manifest_guardian_util.py:20:    LOCK_FILE = Path(".manifest.lock")
agentic_core\L0_routing\utils\manifest_guardian_util.py:29:        with open(file_path, "rb") as f:
agentic_core\L0_routing\utils\manifest_guardian_util.py:41:        with open(cls.LOCK_FILE, "w") as f:
agentic_core\L0_routing\utils\manifest_guardian_util.py:64:        with open(cls.LOCK_FILE) as f:
agentic_core\L0_routing\utils\path_utils.py:37:        path = Path(path).resolve()
agentic_core\L0_routing\utils\path_utils.py:38:        project_root = Path(project_root).resolve()
agentic_core\L0_routing\utils\path_utils.py:47:    project_root = Path(project_root).resolve()
agentic_core\L0_routing\utils\project_root.py:25:    current = Path(__file__).resolve()
agentic_core\L0_routing\utils\project_root_util.py:38:    current = Path(start_path).resolve() if start_path else Path.cwd().resolve()
agentic_core\L0_routing\utils\project_root_util.py:61:        current = Path(start_path).resolve() if start_path else Path.cwd().resolve()
agentic_core\L0_routing\utils\project_root_util.py:67:            return Path(*parts[:idx])
agentic_core\L0_routing\utils\scorched_earth_merge_util.py:17:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\scorched_earth_merge_util.py:85:            shutil.move(str(item), str(dest_path))
agentic_core\L0_routing\utils\scorched_earth_merge_util.py:94:                    shutil.rmtree(item)
agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:39:                shutil.move(str(item), str(dest_item))
agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:54:        with open(init_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:73:            with open(py_file, encoding="utf-8") as f:
agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:79:                with open(py_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\utils\sovereign_convergence_util.py:31:                    shutil.move(str(item), str(dest_path / item.name))
agentic_core\L0_routing\utils\sovereign_convergence_util.py:34:                    shutil.move(str(item), str(dest_path / item.name))
agentic_core\L0_routing\utils\sovereign_convergence_util.py:52:            with open(py_file, encoding="utf-8") as f:
agentic_core\L0_routing\utils\sovereign_convergence_util.py:58:                with open(py_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\utils\ssot_discovery_util.py:96:        with open(discovery_path, encoding="utf-8") as f:
agentic_core\L0_routing\utils\structural_fix_util.py:15:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\structural_fix_util.py:34:        with open(agent_logic_file, encoding="utf-8") as f:
agentic_core\L0_routing\utils\structural_fix_util.py:39:            with open(agent_logic_file, "w", encoding="utf-8") as f:
agentic_core\L0_routing\utils\structural_fix_util.py:45:        with open(mission_runner, encoding="utf-8") as f:
agentic_core\L0_routing\utils\structural_fix_util.py:61:        with open(mission_runner, "w", encoding="utf-8") as f:
agentic_core\L0_routing\utils\structural_fix_util.py:71:        shutil.move(str(analysis_file), str(target_file))
agentic_core\L0_routing\utils\structural_fix_util.py:78:        shutil.move(str(verify_file), str(target_file))
agentic_core\L0_routing\utils\structural_fix_util.py:93:            shutil.move(str(src), str(dest))
agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py:14:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py:53:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py:54:    init_file.write_text(content, encoding="utf-8")
agentic_core\L1_cognition\engines\cache_manager.py:314:                serialized = json.dumps(value, default=str)
agentic_core\L1_cognition\engines\codebase_mapper.py:72:                    path_obj = Path(root_path)
agentic_core\L1_cognition\engines\meta_client.py:169:                json.dumps(data)  # Ensure serializable
agentic_core\L1_cognition\engines\meta_client.py:182:        signature_str = json.dumps(signature_data, sort_keys=True)
agentic_core\L1_cognition\engines\meta_client.py:257:                    json.dumps(value),
agentic_core\L1_cognition\engines\pitch_engine.py:98:        return f"\nGenerate a professional outreach email based on the following:\n\nCOMPANY CONTEXT:\n{json.dumps(context, indent=2)}\n\nRELATIONSHIP CONTEXT:\n{json.dumps(relationships, indent=2)}\n\nRequirements:\n- Write a compelling subject line\n- Keep the email concise (150-200 words)\n- Personalize with recent company news or developments\n- Mention mutual connections if available\n- Include a clear call to action\n- Maintain professional but friendly tone\n- Avoid sales-heavy language\n\nFormat the response with the subject line first, followed by the email body.\n"
agentic_core\L1_cognition\engines\reasoning_cache.py:41:        context_str = json.dumps(context, sort_keys=True, default=str)
agentic_core\L1_cognition\engines\reasoning_cache.py:42:        params_str = json.dumps(params, sort_keys=True, default=str)
agentic_core\L1_cognition\engines\reasoning_cache.py:232:        context_str = json.dumps(context, sort_keys=True, default=str)
agentic_core\L1_cognition\reasoning\ASTValidatorAgent.py:403:            file_path = Path(file_path)
agentic_core\L1_cognition\reasoning\StrategicRecommendationAgent.py:57:        self.project_root = Path(project_root) if project_root else Path.cwd()
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:33:    canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
agentic_core\L1_cognition\types\memory_types.py:48:            context_str = json.dumps(self.context, default=str)[:500]
agentic_core\L1_cognition\utils\guardrails.py:124:            value_str = json.dumps(value)
agentic_core\L1_cognition\utils\guardrails.py:435:        sorted_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
agentic_core\L1_cognition\utils\guardrails_util.py:124:            value_str = json.dumps(value)
agentic_core\L1_cognition\utils\guardrails_util.py:435:        sorted_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
agentic_core\L1_cognition\validators\dark_reasoning_visitor_validator.py:105:    for path in get_python_files(Path(target_dir)):
agentic_core\L1_cognition\validators\truth_keeper_validator.py:52:            with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\config\hybrid_retriever_config.py:176:        cache_path = Path("agentic_core/L4_state/memory/.sovereign_local_index.json")
agentic_core\L2_execution\config\hybrid_retriever_config.py:209:                    cache_path = Path("agentic_core/L4_state/memory/.sovereign_local_index.json")
agentic_core\L2_execution\config\hybrid_retriever_config.py:212:                        json.dump({"chunks": chunks}, tf, ensure_ascii=False)
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline.py:67:        data = json.load(open(self.discovery_path))
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline.py:92:            path = Path(agent["path"])
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline.py:143:                path.write_text(new_content, encoding="utf-8")
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline.py:189:            data = json.load(open(self.discovery_path))
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline_enforcer.py:67:        data = json.load(open(self.discovery_path))
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline_enforcer.py:92:            path = Path(agent["path"])
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline_enforcer.py:143:                path.write_text(new_content, encoding="utf-8")
agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline_enforcer.py:189:            data = json.load(open(self.discovery_path))
agentic_core\L2_execution\enforcement\preventative_sandbox.py:8:  Filesystem  — builtins.open (write), pathlib, os.remove/rename
agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp.py:91:                json.dumps(
agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp.py:117:            redis_shield.execute("set", self.roots_key, json.dumps(validated), ex=60 * 60 * 24)
agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp_enforcer.py:91:                json.dumps(
agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp_enforcer.py:117:            redis_shield.execute("set", self.roots_key, json.dumps(validated), ex=60 * 60 * 24)
agentic_core\L2_execution\enforcement\tool_policy_enforcer.py:32:    serialized = json.dumps(args, sort_keys=True, default=str)
agentic_core\L2_execution\engines\action_node_core.py:40:        self.work_dir = Path(work_dir).resolve()
agentic_core\L2_execution\engines\execute_command_executor.py:36:    current_path: Any = Path(__file__).resolve().parent
agentic_core\L2_execution\engines\execute_command_executor.py:41:    _cached_project_root = Path(__file__).resolve().parent
agentic_core\L2_execution\engines\execute_command_executor.py:117:    command_name: Any = Path(command).stem.lower()
agentic_core\L2_execution\engines\execute_command_executor.py:120:            if command_name == Path(allowed).stem.lower():
agentic_core\L2_execution\engines\secure_tools_impl.py:66:        with open(target, "w", encoding="utf-8") as f:
agentic_core\L2_execution\engines\secure_tools_impl.py:88:        with open(target, encoding="utf-8") as f:
agentic_core\L2_execution\engines\tool_intent_executor.py:81:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L2_execution\engines\tool_registry.py:215:                Recommendation += f"   Parameters: {json.dumps(tool.parameters, indent=6)}\n"
agentic_core\L2_execution\engines\validation_orchestrator.py:142:            with open(file_path, "rb") as f:
agentic_core\L2_execution\engines\validation_orchestrator.py:260:            with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\engines\validation_orchestrator.py:296:                trace_id = f"healing:{violation_key}:{Path(file_path).name}:r{round_num}"
agentic_core\L2_execution\healers\classification_compliance_healer.py:117:        parts = Path(rel_path).parts
agentic_core\L2_execution\healers\classification_compliance_healer.py:123:        target_rel = Path(*parts[:2]) / expected_folder / parts[-1]
agentic_core\L2_execution\healers\classification_compliance_healer.py:131:        shutil.move(str(source), str(target))
agentic_core\L2_execution\healers\drift_detection_healer.py:95:                shutil.rmtree(target)
agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py:380:                        source_lines = ast.get_source_segment(open(py_file).read(), node) or ""
agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py:411:                self.redis.set(cache_key, json.dumps(m), ex=86400)  # 24h
agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py:443:                self.redis.set(cache_key, json.dumps(results), ex=3600)  # 1h
agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py:458:        print(f"   [EXECUTE] Invoking {meta['method']} from {Path(meta['path']).name}")
agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py:467:            module_path = Path(method_meta["path"]).relative_to(self.root)
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:118:                    implementation="    with open(file_path, 'r', encoding=encoding) as f:\n        return f.read()",
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:127:                    implementation="    try:\n        with open(file_path, 'w', encoding=encoding) as f:\n            f.write(content)\n        return True\n    except Exception as e:\n        Logger.error(f\"Failed to write file: {e}\")\n        return False",
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:352:        directory: Any = directory or Path("generated_tools")
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:355:        with open(file_path, "w") as f:
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:359:            with open(test_path, "w") as f:
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:362:        with open(spec_path, "w") as f:
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:363:            json.dump(tool.spec.to_dict(), f, indent=2)
agentic_core\L2_execution\reasoning\ToolsmithAgent.py:500:                        file_path.write_text(content, encoding="utf-8")
agentic_core\L2_execution\scripts\remediation_dispatcher.py:528:    out_path.write_text(result.to_json(), encoding="utf-8")
agentic_core\L2_execution\scripts\remediation_dispatcher.py:589:            guardian_result_path=Path(args.guardian_result),
agentic_core\L2_execution\scripts\remediation_dispatcher.py:590:            write_artifacts_dir=Path(args.write_artifacts),
agentic_core\L2_execution\scripts\remediation_dispatcher.py:593:            approval_bundle_path=Path(args.approval_bundle) if args.approval_bundle else None,
agentic_core\L2_execution\scripts\remediation_dispatcher.py:595:            repo_root=Path(args.repo_root) if args.repo_root else None,
agentic_core\L2_execution\tools\file_io_impl.py:41:            with open(file_path, "rb") as f:
agentic_core\L2_execution\tools\file_io_impl.py:78:            with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\tools\file_io_impl.py:121:            with open(file_path, "w", encoding="utf-8") as f:
agentic_core\L2_execution\tools\write_gateway.py:35:        _REPO_ROOT = Path(__file__).resolve().parents[3]
agentic_core\L2_execution\tools\write_gateway.py:78:def write_text(path: str | Path, content: str, encoding: str = "utf-8") -> str:
agentic_core\L2_execution\tools\write_gateway.py:80:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:83:    p.write_text(content, encoding=encoding)
agentic_core\L2_execution\tools\write_gateway.py:84:    Logger.debug(f"[WriteGateway] write_text: {p}")
agentic_core\L2_execution\tools\write_gateway.py:88:def write_bytes(path: str | Path, data: bytes) -> str:
agentic_core\L2_execution\tools\write_gateway.py:90:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:93:    p.write_bytes(data)
agentic_core\L2_execution\tools\write_gateway.py:94:    Logger.debug(f"[WriteGateway] write_bytes: {p}")
agentic_core\L2_execution\tools\write_gateway.py:100:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:103:    with open(p, "w", encoding="utf-8") as f:
agentic_core\L2_execution\tools\write_gateway.py:104:        json.dump(obj, f, indent=indent)
agentic_core\L2_execution\tools\write_gateway.py:111:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:114:    with open(p, "a", encoding=encoding) as f:
agentic_core\L2_execution\tools\write_gateway.py:122:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:125:    with open(p, "w", encoding=encoding) as f:
agentic_core\L2_execution\tools\write_gateway.py:133:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:142:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:152:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:161:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:164:        shutil.rmtree(p)
agentic_core\L2_execution\tools\write_gateway.py:170:    s, d = Path(src), Path(dst)
agentic_core\L2_execution\tools\write_gateway.py:173:    shutil.copy2(s, d)
agentic_core\L2_execution\tools\write_gateway.py:180:    s, d = Path(src), Path(dst)
agentic_core\L2_execution\tools\write_gateway.py:183:    shutil.move(str(s), str(d))
agentic_core\L2_execution\tools\write_gateway.py:190:    s, d = Path(src), Path(dst)
agentic_core\L2_execution\tools\write_gateway.py:199:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:209:    s, d = Path(src), Path(dst)
agentic_core\L2_execution\tools\write_gateway.py:211:    shutil.copytree(str(s), str(d), dirs_exist_ok=True)
agentic_core\L2_execution\tools\write_gateway.py:218:    _deny_writes_into_source_roots(Path(path), "mkdir")
agentic_core\L2_execution\tools\write_gateway.py:230:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:239:        with os.fdopen(fd, "w", encoding="utf-8") as f:
agentic_core\L2_execution\tools\write_gateway.py:240:            json.dump(obj, f, indent=indent)
agentic_core\L2_execution\tools\write_gateway.py:244:        Path(tmp).replace(p)
agentic_core\L2_execution\tools\write_gateway.py:247:            os.unlink(tmp)
agentic_core\L2_execution\tools\write_gateway.py:260:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:263:    with open(p, "w", newline="", encoding="utf-8") as f:
agentic_core\L2_execution\tools\write_gateway.py:274:    p = Path(path)
agentic_core\L2_execution\tools\write_gateway.py:276:    with open(p, "a", newline="", encoding="utf-8") as f:
agentic_core\L2_execution\tools\write_gateway.py:283:    "write_text",
agentic_core\L2_execution\tools\write_gateway.py:284:    "write_bytes",
agentic_core\L2_execution\types\capability_token_types.py:48:    return json.dumps(obj, sort_keys=True, separators=(",", ":"))
agentic_core\L2_execution\types\heal_contract.py:203:        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)
agentic_core\L2_execution\types\heal_contract_types.py:203:        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)
agentic_core\L2_execution\types\ml_pattern_record.py:95:        return json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
agentic_core\L2_execution\types\ml_pattern_record.py:120:        raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
agentic_core\L2_execution\types\ml_write_intent.py:70:        raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
agentic_core\L2_execution\types\ml_write_intent.py:79:        return json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
agentic_core\L2_execution\types\self_healing_trigger_types.py:140:    canonical = json.dumps(
agentic_core\L2_execution\types\tool_intent.py:185:            self.args_hash = _sha256(json.dumps(self.args, sort_keys=True, separators=(",", ":")).encode())
agentic_core\L2_execution\types\tool_intent.py:202:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L2_execution\utils\analysis_ops_util.py:28:        with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\utils\analysis_ops_util.py:105:        with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\utils\analysis_ops_util.py:169:        with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\utils\analysis_ops_util.py:193:        with open(file_path, encoding="utf-8") as f:
agentic_core\L2_execution\utils\deterministic_cleaner_util.py:117:                with open(temp_file) as f:
agentic_core\L2_execution\utils\deterministic_cleaner_util.py:120:                os.unlink(temp_file)
agentic_core\L2_execution\utils\deterministic_cleaner_util.py:171:        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
agentic_core\L2_execution\utils\deterministic_cleaner_util.py:187:            path: Any = Path(file_path)
agentic_core\L2_execution\utils\deterministic_cleaner_util.py:199:            with open(path, "w", encoding="utf-8") as f:
agentic_core\L2_execution\utils\tool_registry_util.py:72:            path = Path(tool_path)
agentic_core\L3_orchestration\enforcement\mission_runner.py:573:        esc_dir = Path("observability/human_review")
agentic_core\L3_orchestration\enforcement\mission_runner.py:576:        _wg.write_text(esc_dir / f"escalation_{int(time.time())}.md", report)
agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py:573:        esc_dir = Path("observability/human_review")
agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py:576:        _wg.write_text(esc_dir / f"escalation_{int(time.time())}.md", report)
agentic_core\L3_orchestration\engines\action_router.py:36:        self.work_dir: Path = Path(work_dir).resolve()
agentic_core\L3_orchestration\engines\autonomous_execution_engine.py:71:        self.state_path = Path(".canon_memory/execution_state.json")
agentic_core\L3_orchestration\engines\convergence_engine.py:22:        with open(file_path, "rb") as f:
agentic_core\L3_orchestration\engines\convergence_engine.py:62:                file_path = Path(violation.get("path", ""))
agentic_core\L3_orchestration\engines\decomposition_orchestrator.py:88:        discovery_path = Path(__file__).resolve().parents[3] / "agent_discovery_full.json"
agentic_core\L3_orchestration\engines\decomposition_orchestrator.py:233:        return json.dumps(
agentic_core\L3_orchestration\engines\omni_context_engine.py:50:                with open(file_path, encoding="utf-8") as f:
agentic_core\L3_orchestration\engines\orchestrator_engine.py:126:                self._available_agents = [Path(p).stem for p in agent_paths]
agentic_core\L3_orchestration\engines\orchestrator_engine.py:550:                self._available_agents = [Path(p).stem for p in agent_paths]
agentic_core\L3_orchestration\engines\orchestrator_engine.py:608:            agent_path = next((p for p in agent_paths if Path(p).stem == agent_name), None)
agentic_core\L3_orchestration\engines\orchestrator_engine.py:614:            agent_file = Path(agent_path)
agentic_core\L3_orchestration\engines\proactive_fission_scanner.py:61:            with open(file_path, encoding="utf-8") as f:
agentic_core\L3_orchestration\engines\proactive_fission_scanner.py:164:        base_name = Path(file_path).stem
agentic_core\L3_orchestration\engines\proactive_fission_scanner.py:165:        parent_dir = Path(file_path).parent
agentic_core\L3_orchestration\engines\sovereign_mcp_router.py:29:        self.config_path = Path(config_path)
agentic_core\L3_orchestration\engines\sovereign_mcp_router.py:178:                                json.dumps(reasoning_result.get("steps", [])),
agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:71:        self.config_path: Path = Path("agentic_core/L4_state/memory/.sovereign_config.json")
agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:129:        _wg.write_text(
agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:131:            json.dumps(
agentic_core\L3_orchestration\reasoning\NervousSystemAgent.py:89:        self.project_root = Path(__file__).resolve().parents[3]
agentic_core\L3_orchestration\reasoning\NervousSystemAgent.py:792:        affected_paths = [Path(f) for f in (files or list(self._modified_files))]
agentic_core\L3_orchestration\reasoning\NervousSystemAgent.py:805:                        file_path=Path(loc_viol.get("file", "")) if loc_viol.get("file") else None,
agentic_core\L3_orchestration\reasoning\NervousSystemAgent.py:815:                        file_path=Path(hier_viol.get("file", "")) if hier_viol.get("file") else None,
agentic_core\L3_orchestration\reasoning\NervousSystemAgent.py:825:                        file_path=Path(imp_viol.get("file", "")) if imp_viol.get("file") else None,
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:92:                self.redis.set(cache_key, json.dumps(capable), ex=3600)
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:137:            _l3_log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:183:                _artifacts_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:219:                    _hil_log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:126:    memory_root: Path = field(default_factory=lambda: Path(".canon_memory"))
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:143:            self.memory_root = Path(self.memory_root)
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:223:                with open(self.manifest_path, encoding="utf-8") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:271:        with open(self.manifest_path, encoding="utf-8") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:295:            data_json = json.dumps(data, sort_keys=True, default=str)
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:351:                with open(file_path, encoding="utf-8") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:443:                        with open(file_path, "rb") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:507:                    key = Path(ghost).stem
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:511:                        with open(file_path, "rb") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:540:                            with open(file_path, "rb") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:741:                        file_path_obj = Path(file_path)
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:747:                            with open(file_path_obj, "rb") as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:938:            with open(self.manifest_path) as f:
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:971:        memory_root = Path(".canon_memory")
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:1005:    manager = get_state_manager(Path(args.root))
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:1010:            print(json.dumps(results, indent=2))
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:1020:            print(json.dumps(report.to_dict(), indent=2))
agentic_core\L3_orchestration\reasoning\UnifiedAgent.py:156:            return json.dumps(content, ensure_ascii=False)
agentic_core\L3_orchestration\reasoning\UnifiedAgent.py:594:            violations = agent.validate_file(Path(file_path))
agentic_core\L3_orchestration\reasoning\UnifiedAgent.py:641:            violations = agent.validate_file(Path(file_path))
agentic_core\L3_orchestration\reasoning\UnifiedAgent.py:693:            actions = agent.heal_all(Path(file_path))
agentic_core\L3_orchestration\reasoning\UnifiedAgent.py:724:            result_actions = agent.heal_all(Path(file_path))
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:88:    assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:89:    tmp_dir = write_artifacts_dir or Path(tempfile.gettempdir())
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:145:            Path(write_artifacts_dir).resolve().relative_to(repo_root.resolve())
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:167:    heal_dir = Path(write_artifacts_dir) if write_artifacts_dir else repo_root / "docs" / "reports" / "plans"
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:226:            repo_root=Path(args.repo_root) if args.repo_root else None,
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:240:        print(json.dumps(result, indent=2))
agentic_core\L3_orchestration\types\approval_contract.py:182:        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)
agentic_core\L3_orchestration\types\approval_contract_types.py:182:        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)
agentic_core\L3_orchestration\types\cognitive_diff_types.py:205:    canonical = json.dumps(
agentic_core\L3_orchestration\types\recursion_monitor_types.py:390:    def is_circuit_open(self) -> bool:
agentic_core\L3_orchestration\types\telepathy_interface_types.py:33:        self.instructions_path = Path(instructions_path)
agentic_core\L3_orchestration\types\telepathy_interface_types.py:141:            _wg.write_text(self.instructions_path, done_content, encoding="utf-8")
agentic_core\L3_orchestration\types\workflow_loader_types.py:86:            workflow_path = Path(__file__).parent / "active_workflow.json"
agentic_core\L3_orchestration\types\workflow_loader_types.py:88:            workflow_path = Path(workflow_path)
agentic_core\L3_orchestration\types\workflow_loader_types.py:108:            with open(self.workflow_path, encoding="utf-8") as f:
agentic_core\L4_state\config\versioned_configs.py:44:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\config\versioned_configs.py:78:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\config\versioned_configs.py:101:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\config\versioned_configs.py:126:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\config\versioned_configs.py:171:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\enforcement\change_tracker.py:20:        self.file_path = str(Path(file_path).resolve())
agentic_core\L4_state\enforcement\change_tracker_enforcer.py:20:        self.file_path = str(Path(file_path).resolve())
agentic_core\L4_state\enforcement\citation_enforcement.py:55:    raw = json.dumps(subset, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\enforcement\mission_historian.py:31:        self.log_path = log_path or Path("mission_audit.csv")
agentic_core\L4_state\enforcement\mission_historian.py:72:            with open(self.log_path, newline="", encoding="utf-8") as f:
agentic_core\L4_state\enforcement\mission_historian_enforcer.py:31:        self.log_path = log_path or Path("mission_audit.csv")
agentic_core\L4_state\enforcement\mission_historian_enforcer.py:72:            with open(self.log_path, newline="", encoding="utf-8") as f:
agentic_core\L4_state\enforcement\telemetry_recorder.py:79:        event_json = json.dumps(event, sort_keys=True, separators=(",", ":"))
agentic_core\L4_state\enforcement\trace_event.py:54:                json.dumps(event.payload),
agentic_core\L4_state\enforcement\trace_event_enforcer.py:54:                json.dumps(event.payload),
agentic_core\L4_state\memory\blob_storage_provider.py:58:        self.base_path = Path(base_path)
agentic_core\L4_state\memory\blob_storage_provider.py:74:        safe_key = Path(*parts)
agentic_core\L4_state\memory\blob_storage_provider.py:98:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\memory\blob_storage_provider.py:122:        with open(target_path, "rb") as f:
agentic_core\L4_state\memory\blob_storage_provider.py:462:            serialized: Any = json.dumps(value)
agentic_core\L4_state\memory\blob_storage_provider.py:669:        json_line: Any = json.dumps(result_dict) + "\n"
agentic_core\L4_state\memory\blob_storage_provider.py:850:        serialized: Any = json.dumps(value)
agentic_core\L4_state\memory\runtime_state_guard.py:44:            with open(self.state_path) as f:
agentic_core\L4_state\memory\runtime_state_guard.py:50:                with open(self.state_path) as f:
agentic_core\L4_state\memory\runtime_state_guard.py:82:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\memory\semantic_cache_manager.py:556:        payload_json = json.dumps(enriched_result)
agentic_core\L4_state\memory\semantic_cache_manager.py:613:        payload_json = json.dumps(enriched_result)
agentic_core\L4_state\memory\semantic_cache_manager.py:678:        payload_json = json.dumps(enriched_result)
agentic_core\L4_state\memory\semantic_cache_manager.py:768:            payload_json = json.dumps(result)
agentic_core\L4_state\memory\sovereign_memory_store.py:28:        self.pinecone = PineconeSovereignAgent(Path("."))
agentic_core\L4_state\memory\sovereign_memory_store.py:39:                redis_shield.execute("hset", f"{self.graph_key}:entities", name, json.dumps(entity))
agentic_core\L4_state\memory\sovereign_reasoning_memory_ledger.py:52:            "file": Path(file_path).name,
agentic_core\L4_state\memory\sovereign_reasoning_memory_ledger.py:64:                self.redis_client.rpush(self.redis_reasoning_key, json.dumps(entry))
agentic_core\L4_state\memory\sovereign_semantic_cache.py:42:        self.pinecone = pinecone_agent or PineconeSovereignAgent(Path("."))
agentic_core\L4_state\memory\sovereign_semantic_cache.py:56:        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
agentic_core\L4_state\memory\sovereign_semantic_cache.py:88:                    Logger.info(f"[L4 HIT] Redis MCP recall for {Path(file_path).name}")
agentic_core\L4_state\memory\sovereign_semantic_cache.py:94:        embed_text: Any = f"File: {file_path}\nStructure: {json.dumps(ast_features)}\nContent: {code[:1000]}"
agentic_core\L4_state\memory\sovereign_semantic_cache.py:108:                entry_json: Any = json.dumps(entry)
agentic_core\L4_state\memory\sovereign_semantic_cache.py:116:            Logger.info(f"[L4 STORE] Dual-sync complete for {Path(file_path).name}")
agentic_core\L4_state\memory\sovereign_semantic_cache.py:133:            Logger.info(f"[L4 PURGE] Purged semantic trail for {Path(file_path).name}")
agentic_core\L4_state\memory\verifiable_checkpoint_manager.py:49:        payload_str: Any = json.dumps(state, sort_keys=True)
agentic_core\L4_state\memory\verifiable_checkpoint_manager.py:170:        payload_str: Any = json.dumps(state, sort_keys=True, indent=2)
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:81:                self.redis.set(full_key, json.dumps(context), ex=86400)  # 24h
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:130:                self.redis.rpush(f"{self.prefix_historian}:successful_traces", json.dumps(trace))
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:154:                self.redis.rpush(trail_key, json.dumps(event))
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:135:    storage_path: Path = field(default_factory=lambda: Path(".canon_memory/checkpoints"))
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:155:            self.storage_path = Path(self.storage_path)
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:282:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:329:            task = asyncio.create_task(self._mirror_checkpoint(Path(file_path)))
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:468:                with open(file_path, encoding="utf-8") as f:
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:560:                with open(index_path, encoding="utf-8") as f:
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:586:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:861:        storage_path = Path(".canon_memory/checkpoints")
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:893:    manager = get_checkpoint_manager(mode=args.mode, storage_path=Path(args.storage))
agentic_core\L4_state\reasoning\GravityStateAgent.py:108:                        file_key = str(Path(file_path).relative_to(self.root))
agentic_core\L4_state\reasoning\GravityStateAgent.py:201:            with open(self.state_file, encoding="utf-8") as f:
agentic_core\L4_state\reasoning\GravityStateAgent.py:212:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\GravityStateAgent.py:235:        file_key = str(Path(record.file_path).relative_to(self.root))
agentic_core\L4_state\reasoning\GravityStateAgent.py:353:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\GravityStateAgent.py:374:            with open(checkpoint_file, encoding="utf-8") as f:
agentic_core\L4_state\reasoning\PineconeSovereignAgent.py:61:        self.project_root: Path = project_root or Path(__file__).resolve().parents[4]
agentic_core\L4_state\reasoning\PineconeSovereignAgent.py:133:                content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
agentic_core\L4_state\reasoning\PineconeSovereignAgent.py:208:            self.redis.set(cache_key, json.dumps(validated_embedding), ex=604800)
agentic_core\L4_state\reasoning\PineconeSovereignAgent.py:337:        file_id = f"file_{str(file_path.relative_to(Path('.').resolve())).replace('/', '_')}"
agentic_core\L4_state\reasoning\PineconeSovereignAgent.py:408:        file_id = f"file_{file_path.relative_to(Path('.').resolve())}".replace("/", "_")
agentic_core\L4_state\reasoning\RedisSovereignAgent.py:148:            rel_path = str(file_path.relative_to(Path(".").resolve())).replace("/", "_")
agentic_core\L4_state\types\citation_bundle.py:80:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\types\cycle_types.py:306:        assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\types\cycle_types.py:317:        with open(path) as f:
agentic_core\L4_state\types\replay_bundle.py:120:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\types\retrieval_boundary_snapshot.py:104:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\types\retrieval_boundary_snapshot.py:124:    raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\types\validation_context_types.py:77:        self.memory_dir = memory_dir or Path("observability/memory")
agentic_core\L4_state\types\validation_context_types.py:101:                with open(self.file_history_file) as f:
agentic_core\L4_state\types\validation_context_types.py:127:            with open(file_path, "rb") as f:
agentic_core\L4_state\types\violation_event.py:88:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L4_state\utils\complexity_analyzer_util.py:87:        with open(file_path, encoding="utf-8") as f:
agentic_core\L4_state\utils\experience_buffer_util.py:51:        self.path = Path(path)
agentic_core\L4_state\utils\experience_buffer_util.py:61:            assert_no_persistent_write("L4", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\utils\experience_buffer_util.py:62:            _wg.write_text(self.path, "")  # Empty JSONL file
agentic_core\L4_state\utils\experience_buffer_util.py:88:            with self.path.open("r", encoding="utf-8") as f:
agentic_core\L4_state\utils\experience_buffer_util.py:97:                assert_no_persistent_write("L4", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\utils\experience_buffer_util.py:98:                _wg.write_text(self.path, "".join(kept), encoding="utf-8")
agentic_core\L4_state\utils\experience_buffer_util.py:107:            with self.path.open("r", encoding="utf-8") as f:
agentic_core\L4_state\utils\get_existing_filenames_util.py:14:    repo_root: Any = Path(".")
agentic_core\L4_state\utils\get_existing_files_util.py:14:    repo_root: Any = Path(".")
agentic_core\L4_state\utils\get_existing_file_hashes_util.py:18:    repo_root: Any = Path(".")
agentic_core\L4_state\utils\get_file_hash_util.py:15:    with open(filepath, "rb") as f:
agentic_core\L4_state\utils\local_disk_adapter.py:25:        self.root = Path(config.get("storage_path", "./data/storage"))
agentic_core\L4_state\utils\local_disk_adapter_util.py:25:        self.root = Path(config.get("storage_path", "./data/storage"))
agentic_core\L5_safety\config\gravity_leak_config.py:62:        self.project_root = Path(project_root).resolve()
agentic_core\L5_safety\config\gravity_leak_config.py:162:            path = Path(grav["path"]) if isinstance(grav["path"], str) else grav["path"]
agentic_core\L5_safety\config\gravity_leak_config.py:257:        _wg.write_text(path, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\agent_info.py:193:    base = Path(base_path)
agentic_core\L5_safety\enforcement\agent_info.py:274:        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
agentic_core\L5_safety\enforcement\agent_info.py:481:    report_path = Path(r"C:\Git\Agentic-Workflow\ast_redundancy_report.json")
agentic_core\L5_safety\enforcement\agent_info.py:504:    _wg.write_text(report_path, json.dumps(json_data, indent=2))
agentic_core\L5_safety\enforcement\agent_info_enforcer.py:193:    base = Path(base_path)
agentic_core\L5_safety\enforcement\agent_info_enforcer.py:274:        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
agentic_core\L5_safety\enforcement\agent_info_enforcer.py:481:    report_path = Path(r"C:\Git\Agentic-Workflow\ast_redundancy_report.json")
agentic_core\L5_safety\enforcement\agent_info_enforcer.py:504:    _wg.write_text(report_path, json.dumps(json_data, indent=2))
agentic_core\L5_safety\enforcement\airlock_trimmer.py:16:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L5_safety\enforcement\airlock_trimmer.py:47:    _wg.write_text(init_file, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\airlock_trimmer_enforcer.py:16:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L5_safety\enforcement\airlock_trimmer_enforcer.py:47:    _wg.write_text(init_file, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:121:        self.project_root = Path(project_root).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:184:            rel_path = Path(str(source_path).replace(":", "_").lstrip("/\\"))
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:200:                _wg.append_text(self.audit_log_path, json.dumps(result.to_dict()) + "\n")
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:396:        source = Path(source).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:397:        destination = Path(destination).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:440:            # because shutil.move behavior varies (might nest directories)
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:496:        source = Path(source).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:592:        source = Path(source).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:684:            with open(self.audit_log_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:720:        archived_path = Path(archived_path).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:752:        original_rel_path = Path(*parts[1:])
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:121:        self.project_root = Path(project_root).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:184:            rel_path = Path(str(source_path).replace(":", "_").lstrip("/\\"))
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:200:                _wg.append_text(self.audit_log_path, json.dumps(result.to_dict()) + "\n")
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:396:        source = Path(source).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:397:        destination = Path(destination).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:440:            # because shutil.move behavior varies (might nest directories)
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:496:        source = Path(source).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:592:        source = Path(source).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:684:            with open(self.audit_log_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:720:        archived_path = Path(archived_path).resolve()
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:752:        original_rel_path = Path(*parts[1:])
agentic_core\L5_safety\enforcement\audit_healing_strategy.py:42:        self.audit_log_path = Path("agentic_core/L0_routing/utils/healing_audit.jsonl")
agentic_core\L5_safety\enforcement\circuit_breaker.py:116:    def is_open(self) -> bool:
agentic_core\L5_safety\enforcement\circuit_breaker.py:121:    def is_half_open(self) -> bool:
agentic_core\L5_safety\enforcement\circuit_breaker.py:143:                    self._transition_to_half_open()
agentic_core\L5_safety\enforcement\circuit_breaker.py:185:                self._transition_to_open()
agentic_core\L5_safety\enforcement\circuit_breaker.py:189:                    self._transition_to_open()
agentic_core\L5_safety\enforcement\circuit_breaker.py:207:    def _transition_to_open(self) -> None:
agentic_core\L5_safety\enforcement\circuit_breaker.py:214:    def _transition_to_half_open(self) -> None:
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:116:    def is_open(self) -> bool:
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:121:    def is_half_open(self) -> bool:
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:143:                    self._transition_to_half_open()
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:185:                self._transition_to_open()
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:189:                    self._transition_to_open()
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:207:    def _transition_to_open(self) -> None:
agentic_core\L5_safety\enforcement\circuit_breaker_gate.py:214:    def _transition_to_half_open(self) -> None:
agentic_core\L5_safety\enforcement\circular_import_fixer.py:36:        rel_to_core: Any = Path(".")
agentic_core\L5_safety\enforcement\circular_import_fixer.py:83:        with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\circular_import_fixer.py:116:    script_dir: Any = Path(__file__).parent
agentic_core\L5_safety\enforcement\circular_import_fixer_enforcer.py:36:        rel_to_core: Any = Path(".")
agentic_core\L5_safety\enforcement\circular_import_fixer_enforcer.py:83:        with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\circular_import_fixer_enforcer.py:116:    script_dir: Any = Path(__file__).parent
agentic_core\L5_safety\enforcement\data.py:31:discovery_path = Path("agent_discovery_full.json")
agentic_core\L5_safety\enforcement\data.py:36:data = json.load(open(discovery_path))
agentic_core\L5_safety\enforcement\data_enforcer.py:31:discovery_path = Path("agent_discovery_full.json")
agentic_core\L5_safety\enforcement\data_enforcer.py:36:data = json.load(open(discovery_path))
agentic_core\L5_safety\enforcement\dependency_graph.py:32:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\dependency_graph_enforcer.py:32:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:65:        data = json.load(open(self.discovery_path))
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:74:            path = Path(agent["path"])
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:118:                _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:137:        data = json.load(open(self.discovery_path))
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:146:            path = Path(agent["path"])
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:195:                _wg.write_text(path, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:214:            data = json.load(open(self.discovery_path))
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:226:                    path = Path(agent["path"])
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:65:        data = json.load(open(self.discovery_path))
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:74:            path = Path(agent["path"])
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:118:                _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:137:        data = json.load(open(self.discovery_path))
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:146:            path = Path(agent["path"])
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:195:                _wg.write_text(path, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:214:            data = json.load(open(self.discovery_path))
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:226:                    path = Path(agent["path"])
agentic_core\L5_safety\enforcement\final_airlock_trimmer.py:13:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L5_safety\enforcement\final_airlock_trimmer.py:31:    _wg.write_text(file_path, "\n".join(cleaned) + "\n", encoding="utf-8")
agentic_core\L5_safety\enforcement\final_airlock_trimmer_enforcer.py:13:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L5_safety\enforcement\final_airlock_trimmer_enforcer.py:31:    _wg.write_text(file_path, "\n".join(cleaned) + "\n", encoding="utf-8")
agentic_core\L5_safety\enforcement\git_health_sensor.py:45:        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
agentic_core\L5_safety\enforcement\git_health_sensor.py:99:                    affected_files.append(Path(file_path))
agentic_core\L5_safety\enforcement\git_health_sensor.py:143:        conflicted_files = [Path(f.strip()) for f in stdout.strip().split("\n") if f.strip()]
agentic_core\L5_safety\enforcement\git_health_sensor.py:307:    print(json.dumps(signal.to_dict(), indent=2, default=str))
agentic_core\L5_safety\enforcement\git_health_sensor_enforcer.py:45:        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
agentic_core\L5_safety\enforcement\git_health_sensor_enforcer.py:99:                    affected_files.append(Path(file_path))
agentic_core\L5_safety\enforcement\git_health_sensor_enforcer.py:143:        conflicted_files = [Path(f.strip()) for f in stdout.strip().split("\n") if f.strip()]
agentic_core\L5_safety\enforcement\git_health_sensor_enforcer.py:307:    print(json.dumps(signal.to_dict(), indent=2, default=str))
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:11:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:70:# Path() constructor patterns
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:182:        # Apply Path() constructor replacements
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:194:                _wg.write_text(file_path, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:11:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:70:# Path() constructor patterns
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:182:        # Apply Path() constructor replacements
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:194:                _wg.write_text(file_path, content, encoding="utf-8")
agentic_core\L5_safety\enforcement\HealingStrategy.py:53:        self.project_root = Path(project_root) if project_root else Path.cwd()
agentic_core\L5_safety\enforcement\healing_invocation_audit.py:57:                file_path = Path(file_path)
agentic_core\L5_safety\enforcement\healing_invocation_audit.py:97:            with open(file_path) as f:
agentic_core\L5_safety\enforcement\healing_invocation_audit.py:112:            with open(file_path) as f:
agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py:57:                file_path = Path(file_path)
agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py:97:            with open(file_path) as f:
agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py:112:            with open(file_path) as f:
agentic_core\L5_safety\enforcement\human_review_queue.py:378:            _log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:378:            _log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
agentic_core\L5_safety\enforcement\import_surgeon.py:42:        self.root_path = Path(root_path)
agentic_core\L5_safety\enforcement\import_surgeon.py:59:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\import_surgeon.py:120:                    py_files.append(Path(root) / file)
agentic_core\L5_safety\enforcement\import_surgeon.py:187:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\import_surgeon.py:207:    report_path: Any = Path(project_root) / "08_scripts" / "import_surgery_report.txt"
agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:42:        self.root_path = Path(root_path)
agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:59:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:120:                    py_files.append(Path(root) / file)
agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:187:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:207:    report_path: Any = Path(project_root) / "08_scripts" / "import_surgery_report.txt"
agentic_core\L5_safety\enforcement\mock_context.py:10:project_root = Path(__file__).resolve().parents[1]
agentic_core\L5_safety\enforcement\mock_context_enforcer.py:10:project_root = Path(__file__).resolve().parents[1]
agentic_core\L5_safety\enforcement\module_collision_guard.py:210:    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
agentic_core\L5_safety\enforcement\module_collision_guard.py:214:    with open(baseline_path) as f:
agentic_core\L5_safety\enforcement\module_collision_guard.py:242:    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
agentic_core\L5_safety\enforcement\module_collision_guard.py:245:    content = json.dumps(baseline, indent=2, sort_keys=True) + "\n"
agentic_core\L5_safety\enforcement\module_collision_guard.py:302:        return Path(result.stdout.strip())
agentic_core\L5_safety\enforcement\module_collision_guardrail.py:210:    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
agentic_core\L5_safety\enforcement\module_collision_guardrail.py:214:    with open(baseline_path) as f:
agentic_core\L5_safety\enforcement\module_collision_guardrail.py:242:    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
agentic_core\L5_safety\enforcement\module_collision_guardrail.py:301:        return Path(result.stdout.strip())
agentic_core\L5_safety\enforcement\mutation_prohibition.py:6:Persistent writes include: Path.write_text/write_bytes, json.dump to file,
agentic_core\L5_safety\enforcement\mutation_prohibition.py:7:os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').
agentic_core\L5_safety\enforcement\mutation_prohibition.py:52:        op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
agentic_core\L5_safety\enforcement\mutation_prohibition.py:83:def safe_write_text(
agentic_core\L5_safety\enforcement\mutation_prohibition.py:91:    """Guarded Path.write_text replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:92:    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:93:    _wg.write_text(Path(filepath), content, encoding=encoding)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:96:def safe_write_bytes(
agentic_core\L5_safety\enforcement\mutation_prohibition.py:103:    """Guarded Path.write_bytes replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:104:    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:105:    _wg.write_bytes(Path(filepath), data)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:118:    """Guarded json.dump-to-file replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:119:    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:130:    """Guarded shutil.move replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:131:    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:141:    """Guarded shutil.rmtree replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:142:    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:152:    """Guarded os.remove replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:153:    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:177:    """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
agentic_core\L5_safety\enforcement\mutation_prohibition.py:178:    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:179:    return open(filepath, mode, encoding=encoding)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:212:    "safe_write_bytes",
agentic_core\L5_safety\enforcement\mutation_prohibition.py:213:    "safe_write_text",
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:6:Persistent writes include: Path.write_text/write_bytes, json.dump to file,
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:7:os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:52:        op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:83:def safe_write_text(
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:91:    """Guarded Path.write_text replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:92:    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:93:    _wg.write_text(Path(filepath), content, encoding=encoding)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:96:def safe_write_bytes(
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:103:    """Guarded Path.write_bytes replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:104:    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:105:    _wg.write_bytes(Path(filepath), data)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:118:    """Guarded json.dump-to-file replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:119:    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:130:    """Guarded shutil.move replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:131:    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:141:    """Guarded shutil.rmtree replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:142:    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:152:    """Guarded os.remove replacement."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:153:    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:177:    """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:178:    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:179:    return open(filepath, mode, encoding=encoding)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:212:    "safe_write_bytes",
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:213:    "safe_write_text",
agentic_core\L5_safety\enforcement\namespace_medic.py:30:    ("Path(", "from pathlib import Path", "simple"),
agentic_core\L5_safety\enforcement\namespace_medic.py:93:        with open(file_path, encoding="utf-8", errors="replace") as f:
agentic_core\L5_safety\enforcement\namespace_medic.py:127:    project_root: Any = Path(__file__).parent
agentic_core\L5_safety\enforcement\namespace_medic.py:153:                with open(file_path, encoding="utf-8", errors="replace") as f:
agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py:30:    ("Path(", "from pathlib import Path", "simple"),
agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py:93:        with open(file_path, encoding="utf-8", errors="replace") as f:
agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py:127:    project_root: Any = Path(__file__).parent
agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py:153:                with open(file_path, encoding="utf-8", errors="replace") as f:
agentic_core\L5_safety\enforcement\phase_acceptance_guard.py:200:    repo_root = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\phase_acceptance_guardrail.py:200:    repo_root = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\pytest_config_guard.py:226:    repo_root = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\pytest_config_guard.py:259:            tmpdir = Path(tmpdir)
agentic_core\L5_safety\enforcement\pytest_config_guard.py:263:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guard.py:271:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guard.py:289:            tmpdir = Path(tmpdir)
agentic_core\L5_safety\enforcement\pytest_config_guard.py:293:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guard.py:301:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:226:    repo_root = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:259:            tmpdir = Path(tmpdir)
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:263:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:271:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:289:            tmpdir = Path(tmpdir)
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:293:            _wg.write_text(
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:301:            _wg.write_text(
agentic_core\L5_safety\enforcement\registry_verification.py:88:        current = Path(__file__).resolve()
agentic_core\L5_safety\enforcement\registry_verification.py:117:        parts = Path(relative_path).parts
agentic_core\L5_safety\enforcement\registry_verification.py:200:            with open(self.discovery_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\registry_verification_enforcer.py:88:        current = Path(__file__).resolve()
agentic_core\L5_safety\enforcement\registry_verification_enforcer.py:117:        parts = Path(relative_path).parts
agentic_core\L5_safety\enforcement\registry_verification_enforcer.py:200:            with open(self.discovery_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\safe_subprocess_handler.py:99:def safe_popen(
agentic_core\L5_safety\enforcement\safe_subprocess_handler.py:136:    process = subprocess.Popen(
agentic_core\L5_safety\enforcement\safe_subprocess_handler_enforcer.py:99:def safe_popen(
agentic_core\L5_safety\enforcement\safe_subprocess_handler_enforcer.py:136:    process = subprocess.Popen(
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:151:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:162:                success = await _wg.write_text(self.fs_client, file_path, new_content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:190:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:199:            return await _wg.write_text(self.fs_client, file_path, content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:218:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:228:            return await _wg.write_text(self.fs_client, file_path, content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:247:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:257:                "open(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:258:                f"# TODO: Use {fix['new_client']}.read_text() or write_text()\n# open(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:261:                "Path(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:262:                f"# TODO: Use {fix['new_client']} for file operations\n# Path(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:264:            return await _wg.write_text(self.fs_client, file_path, content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:151:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:162:                success = await _wg.write_text(self.fs_client, file_path, new_content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:190:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:199:            return await _wg.write_text(self.fs_client, file_path, content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:218:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:228:            return await _wg.write_text(self.fs_client, file_path, content)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:247:            path_obj = Path(file_path)
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:257:                "open(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:258:                f"# TODO: Use {fix['new_client']}.read_text() or write_text()\n# open(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:261:                "Path(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:262:                f"# TODO: Use {fix['new_client']} for file operations\n# Path(",
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:264:            return await _wg.write_text(self.fs_client, file_path, content)
agentic_core\L5_safety\enforcement\ssot_guardrail.py:283:                fp = Path(dirpath) / fn
agentic_core\L5_safety\enforcement\ssot_guardrail.py:326:    project_root = Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\enforcement\ssot_guardrail.py:351:        print(json.dumps(output, indent=2))
agentic_core\L5_safety\enforcement\ssot_import_enforcer.py:14:PROJECT_ROOT = Path(__file__).resolve().parents[3]
agentic_core\L5_safety\enforcement\ssot_import_enforcer.py:73:    _wg.write_text(file_path, new_content, encoding="utf-8")
agentic_core\L5_safety\enforcement\system.py:93:        with open(self.discovery_path) as f:
agentic_core\L5_safety\enforcement\system.py:136:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\system.py:296:    project_root = Path(__file__).resolve().parents[1]
agentic_core\L5_safety\enforcement\system_enforcer.py:93:        with open(self.discovery_path) as f:
agentic_core\L5_safety\enforcement\system_enforcer.py:136:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\system_enforcer.py:296:    project_root = Path(__file__).resolve().parents[1]
agentic_core\L5_safety\enforcement\toxic_dependency_auditor.py:31:        self.root = Path(root_dir)
agentic_core\L5_safety\enforcement\toxic_dependency_auditor_enforcer.py:31:        self.root = Path(root_dir)
agentic_core\L5_safety\enforcement\verification_gate.py:69:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\verification_gate.py:196:            with open(context.file_path, encoding="utf-8") as f:
agentic_core\L5_safety\governance\lazy_seam_classifier.py:32:        with open(self.allowlist_path, encoding="utf-8") as f:
agentic_core\L5_safety\governance\lazy_seam_enforcer.py:197:        with open(self.allowlist_path, encoding="utf-8") as f:
agentic_core\L5_safety\governance\lazy_seam_enforcer.py:222:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:97:            self.project_root = Path(self.project_root)
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:228:                file_path_obj = Path(file_path)
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:752:        file_path = Path(file_path)
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:797:        Logger.info(f"  [GRAVITY] Attempting repair: {Path(file_path).name}")
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:806:                file_path=Path(file_path),
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:854:        file_path = Path(file_path)
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:1015:        files = [Path(f) if not isinstance(f, Path) else f for f in files]
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:1201:            with open(baseline_path) as f:
agentic_core\L5_safety\reasoning\AutonomousThreatEvolutionAgent.py:49:        self.log_path: Path = Path("agentic_core/L6_observability/reasoning/threat_detections.json")
agentic_core\L5_safety\reasoning\AutonomousThreatEvolutionAgent.py:85:            with open(self.log_path) as f:
agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:248:        _wg.write_text(report_path, md, encoding="utf-8")
agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:322:                    with open(self.discovery_json_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:351:                    with open(agent_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:472:                    asyncio.run(self.cache_set(key=cache_key, value=json.dumps(summary), ttl=86400))
agentic_core\L5_safety\reasoning\BenchmarkingAgent.py:406:        alert_file = Path("observability/alerts/performance.json")
agentic_core\L5_safety\reasoning\BenchmarkingAgent.py:411:                with open(alert_file) as f:
agentic_core\L5_safety\reasoning\BootstrapAgent.py:78:                full_path = Path(target_path) / file_path
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:283:            file_path: Any = Path(file_str)
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:350:        _wg.write_text(candidate, header + textwrap.dedent(code), encoding="utf-8")
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:386:                    _wg.write_text(file_path, "".join(new_lines), encoding="utf-8")
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:781:                        "scan_date": str(Path(__file__).stat().st_mtime),
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:834:        python_paths = [Path(f) for f in ctx.python_files]
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:835:        project_root_path = Path(ctx.project_root)
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:998:                _wg.write_text(file_path, "".join(new_lines), encoding="utf-8")
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:115:        violations = enforcer.validate_file(Path("my_agent.py"))
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:118:        can_modify = enforcer.check_sovereignty("L3", Path("L5/agent.py"))
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:426:                _wg.write_text(
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:428:                    json.dumps(self._ssot_registry, indent=2),
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:474:                    file_path = Path(path)
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:485:                    file_path = Path(path)
agentic_core\L5_safety\reasoning\CodeFormatterAgent.py:57:        file: Path = Path(file_path)
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:87:            actions = agent.heal_all(Path(file_path))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:159:        actions = healer.heal_imports(Path("my_agent.py"))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:162:        actions = healer.heal_all(Path("my_agent.py"))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:242:            actions = self.heal_all(Path(target_file))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:260:            with os.fdopen(temp_fd, "w", encoding="utf-8") as tf:
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:676:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:699:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:722:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:745:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\CodeValidatorAgent.py:146:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\CodeValidatorAgent.py:177:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\CodeValidatorAgent.py:227:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\CodeValidatorAgent.py:278:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\CognitiveDispositionAgent.py:161:        Context: {json.dumps(context)}
agentic_core\L5_safety\reasoning\CognitiveDispositionAgent.py:163:        Determine if this file should be MOVED, ARCHIVED, or IGNORED based on {json.dumps(self.layer_map)}.
agentic_core\L5_safety\reasoning\CognitiveDispositionAgent.py:199:                file_path = Path(path)
agentic_core\L5_safety\reasoning\CognitiveDispositionAgent.py:227:                            target = Path(target_path)
agentic_core\L5_safety\reasoning\ComplexityAnalyzerAgent.py:57:            report = agent.analyze_repository(Path(target_path))
agentic_core\L5_safety\reasoning\ConstitutionalReviewerAgent.py:72:        constitution_text = json.dumps(rules)
agentic_core\L5_safety\reasoning\CredentialScannerAgent.py:459:                    report_path = Path(self.project_root) / "logs" / "credential_scan_report.json"
agentic_core\L5_safety\reasoning\CredentialScannerAgent.py:463:                        "scan_date": str(Path(__file__).stat().st_mtime),
agentic_core\L5_safety\reasoning\DDDAlignmentAgent.py:256:            self.project_root = Path(self.project_root).resolve()
agentic_core\L5_safety\reasoning\DDDAlignmentAgent.py:522:    agent = DDDAlignmentAgent(project_root=Path(target_dir))
agentic_core\L5_safety\reasoning\DDDAlignmentAgent.py:532:    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
agentic_core\L5_safety\reasoning\DependencyPruningAgent.py:12:    agent = DependencyPruningAgent(project_root=Path("/path/to/project"), ctx=context)
agentic_core\L5_safety\reasoning\DependencyPruningAgent.py:59:        self.project_root: Path = Path(project_root)
agentic_core\L5_safety\reasoning\DependencyPruningAgent.py:124:            _wg.write_text(self.requirements_path, "\n".join(new_lines) + "\n", encoding="utf-8")
agentic_core\L5_safety\reasoning\DocstringComplianceAgent.py:67:        return await self.heal_violation(Path(file_path), self.ctx)
agentic_core\L5_safety\reasoning\DocstringComplianceAgent.py:118:                _wg.write_text(file_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\DocumentationAgent.py:134:                with open(fp, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py:10:    agent = DuplicateCodeDetectorAgent(project_root=Path("/path/to/project"))
agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py:134:        self.project_root: Path = Path(project_root) if project_root else Path.cwd()
agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py:340:                    relative_path = Path(delete_path_str)
agentic_core\L5_safety\reasoning\DynamicSealAgent.py:75:        self.root = Path(root_dir).resolve()
agentic_core\L5_safety\reasoning\DynamicSealAgent.py:176:            seal_result = self._apply_seal(Path(file_path), file_violations, dry_run)
agentic_core\L5_safety\reasoning\DynamicSealAgent.py:201:                print(f"  ✅ {Path(file_path).relative_to(self.root)}")
agentic_core\L5_safety\reasoning\DynamicSealAgent.py:206:                print(f"  ❌ {Path(error['file']).relative_to(self.root)}: {error['error']}")
agentic_core\L5_safety\reasoning\DynamicSealAgent.py:252:                _wg.write_text(file_path, content, encoding="utf-8")
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:313:                agentic_root = Path(*parts[: agentic_idx + 1])
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:330:                    layer_root = Path(*parts[: i + 1])
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:346:                agentic_root = Path(*parts[: agentic_idx + 1])
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:356:                agentic_root = Path(*parts[: agentic_idx + 1])
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:706:                            new_stem = Path(new_name).stem
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1120:                "open(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1125:                "os.remove",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1402:            "open(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1405:            ".write_text(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1406:            ".write_bytes(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1409:            "shutil.move(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1410:            "shutil.copy(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1411:            "shutil.rmtree(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1412:            "os.remove(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1413:            "os.unlink(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1420:            "subprocess.Popen(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1507:            "open(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1508:            ".write_text(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1509:            ".write_bytes(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1510:            "shutil.move(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1511:            "shutil.copy(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1512:            "os.remove(",
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1931:        - Path string references like `Path("apps_rg/...")`
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:2797:                layer_root = Path(*path.parts[: part_idx + 1])
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:2805:                    layer_root = Path(*path.parts[: part_idx + 1])
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:3952:                    conflict_path = Path(dirpath) / filename
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:3954:                    live_path = Path(dirpath) / original_name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:3979:                _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4002:                    new_test_name = f"test_{Path(new_name).stem}.py"
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4005:                    new_test_name = f"{Path(new_name).stem}_test.py"
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4033:                            _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4078:                        _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4128:                        _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4689:                target_path = Path(*parts[: root_index + 1]) / target_dir / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4712:                            target_path = Path(*path.parts[: i + 1]) / "L0_routing" / "scripts" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4721:                            target_path = Path(*path.parts[: i + 1]) / "utils" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4733:                            target_path = Path(*path.parts[: i + 1]) / "engines" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4750:                            target_path = Path(*path.parts[: i + 1]) / target_folder / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4764:                            target_path = Path(*path.parts[: i + 1]) / "L0_routing" / "scripts" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4772:                            target_path = Path(*path.parts[: i + 1]) / "utils" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4780:                            target_path = Path(*path.parts[: i + 1]) / "types" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4788:                            target_path = Path(*path.parts[: i + 1]) / "validators" / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4822:                        target_path = Path(*path.parts[: i + 1]) / purity_relocation_folder / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4834:                        target_path = Path(*path.parts[: i + 1]) / purity_relocation_folder / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4846:                        target_path = Path(*path.parts[: i + 1]) / purity_relocation_folder / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4937:        new_path = Path(*root_parts) / target_folder / path.name
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:5224:        file_path = Path(path)
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:5454:    agent = FileClassificationAgent(project_root=Path("."), dry_run=is_dry_run, validate_only=args.validate)
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:198:    BLUEPRINT_PATH = Path("agentic_core/L5_safety/config/structure_blueprint_config.py")
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:200:    ARCHIVE_ROOT = Path(".healing_backups/unmapped_drift/")
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:436:                with open(discovery_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:809:                path = Path(prop["target"])
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:815:                source = Path(prop["source"])
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:816:                target = Path(prop["target"])
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:889:        Path(tmp_path).replace(self.blueprint_file)
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:1277:                    file_path=Path(drift.get("path", "")) if drift.get("path") else None,
agentic_core\L5_safety\reasoning\GenerativeGuardAgent.py:64:    _root = Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\reasoning\GenerativeGuardAgent.py:205:            normalized_file_path = Path(file_path).as_posix()
agentic_core\L5_safety\reasoning\GitHygieneAgent.py:11:    agent = GitHygieneAgent(project_root=Path("/path/to/repo"), ctx=context)
agentic_core\L5_safety\reasoning\GitHygieneAgent.py:58:        self.project_root: Path = Path(project_root)
agentic_core\L5_safety\reasoning\GospelSyncAgent.py:57:        self.root = Path(root_dir)
agentic_core\L5_safety\reasoning\GovernanceAgent.py:158:            root_path: Any = Path(root_dir).resolve()
agentic_core\L5_safety\reasoning\GovernanceAgent.py:166:            file_path: Any = str(Path(file_path).relative_to(root_path))
agentic_core\L5_safety\reasoning\GovernanceAgent.py:175:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\GovernanceAgent.py:360:        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
agentic_core\L5_safety\reasoning\GovernanceAgent.py:576:        path: Any = Path(file_path)
agentic_core\L5_safety\reasoning\GovernanceAgent.py:603:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\GovernanceAgent.py:636:        path: Any = Path(file_path)
agentic_core\L5_safety\reasoning\GovernanceAgent.py:682:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\GovernanceAgent.py:713:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\GovernanceAgent.py:881:            path_objects = [Path(fp) for fp in file_paths if Path(fp).exists()]
agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:79:        self.project_root = Path(project_root) if project_root else Path.cwd()
agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:250:                with os.fdopen(temp_fd, "w", encoding="utf-8") as tf:
agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:423:                        file_path=Path(path),
agentic_core\L5_safety\reasoning\HierarchyAgent.py:136:            Path(file_path)
agentic_core\L5_safety\reasoning\HierarchyAgent.py:1060:                orphaned_files.append(Path(root) / file)
agentic_core\L5_safety\reasoning\HierarchyAgent.py:1169:            _wg.write_text(gitignore_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\HygieneGuardianAgent.py:105:        self.project_root = Path(project_root).resolve()
agentic_core\L5_safety\reasoning\HygieneGuardianAgent.py:530:                path = Path(root) / f
agentic_core\L5_safety\reasoning\IntegrityGateExecutorAgent.py:583:                        with open(json_file, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\IntegrityGateExecutorAgent.py:608:                        content_str = json.dumps(data)
agentic_core\L5_safety\reasoning\IntegrityGateExecutorAgent.py:635:                                    "validated_at": str(Path(__file__).stat().st_mtime),
agentic_core\L5_safety\reasoning\InterfaceBoundaryAgent.py:62:        self.root = Path(root_dir)
agentic_core\L5_safety\reasoning\InterfaceBoundaryAgent.py:95:        source_path = Path(violation["file"])
agentic_core\L5_safety\reasoning\InterfaceBoundaryAgent.py:126:            print(f"   Recommended: Extract to utils/core_extensions/Interface_{Path(v['file']).stem}.py")
agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py:151:            dummy_paths = [Path("agentic_core/L5_safety/dummy.py")]
agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py:163:            temp_file = Path(tmpdir) / "synthetic_gravity_test.py"
agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py:164:            _wg.write_text(temp_file, "import sys\nprint('gravity test')\n")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:172:            file_path = Path(file_path)
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:257:                        (Path(file_path) if isinstance(file_path, str) else file_path, message),
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:393:                file_path = Path(v["file"]) if isinstance(v, dict) else v[0]
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:571:        _wg.write_text(file_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:680:            python_files = [Path(f) for f in get_agent_files(str(self.project_root))]
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:710:                    _wg.write_text(py_file, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:932:                parts = rel_path.parts if isinstance(rel_path, Path) else Path(str(rel_path)).parts
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:1178:                _wg.write_text(blueprint_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:1426:                    _wg.write_text(blueprint_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:1693:            _wg.write_text(path, content + todo, encoding="utf-8")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:2120:                        _wg.write_text(path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:2158:                            with open(path) as f:
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:2518:                violation_tuples.append((Path(v["file"]), v["reason"]))
agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py:124:        self.root = Path(root_dir).resolve()
agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py:306:repo_root = Path(__file__).resolve().parents[2]
agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py:318:            _wg.write_text(hook_path, hook_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\RedSentinelAgent.py:68:        self.audit_path: Path = Path("observability/audit/fuzz_results.json")
agentic_core\L5_safety\reasoning\RedSentinelAgent.py:208:                with open(self.audit_path) as f:
agentic_core\L5_safety\reasoning\RedSentinelAgent.py:242:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\RedTeamAgent.py:28:TEMPLATE_ROOT = Path(__file__).parents[3] / "templates"
agentic_core\L5_safety\reasoning\RegressionOracleAgent.py:54:        self.test_dir = Path("tests/autogen")
agentic_core\L5_safety\reasoning\ReportLocationAgent.py:13:    agent = ReportLocationAgent(project_root=Path("."))
agentic_core\L5_safety\reasoning\RootHygieneAgent.py:280:                    if target and Path(target).exists():
agentic_core\L5_safety\reasoning\RootHygieneAgent.py:281:                        if Path(target).is_dir():
agentic_core\L5_safety\reasoning\RootHygieneAgent.py:284:                            _wg.remove_file(Path(target))
agentic_core\L5_safety\reasoning\RootHygieneAgent.py:359:    project_root = Path(".")
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:237:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:310:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:395:                Path(self.project_root) / "agentic_core",
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:396:                Path(self.project_root) / "apps_lic",
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:397:                Path(self.project_root) / "apps_rg",
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:398:                Path(self.project_root) / "apps_shared",
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:428:                    report_path = Path(self.project_root) / "logs" / "security_scan_report.json"
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:432:                        "scan_date": str(Path(__file__).stat().st_mtime),
agentic_core\L5_safety\reasoning\SelfUpdatingSafetyEngineAgent.py:222:            with open(self.rules_storage_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py:62:        tool_code: Any = f'#!/usr/bin/env python3\n"""Diagnostic tool generated by Sovereign Toolsmith at {time.time()}"""\n\nimport json\nimport sys\nimport os\nfrom pathlib import Path\nfrom agentic_core.utils.security import safe_popen\n\ndef main():\n    """Execute diagnostic probe."""\n    try:\n        # Basic environment probe\n        diagnostics = {{\n            "timestamp": "{time.time()}",\n            "failure_context": {repr(failure_context)},\n            "environment": {{\n                "cwd": os.getcwd(),\n                "python_version": sys.version,\n                "path": os.environ.get("PATH", "")[:100] + "..." if os.environ.get("PATH") else ""\n            }},\n            "file_system": {{\n                "scripts_dir": str(Path(SCRIPTS_DIR).exists()),\n                "agentic_core_dir": str(Path(AGENTIC_CORE_DIR).exists()),\n            }},\n            "status": "probing_complete"\n        }}\n\n        print(json.dumps(diagnostics, indent=2))\n        return 0\n    except Exception as e:\n        print(json.dumps({{"error": str(e), "status": "error"}}))\n        return 1\n\nif __name__ == "__main__":\n    sys.exit(main())\n'
agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py:118:            process: Any = safe_popen(
agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py:409:            with open(tool_path) as f:
agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py:467:                with open(file_path) as f:
agentic_core\L5_safety\reasoning\SprawlInspectorAgent.py:44:        self.root: Path = Path(target_path)
agentic_core\L5_safety\reasoning\SprawlInspectorAgent.py:65:            p: Path = Path(root)
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:89:                resolved_path: Any = Path(file_path).resolve()
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:90:                with open(resolved_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:129:                resolved_path: Any = Path(file_path).resolve()
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:130:                with open(resolved_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:157:                resolved_path: Any = Path(file_path).resolve()
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:158:                with open(resolved_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:214:            resolved_path = Path(file_path).resolve()
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:215:            with open(resolved_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\StructuralValidatorAgent.py:265:                with os.fdopen(temp_fd, "w", encoding="utf-8") as tf:
agentic_core\L5_safety\reasoning\StructuralValidatorAgent.py:313:                    Path(path),
agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:104:        violations = enforcer.validate_file(Path("my_agent.py"))
agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:110:        enforcer.force_rename_class(Path("BadName.py"), "BadName", "BadNameAgent")
agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:393:            _wg.write_text(file_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:459:            file_path = Path(path) if path else None
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:101:        actions = healer.heal_naming(Path("BadName.py"))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:104:        actions = healer.heal_all(Path("my_agent.py"))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:150:            actions = self.heal_all(Path(target_file))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:217:                    _wg.write_text(file_path, new_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:271:            _wg.write_text(file_path, "\n".join(new_lines), encoding="utf-8")
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:402:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:425:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:448:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:471:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:494:            path = Path(violation.get("path", ""))
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:97:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:127:        project_root: Any = Path(self.ctx.project_root or os.getcwd()).resolve()
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:268:        project_root: Any = Path(self.ctx.project_root or os.getcwd()).resolve()
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:270:            file_path: Any = Path(file_path_str).resolve()
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:301:                resolved_path: Any = Path(file_path).resolve()
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:302:                with open(resolved_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:318:            folder_path = Path(os.getcwd()) / folder_rel
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:354:            resolved_path = Path(file_path).resolve()
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:355:            with open(resolved_path, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\TerritoryChangeHandlerAgent.py:104:        watch_path = Path(AGENTIC_CORE_DIR)
agentic_core\L5_safety\reasoning\TestGeneratorAgent.py:55:        self.tests_dir: Path = tests_dir or Path("tests/autogen")
agentic_core\L5_safety\reasoning\TestGeneratorAgent.py:70:        path = Path(agent_path)
agentic_core\L5_safety\reasoning\TestGeneratorAgent.py:100:            _wg.write_text(test_path, test_content, encoding="utf-8")
agentic_core\L5_safety\reasoning\TypeMechanicAgent.py:75:            with open(fp, encoding="utf-8") as f:  # Depth 2
agentic_core\L5_safety\reasoning\TypeMechanicAgent.py:193:            with open(fp, encoding="utf-8") as f:
agentic_core\L5_safety\reasoning\UnusedCleanupAgent.py:54:        file: Path = Path(file_path)
agentic_core\L5_safety\runners\agent_roster_runner.py:21:    return Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\runners\agent_roster_runner.py:124:        print(json.dumps(result, default=str))
agentic_core\L5_safety\runners\agent_roster_runner.py:129:        print(json.dumps({"success": False, "error": str(e)}))
agentic_core\L5_safety\runners\arch_governor_runner.py:23:    return Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\runners\arch_governor_runner.py:103:    project_root = Path(args.project_root) if args.project_root else get_project_root()
agentic_core\L5_safety\runners\arch_governor_runner.py:116:        print(json.dumps(result, default=str))
agentic_core\L5_safety\runners\arch_governor_runner.py:121:        print(json.dumps({"success": False, "error": str(e)}))
agentic_core\L5_safety\runners\code_validator_runner.py:22:    return Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\runners\code_validator_runner.py:71:        if target_dir in Path(v.file_path).parents:
agentic_core\L5_safety\runners\code_validator_runner.py:113:    project_root = Path(args.project_root) if args.project_root else get_project_root()
agentic_core\L5_safety\runners\code_validator_runner.py:126:        print(json.dumps(result, default=str))
agentic_core\L5_safety\runners\code_validator_runner.py:131:        print(json.dumps({"success": False, "error": str(e)}))
agentic_core\L5_safety\runners\hierarchy_runner.py:23:    return Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\runners\hierarchy_runner.py:89:    project_root = Path(args.project_root) if args.project_root else get_project_root()
agentic_core\L5_safety\runners\hierarchy_runner.py:101:        print(json.dumps(result, default=str))
agentic_core\L5_safety\runners\hierarchy_runner.py:106:        print(json.dumps({"success": False, "error": str(e)}))
agentic_core\L5_safety\runners\orchestrator_runner.py:22:    return Path(__file__).resolve().parent.parent.parent.parent
agentic_core\L5_safety\runners\orchestrator_runner.py:106:    project_root = Path(args.project_root) if args.project_root else get_project_root()
agentic_core\L5_safety\runners\orchestrator_runner.py:115:        print(json.dumps(result, default=str))
agentic_core\L5_safety\runners\orchestrator_runner.py:120:        print(json.dumps({"success": False, "error": str(e)}))
agentic_core\L5_safety\types\agent_audit_result.py:82:    agentic_core = Path("C:/Git/Agentic-Workflow/agentic_core")
agentic_core\L5_safety\types\agent_audit_result_types.py:82:    agentic_core = Path("C:/Git/Agentic-Workflow/agentic_core")
agentic_core\L5_safety\types\file_health_score_types.py:139:            with open(file_path, "rb") as f:
agentic_core\L5_safety\types\heal_llm_seam.py:252:        record_str = json.dumps(self.to_dict(), sort_keys=True)
agentic_core\L5_safety\types\heal_llm_seam.py:274:        current = Path(__file__).resolve()
agentic_core\L5_safety\types\heal_llm_seam.py:284:    content = json.dumps(record.to_dict(), sort_keys=True, indent=2)
agentic_core\L5_safety\types\heal_llm_seam.py:298:    _wg.write_bytes(filepath, content_bytes)
agentic_core\L5_safety\types\heal_llm_seam.py:376:        plan_str = json.dumps(self.to_dict(), sort_keys=True)
agentic_core\L5_safety\types\heal_llm_seam.py:438:    root = Path(repo_root)
agentic_core\L5_safety\types\heal_llm_seam.py:445:        rel_dir = Path(dirpath).relative_to(root)
agentic_core\L5_safety\types\heal_llm_seam.py:463:            rel_path = str(PurePosixPath(rel_dir / filename))
agentic_core\L5_safety\types\heal_llm_seam.py:503:    root = Path(plan.repo_root)
agentic_core\L5_safety\types\learning_types.py:88:            self.storage_path = Path(pattern_storage_path)
agentic_core\L5_safety\types\learning_types.py:92:        self.backup_dir = Path(".canon_memory/backups")
agentic_core\L5_safety\types\learning_types.py:131:            with open(self.pattern_storage_path, encoding="utf-8") as f:
agentic_core\L5_safety\types\safety_types.py:222:            with open(self.rules_storage_path, encoding="utf-8") as f:
agentic_core\L5_safety\types\ssot_relocator_types.py:192:            parts = Path(violation.folder_path).parts
agentic_core\L5_safety\types\ssot_relocator_types.py:194:            target = self.project_root / Path(*target_parts)
agentic_core\L5_safety\types\surgical_context_types.py:136:            file_path=Path(data["file_path"]),
agentic_core\L5_safety\utils\code_tool_runner_core.py:106:                file_path = Path(path)
agentic_core\L5_safety\utils\code_tool_runner_core_util.py:106:                file_path = Path(path)
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:69:        self.checkpoint_file = Path(checkpoint_file)
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:103:            _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:149:                Logger.debug(f"[BATCH] [{i}/{len(violations)}] Skipping (cached): {Path(file_path).name}")
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:154:            Logger.info(f"[BATCH] [{i}/{len(violations)}] Processing: {Path(file_path).name}")
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:195:            return Path(violation.file_path)
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:199:                return Path(file)
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:250:                    Logger.error(f"    Max retries exceeded for {Path(file_path_str).name}")
agentic_core\L5_safety\utils\extract_pattern_util.py:18:SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/canon_agents_pattern.py")
agentic_core\L5_safety\utils\extract_pattern_util.py:19:TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")
agentic_core\L5_safety\utils\extract_pattern_util.py:87:    with open(source_file, encoding="utf-8") as f:
agentic_core\L5_safety\utils\extract_pattern_util.py:118:    with open(source_file, encoding="utf-8") as f:
agentic_core\L5_safety\utils\extract_pattern_util.py:152:    with open(SOURCE_FILE, encoding="utf-8") as f:
agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:21:PROJECT_ROOT = Path(__file__).resolve().parent.parent
agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:33:    with open(DISCOVERY_JSON, encoding="utf-8") as f:
agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:120:        _wg.write_text(file_path, new_source, encoding="utf-8")
agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:155:        file_path = Path(file_path_str)
agentic_core\L5_safety\utils\force_app_depth_util.py:70:            _wg.write_text(app_p1 / "__init__.py", '"""App Core Implementation"""\n')
agentic_core\L5_safety\utils\forge_fortress_util.py:12:root: Any = Path("C:/Git/Agentic-Workflow")
agentic_core\L5_safety\utils\gravity_visitor_util.py:10:    imports = get_file_imports(Path("my_file.py"))
agentic_core\L5_safety\utils\guard_ddd_alignment_util.py:32:    root = Path(root_path)
agentic_core\L5_safety\utils\guard_observability_footprint_util.py:87:    for path in get_python_files(Path(target_dir)):
agentic_core\L5_safety\utils\location_path_util.py:59:    path = Path(file_path)
agentic_core\L5_safety\utils\location_utils_util.py:117:        file_path = Path(file_path)
agentic_core\L5_safety\utils\pre_deploy_check_util.py:26:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L5_safety\utils\set_complexity_health_100_util.py:16:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L5_safety\utils\set_complexity_health_100_util.py:64:    _wg.write_text(DASHBOARD_PATH, updated_content, encoding="utf-8")
agentic_core\L5_safety\utils\ssot_folder_check_util.py:54:        default=Path(".").resolve(),
agentic_core\L5_safety\utils\ssot_folder_check_util.py:81:        print(json.dumps(results, indent=2))
agentic_core\L5_safety\utils\subprocess_security_util.py:163:        cwd_path = Path(cwd)
agentic_core\L5_safety\utils\subprocess_security_util.py:219:def safe_popen(
agentic_core\L5_safety\utils\subprocess_security_util.py:249:        >>> proc = safe_popen(['python', 'server.py'])
agentic_core\L5_safety\utils\subprocess_security_util.py:270:        cwd = str(Path(cwd))
agentic_core\L5_safety\utils\subprocess_security_util.py:277:        proc = subprocess.Popen(
agentic_core\L5_safety\utils\subprocess_security_util.py:320:        command = Path(command).name
agentic_core\L5_safety\utils\tiered_batch_util.py:61:        self.checkpoint_file = Path(checkpoint_file)
agentic_core\L5_safety\utils\tiered_batch_util.py:95:            _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")
agentic_core\L5_safety\utils\tiered_batch_util.py:142:            content = self.agent._read_file_safe(Path(file_path))
agentic_core\L5_safety\utils\tiered_batch_util.py:167:                content = self.agent._read_file_safe(Path(file_path))
agentic_core\L5_safety\utils\tiered_batch_util.py:276:            file_name = Path(file_path).name
agentic_core\L5_safety\utils\tiered_batch_util.py:332:            return Path(violation.file_path)
agentic_core\L5_safety\utils\tiered_batch_util.py:336:                return Path(file)
agentic_core\L5_safety\utils\unified_cst_healer_util.py:371:                _wg.write_text(context.file_path, modified_code, encoding="utf-8")
agentic_core\L5_safety\utils\validate_dashboard_data_sourcing_util.py:12:project_root = Path(__file__).parent.parent
agentic_core\L5_safety\utils\validate_dashboard_data_sourcing_util.py:19:    with open(source_file, encoding="utf-8") as f:
agentic_core\L5_safety\utils\validate_path_ssot_util.py:10:PROJECT_ROOT = Path(__file__).parent.parent
agentic_core\L5_safety\utils\verify_semantic_meta_learning_util.py:23:sys.path.insert(0, str(Path(__file__).parent.parent))
agentic_core\L5_safety\utils\verify_semantic_meta_learning_util.py:146:    project_root = Path(__file__).parent.parent
agentic_core\L5_safety\validators\anti_pattern_scanner_validator.py:150:        self.project_root = Path(project_root).resolve()
agentic_core\L5_safety\validators\ats_validator.py:104:        full_content = json.dumps(resume, ensure_ascii=False)
agentic_core\L5_safety\validators\ats_validator.py:152:        resume_text = json.dumps(resume).lower()
agentic_core\L5_safety\validators\content_quality_validator.py:121:        resume_text = json.dumps(resume, ensure_ascii=False)
agentic_core\L5_safety\validators\content_quality_validator.py:137:        resume_text = json.dumps(resume, ensure_ascii=False)
agentic_core\L5_safety\validators\content_quality_validator.py:162:        resume_text = json.dumps(resume).lower()
agentic_core\L5_safety\validators\content_quality_validator.py:219:        resume_text = json.dumps(resume, ensure_ascii=False)
agentic_core\L5_safety\validators\content_quality_validator.py:235:        text = json.dumps(resume, ensure_ascii=False)
agentic_core\L5_safety\validators\context_validator.py:215:        signature_str = json.dumps(characteristics, sort_keys=True)
agentic_core\L5_safety\validators\context_validator.py:303:        project_root = Path(project_root)
agentic_core\L5_safety\validators\ddd_alignment_validator.py:90:    for path in get_python_files(Path(target_dir)):
agentic_core\L5_safety\validators\dependencygraph_validator.py:202:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\validators\dependencygraph_validator.py:279:    memory_file: Path = field(default_factory=lambda: Path("canon_memory.json"))
agentic_core\L5_safety\validators\dependencygraph_validator.py:327:                with open(self.memory_file) as f:
agentic_core\L5_safety\validators\dependencygraph_validator.py:348:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\validators\dependencygraph_validator.py:448:                with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\validators\gravity_validator.py:394:                    folder = Path(root) / dir_name
agentic_core\L5_safety\validators\hop_validator.py:97:        profile_text = json.dumps(profile).lower()
agentic_core\L5_safety\validators\hop_validator.py:108:        profile_text = json.dumps(profile).lower()
agentic_core\L5_safety\validators\hop_validator.py:167:        json_text = json.dumps(json_data)
agentic_core\L5_safety\validators\intervention_server_validator.py:98:        self.instructions_path = Path(instructions_path)
agentic_core\L5_safety\validators\intervention_server_validator.py:232:            instruction_file = Path("observability/human_instructions.md")
agentic_core\L5_safety\validators\mission_preflight_validator.py:97:        target_path = Path(target_sector).resolve()
agentic_core\L5_safety\validators\mission_preflight_validator.py:205:                    py_file = Path(root) / file
agentic_core\L5_safety\validators\mission_preflight_validator.py:243:                    py_file = Path(root) / file
agentic_core\L5_safety\validators\path_fragility_validator.py:197:    path = Path(base) / "subdir" / "file.txt" """
agentic_core\L5_safety\validators\path_fragility_validator.py:215:    if Path(path).exists():"""
agentic_core\L5_safety\validators\path_fragility_validator.py:221:    path = Path(base) / "subdir" / "file.txt"
agentic_core\L5_safety\validators\read_file_args_validator.py:27:        if Path(v).is_absolute():
agentic_core\L5_safety\validators\read_file_args_validator.py:41:        if Path(v).is_absolute():
agentic_core\L5_safety\validators\read_file_args_validator.py:55:        if Path(v).is_absolute():
agentic_core\L5_safety\validators\read_file_args_validator.py:69:        if Path(v).is_absolute():
agentic_core\L5_safety\validators\read_file_args_validator.py:81:        if Path(v).is_absolute():
agentic_core\L5_safety\validators\read_file_args_validator.py:94:        if Path(v).is_absolute():
agentic_core\L5_safety\validators\read_file_args_validator.py:123:        if v and Path(v).is_absolute():
agentic_core\L5_safety\validators\structure_drift_validator.py:16:PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
agentic_core\L5_safety\validators\structure_drift_validator.py:61:    content_for_hash = json.dumps(
agentic_core\L5_safety\validators\structure_drift_validator.py:89:    with open(manifest_path, encoding="utf-8") as f:
agentic_core\L5_safety\config\structure_blueprint\artifacts.py:442:    file_ext = Path(filename).suffix.lower()
agentic_core\L5_safety\config\structure_blueprint\ssot.py:212:    current = Path(__file__).resolve()
agentic_core\L5_safety\config\structure_blueprint\ssot.py:228:        path = Path(path).resolve()
agentic_core\L5_safety\config\structure_blueprint\ssot.py:229:        project_root = Path(project_root).resolve()
agentic_core\L5_safety\config\structure_blueprint\ssot.py:238:    project_root = Path(project_root).resolve()
agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:32:    with open(path, "rb") as f:
agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:128:            with open(baseline_path, encoding="utf-8") as bf:
agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:159:            with open(baseline_path, encoding="utf-8") as bf:
agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:177:            with open(baseline_path, encoding="utf-8") as bf:
agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:211:            with open(wf_path, encoding="utf-8") as wf:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:202:            with open(bp, encoding="utf-8") as bf:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:225:        with open(hp, encoding="utf-8") as hf:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:254:        with open(fpath, encoding="utf-8") as f:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:463:            with open(fpath, encoding="utf-8", errors="replace") as f:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:539:            with open(baseline_path, encoding="utf-8") as bf:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:652:    with open(shim_path, encoding="utf-8") as f:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:722:    with open(constants_path, encoding="utf-8") as f:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:801:        with open(hash_path, encoding="utf-8") as hf:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:839:            with open(fpath, encoding="utf-8", errors="replace") as f:
agentic_core\L5_safety\config\structure_blueprint\_verify.py:924:    enforcement_root = _Path(root)
agentic_core\L5_safety\config\structure_blueprint\_verify.py:979:    blueprint_dir = _Path(__file__).resolve().parent
agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py:61:        _wg.write_text(hash_path, current_hash + "\n", encoding="utf-8")
agentic_core\L5_safety\config\structure_blueprint\enforcement\cross_layer.py:45:_BASELINE_PATH = Path(__file__).resolve().parent / "known_debt_baseline.json"
agentic_core\L5_safety\config\structure_blueprint\enforcement\import_graph.py:136:                    fpath = Path(dirpath) / fn
agentic_core\L5_safety\config\structure_blueprint\enforcement\territory_diff.py:25:_OPTIONAL_BASELINE_PATH = Path(__file__).resolve().parent / "missing_optional_baseline.json"
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:78:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:110:                    repo_relative = str(PurePosixPath(file_path.relative_to(self.repo_root)))
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:199:        json_output = json.dumps(result, indent=2, sort_keys=True)
agentic_core\L5_safety\enforcement\governance\artifacts_guard.py:38:        with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L5_safety\enforcement\governance\artifacts_guard.py:103:    root_path = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\governance\cache_guard.py:43:                file_path = Path(root) / file
agentic_core\L5_safety\enforcement\governance\cache_guard.py:164:    root_path = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\governance\docs_structure_guard.py:28:        with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\governance\docs_structure_guard.py:116:    root_path = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\governance\logs_guard.py:59:        prefix_path = Path(*relative_path.parts[: i + 1])
agentic_core\L5_safety\enforcement\governance\logs_guard.py:83:        with open(file_path, encoding="utf-8", errors="ignore") as f:
agentic_core\L5_safety\enforcement\governance\logs_guard.py:181:    root_path = Path(__file__).parent.parent.parent
agentic_core\L5_safety\enforcement\security\credential_guard.py:78:            with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\security\credential_guard.py:92:        with open(file_path, encoding="utf-8") as f:
agentic_core\L5_safety\enforcement\security\credential_guard.py:147:    root_path = Path(__file__).parent.parent.parent
agentic_core\L6_observability\dashboards\dashboard_generator.py:119:            with open(self.discovery_path, encoding="utf-8") as f:
agentic_core\L6_observability\dashboards\dashboard_generator.py:811:            new_json = json.dumps(data, indent=2)
agentic_core\L6_observability\dashboards\dashboard_generator.py:814:            agent_json = json.dumps(per_agent_data, indent=2)
agentic_core\L6_observability\dashboards\dashboard_generator.py:830:            assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\dashboards\dashboard_generator.py:831:            _wg.write_text(self.dashboard_path, new_html, encoding="utf-8")
agentic_core\L6_observability\dashboards\dashboard_qa.py:30:        self.root = Path(__file__).parent.parent
agentic_core\L6_observability\dashboards\verify_dashboard_e2e_playwright_util.py:103:    serve_path = Path(__file__).parent / "serve_dashboard.py"
agentic_core\L6_observability\dashboards\verify_dashboard_e2e_playwright_util.py:105:    proc = safe_popen([sys.executable, str(serve_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
agentic_core\L6_observability\dashboards\verify_dashboard_e2e_playwright_util.py:131:        screenshot_dir = Path(__file__).parent
agentic_core\L6_observability\enforcement\outcome_logger.py:40:        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
agentic_core\L6_observability\enforcement\reasoning_streamer.py:29:    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
agentic_core\L6_observability\enforcement\reasoning_streamer.py:56:        self.stream_dir = Path(stream_dir)
agentic_core\L6_observability\enforcement\reasoning_streamer.py:88:                    _wg.append_text(self.log_path, json.dumps(payload) + "\n")
agentic_core\L6_observability\enforcement\reasoning_streamer.py:90:                        message = json.dumps(payload)
agentic_core\L6_observability\enforcement\reasoning_streamer.py:117:                    json.dumps(
agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:29:    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:56:        self.stream_dir = Path(stream_dir)
agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:88:                    _wg.append_text(self.log_path, json.dumps(payload) + "\n")
agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:90:                        message = json.dumps(payload)
agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:117:                    json.dumps(
agentic_core\L6_observability\engines\SovereignHealthMonitor.py:57:            self.redis.lpush("sovereign_health_history", json.dumps(snapshot))
agentic_core\L6_observability\engines\SovereignHealthMonitor.py:62:                json.dumps({"compliance_score": score, "total_fixes": fixes, "last_updated": timestamp}),
agentic_core\L6_observability\golden_evaluation\injection_regression_suite.py:38:        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
agentic_core\L6_observability\golden_evaluation\injection_regression_suite.py:40:    golden_dir = Path(data_root) / "golden"
agentic_core\L6_observability\golden_evaluation\injection_regression_suite.py:58:    with open(injection_file, encoding="utf-8") as f:
agentic_core\L6_observability\golden_evaluation\injection_regression_suite.py:96:        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py:37:        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py:39:    golden_dir = Path(data_root) / "golden"
agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py:56:    with open(resume_file, encoding="utf-8") as f:
agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py:92:        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py:39:        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py:41:    golden_dir = Path(data_root) / "golden"
agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py:59:    with open(tool_file, encoding="utf-8") as f:
agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py:108:        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L6_observability\types\detection_signal.py:74:        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L6_observability\types\detection_signal.py:96:        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
agentic_core\L6_observability\utils\fix_testing_observability_util.py:27:PROJECT_ROOT = Path(__file__).resolve().parent.parent
agentic_core\L6_observability\utils\fix_testing_observability_util.py:39:    with open(DISCOVERY_JSON, encoding="utf-8") as f:
agentic_core\L6_observability\utils\fix_testing_observability_util.py:97:            assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\utils\fix_testing_observability_util.py:98:            _wg.write_text(file_path, source, encoding="utf-8")
agentic_core\L6_observability\utils\fix_testing_observability_util.py:151:            assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\utils\fix_testing_observability_util.py:152:            _wg.write_text(file_path, new_source, encoding="utf-8")
agentic_core\L6_observability\utils\fix_testing_observability_util.py:185:        file_path = Path(file_path_str)
agentic_core\L6_observability\utils\integrity_report_generator_util.py:386:        assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\utils\integrity_report_generator_util.py:387:        _wg.write_text(output_path, report_content, encoding="utf-8")
agentic_core\L6_observability\dashboards\core\dashboard_handler.py:20:        dashboard_dir = Path(__file__).parent
agentic_core\L6_observability\dashboards\core\dashboard_handler.py:38:    dashboard_dir = Path(__file__).parent
agentic_core\L6_observability\dashboards\core\experiencein_config.py:45:RUNTIME_STATE_FILE = Path("runtime_state.json")
agentic_core\L6_observability\dashboards\core\StaticFileApp.py:51:                with open(filepath, "rb") as f:
agentic_core\prompt_governance\core\prompt_assembler.py:86:        return _json.dumps(obj)
agentic_core\prompt_governance\core\prompt_assembler.py:211:        template_dir = Path("./templates/prompts")
agentic_core\prompt_governance\core\prompt_assembler.py:219:                with open(file_path, encoding="utf-8") as f:
agentic_core\prompt_governance\core\prompt_assembler.py:481:                value_str = json.dumps(value, indent=2)
agentic_core\prompt_governance\core\prompt_assembler.py:627:        template_dir = Path("./templates/prompts")
agentic_core\prompt_governance\core\prompt_assembler.py:631:        with open(file_path, "w", encoding="utf-8") as f:
agentic_core\prompt_governance\core\sovereign_prompt_renderer.py:63:            template_root = Path(__file__).parent / "templates"
agentic_core\prompt_governance\scripts\audit_registry_linkages.py:17:        with open(registry_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\audit_registry_linkages.py:27:        with open(template_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\audit_registry_linkages.py:121:    script_dir = Path(__file__).parent
agentic_core\prompt_governance\scripts\detect_template_drift.py:19:        with open(registry_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\detect_template_drift.py:106:    script_dir = Path(__file__).parent
agentic_core\prompt_governance\scripts\dry_run_compiler.py:122:    script_dir = Path(__file__).parent
agentic_core\prompt_governance\scripts\file_intent.py:381:        target_dir = Path(sys.argv[1])
agentic_core\prompt_governance\scripts\file_intent.py:383:        target_dir = Path("agentic_core/prompt_governance")
agentic_core\prompt_governance\scripts\harden_templates.py:99:        with open(file_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\harden_templates.py:124:            with open(file_path, "w", encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\harden_templates.py:149:        base_dir = Path(args.base_dir)
agentic_core\prompt_governance\scripts\import_violation_visitor.py:72:        with open(file_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\import_violation_visitor.py:126:    script_dir = Path(__file__).parent
agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:19:        with open(registry_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:30:        with open(registry_path, "w", encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:31:            json.dump(registry, f, indent=2, ensure_ascii=False)
agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:95:    script_dir = Path(__file__).parent
agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:114:        shutil.copy2(registry_path, backup_path)
agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:127:    registry["last_sync_date"] = str(Path(__file__).stat().st_mtime)
agentic_core\prompt_governance\scripts\template_render_visitor.py:19:        with open(full_path, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\template_render_visitor.py:98:        template_path = Path(template_name)
agentic_core\prompt_governance\scripts\template_render_visitor.py:148:            with open(py_file, encoding="utf-8") as f:
agentic_core\prompt_governance\scripts\template_render_visitor.py:169:    script_dir = Path(__file__).parent
agentic_core\prompt_governance\validation\validate_assembly.py:23:REPO_ROOT = Path(__file__).resolve().parents[4]
agentic_core\prompt_governance\validation\validate_assembly.py:45:    with open(MANIFEST_PATH, encoding="utf-8") as f:
agentic_core\runtime\config\model_provider_config.py:40:PROJECT_ROOT = Path(__file__).parent.parent.absolute()
agentic_core\runtime\config\prompt_injection_loader_config.py:30:        injection_dir: Path = Path("data/injections")
agentic_core\runtime\config\prompt_injection_loader_config.py:92:                with open(file_path, encoding="utf-8") as f:
agentic_core\runtime\config\prompt_injection_loader_config.py:196:        with open(file_path, "w", encoding="utf-8") as f:
agentic_core\runtime\config\prompt_injection_loader_config.py:197:            json.dump(injection, f, indent=2, default=str)
agentic_core\runtime\config\security_level_config.py:249:        resume_str = json.dumps(resume)
agentic_core\runtime\config\security_level_config.py:597:        resume_str = json.dumps(resume).lower()
agentic_core\runtime\config\security_level_config.py:686:                        items.append(json.dumps(item, indent=2))
agentic_core\runtime\config\security_level_config.py:691:                section_text = f"# {section_name.upper()}\n{json.dumps(content)}"
agentic_core\runtime\engine\ast_relocator.py:13:    project_root = Path(__file__).resolve().parents[3]
agentic_core\runtime\types\cache_entry_types.py:142:            context_str = json.dumps(context, sort_keys=True, default=str)
agentic_core\runtime\types\cache_entry_types.py:168:                query_text += f"::{json.dumps(context, sort_keys=True, default=str)}"
agentic_core\runtime\types\cache_entry_types.py:215:                set_text += f"::{json.dumps(context, sort_keys=True, default=str)}"
agentic_core\runtime\types\cost_governor_types.py:159:            return json.dumps(self.get_usage_summary(), indent=2)
agentic_core\runtime\types\sovereign_events_types.py:115:            stream_payload = {"event": json.dumps(event_data)}
agentic_core\runtime\types\sovereign_events_types.py:151:                    {"event": json.dumps(event.model_dump())},
agentic_core\runtime\utils\discovery_parser_util.py:42:    with open(discovery_path, encoding="utf-8") as f:
agentic_core\runtime\utils\discovery_parser_util.py:48:AGENT_METADATA: Final[Mapping[str, Any]] = load_hardened_agent_metadata(Path("agent_discovery_full.json"))
agentic_core\runtime\utils\discovery_util.py:39:        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
agentic_core\runtime\utils\discovery_util.py:86:            with open(file_path, encoding="utf-8") as f:
agentic_core\runtime\utils\file_cache_util.py:111:        current = Path(__file__).resolve()
agentic_core\runtime\utils\file_cache_util.py:123:        return Path(__file__).resolve().parent.parent.parent
agentic_core\runtime\utils\file_cache_util.py:148:                    file_path = Path(root) / file
agentic_core\runtime\utils\sovereign_index_util.py:110:        self._project_root = Path(project_root).resolve()
agentic_core\runtime\utils\sovereign_index_util.py:142:                resolved = Path(project_root).resolve()
agentic_core\runtime\utils\sovereign_index_util.py:377:                            self._scan_directory(Path(entry.path))
agentic_core\runtime\utils\sovereign_index_util.py:379:                            self._all_files.append(Path(entry.path))
```

## Wave 1 — Fence References Audit (raw)
```
agentic_core\L0_routing\enforcement\mutation_prohibition.py:42:def assert_no_persistent_write(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:92:    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:104:    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:119:    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:132:    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:143:    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:154:    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:166:    assert_no_persistent_write(layer, "os.rename", str(dst), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:179:    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:195:    assert_no_persistent_write(layer, "mutation_guard_enter")
agentic_core\L0_routing\enforcement\mutation_prohibition.py:205:    "assert_no_persistent_write",
agentic_core\L0_routing\meta_control\meta_apply.py:24:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\meta_control\meta_apply.py:147:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\reasoning\RootCustomsAgent.py:23:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\reasoning\RootCustomsAgent.py:563:            assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py:28:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py:410:                        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:16:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:118:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:13:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:127:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:11:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:112:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:11:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:146:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\agent_analysis_config.py:23:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\agent_analysis_config.py:307:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\agent_capability_supplement_util.py:29:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\agent_capability_supplement_util.py:406:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\archive_duplicates_util.py:6:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\archive_duplicates_util.py:47:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\archive_duplicate_tests_util.py:14:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\archive_duplicate_tests_util.py:57:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:23:from agentic_core.L0_routing.enforcement.mutation_prohibition import (
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:24:    assert_no_persistent_write,
agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:101:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:14:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:61:                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:79:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\class_info.py:19:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\class_info.py:734:        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\code_entity.py:25:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\code_entity.py:540:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\collision_resolver.py:16:from agentic_core.L0_routing.enforcement.mutation_prohibition import (
agentic_core\L0_routing\scripts\colors.py:25:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\colors.py:151:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\core_synthesis_executor.py:13:from agentic_core.L0_routing.enforcement.mutation_prohibition import (
agentic_core\L0_routing\scripts\core_synthesis_executor.py:14:    assert_no_persistent_write,
agentic_core\L0_routing\scripts\core_synthesis_executor.py:99:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\core_synthesis_executor.py:246:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\core_synthesis_executor.py:280:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\c_c_measurement.py:16:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\c_c_measurement.py:180:                assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\debris_hunter.py:17:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\debris_hunter.py:85:                assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\disposition.py:17:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\disposition.py:459:        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:39:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\execute_ssot.py:1206:                assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:1223:                    assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:1357:                    assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:1368:                    assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\execute_ssot.py:2260:            assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\extract_net.py:11:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\extract_net.py:19:        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\find_corrupted_files_util.py:23:from agentic_core.L0_routing.enforcement.mutation_prohibition import (
agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py:12:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py:57:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:41:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\forensic_discovery_prep.py:309:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:25:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:161:                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:171:                        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\root_hygiene_util.py:14:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\root_hygiene_util.py:57:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\root_hygiene_util.py:69:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\root_hygiene_util.py:71:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\root_hygiene_util.py:92:            assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\root_hygiene_util.py:96:        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\root_hygiene_util.py:110:        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py:17:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py:114:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:24:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:349:        assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\scripts\ssot_cli.py:34:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\scripts\ssot_cli.py:167:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\guardian_contract.py:27:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\types\guardian_contract.py:936:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\guardian_contract_types.py:27:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\types\guardian_contract_types.py:936:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\integration_contract.py:16:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\types\integration_contract.py:80:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\types\integration_contract_types.py:16:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\types\integration_contract_types.py:80:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\add_test_coverage_util.py:12:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\add_test_coverage_util.py:70:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\add_test_coverage_util.py:432:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\complexity_visitor_util.py:39:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\complexity_visitor_util.py:1288:                    assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\complexity_visitor_util.py:1668:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\complexity_visitor_util.py:1690:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\core_integrity_util.py:15:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\core_integrity_util.py:69:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\core_integrity_util.py:92:            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\core_integrity_util.py:151:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\file_utils_util.py:17:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\file_utils_util.py:95:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\file_utils_util.py:195:        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_all_tunnels_util.py:12:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\fix_all_tunnels_util.py:43:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_depth_violations_util.py:13:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\fix_depth_violations_util.py:50:                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_depth_violations_util.py:54:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:10:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:24:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:33:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:41:        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\fix_remaining_depth_util.py:50:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\force_annexation_util.py:15:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\force_annexation_util.py:52:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\force_annexation_util.py:59:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\scorched_earth_merge_util.py:15:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\scorched_earth_merge_util.py:84:            assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\scorched_earth_merge_util.py:93:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:13:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:38:                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\sovereign_convergence_util.py:12:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\sovereign_convergence_util.py:30:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\sovereign_convergence_util.py:33:                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\structural_fix_util.py:11:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\structural_fix_util.py:70:        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\structural_fix_util.py:77:        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\structural_fix_util.py:92:            assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py:12:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py:53:    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L2_execution\tools\write_gateway.py:60:    if os.environ.get("AGENTIC_DENY_SOURCE_MUTATION") != "1":
agentic_core\L3_orchestration\enforcement\mission_runner.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\engines\action_router.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\engines\autonomous_execution_engine.py:6:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:10:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:30:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:32:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:88:    assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L3_orchestration\types\telepathy_interface_types.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\enforcement\mission_historian.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\enforcement\mission_historian_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\memory\blob_storage_provider.py:4:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\memory\blob_storage_provider.py:18:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L4_state\memory\blob_storage_provider.py:98:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\memory\blob_storage_provider.py:100:        assert_no_persistent_write("L4", "shutil.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\memory\runtime_state_guard.py:7:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L4_state\memory\runtime_state_guard.py:8:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\memory\runtime_state_guard.py:82:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\memory\runtime_state_guard.py:94:                assert_no_persistent_write("L4", "os.mutate")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:41:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:282:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\CheckpointManagerAgent.py:586:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\GravityStateAgent.py:8:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\reasoning\GravityStateAgent.py:40:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L4_state\reasoning\GravityStateAgent.py:212:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\reasoning\GravityStateAgent.py:353:            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\types\cycle_types.py:12:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L4_state\types\cycle_types.py:13:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\types\cycle_types.py:306:        assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\types\validation_context_types.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\utils\experience_buffer_util.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\utils\experience_buffer_util.py:28:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L4_state\utils\experience_buffer_util.py:61:            assert_no_persistent_write("L4", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\utils\experience_buffer_util.py:97:                assert_no_persistent_write("L4", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L4_state\utils\local_disk_adapter.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L4_state\utils\local_disk_adapter_util.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\config\gravity_leak_config.py:4:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\activation_gate.py:7:2. Mutation prohibition guard  (assert_no_persistent_write)
agentic_core\L5_safety\enforcement\activation_gate.py:31:        "agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer",
agentic_core\L5_safety\enforcement\activation_gate.py:32:        "assert_no_persistent_write",
agentic_core\L5_safety\enforcement\activation_gate.py:33:        "mutation_prohibition",
agentic_core\L5_safety\enforcement\agent_info.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\agent_info_enforcer.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\airlock_trimmer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\airlock_trimmer_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\archival_gatekeeper.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\circular_import_fixer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\circular_import_fixer_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\final_airlock_trimmer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\final_airlock_trimmer_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\healing_invocation_audit.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\import_surgeon.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\module_collision_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\module_collision_guardrail.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\mutation_prohibition.py:20:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\mutation_prohibition.py:42:def assert_no_persistent_write(
agentic_core\L5_safety\enforcement\mutation_prohibition.py:92:    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:104:    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:119:    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:131:    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:142:    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:153:    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:165:    assert_no_persistent_write(layer, "os.rename", str(dst), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:178:    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition.py:194:    assert_no_persistent_write(layer, "mutation_guard_enter")
agentic_core\L5_safety\enforcement\mutation_prohibition.py:204:    "assert_no_persistent_write",
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:20:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:42:def assert_no_persistent_write(
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:92:    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:104:    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:119:    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:131:    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:142:    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:153:    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:165:    assert_no_persistent_write(layer, "os.rename", str(dst), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:178:    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:194:    assert_no_persistent_write(layer, "mutation_guard_enter")
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:204:    "assert_no_persistent_write",
agentic_core\L5_safety\enforcement\namespace_medic.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\pytest_config_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:6:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:6:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\ssot_import_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\system.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\system_enforcer.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\governance\lazy_seam_classifier.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\governance\lazy_seam_scanner.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:8:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\BenchmarkingAgent.py:8:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:13:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\CodeHealerAgent.py:43:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\CognitiveDispositionAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\CredentialScannerAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\DependencyPruningAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\DocstringComplianceAgent.py:10:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\DynamicSealAgent.py:4:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\GenerativeGuardAgent.py:11:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\GovernanceAgent.py:11:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:6:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\HierarchyAgent.py:11:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\IntegrityGateExecutorAgent.py:10:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py:11:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\LocationHealerAgent.py:33:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py:4:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\RedSentinelAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\RegressionOracleAgent.py:11:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\ReportLocationAgent.py:38:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\RootHygieneAgent.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\SelfUpdatingSafetyEngineAgent.py:8:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py:14:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\SprawlInspectorAgent.py:10:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:10:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\StructuralValidatorAgent.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\StructureHealerAgent.py:38:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:10:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\reasoning\TestGeneratorAgent.py:14:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\types\heal_llm_seam.py:19:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\types\learning_types.py:8:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\types\safety_types.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\types\ssot_relocator_types.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\extract_pattern_util.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\force_app_depth_util.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\forge_fortress_util.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\set_complexity_health_100_util.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\tiered_batch_util.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\utils\unified_cst_healer_util.py:19:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\validators\dependencygraph_validator.py:5:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\validators\report_location_validator.py:29:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\validators\structure_drift_validator.py:14:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:19:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\config\structure_blueprint\_verify.py:24:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py:16:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\governance\artifacts_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\governance\cache_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\governance\docs_structure_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\governance\logs_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L5_safety\enforcement\security\credential_guard.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L6_observability\dashboards\dashboard_generator.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L6_observability\dashboards\dashboard_generator.py:16:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L6_observability\dashboards\dashboard_generator.py:830:            assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\enforcement\reasoning_streamer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:3:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L6_observability\utils\fix_testing_observability_util.py:1:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L6_observability\utils\fix_testing_observability_util.py:18:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L6_observability\utils\fix_testing_observability_util.py:97:            assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\utils\fix_testing_observability_util.py:151:            assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
agentic_core\L6_observability\utils\integrity_report_generator_util.py:26:from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
agentic_core\L6_observability\utils\integrity_report_generator_util.py:27:from agentic_core.L2_execution.tools import write_gateway as _wg
agentic_core\L6_observability\utils\integrity_report_generator_util.py:386:        assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
```

## Wave 3 — Tests (unit_min_deps)
```
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 8 items

tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 37%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 50%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 62%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 75%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 87%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m8 passed[0m[32m in 0.03s[0m[32m ==============================[0m


```

## Wave 3 — Tests (full pytest)
```
❌ agent_discovery_full.json not found
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4209 items / 46 errors
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
INTERNALERROR>     config.hook.pytest_collection(session=session)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
INTERNALERROR>     session.perform_collect()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
INTERNALERROR>     self.items.extend(self.genitems(node))
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
INTERNALERROR>     rep = collect_one_node(node)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
INTERNALERROR>     rep = yield
INTERNALERROR>           ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
INTERNALERROR>     call = CallInfo.from_call(
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
INTERNALERROR>     result: TResult | None = func()
INTERNALERROR>                              ^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
INTERNALERROR>     return list(collector.collect())
INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
INTERNALERROR>     self._register_setup_module_fixture()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
INTERNALERROR>     ^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
INTERNALERROR>     self._obj = obj = self._getobj()
INTERNALERROR>                       ^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
INTERNALERROR>     return importtestmodule(self.path, self.config)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
INTERNALERROR>     mod = import_path(
INTERNALERROR>           ^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
INTERNALERROR>     importlib.import_module(module_name)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
INTERNALERROR>     exec(co, module.__dict__)
INTERNALERROR>   File "c:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
INTERNALERROR>     sys.exit(1)
INTERNALERROR> SystemExit: 1

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.54s[0m[31m ========================[0m

mainloop: caught unexpected SystemExit!

```

## Wave 3 — Full Pytest Fail Lines
```

```

## Wave 3 — Repro Run Output
```
ARGV=['python', '-m', 'agentic_core.L0_routing.scripts.execute_ssot', '--domains', 'L0_routing,L2_execution,L3_orchestration,L5_safety']



STDERR:
ERROR: Direct invocation of execute_ssot.py is not supported.
Use the entrypoint instead:
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy


```

## Wave 3 — Protected Root Mutation Proof
### Before
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```
### After
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

## RCA (<=12 lines)
- Runner previously allowed protected-root writes because enforcement was not structurally bound at the L2 write boundary.
- A writable repo root meant agent behavior could persist mutations into agentic_core/ during SSOT runs.
- Fix: add enforce_protected_root() (deterministic) and call it in write_gateway before any filesystem write.
- Override is explicit via --allow-protected-root-mutation and is logged once, preventing accidental escalation.
- Domain mode adds forced dry_run for protected domains when override is disabled, reducing accidental mutation attempts.

## Follow-ons (out-of-scope)
- (1) Add policy-level audit to enumerate all durable write entrypoints across L2 tools.
- (2) Extend protected roots list to include additional repo-critical directories if needed.
- (3) Add telemetry event for blocked write attempts with target path + agent id.
