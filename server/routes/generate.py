from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from agents import intent_agent, completeness_agent, planning_agent, executor
from services import validators
from exporters import svg, dxf, ifc
from schemas.geometry import GeometryOutput

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    previous_plan: Optional[Dict[str, Any]] = None
    clarification_answers: Optional[Dict[str, Any]] = None

class ExportRequest(BaseModel):
    """Request model for direct export endpoints"""
    geometry: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None
    previous_plan: Optional[Dict[str, Any]] = None

class GenerateResponse(BaseModel):
    status: str
    plan: Optional[Dict[str, Any]] = None
    geometry: Optional[Dict[str, Any]] = None
    missing_fields: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    artifacts: Optional[Dict[str, str]] = None
    warnings: Optional[List[str]] = None

@router.post("/generate", response_model=GenerateResponse)
async def generate_design(request: GenerateRequest):
    """
    Main design generation endpoint
    
    Flow:
    1. Classify intent and domain
    2. Check completeness
    3. Generate engineering plan
    4. Generate geometry
    5. Validate
    6. Export to multiple formats
    """
    
    # Step 1: Intent Classification (Skip if refining/clarifying)
    intent_data = {}
    if request.previous_plan:
        # Re-use existing intent data from the plan to avoid re-classification errors
        intent_data = {
            "domain": request.previous_plan.get("domain", "industrial"),
            "subdomain": request.previous_plan.get("subdomain", "unknown"),
            "intent": "generate_design"
        }
    else:
        try:
            intent_data = intent_agent.get_intent(request.prompt)
            if intent_data.get("error"):
                raise HTTPException(status_code=500, detail="Failed to classify intent")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"DEBUG: Intent Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Intent classification failed: {str(e)}")
    
    # Step 2: Generate or Merge Plan
    if request.previous_plan and request.clarification_answers:
        # Merge previous plan with new answers
        merged_input = {**request.previous_plan, **request.clarification_answers}
        current_plan = planning_agent.create_plan(merged_input)
    else:
        # Initial plan generation
        initial_input = {
            "raw_prompt": request.prompt,
            **intent_data
        }
        current_plan = planning_agent.create_plan(initial_input)

    if current_plan.get("error"):
        raise HTTPException(status_code=500, detail="Failed to generate plan")

    # Step 3: Completeness Check
    print("DEBUG: Starting Completeness Check...")
    try:
        completeness = completeness_agent.check_completeness(
            intent_data.get("domain", "general"), 
            current_plan
        )
        print("DEBUG: Completeness Check Finished.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Completeness check failed: {str(e)}")
    
    if completeness.get("status") == "incomplete":
        return GenerateResponse(
            status="incomplete",
            plan=current_plan,
            missing_fields=completeness.get("missing_fields"),
            questions=completeness.get("questions")
        )

    # Step 4: Geometry Generation
    print("DEBUG: Starting Geometry Generation...")
    try:
        geometry = executor.run_geometry_agent(current_plan)
        print("DEBUG: Geometry Generation Finished.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Geometry generation failed: {str(e)}")

    # Step 5: Validation
    warnings_list = []
    try:
        is_valid, warnings = validators.validate_geometry(geometry)
        warnings_list = [w.message for w in warnings]
    except validators.ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")
    except Exception as e:
        # Non-critical validation errors - continue
        warnings_list.append(f"Validation warning: {str(e)}")

    # Step 6: Export to Multiple Formats
    svg_output = ""
    dxf_output = ""
    ifc_base64 = ""

    # 6a. SVG Export
    try:
        svg_output = svg.export_to_svg(geometry)
    except Exception as e:
        warnings_list.append(f"SVG Export warning: {str(e)}")

    # 6b. DXF Export
    try:
        dxf_output = dxf.export_to_dxf(geometry)
    except Exception as e:
        warnings_list.append(f"DXF Export warning: {str(e)}")

    return GenerateResponse(
        status="complete",
        plan=current_plan,
        geometry=geometry.dict(),
        artifacts={
            "svg": svg_output,
            "dxf": dxf_output,
            "ifc": ifc_base64
        },
        warnings=warnings_list if warnings_list else None
    )

@router.post("/generate/ifc")
async def generate_design_ifc(request: ExportRequest):
    """
    Export geometry to IFC format directly
    Accepts either geometry dict or generates from prompt
    """
    try:
        # If geometry is provided, use it directly
        if request.geometry:
            try:
                geometry = GeometryOutput(**request.geometry)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid geometry data: {str(e)}")
        else:
            # Generate geometry from prompt if no geometry provided
            if not request.prompt:
                raise HTTPException(status_code=400, detail="Either geometry or prompt must be provided")
            
            gen_request = GenerateRequest(
                prompt=request.prompt,
                previous_plan=request.previous_plan
            )
            result = await generate_design(gen_request)
            
            if result.status != "complete":
                raise HTTPException(status_code=400, detail="Design generation incomplete")
            
            geometry = GeometryOutput(**result.geometry)
        
        # Export to IFC
        ifc_output = ifc.export_to_ifc(
            geometry,
            project_name=geometry.project_name or "Generated Design"
        )
        
        return Response(
            content=ifc_output,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=design.ifc"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"IFC export failed: {str(e)}")

@router.post("/generate/dxf")
async def generate_design_dxf(request: ExportRequest):
    """
    Export geometry to DXF format directly
    Accepts either geometry dict or generates from prompt
    """
    try:
        # If geometry is provided, use it directly
        if request.geometry:
            try:
                geometry = GeometryOutput(**request.geometry)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid geometry data: {str(e)}")
        else:
            # Generate geometry from prompt if no geometry provided
            if not request.prompt:
                raise HTTPException(status_code=400, detail="Either geometry or prompt must be provided")
            
            gen_request = GenerateRequest(
                prompt=request.prompt,
                previous_plan=request.previous_plan
            )
            result = await generate_design(gen_request)
            
            if result.status != "complete":
                raise HTTPException(status_code=400, detail="Design generation incomplete")
            
            geometry = GeometryOutput(**result.geometry)
        
        # Export to DXF
        dxf_output = dxf.export_to_dxf(geometry)
        
        return Response(
            content=dxf_output,
            media_type="application/dxf",
            headers={
                "Content-Disposition": "attachment; filename=design.dxf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DXF export failed: {str(e)}")

@router.get("/capabilities")
async def get_capabilities():
    """
    Return system capabilities and supported domains
    """
    return {
        "domains": {
            "industrial": {
                "subdomains": [
                    "desalination_plant",
                    "water_treatment",
                    "chemical_processing",
                    "power_plant"
                ],
                "features": [
                    "piping_layout",
                    "equipment_placement",
                    "process_units",
                    "valve_positioning"
                ]
            },
            "residential": {
                "subdomains": [
                    "single_family_house",
                    "apartment",
                    "villa"
                ],
                "features": [
                    "room_layout",
                    "wall_placement",
                    "door_windows",
                    "floor_plans"
                ]
            },
            "commercial": {
                "subdomains": [
                    "office",
                    "retail",
                    "warehouse"
                ],
                "features": [
                    "space_planning",
                    "circulation",
                    "loading_areas"
                ]
            }
        },
        "export_formats": [
            "IFC (Industry Foundation Classes - BIM)",
            "DXF (AutoCAD)",
            "SVG (Scalable Vector Graphics)",
            "JSON (Structured Data)"
        ],
        "validation": [
            "Engineering clearances",
            "Flow continuity",
            "Code compliance",
            "Dimension checks"
        ]
    }
