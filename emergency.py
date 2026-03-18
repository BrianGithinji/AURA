def check_emergency(congestion: str, vehicle_count: int) -> str | None:
    if vehicle_count > 40:
        return f"Critical vehicle overflow detected — {vehicle_count} vehicles. Activating emergency protocols."
    if congestion == "High" and vehicle_count > 30:
        return f"Severe congestion in monitored zone — {vehicle_count} vehicles. Rerouting recommended."
    return None
