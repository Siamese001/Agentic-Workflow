# Minimal offline LangGraph stub for Codex v10.7 workflows

class StateGraph:
    def __init__(self, state_type):
        self.nodes = {}
        self.edges = {}
        self.entry = None

    def add_node(self, name, func):
        self.nodes[name] = func

    def set_entry_point(self, name):
        self.entry = name

    def add_edge(self, source, destination):
        self.edges.setdefault(source, []).append(destination)

    def add_conditional_edges(self, source, selector, mapping):
        self.edges.setdefault(source, []).append(("COND", selector, mapping))

    def compile(self, checkpointer=None):
        graph = self

        class App:
            async def astream(self, state, run_config=None):
                current = graph.entry
                while current:
                    func = graph.nodes[current]
                    patch = await func(state)
                    yield {current: patch}

                    next_edges = graph.edges.get(current, [])
                    if not next_edges:
                        break

                    edge = next_edges[0]
                    if isinstance(edge, tuple) and edge[0] == "COND":
                        _, selector, mapping = edge
                        key = selector(state)
                        current = mapping.get(key)
                    else:
                        current = edge

            async def astream_events(self, state, run_config=None, version="v1"):
                async for step in self.astream(state, run_config):
                    node = list(step.keys())[0]
                    yield {"event": "on_node_start", "data": {"name": node}}
                    yield {"event": "on_node_end", "data": {"name": node, "output": step}}

        return App()


END = "END"
