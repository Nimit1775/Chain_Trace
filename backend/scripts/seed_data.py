"""
Loads demo cryptocurrency transaction data into TigerGraph.
Uses direct REST API with GSQL-Secret header (works with Savanna 4.2)
Usage: python scripts/seed_data.py
"""
import sys, os, random, json
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import requests

load_dotenv()

HOST   = os.getenv("TG_HOST")
SECRET = os.getenv("TG_SECRET")
GRAPH  = os.getenv("TG_GRAPH_NAME", "chain_trace")

HEADERS = {
    "Authorization": f"GSQL-Secret {SECRET}",
    "Content-Type": "application/json"
}

BASE_URL = f"{HOST}/restpp/graph/{GRAPH}"

def upsert(payload):
    r = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if r.status_code not in (200, 202):
        print(f"  ERROR {r.status_code}: {r.text[:200]}")
    return r

# ── Wallet pool ───────────────────────────────────────────────────
LEGIT_WALLETS = [f"0xLEGIT{i:04d}" for i in range(1, 11)]
FRAUD_RING_A  = [f"0xRINGA{i:04d}" for i in range(1, 8)]
FRAUD_RING_B  = [f"0xRINGB{i:04d}" for i in range(1, 5)]
MIXER_WALLET  = "0xMIXER0001"
ENTRY_WALLET  = "0xENTRY0001"
ALL_WALLETS   = LEGIT_WALLETS + FRAUD_RING_A + FRAUD_RING_B + [MIXER_WALLET, ENTRY_WALLET]

print("Inserting wallets...")
vertices = []
for w in ALL_WALLETS:
    flagged = w in FRAUD_RING_A or w == MIXER_WALLET
    risk    = random.randint(70, 95) if flagged else random.randint(5, 30)
    vertices.append({
        "v_type": "Wallet",
        "v_id": w,
        "attributes": {
            "risk_score":     risk,
            "flagged":        flagged,
            "tx_count":       random.randint(100, 500) if flagged else random.randint(1, 50),
            "total_sent":     round(random.uniform(10000, 500000), 2) if flagged else round(random.uniform(100, 5000), 2),
            "total_received": round(random.uniform(10000, 500000), 2) if flagged else round(random.uniform(100, 5000), 2),
        }
    })

r = upsert({"vertices": {v["v_type"]: {v["v_id"]: v["attributes"]} for v in vertices}})
print(f"  Wallets: {r.status_code}")

print("Inserting exchanges...")
exchanges = {}
for ex in ["Binance", "Coinbase", "Kraken"]:
    exchanges[ex] = {"country": "US", "regulated": True}
r = upsert({"vertices": {"Exchange": exchanges}})
print(f"  Exchanges: {r.status_code}")

print("Generating transactions...")
tx_vertices = {}
sends_edges = {"Wallet": {"sends": {"Transaction": {}}}}
recv_edges  = {"Transaction": {"received_by": {"Wallet": {}}}}
tx_counter  = [1]
base_time   = datetime.now() - timedelta(days=30)

def make_tx(src, dst, amount=None):
    tid = f"TX{tx_counter[0]:06d}"
    tx_counter[0] += 1
    amt = amount or round(random.uniform(500, 50000), 2)
    ts  = (base_time + timedelta(hours=random.randint(0, 720))).isoformat()
    tx_vertices[tid] = {"amount": amt, "currency": "BTC", "timestamp": ts, "suspicious": False}
    sends_edges["Wallet"]["sends"]["Transaction"][src] = sends_edges["Wallet"]["sends"]["Transaction"].get(src, {})
    sends_edges["Wallet"]["sends"]["Transaction"][src][tid] = {"amount": amt}
    recv_edges["Transaction"]["received_by"]["Wallet"][tid]  = recv_edges["Transaction"]["received_by"]["Wallet"].get(tid, {})
    recv_edges["Transaction"]["received_by"]["Wallet"][tid][dst] = {"amount": amt}

# Fraud Ring A — circular loop
for i in range(len(FRAUD_RING_A)):
    src = FRAUD_RING_A[i]
    dst = FRAUD_RING_A[(i + 1) % len(FRAUD_RING_A)]
    for _ in range(3):
        make_tx(src, dst, round(random.uniform(5000, 25000), 2))

# Ring A → Mixer
for w in FRAUD_RING_A[:3]:
    make_tx(w, MIXER_WALLET, round(random.uniform(10000, 50000), 2))
    make_tx(MIXER_WALLET, w, round(random.uniform(9000, 48000), 2))

# Entry wallet → Ring A
make_tx(ENTRY_WALLET, FRAUD_RING_A[0], 15000)
make_tx(ENTRY_WALLET, FRAUD_RING_A[2], 8500)
make_tx(FRAUD_RING_A[3], ENTRY_WALLET, 12000)

# Ring B — smurfing
for w in FRAUD_RING_B:
    for _ in range(5):
        make_tx(w, random.choice(LEGIT_WALLETS), round(random.uniform(200, 900), 2))

# Legit transactions
for w in LEGIT_WALLETS:
    for _ in range(random.randint(2, 5)):
        make_tx(w, random.choice(LEGIT_WALLETS))

print(f"  {len(tx_vertices)} transactions created")

# Upload transactions in batches of 50
tx_items = list(tx_vertices.items())
for i in range(0, len(tx_items), 50):
    batch = dict(tx_items[i:i+50])
    r = upsert({"vertices": {"Transaction": batch}})
    print(f"  Tx batch {i//50+1}: {r.status_code}")

# Upload edges — sends
print("Uploading send edges...")
for src, targets in sends_edges["Wallet"]["sends"]["Transaction"].items():
    payload = {"edges": {"Wallet": {src: {"sends": {"Transaction": targets}}}}}
    r = upsert(payload)
    if r.status_code not in (200, 202):
        print(f"  Edge error: {r.text[:100]}")

# Upload edges — received_by
print("Uploading receive edges...")
for tid, targets in recv_edges["Transaction"]["received_by"]["Wallet"].items():
    payload = {"edges": {"Transaction": {tid: {"received_by": {"Wallet": targets}}}}}
    r = upsert(payload)
    if r.status_code not in (200, 202):
        print(f"  Edge error: {r.text[:100]}")

print("\n✅ Seed data loaded!")
print(f"   Total wallets:      {len(ALL_WALLETS)}")
print(f"   Total transactions: {len(tx_vertices)}")
print(f"   Demo wallet:        {ENTRY_WALLET}  ← use this in the UI")
print(f"   Fraud ring A:       {FRAUD_RING_A[0]} → {FRAUD_RING_A[-1]}")

with open("../data/demo_addresses.json", "w") as f:
    json.dump({
        "demo_entry": ENTRY_WALLET,
        "fraud_ring_a": FRAUD_RING_A,
        "fraud_ring_b": FRAUD_RING_B,
        "mixer": MIXER_WALLET,
        "legit_samples": LEGIT_WALLETS[:5],
    }, f, indent=2)
print("   Saved → data/demo_addresses.json")