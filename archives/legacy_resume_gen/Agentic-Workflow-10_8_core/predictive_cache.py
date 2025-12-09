class PredictiveCache:
    def __init__(self):
        self.cache = {}

    def get(self, signature: str):
        return self.cache.get(signature)

    def set(self, signature: str, value):
        self.cache[signature] = value

    def snapshot(self):
        return self.cache.copy()
