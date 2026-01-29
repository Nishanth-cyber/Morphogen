from fastapi import APIRouter, HTTPException
from agents.executor import run_geometry_agent

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/geometry")
def geometry_agent_endpoint(payload: dict):
    try:
        result = run_geometry_agent(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
