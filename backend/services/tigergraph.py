"""
TigerGraph service — all graph queries.
Set DEMO_MODE=true in .env to use mock data (no TigerGraph required).
"""
import os
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


class Settings:
    tg_host:       str = os.getenv("TG_HOST", "")
    tg_username:   str = os.getenv("TG_USERNAME", "tigergraph")
    tg_password:   str = os.getenv("TG_PASSWORD", "")
    tg_graph_name: str = os.getenv("TG_GRAPH_NAME", "ChainTrace")

@lru_cache
def get_settings():
    return Settings()

def get_conn():
    import pyTigerGraph as tg
    s = get_settings()
    conn = tg.TigerGraphConnection(
        host=s.tg_host,
        graphname=s.tg_graph_name,
        gsqlSecret=os.getenv("TG_SECRET", ""),
    )
    return conn


# ── Public API ────────────────────────────────────────────────────

def get_wallet_neighbors(address: str, hops: int = 2) -> dict:
    if DEMO_MODE:
        from services.mock_data import mock_wallet_network
        return mock_wallet_network(address, hops)
    return _real_wallet_neighbors(address, hops)


def get_wallet_details(address: str) -> dict:
    if DEMO_MODE:
        from services.mock_data import mock_wallet_details
        return mock_wallet_details(address)
    return _real_wallet_details(address)


def get_shortest_path(source: str, target: str) -> dict:
    if DEMO_MODE:
        from services.mock_data import mock_shortest_path
        return mock_shortest_path(source, target)
    return _real_shortest_path(source, target)


def run_community_detection() -> list:
    if DEMO_MODE:
        from services.mock_data import mock_clusters
        return mock_clusters()
    return _real_community_detection()


def run_pagerank() -> list:
    if DEMO_MODE:
        from services.mock_data import mock_pagerank
        return mock_pagerank()
    return _real_pagerank()


def detect_cycles(address: str) -> list:
    if DEMO_MODE:
        from services.mock_data import mock_cycles
        return mock_cycles(address)
    return _real_cycles(address)


def update_risk_scores():
    if not DEMO_MODE:
        _real_update_risk_scores()


# ── Real TigerGraph implementations ──────────────────────────────

def _real_wallet_neighbors(address: str, hops: int) -> dict:
    conn = get_conn()
    results = conn.runInstalledQuery(
        "get_wallet_network",
        params={"wallet_id": address, "max_hops": hops}
    )
    return _format_graph(results)


def _real_wallet_details(address: str) -> dict:
    conn = get_conn()
    vertex = conn.getVerticesById("Wallet", address)
    if not vertex:
        return {}
    attrs = vertex[0]["attributes"]
    return {
        "address":        address,
        "risk_score":     attrs.get("risk_score", 0),
        "flagged":        attrs.get("flagged", False),
        "total_sent":     attrs.get("total_sent", 0),
        "total_received": attrs.get("total_received", 0),
        "tx_count":       attrs.get("tx_count", 0),
        "pagerank":       attrs.get("pagerank", 0),
    }


def _real_shortest_path(source: str, target: str) -> dict:
    conn = get_conn()
    results = conn.runInstalledQuery(
        "shortest_path", params={"source": source, "target": target}
    )
    return _format_path(results)


def _real_community_detection() -> list:
    conn = get_conn()
    results = conn.runInstalledQuery("community_detection")
    clusters = {}
    for r in results:
        for item in r.get("@@community_map", []):
            clusters.setdefault(item["val"], []).append(item["key"])
    return [{"cluster_id": k, "wallets": v, "size": len(v)} for k, v in clusters.items() if len(v) > 1]


def _real_pagerank() -> list:
    conn = get_conn()
    results = conn.runInstalledQuery("pagerank")
    ranks = []
    for r in results:
        for item in r.get("@@top_scores", []):
            ranks.append({"address": item["key"], "pagerank": round(item["val"], 4)})
    return sorted(ranks, key=lambda x: x["pagerank"], reverse=True)[:20]


def _real_cycles(address: str) -> list:
    conn = get_conn()
    results = conn.runInstalledQuery("detect_cycles", params={"start_wallet": address})
    return [r["vertices"] for result in results for r in result.get("@@cycle_paths", [])]


def _real_update_risk_scores():
    get_conn().runInstalledQuery("compute_risk_scores")


# ── Formatters ────────────────────────────────────────────────────

def _format_graph(raw: list) -> dict:
    nodes, edges = [], []
    seen_nodes, seen_edges = set(), set()
    for result in raw:
        for wallet in result.get("wallets", []):
            wid = wallet["v_id"]
            if wid not in seen_nodes:
                seen_nodes.add(wid)
                a = wallet.get("attributes", {})
                nodes.append({"id": wid, "type": "wallet",
                    "risk_score": a.get("risk_score",0), "flagged": a.get("flagged",False),
                    "tx_count": a.get("tx_count",0), "total_sent": a.get("total_sent",0),
                    "total_received": a.get("total_received",0), "pagerank": a.get("pagerank",0)})
        for tx in result.get("transactions", []):
            tid = tx["v_id"]
            if tid not in seen_nodes:
                seen_nodes.add(tid)
                a = tx.get("attributes", {})
                nodes.append({"id": tid, "type": "transaction", "amount": a.get("amount",0), "timestamp": a.get("timestamp","")})
        for edge in result.get("edges", []):
            eid = f"{edge['from_id']}-{edge['to_id']}"
            if eid not in seen_edges:
                seen_edges.add(eid)
                edges.append({"source": edge["from_id"], "target": edge["to_id"],
                    "type": edge["e_type"], "amount": edge.get("attributes",{}).get("amount",0)})
    return {"nodes": nodes, "edges": edges}


def _format_path(raw: list) -> dict:
    path_nodes, path_edges = [], []
    for result in raw:
        for step in result.get("path", []):
            path_nodes.append(step["v_id"])
            if len(path_nodes) > 1:
                path_edges.append({"source": path_nodes[-2], "target": path_nodes[-1]})
    return {"path": path_nodes, "edges": path_edges}
