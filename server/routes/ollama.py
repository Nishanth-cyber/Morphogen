from fastapi import APIRouter, HTTPException
import requests
from config import settings

router = APIRouter(prefix="/ollama", tags=["ollama"])

@router.get("/health")
def ollama_health():
    try:
        res = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=3
        )
        return {"status": "ok", "models": res.json()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
