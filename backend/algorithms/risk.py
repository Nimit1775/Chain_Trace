"""
Risk scoring logic — computes a 0-100 risk score from graph analysis data.
Can run standalone without TigerGraph for testing.
"""


def compute_risk_score(
    flagged_neighbors: int = 0,
    tx_count: int = 0,
    total_sent: float = 0,
    total_received: float = 0,
    cycle_count: int = 0,
    cluster_size: int = 0,
    pagerank: float = 0.0,
    flagged: bool = False,
) -> float:
    score = 0.0

    # Already flagged — start high
    if flagged:
        score += 40

    # Flagged neighbors (each one adds weight)
    score += min(flagged_neighbors * 15, 30)

    # Circular flows — strong laundering signal
    score += min(cycle_count * 20, 40)

    # Part of a large cluster
    if cluster_size > 5:
        score += 15
    elif cluster_size > 2:
        score += 8

    # PageRank centrality — central nodes are more suspicious
    if pagerank > 0.5:
        score += 15
    elif pagerank > 0.2:
        score += 8

    # Volume anomaly — very high tx count is suspicious
    if tx_count > 200:
        score += 10
    elif tx_count > 100:
        score += 5

    # Imbalanced sent/received (money laundering pattern)
    if total_sent > 0 and total_received > 0:
        ratio = max(total_sent, total_received) / min(total_sent, total_received)
        if ratio > 10:
            score += 10
        elif ratio > 5:
            score += 5

    return round(min(score, 100), 1)


def risk_label(score: float) -> str:
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 35: return "MEDIUM"
    return "LOW"


def risk_color(score: float) -> str:
    if score >= 80: return "#ef4444"
    if score >= 60: return "#f97316"
    if score >= 35: return "#eab308"
    return "#22c55e"
