class TrafficPredictor:
    def predict(self, history: list) -> int:
        if not history:
            return 0
        weights = list(range(1, len(history) + 1))
        weighted = sum(v * w for v, w in zip(history, weights))
        return round(weighted / sum(weights))
