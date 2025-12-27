class RemoteGitClient:
    """Stub for remote code operations."""
    def clone(self, url: str): return True
    def commit_and_push(self, msg: str): return {"hash": "stub_sha"}
