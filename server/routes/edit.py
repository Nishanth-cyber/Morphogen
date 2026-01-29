from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from agents import edit_agent
from services import validators
from exporters import svg, dxf
from schemas.geometry import GeometryOutput

router = APIRouter()

class EditRequest(BaseModel):
    geometry: Dict[str, Any]
    instruction: str

@router.post("/edit")
async def edit_design(request: EditRequest):
    # Step 1: Run Edit Agent
    new_geometry_dict = edit_agent.edit_geometry(request.geometry, request.instruction)
    
    if new_geometry_dict.get("error"):
        raise HTTPException(status_code=500, detail="Failed to edit geometry")
        
    try:
        new_geometry = GeometryOutput(**new_geometry_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid geometry schema after edit: {e}")

    # Step 2: Validate
    try:
        validators.validate_geometry(new_geometry)
    except ValueError as e:
        print(f"Validation Warning (Edit): {e}")

    # Step 3: Re-Export
    svg_out = svg.export_to_svg(new_geometry)
    dxf_out = dxf.export_to_dxf(new_geometry)

    return {
        "status": "complete",
        "geometry": new_geometry.dict(),
        "artifacts": {
            "svg": svg_out,
            "dxf": dxf_out
        }
    }
