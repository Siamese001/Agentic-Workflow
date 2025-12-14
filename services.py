import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)

class SemanticMapper(SubAtomicAgent):
    """
    ROLE: The Architect.
    LOGIC: Analyzes 'God Files' and proposes logical splits based on call graphs.
    """

    def can_run(self):
        return 'AST_VALID' in self.ctx.signals

    def execute(self):
        ConfigurationService().logger.info(f'\n[>>>] {self.name} ACTIVATED: Calculating Dependency Graphs...')
        self.ctx.refactor_plan = {}
        for fpath in self.ctx.python_files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    f.read()
                    if len(ConfigurationService().content.splitlines()) > 300:
                        ConfigurationService().large_files.append(fpath)
            except Exception as e:
                ConfigurationService().logger.info(f'      ❌ Failed to read {fpath}: {e}')
                continue
        if 17 in self.ctx.results and (not self.ctx.results[17]['passed']):
            if 'canon_validator.py' not in ConfigurationService().large_files and os.path.exists('canon_validator.py'):
                ConfigurationService().large_files.append('canon_validator.py')
        if not ConfigurationService().large_files:
            ConfigurationService().logger.info('   No Semantic Analysis needed (No large files).')
            self.ctx.signals.add('PLAN_READY')
            return
        for fpath in ConfigurationService().large_files[:3]:
            ConfigurationService().logger.info(f'   🧠 Analyzing Logic Flow: {fpath}...')
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
                            ConfigurationService().logger.info(f'      🛡️  Canon Enforcer Intervened: Relocating to {ConfigurationService().compliant_dir} to satisfy Key 41.')
                        ConfigurationService().moves.append({'cluster': cluster_id, 'functions': funcs, 'target_path': ConfigurationService().compliant_path})
                    self.ctx.refactor_plan[fpath] = {'action': 'SPLIT_MODULE', 'clusters': ConfigurationService().major_clusters, 'moves': ConfigurationService().moves, 'total_functions': len(ConfigurationService().grapher.functions), 'call_edges': len(ConfigurationService().grapher.edges)}
                    ConfigurationService().logger.info(f'      👉 Found {len(ConfigurationService().major_clusters)} safe logic clusters to extract.')
                    ConfigurationService().logger.info(f'      📊 Total functions: {len(ConfigurationService().grapher.functions)}, Call edges: {len(ConfigurationService().grapher.edges)}')
                else:
                    ConfigurationService().logger.info(f'      ℹ No significant clusters found in {fpath}')
            except Exception as e:
                ConfigurationService().logger.info(f'      ❌ Failed to analyze {fpath}: {e}')
        self.ctx.signals.add('PLAN_READY')
        if self.ctx.refactor_plan:
            ConfigurationService().logger.info(f'\n   ✅ Semantic mapping complete. Generated plans for {len(self.ctx.refactor_plan)} files.')
        else:
            ConfigurationService().logger.info('\n   ℹ No refactoring opportunities identified.')