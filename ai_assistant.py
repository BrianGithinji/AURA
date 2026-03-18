def get_ai_tip(congestion: str, vehicle_count: int, query: str = "") -> str:
    if query:
        q = query.lower()
        if any(w in q for w in ["signal", "light", "traffic"]):
            return ("Based on current flow patterns, I recommend extending green light duration "
                    "on the primary corridor by 15 seconds to reduce queue buildup.")
        if any(w in q for w in ["emergency", "accident", "incident"]):
            return ("Activating emergency corridor on Route B. All signals ahead set to green. "
                    "ETA to incident zone: ~3 minutes.")
        if any(w in q for w in ["predict", "forecast", "next"]):
            return (f"With {vehicle_count} vehicles currently detected and {congestion} congestion, "
                    "I forecast a 12% increase in the next 10 minutes based on historical patterns.")
        return (f"AURA is monitoring {vehicle_count} vehicles with {congestion} congestion. "
                "All systems nominal. How can I assist further?")

    tips = {
        "Low":    "Traffic flow is optimal. No intervention required. Green wave synchronization active.",
        "Medium": "Moderate congestion detected. Consider activating alternate route signage on Zone B.",
        "High":   "High congestion alert! Recommend extending red phase on incoming lanes and notifying traffic control.",
    }
    return tips.get(congestion, "System monitoring active.")
