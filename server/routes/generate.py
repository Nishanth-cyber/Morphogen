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
    lsp_output = ""
    
    # Track export success for each format
    export_status = {
        "dxf": False,
        "lsp": False,
        "svg": False,
        "ifc": False
    }

    # 6a. DXF Export (CRITICAL - Must work)
    try:
        print("DEBUG: Starting DXF Export...")
        dxf_output = dxf.export_to_dxf(geometry)
        export_status["dxf"] = True
        print(f"DEBUG: DXF Export successful ({len(dxf_output)} bytes)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        warnings_list.append(f"DXF Export FAILED: {str(e)}")
        # Generate minimal DXF as fallback
        try:
            from exporters.dxf import generate_minimal_dxf
            dxf_output = generate_minimal_dxf("Export failed - see warnings")
            warnings_list.append("Using minimal fallback DXF")
        except:
            pass

    # 6b. LSP Export (High Priority)
    try:
        print("DEBUG: Starting LSP Generation...")
        lsp_output = executor.run_lsp_agent(current_plan, geometry)
        export_status["lsp"] = True
        print(f"DEBUG: LSP Generation successful ({len(lsp_output)} bytes)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        warnings_list.append(f"LSP Generation FAILED: {str(e)}")

    # 6c. SVG Export (Multi-Strategy)
    # Strategy 1: Try LSP → SVG if LSP available
    if lsp_output and export_status["lsp"]:
        try:
            print("DEBUG: Attempting LSP to SVG Conversion...")
            svg_from_lsp = executor.run_lsp_to_svg_agent(lsp_output)
            if svg_from_lsp and len(svg_from_lsp) > 100 and "<svg" in svg_from_lsp.lower():
                svg_output = svg_from_lsp
                export_status["svg"] = True
                print("DEBUG: LSP to SVG successful")
            else:
                raise ValueError("LSP to SVG produced invalid output")
        except Exception as e:
            print(f"DEBUG: LSP to SVG failed: {str(e)}")
            warnings_list.append(f"LSP to SVG conversion failed: {str(e)}")
    
    # Strategy 2: Fallback to direct Geometry → SVG
    if not export_status["svg"]:
        try:
            print("DEBUG: Using direct Geometry to SVG fallback...")
            svg_output = svg.export_to_svg(geometry)
            export_status["svg"] = True
            warnings_list.append("SVG generated from geometry (LSP conversion unavailable)")
            print("DEBUG: Direct SVG generation successful")
        except Exception as e:
            import traceback
            traceback.print_exc()
            warnings_list.append(f"Direct SVG generation FAILED: {str(e)}")
            # Last resort: empty SVG
            from exporters.svg import generate_empty_svg
            svg_output = generate_empty_svg("Failed to generate visualization")
    
    # 6d. IFC Export (Optional)
    # Note: IFC export is handled separately via /generate/ifc endpoint
    # Skipping here to avoid performance issues
    
    # Validation summary
    successful_exports = [fmt for fmt, success in export_status.items() if success]
    failed_exports = [fmt for fmt, success in export_status.items() if not success]
    
    if failed_exports:
        warnings_list.append(f"Some exports failed: {', '.join(failed_exports)}")
    
    print(f"DEBUG: Export Summary - Success: {successful_exports}, Failed: {failed_exports}")

    return GenerateResponse(
        status="complete",
        plan=current_plan,
        geometry=geometry.dict(),
        artifacts={
            "svg": svg_output,
            "dxf": dxf_output,
            "ifc": ifc_base64,
            "lsp": lsp_output
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