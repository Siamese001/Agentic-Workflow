class PolicyAutoTunerStub:
    def suggest_config(self, state, metrics):
        # deterministic suggestion stub
        return {
            "temperature": 0.3,
            "max_tokens": 500,
            "routing_adjustment": "none",
        }
