import os
import json
import uuid
from datetime import datetime
from pathlib import Path

class ProjectFileManager:
    """
    Manages all files for a design project:
    - JSON (master data)
    - AutoLISP (.lsp)
    - DXF (intermediate)
    - DWG (final)
    """
    
    def __init__(self, base_dir="projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_project(self, design_data, autolisp_code):
        """
        Create new project with all file formats
        Returns: project_id, project_dir
        """
        project_id = str(uuid.uuid4())[:8]
        project_dir = self.base_dir / f"project_{project_id}"
        project_dir.mkdir(exist_ok=True)
        
        # Add metadata
        if 'metadata' not in design_data:
            design_data['metadata'] = {}
            
        design_data['metadata']['project_id'] = project_id
        design_data['metadata']['created_at'] = datetime.now().isoformat()
        design_data['metadata']['last_modified'] = datetime.now().isoformat()
        design_data['metadata']['version'] = 1
        
        # Save JSON (master data)
        json_path = project_dir / "design.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(design_data, f, indent=2)
        
        # Save AutoLISP
        lsp_path = project_dir / "floorplan.lsp"
        with open(lsp_path, 'w', encoding='utf-8') as f:
            f.write(autolisp_code)
        
        # Generate and save DXF
        from converters.json_to_dxf import convert_json_to_dxf
        dxf_path = project_dir / "floorplan.dxf"
        convert_json_to_dxf(design_data, str(dxf_path))
        
        # Generate and save DWG
        from converters.dxf_to_dwg import convert_dxf_to_dwg
        dwg_path = project_dir / "floorplan.dwg"
        convert_dxf_to_dwg(str(dxf_path), str(dwg_path))
        
        return project_id, str(project_dir)
    
    def update_project(self, project_id, updated_design_data):
        """
        Update existing project when user edits design
        Regenerates all file formats
        """
        project_dir = self.base_dir / f"project_{project_id}"
        
        if not project_dir.exists():
            raise FileNotFoundError(f"Project {project_id} not found")
        
        # Update metadata
        if 'metadata' not in updated_design_data:
            updated_design_data['metadata'] = {}
            
        updated_design_data['metadata']['last_modified'] = datetime.now().isoformat()
        updated_design_data['metadata']['version'] = updated_design_data['metadata'].get('version', 0) + 1
        
        # Save updated JSON
        json_path = project_dir / "design.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(updated_design_data, f, indent=2)
        
        # Regenerate AutoLISP from updated data
        from converters.json_to_autolisp import convert_json_to_autolisp
        lsp_path = project_dir / "floorplan.lsp"
        autolisp_code = convert_json_to_autolisp(updated_design_data)
        with open(lsp_path, 'w', encoding='utf-8') as f:
            f.write(autolisp_code)
        
        # Regenerate DXF
        from converters.json_to_dxf import convert_json_to_dxf
        dxf_path = project_dir / "floorplan.dxf"
        convert_json_to_dxf(updated_design_data, str(dxf_path))
        
        # Regenerate DWG
        from converters.dxf_to_dwg import convert_dxf_to_dwg
        dwg_path = project_dir / "floorplan.dwg"
        convert_dxf_to_dwg(str(dxf_path), str(dwg_path))
        
        return str(project_dir)
    
    def get_project(self, project_id):
        """Load project data"""
        json_path = self.base_dir / f"project_{project_id}" / "design.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_file_path(self, project_id, file_type):
        """Get path to specific file type"""
        project_dir = self.base_dir / f"project_{project_id}"
        
        file_map = {
            'json': 'design.json',
            'lsp': 'floorplan.lsp',
            'dxf': 'floorplan.dxf',
            'dwg': 'floorplan.dwg'
        }
        
        return str(project_dir / file_map[file_type])
    
    def list_projects(self):
        """List all projects"""
        projects = []
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir():
                json_path = project_dir / "design.json"
                if json_path.exists():
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            projects.append({
                                'project_id': data['metadata'].get('project_id', 'unknown'),
                                'building_type': data['metadata'].get('building_type', 'unknown'),
                                'created_at': data['metadata'].get('created_at', ''),
                                'last_modified': data['metadata'].get('last_modified', ''),
                                'version': data['metadata'].get('version', 1)
                            })
                    except Exception as e:
                        print(f"Error reading project {project_dir.name}: {e}")
        return projects
    
    def delete_project(self, project_id):
        """Delete project and all files"""
        import shutil
        project_dir = self.base_dir / f"project_{project_id}"
        
        if not project_dir.exists():
            raise FileNotFoundError(f"Project {project_id} not found")
        
        shutil.rmtree(project_dir)
        return True
