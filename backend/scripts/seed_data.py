"""
Loads demo cryptocurrency transaction data into TigerGraph.
Usage: python scripts/seed_data.py
"""
import sys, os, random, json
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyTigerGraph as tg
from dotenv import load_dotenv
load_dotenv()

conn = tg.TigerGraphConnection(
    host=os.getenv("TG_HOST"),
    username=os.getenv("TG_USERNAME"),
    password=os.getenv("TG_PASSWORD"),
    graphname=os.getenv("TG_GRAPH_NAME", "ChainTrace"),
)
conn.getToken(conn.createSecret())

# ── Wallet pool ────────────────────────────────────────────────────
LEGIT_WALLETS = [f"0xLEGIT{i:04d}" for i in range(1, 21)]
FRAUD_RING_A  = [f"0xRINGA{i:04d}" for i in range(1, 8)]   # 7-wallet laundering ring
FRAUD_RING_B  = [f"0xRINGB{i:04d}" for i in range(1, 5)]   # 4-wallet smurfing ring
MIXER_WALLET  = "0xMIXER0001"
ENTRY_WALLET  = "0xENTRY0001"   # demo entry point
ALL_WALLETS   = LEGIT_WALLETS + FRAUD_RING_A + FRAUD_RING_B + [MIXER_WALLET, ENTRY_WALLET]

EXCHANGES = ["Binance", "Coinbase", "Kraken", "Huobi"]

print("Inserting wallets...")
wallet_attrs = []
for w in ALL_WALLETS:
    flagged = w in FRAUD_RING_A or w == MIXER_WALLET
    risk    = random.randint(70, 95) if flagged else random.randint(5, 30)
    wallet_attrs.append({
        "v_type": "Wallet",
        "v_id": w,
        "attributes": {
            "risk_score": risk,
            "flagged": flagged,
            "tx_count": random.randint(50, 500) if flagged else random.randint(1, 50),
            "total_sent": round(random.uniform(10000, 500000), 2) if flagged else round(random.uniform(100, 5000), 2),
            "total_received": round(random.uniform(10000, 500000), 2) if flagged else round(random.uniform(100, 5000), 2),
        }
    })
conn.upsertVertices("Wallet", [(w["v_id"], w["attributes"]) for w in wallet_attrs])

print("Inserting exchanges...")
for ex in EXCHANGES:
    conn.upsertVertex("Exchange", ex, {"country": "US", "regulated": True})

print("Generating transactions...")
edges_sends, edges_recv = [], []
tx_vertices = []
base_time = datetime.now() - timedelta(days=30)

tx_id_counter = 1

def make_tx(src, dst, amount=None):
    global tx_id_counter
    tid = f"TX{tx_id_counter:06d}"
    tx_id_counter += 1
    amt = amount or round(random.uniform(500, 50000), 2)
    ts  = (base_time + timedelta(hours=random.randint(0, 720))).isoformat()
    tx_vertices.append((tid, {"amount": amt, "currency": "BTC", "timestamp": ts, "suspicious": False}))
    edges_sends.append((src, tid, {"amount": amt}))
    edges_recv.append((tid, dst, {"amount": amt}))

# Fraud Ring A — circular laundering loop
# RINGA0001 → RINGA0002 → RINGA0003 → RINGA0004 → RINGA0005 → RINGA0006 → RINGA0007 → RINGA0001
for i in range(len(FRAUD_RING_A)):
    src = FRAUD_RING_A[i]
    dst = FRAUD_RING_A[(i + 1) % len(FRAUD_RING_A)]
    for _ in range(3):   # multiple rounds
        make_tx(src, dst, round(random.uniform(5000, 25000), 2))

# Fraud Ring A also feeds through mixer
for w in FRAUD_RING_A[:3]:
    make_tx(w, MIXER_WALLET, round(random.uniform(10000, 50000), 2))
    make_tx(MIXER_WALLET, w, round(random.uniform(9000, 48000), 2))

# Fraud Ring B — smurfing (many small transactions)
for i in range(len(FRAUD_RING_B)):
    for _ in range(8):
        dst = random.choice(LEGIT_WALLETS)
        make_tx(FRAUD_RING_B[i], dst, round(random.uniform(200, 900), 2))

# Entry wallet connects into fraud ring (demo wallet)
make_tx(ENTRY_WALLET, FRAUD_RING_A[0], 15000)
make_tx(ENTRY_WALLET, FRAUD_RING_A[2], 8500)
make_tx(FRAUD_RING_A[3], ENTRY_WALLET, 12000)

# Legit transactions
for w in LEGIT_WALLETS:
    for _ in range(random.randint(2, 8)):
        dst = random.choice(LEGIT_WALLETS + [random.choice(EXCHANGES)])
        if isinstance(dst, str) and dst.startswith("0x"):
            make_tx(w, dst)

print(f"  {len(tx_vertices)} transactions, {len(edges_sends)} edges")

conn.upsertVertices("Transaction", tx_vertices)
conn.upsertEdges("Wallet", "sends", "Transaction", edges_sends)
conn.upsertEdges("Transaction", "received_by", "Wallet", edges_recv)

# Connect some wallets to exchanges
print("Connecting wallets to exchanges...")
for w in FRAUD_RING_A[:3] + LEGIT_WALLETS[:5]:
    ex = random.choice(EXCHANGES)
    conn.upsertEdge("Wallet", w, "connected_to", "Exchange", ex, {})

print("✅ Seed data loaded!")
print(f"   Wallets:      {len(ALL_WALLETS)}")
print(f"   Transactions: {len(tx_vertices)}")
print(f"   Demo wallet:  {ENTRY_WALLET}  ← use this in the UI")
print(f"   Fraud ring A: {FRAUD_RING_A[0]} through {FRAUD_RING_A[-1]}")

# Save demo addresses for easy reference
with open("../data/demo_addresses.json", "w") as f:
    json.dump({
        "demo_entry": ENTRY_WALLET,
        "fraud_ring_a": FRAUD_RING_A,
        "fraud_ring_b": FRAUD_RING_B,
        "mixer": MIXER_WALLET,
        "legit_samples": LEGIT_WALLETS[:5],
    }, f, indent=2)
print("   Saved demo addresses → data/demo_addresses.json")
