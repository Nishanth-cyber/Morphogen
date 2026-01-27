import subprocess
import os
from pathlib import Path

def convert_dxf_to_dwg(dxf_path, dwg_path):
    """
    Convert DXF to DWG using ODA File Converter
    
    Args:
        dxf_path: Path to input DXF file
        dwg_path: Path to output DWG file
        
    Returns:
        dwg_path if successful, None if conversion failed
    """
    
    # ODA File Converter paths (common installation locations)
    converter_paths = [
        "C:/Program Files/ODA/ODAFileConverter 25.5.0/ODAFileConverter.exe",
        "C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe",
        "C:/Program Files (x86)/ODA/ODAFileConverter/ODAFileConverter.exe",
    ]
    
    converter_path = None
    for path in converter_paths:
        if os.path.exists(path):
            converter_path = path
            break
    
    # Check if ODA converter is installed
    if not converter_path:
        print("Warning: ODA File Converter not found. Skipping DWG conversion.")
        print("Download from: https://www.opendesign.com/guestfiles/oda_file_converter")
        print("Searched paths:", converter_paths)
        return None
    
    try:
        # ODA File Converter command line syntax:
        # ODAFileConverter.exe "input_folder" "output_folder" "output_version" "output_format" "recurse" "audit"
        
        input_folder = str(Path(dxf_path).parent)
        output_folder = str(Path(dwg_path).parent)
        
        result = subprocess.run([
            converter_path,
            input_folder,
            output_folder,
            "ACAD2018",  # Output DWG version (compatible with AutoCAD 2018+)
            "DWG",       # Output format
            "0",         # Don't recurse subdirectories
            "1"          # Audit files
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"DWG conversion successful: {dwg_path}")
            return dwg_path
        else:
            print(f"DWG conversion failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("DWG conversion timed out")
        return None
    except Exception as e:
        print(f"DWG conversion error: {str(e)}")
        return None


def check_oda_converter_installed():
    """
    Check if ODA File Converter is installed
    
    Returns:
        True if installed, False otherwise
    """
    converter_paths = [
        "C:/Program Files/ODA/ODAFileConverter 25.5.0/ODAFileConverter.exe",
        "C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe",
        "C:/Program Files (x86)/ODA/ODAFileConverter/ODAFileConverter.exe",
    ]
    
    for path in converter_paths:
        if os.path.exists(path):
            return True
    
    return False
