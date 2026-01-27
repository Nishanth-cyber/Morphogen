from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from pathlib import Path

from file_manager import ProjectFileManager
from converters.json_to_autolisp import convert_json_to_autolisp
from converters.dxf_to_dwg import check_oda_converter_installed

app = FastAPI(
    title="Generative Design API",
    description="AI-powered generative design system for AutoCAD",
    version="1.0.0"
)

# CORS - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize file manager
file_manager = ProjectFileManager()

# Create projects directory if it doesn't exist
Path("projects").mkdir(exist_ok=True)


# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str

class UpdateRequest(BaseModel):
    project_id: str
    design_data: Dict[Any, Any]


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Generative Design API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "POST /generate",
            "update": "PUT /update",
            "get_project": "GET /project/{project_id}",
            "list_projects": "GET /projects",
            "download": "GET /download/{project_id}/{file_type}",
            "delete": "DELETE /project/{project_id}"
        }
    }


@app.post("/generate")
async def generate_design(request: GenerateRequest):
    """
    Generate new design from natural language prompt
    
    Returns:
        - project_id: Unique project identifier
        - design_data: JSON design data for frontend rendering
        - message: Status message
    """
    try:
        # Import pipeline here to avoid circular imports
        from pipeline import run_pipeline
        from simple_pipeline import run_simple_pipeline
        
        # Run multi-agent pipeline
        print(f"Processing prompt: {request.prompt}")
        
        try:
            design_data = run_pipeline(request.prompt)
        except Exception as pipeline_error:
            print(f"AI pipeline failed: {pipeline_error}")
            print("Falling back to simple rule-based generation...")
            design_data = run_simple_pipeline(request.prompt)
        
        # Generate AutoLISP code
        autolisp_code = convert_json_to_autolisp(design_data)
        
        # Create project with all file formats
        project_id, project_dir = file_manager.create_project(
            design_data,
            autolisp_code
        )
        
        print(f"Project created: {project_id} at {project_dir}")
        
        return {
            "success": True,
            "project_id": project_id,
            "design_data": design_data,
            "message": f"Project created successfully at {project_dir}",
            "files_created": ["design.json", "floorplan.lsp", "floorplan.dxf", "floorplan.dwg"]
        }
        
    except Exception as e:
        print(f"Error in generate_design: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.put("/update")
async def update_design(request: UpdateRequest):
    """
    Update existing design after user edits in canvas
    Regenerates all file formats (JSON, LSP, DXF, DWG)
    
    Args:
        project_id: Project identifier
        design_data: Updated design data from frontend
        
    Returns:
        Success message and updated file list
    """
    try:
        print(f"Updating project: {request.project_id}")
        
        project_dir = file_manager.update_project(
            request.project_id,
            request.design_data
        )
        
        return {
            "success": True,
            "message": "Project updated successfully",
            "project_id": request.project_id,
            "project_dir": project_dir,
            "files_updated": ["design.json", "floorplan.lsp", "floorplan.dxf", "floorplan.dwg"]
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error in update_design: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@app.get("/project/{project_id}")
async def get_project(project_id: str):
    """
    Retrieve project data by ID
    
    Returns:
        Complete design data in JSON format
    """
    try:
        design_data = file_manager.get_project(project_id)
        return {
            "success": True,
            "project_id": project_id,
            "design_data": design_data
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects")
async def list_projects():
    """
    List all available projects
    
    Returns:
        List of projects with metadata
    """
    try:
        projects = file_manager.list_projects()
        return {
            "success": True,
            "total_projects": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{project_id}/{file_type}")
async def download_file(project_id: str, file_type: str):
    """
    Download specific file format
    
    Args:
        project_id: Project identifier
        file_type: File type to download ('lsp', 'dxf', 'dwg', 'json')
        
    Returns:
        File download response
    """
    try:
        # Validate file type
        valid_types = ['lsp', 'dxf', 'dwg', 'json']
        if file_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Must be one of: {', '.join(valid_types)}"
            )
        
        file_path = file_manager.get_file_path(project_id, file_type)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, 
                detail=f"{file_type.upper()} file not found for project {project_id}"
            )
        
        # Set appropriate MIME type and filename
        mime_types = {
            'lsp': 'text/plain',
            'dxf': 'application/dxf',
            'dwg': 'application/acad',
            'json': 'application/json'
        }
        
        filenames = {
            'lsp': 'floorplan.lsp',
            'dxf': 'floorplan.dxf',
            'dwg': 'floorplan.dwg',
            'json': 'design.json'
        }
        
        return FileResponse(
            path=file_path,
            media_type=mime_types[file_type],
            filename=filenames[file_type],
            headers={
                "Content-Disposition": f"attachment; filename={filenames[file_type]}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.delete("/project/{project_id}")
async def delete_project(project_id: str):
    """
    Delete project and all associated files
    
    Args:
        project_id: Project identifier
        
    Returns:
        Success confirmation
    """
    try:
        file_manager.delete_project(project_id)
        
        return {
            "success": True,
            "message": f"Project {project_id} deleted successfully"
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        System status and statistics
    """
    try:
        projects = file_manager.list_projects()
        oda_installed = check_oda_converter_installed()
        
        return {
            "status": "healthy",
            "total_projects": len(projects),
            "oda_converter_installed": oda_installed,
            "supported_formats": ["JSON", "AutoLISP (.lsp)", "DXF", "DWG"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Generative Design API Server")
    print("=" * 60)
    print(f"ODA Converter Installed: {check_oda_converter_installed()}")
    print("Starting server on http://localhost:8000")
    print("API Docs available at http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
