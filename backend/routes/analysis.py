from fastapi import APIRouter, HTTPException
from services.tigergraph import (
    run_community_detection,
    run_pagerank,
    detect_cycles,
    get_wallet_details,
    update_risk_scores,
)

router = APIRouter()


@router.get("/clusters")
def fraud_clusters():
    """Run community detection — return suspected fraud rings."""
    try:
        return {"clusters": run_community_detection()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pagerank")
def pagerank():
    """Top wallets by PageRank centrality."""
    try:
        return {"rankings": run_pagerank()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cycles/{address}")
def cycles(address: str):
    """Detect circular transaction flows from a wallet."""
    try:
        found = detect_cycles(address)
        return {"address": address, "cycles": found, "count": len(found)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/{address}/full")
def full_analysis(address: str):
    """Combined analysis for a wallet — used by AI agent."""
    try:
        details = get_wallet_details(address)
        cycles = detect_cycles(address)
        clusters = run_community_detection()

        cluster_id = None
        cluster_size = 0
        for c in clusters:
            if address in c["wallets"]:
                cluster_id = c["cluster_id"]
                cluster_size = c["size"]
                break

        return {
            **details,
            "cycles": cycles,
            "cluster_id": cluster_id,
            "cluster_size": cluster_size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-scores")
def refresh_scores():
    """Recompute risk scores for all wallets."""
    update_risk_scores()
    return {"status": "Risk scores updated"}
