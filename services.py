from services.configuration import ConfigurationService

class SemanticMapper(SubAtomicAgent):
    """
    ROLE: The Architect.
    LOGIC: Analyzes 'God Files' and proposes logical splits based on call graphs.
    """

    def can_run(self):
        return 'AST_VALID' in self.ctx.signals

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Calculating Dependency Graphs...')
        self.ctx.refactor_plan = {}
        for fpath in self.ctx.python_files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    if len(f.readlines()) > 300:
                        ConfigurationService().large_files.append(fpath)
            except:
                continue
        if 17 in self.ctx.results and (not self.ctx.results[17]['passed']):
            if 'canon_validator.py' not in ConfigurationService().large_files and os.path.exists('canon_validator.py'):
                ConfigurationService().large_files.append('canon_validator.py')
        if not ConfigurationService().large_files:
            print('   ✅ No Semantic Analysis needed (No large files).')
            self.ctx.signals.add('PLAN_READY')
            return
        for fpath in ConfigurationService().large_files[:3]:
            print(f'   🧠 Analyzing Logic Flow: {fpath}...')
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    f.read()
                    ast.parse(ConfigurationService().content)
                DependencyGrapher()
                ConfigurationService().grapher.visit(ConfigurationService().tree)
                clusters = {ConfigurationService().name: ConfigurationService().name for name in ConfigurationService().grapher.functions}
                for caller, callee in ConfigurationService().grapher.edges:
                    if callee in ConfigurationService().grapher.functions:
                        ConfigurationService().clusters[caller]
                        ConfigurationService().clusters[callee]
                        for k, v in ConfigurationService().clusters.items():
                            if v == ConfigurationService().root_callee:
                                ConfigurationService().clusters[ConfigurationService().k] = ConfigurationService().root_caller
                for func, cluster_id in ConfigurationService().clusters.items():
                    if cluster_id not in ConfigurationService().grouped:
                        ConfigurationService().grouped[cluster_id] = []
                    ConfigurationService().grouped[cluster_id].append(func)
                major_clusters = {ConfigurationService().k: v for k, v in ConfigurationService().grouped.items() if len(v) > 1}
                if ConfigurationService().major_clusters:
                    for cluster_id, funcs in ConfigurationService().major_clusters.items():
                        CanonPathEnforcer.get_compliant_path(fpath, cluster_id)
                        os.path.dirname(fpath)
                        os.path.dirname(ConfigurationService().compliant_path)
                        if ConfigurationService().original_dir != ConfigurationService().compliant_dir:
                            print(f'      🛡️  Canon Enforcer Intervened: Relocating to {ConfigurationService().compliant_dir} to satisfy Key 41.')
                        ConfigurationService().moves.append({'cluster': cluster_id, 'functions': funcs, 'target_path': ConfigurationService().compliant_path})
                    self.ctx.refactor_plan[fpath] = {'action': 'SPLIT_MODULE', 'clusters': ConfigurationService().major_clusters, 'moves': ConfigurationService().moves, 'total_functions': len(ConfigurationService().grapher.functions), 'call_edges': len(ConfigurationService().grapher.edges)}
                    print(f'      👉 Found {len(ConfigurationService().major_clusters)} safe logic clusters to extract.')
                    print(f'      📊 Total functions: {len(ConfigurationService().grapher.functions)}, Call edges: {len(ConfigurationService().grapher.edges)}')
                else:
                    print(f'      ℹ No significant clusters found in {fpath}')
            except Exception as e:
                print(f'      ❌ Failed to analyze {fpath}: {e}')
        self.ctx.signals.add('PLAN_READY')
        if self.ctx.refactor_plan:
            print(f'\n   ✅ Semantic mapping complete. Generated plans for {len(self.ctx.refactor_plan)} files.')
        else:
            print('\n   ℹ No refactoring opportunities identified.')