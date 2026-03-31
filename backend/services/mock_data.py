"""
Mock data for demo mode.
Every function here mirrors the exact return shape of services/tigergraph.py.
Switch DEMO_MODE=true in .env to use this instead of TigerGraph.
"""
import random

# ── Wallet definitions ────────────────────────────────────────────

WALLETS = {
    "0xENTRY0001": {"risk_score": 74, "flagged": True,  "tx_count": 87,  "total_sent": 48200, "total_received": 51300, "pagerank": 0.43},
    "0xRINGA0001": {"risk_score": 91, "flagged": True,  "tx_count": 312, "total_sent": 189000,"total_received": 192000,"pagerank": 0.81},
    "0xRINGA0002": {"risk_score": 88, "flagged": True,  "tx_count": 278, "total_sent": 145000,"total_received": 148000,"pagerank": 0.76},
    "0xRINGA0003": {"risk_score": 85, "flagged": True,  "tx_count": 201, "total_sent": 121000,"total_received": 119000,"pagerank": 0.69},
    "0xRINGA0004": {"risk_score": 83, "flagged": True,  "tx_count": 189, "total_sent": 98000, "total_received": 102000,"pagerank": 0.65},
    "0xRINGA0005": {"risk_score": 87, "flagged": True,  "tx_count": 234, "total_sent": 134000,"total_received": 138000,"pagerank": 0.72},
    "0xRINGA0006": {"risk_score": 82, "flagged": True,  "tx_count": 167, "total_sent": 87000, "total_received": 91000, "pagerank": 0.61},
    "0xRINGA0007": {"risk_score": 89, "flagged": True,  "tx_count": 256, "total_sent": 162000,"total_received": 165000,"pagerank": 0.78},
    "0xMIXER0001": {"risk_score": 96, "flagged": True,  "tx_count": 891, "total_sent": 723000,"total_received": 718000,"pagerank": 0.94},
    "0xRINGB0001": {"risk_score": 62, "flagged": True,  "tx_count": 134, "total_sent": 42000, "total_received": 39000, "pagerank": 0.38},
    "0xRINGB0002": {"risk_score": 58, "flagged": True,  "tx_count": 98,  "total_sent": 31000, "total_received": 34000, "pagerank": 0.31},
    "0xRINGB0003": {"risk_score": 61, "flagged": True,  "tx_count": 112, "total_sent": 38000, "total_received": 36000, "pagerank": 0.35},
    "0xRINGB0004": {"risk_score": 55, "flagged": True,  "tx_count": 89,  "total_sent": 28000, "total_received": 31000, "pagerank": 0.28},
    "0xLEGIT0001": {"risk_score": 8,  "flagged": False, "tx_count": 12,  "total_sent": 3200,  "total_received": 2900,  "pagerank": 0.04},
    "0xLEGIT0002": {"risk_score": 12, "flagged": False, "tx_count": 18,  "total_sent": 5400,  "total_received": 4800,  "pagerank": 0.06},
    "0xLEGIT0003": {"risk_score": 6,  "flagged": False, "tx_count": 7,   "total_sent": 1200,  "total_received": 1400,  "pagerank": 0.02},
    "0xLEGIT0004": {"risk_score": 15, "flagged": False, "tx_count": 23,  "total_sent": 7100,  "total_received": 6800,  "pagerank": 0.08},
    "0xLEGIT0005": {"risk_score": 9,  "flagged": False, "tx_count": 14,  "total_sent": 4200,  "total_received": 3900,  "pagerank": 0.05},
}

RING_A = ["0xRINGA0001","0xRINGA0002","0xRINGA0003","0xRINGA0004","0xRINGA0005","0xRINGA0006","0xRINGA0007"]
RING_B = ["0xRINGB0001","0xRINGB0002","0xRINGB0003","0xRINGB0004"]

# ── Graph network builder ────────────────────────────────────────

def _make_tx_id(src, dst, i):
    return f"TX-{src[-4:]}-{dst[-4:]}-{i:03d}"

def mock_wallet_network(address: str, hops: int = 2) -> dict:
    nodes, edges = [], []
    seen_nodes, seen_edges = set(), set()

    def add_wallet(wid):
        if wid in seen_nodes or wid not in WALLETS: return
        seen_nodes.add(wid)
        w = WALLETS[wid]
        nodes.append({"id": wid, "type": "wallet", **w})

    def add_tx(src, dst, amount, idx):
        tid = _make_tx_id(src, dst, idx)
        if tid not in seen_nodes:
            seen_nodes.add(tid)
            nodes.append({"id": tid, "type": "transaction", "amount": amount, "timestamp": "2024-11-15T08:32:00"})
        eid = f"{src}-{tid}"
        if eid not in seen_edges:
            seen_edges.add(eid)
            edges.append({"source": src, "target": tid, "type": "sends", "amount": amount})
        eid2 = f"{tid}-{dst}"
        if eid2 not in seen_edges:
            seen_edges.add(eid2)
            edges.append({"source": tid, "target": dst, "type": "received_by", "amount": amount})
        add_wallet(dst)

    add_wallet(address)

    # Entry wallet neighbours
    if address == "0xENTRY0001":
        add_tx("0xENTRY0001", "0xRINGA0001", 15000, 1)
        add_tx("0xENTRY0001", "0xRINGA0002", 8500,  2)
        add_tx("0xRINGA0003", "0xENTRY0001", 12000, 3)
        add_tx("0xLEGIT0001", "0xENTRY0001", 3200,  4)

    # Fraud ring A — circular
    ring_a_in_scope = [w for w in RING_A if w in WALLETS]
    if address in ring_a_in_scope or address == "0xENTRY0001":
        for i, w in enumerate(RING_A):
            add_wallet(w)
        for i in range(len(RING_A)):
            src = RING_A[i]; dst = RING_A[(i+1) % len(RING_A)]
            add_tx(src, dst, round(random.uniform(8000, 25000), 2), i+10)
        # Ring A → mixer
        add_wallet("0xMIXER0001")
        add_tx("0xRINGA0001", "0xMIXER0001", 45000, 20)
        add_tx("0xRINGA0003", "0xMIXER0001", 28000, 21)
        add_tx("0xMIXER0001", "0xRINGA0005", 41000, 22)

    if address in RING_B:
        for w in RING_B:
            add_wallet(w)
        for i in range(len(RING_B)):
            src = RING_B[i]; dst = RING_B[(i+1) % len(RING_B)]
            add_tx(src, dst, round(random.uniform(500, 900), 2), i+30)
        for w in RING_B:
            dst = random.choice(["0xLEGIT0001","0xLEGIT0002","0xLEGIT0003"])
            add_tx(w, dst, round(random.uniform(200, 800), 2), 40)
            add_wallet(dst)

    if address == "0xMIXER0001":
        for w in RING_A[:4]:
            add_wallet(w)
            add_tx(w, "0xMIXER0001", round(random.uniform(15000, 50000), 2), RING_A.index(w)+50)
            add_tx("0xMIXER0001", w, round(random.uniform(14000, 48000), 2), RING_A.index(w)+60)

    if address.startswith("0xLEGIT"):
        legit = ["0xLEGIT0001","0xLEGIT0002","0xLEGIT0003","0xLEGIT0004","0xLEGIT0005"]
        add_wallet(address)
        for i, w in enumerate(legit):
            if w != address:
                add_wallet(w)
                add_tx(address, w, round(random.uniform(500, 3000), 2), i+70)

    return {"nodes": nodes, "edges": edges}


def mock_wallet_details(address: str) -> dict:
    w = WALLETS.get(address, {})
    return {"address": address, **w} if w else {}


def mock_shortest_path(source: str, target: str) -> dict:
    # Hardcoded demo paths for known wallet pairs
    paths = {
        ("0xENTRY0001", "0xMIXER0001"): ["0xENTRY0001","0xRINGA0001","0xMIXER0001"],
        ("0xRINGA0001", "0xRINGA0007"): ["0xRINGA0001","0xRINGA0002","0xRINGA0003","0xRINGA0007"],
        ("0xLEGIT0001", "0xMIXER0001"): ["0xLEGIT0001","0xENTRY0001","0xRINGA0001","0xMIXER0001"],
    }
    path = paths.get((source, target), paths.get((target, source), [source, target]))
    edges = [{"source": path[i], "target": path[i+1]} for i in range(len(path)-1)]
    return {"path": path, "edges": edges}


def mock_clusters() -> list:
    return [
        {"cluster_id": 1, "wallets": RING_A, "size": len(RING_A)},
        {"cluster_id": 2, "wallets": RING_B, "size": len(RING_B)},
        {"cluster_id": 3, "wallets": ["0xMIXER0001"] + RING_A[:3], "size": 4},
    ]


def mock_pagerank() -> list:
    return sorted(
        [{"address": addr, "pagerank": data["pagerank"]} for addr, data in WALLETS.items()],
        key=lambda x: x["pagerank"], reverse=True
    )[:10]


def mock_cycles(address: str) -> list:
    if address in RING_A:
        idx = RING_A.index(address)
        cycle = RING_A[idx:] + RING_A[:idx+1]
        return [cycle]
    if address == "0xENTRY0001":
        return [["0xENTRY0001","0xRINGA0001","0xRINGA0002","0xRINGA0003","0xENTRY0001"]]
    return []


def mock_full_analysis(address: str) -> dict:
    details  = mock_wallet_details(address)
    cycles   = mock_cycles(address)
    clusters = mock_clusters()
    cluster_id, cluster_size = None, 0
    for c in clusters:
        if address in c["wallets"]:
            cluster_id = c["cluster_id"]
            cluster_size = c["size"]
            break
    return {**details, "cycles": cycles, "cluster_id": cluster_id, "cluster_size": cluster_size}
