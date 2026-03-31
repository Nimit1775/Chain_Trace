from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ai_agent import generate_investigation_report
from services.tigergraph import get_wallet_details, detect_cycles, run_community_detection

router = APIRouter()


class InvestigateRequest(BaseModel):
    wallet_address: str


@router.post("/investigate")
async def investigate(req: InvestigateRequest):
    """Generate an AI investigation report for a wallet."""
    try:
        # Gather all analysis data
        details = get_wallet_details(req.wallet_address)
        cycles = detect_cycles(req.wallet_address)
        clusters = run_community_detection()

        cluster_id = None
        cluster_size = 0
        for c in clusters:
            if req.wallet_address in c["wallets"]:
                cluster_id = c["cluster_id"]
                cluster_size = c["size"]
                break

        analysis = {
            **details,
            "cycles": cycles,
            "cluster_id": cluster_id,
            "cluster_size": cluster_size,
        }

        report = await generate_investigation_report(req.wallet_address, analysis)
        return {
            "wallet": req.wallet_address,
            "report": report,
            "analysis": analysis,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
