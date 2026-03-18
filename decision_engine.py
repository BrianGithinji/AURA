class DecisionEngine:
    def analyze(self, vehicle_count: int) -> str:
        if vehicle_count < 10:
            return "Low"
        elif vehicle_count < 25:
            return "Medium"
        return "High"

    def signal_decision(self, congestion: str) -> str:
        return {
            "Low":    "Green Light",
            "Medium": "Yellow Light",
            "High":   "Red Light",
        }.get(congestion, "Green Light")
