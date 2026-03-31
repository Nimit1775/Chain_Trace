from fastapi import APIRouter, HTTPException
from services.tigergraph import get_wallet_neighbors, get_shortest_path, get_wallet_details

router = APIRouter()


@router.get("/wallet/{address}")
def wallet_network(address: str, hops: int = 2):
    """Get wallet network graph — nodes + edges for Cytoscape."""
    try:
        return get_wallet_neighbors(address, hops)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/wallet/{address}/details")
def wallet_details(address: str):
    """Get detailed attributes for a single wallet."""
    result = get_wallet_details(address)
    if not result:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return result


@router.get("/path")
def shortest_path(source: str, target: str):
    """Shortest transaction path between two wallets."""
    try:
        return get_shortest_path(source, target)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
