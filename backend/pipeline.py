"""
Main pipeline orchestrating all agents and returning JSON + AutoLISP
"""

import json
import os
from datetime import datetime
from config import Config
from agents import (
    IntentAgent,
    RequirementAgent,
    RulesAgent,
    LayoutAgent,
    AutoLispAgent
)


def run_pipeline(user_input: str) -> dict:
    """
    Simplified pipeline runner that returns JSON design data
    
    Args:
        user_input: Natural language construction request
        
    Returns:
        Dictionary with design data in JSON format
    """
    
    print(f"\n{'='*60}")
    print(f"EXECUTING GENERATIVE DESIGN PIPELINE")
    print(f"{'='*60}")
    print(f"Input: {user_input}\n")
    
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize agents
        intent_agent = IntentAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        requirement_agent = RequirementAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        rules_agent = RulesAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        layout_agent = LayoutAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        # Agent 1: Intent Understanding
        print("→ Agent 1: Understanding intent...")
        intent_data = intent_agent.parse(user_input)
        print(f"  ✓ Extracted intent: {intent_data.get('building_type')} - {intent_data.get('bedroom_count')} bedrooms")
        
        # Agent 2: Requirement Expansion
        print("→ Agent 2: Expanding requirements...")
        requirements = requirement_agent.expand(intent_data)
        print(f"  ✓ Generated {len(requirements.get('rooms', []))} rooms - Total area: {requirements.get('total_area_sqft')} sqft")
        
        # Agent 3: Engineering Rules
        print("→ Agent 3: Applying engineering rules...")
        dimensions = rules_agent.validate(requirements)
        print(f"  ✓ Validated dimensions - Wall thickness: {dimensions.get('wall_thickness_mm')}mm")
        
        # Agent 4: Layout Planning
        print("→ Agent 4: Planning spatial layout...")
        layout = layout_agent.plan(dimensions)
        bbox = layout.get('bounding_box', {})
        print(f"  ✓ Generated layout - Size: {bbox.get('width_mm')}mm × {bbox.get('height_mm')}mm")
        
        # Convert layout to JSON format for frontend
        design_json = convert_layout_to_json(layout, intent_data, requirements)
        
        print(f"\n{'='*60}")
        print(f"✓ PIPELINE COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
        return design_json
        
    except Exception as e:
        print(f"\n✗ PIPELINE ERROR: {e}\n")
        raise e


def convert_layout_to_json(layout: dict, intent_data: dict, requirements: dict) -> dict:
    """
    Convert layout data to JSON format compatible with frontend
    
    Args:
        layout: Layout data from Agent 4
        intent_data: Intent data from Agent 1
        requirements: Requirements data from Agent 2
        
    Returns:
        JSON design data
    """
    
    # Extract bounding box
    bbox = layout.get('bounding_box', {})
    
    # Extract rooms
    rooms_data = []
    for room in layout.get('rooms', []):
        rooms_data.append({
            "id": room.get('id', f"room_{len(rooms_data)}"),
            "name": room.get('name', 'Room'),
            "bounds": {
                "x": room.get('x_mm', 0),
                "y": room.get('y_mm', 0),
                "width": room.get('width_mm', 0),
                "height": room.get('height_mm', 0)
            },
            "area": room.get('area_sqft', 0),
            "label_position": [
                room.get('x_mm', 0) + room.get('width_mm', 0) / 2,
                room.get('y_mm', 0) + room.get('height_mm', 0) / 2
            ]
        })
    
    # Extract walls
    walls_data = []
    for wall in layout.get('walls', []):
        walls_data.append({
            "id": wall.get('id', f"wall_{len(walls_data)}"),
            "type": "line",
            "start": [wall.get('x1_mm', 0), wall.get('y1_mm', 0)],
            "end": [wall.get('x2_mm', 0), wall.get('y2_mm', 0)],
            "layer": "walls",
            "thickness": wall.get('thickness_mm', 230)
        })
    
    # Extract doors
    doors_data = []
    for door in layout.get('doors', []):
        doors_data.append({
            "id": door.get('id', f"door_{len(doors_data)}"),
            "type": "door",
            "position": [door.get('x_mm', 0), door.get('y_mm', 0)],
            "width": door.get('width_mm', 900),
            "orientation": door.get('orientation', 'horizontal'),
            "layer": "doors"
        })
    
    # Extract windows (if present)
    windows_data = []
    for window in layout.get('windows', []):
        windows_data.append({
            "id": window.get('id', f"window_{len(windows_data)}"),
            "type": "window",
            "position": [window.get('x_mm', 0), window.get('y_mm', 0)],
            "width": window.get('width_mm', 1200),
            "orientation": window.get('orientation', 'horizontal'),
            "layer": "windows"
        })
    
    # Create external boundary points
    boundary_points = [
        [0, 0],
        [bbox.get('width_mm', 10000), 0],
        [bbox.get('width_mm', 10000), bbox.get('height_mm', 10000)],
        [0, bbox.get('height_mm', 10000)]
    ]
    
    # Build final JSON structure
    design_json = {
        "metadata": {
            "units": "mm",
            "building_type": intent_data.get('building_type', 'residential'),
            "total_area": requirements.get('total_area_sqft', 1000),
            "bedroom_count": intent_data.get('bedroom_count', 2),
            "timestamp": datetime.now().isoformat()
        },
        "elements": {
            "external_boundary": {
                "type": "polyline",
                "points": boundary_points,
                "closed": True,
                "layer": "walls"
            },
            "walls": walls_data,
            "doors": doors_data,
            "windows": windows_data,
            "rooms": rooms_data
        }
    }
    
    return design_json


class GenerativeDesignPipeline:
    """
    Main pipeline class (for backward compatibility)
    """
    
    def __init__(self):
        Config.validate()
        self.execution_log = []
    
    def execute(self, user_input: str) -> dict:
        """
        Execute the full pipeline
        
        Args:
            user_input: Natural language construction request
            
        Returns:
            Dictionary with design data and metadata
        """
        try:
            design_json = run_pipeline(user_input)
            
            return {
                "success": True,
                "design_data": design_json,
                "message": "Design generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Test function
def test_pipeline():
    """Test the pipeline with sample inputs"""
    
    test_inputs = [
        "Build me a 2-bedroom house",
        "I need a small residential building with 3 bedrooms",
        "Design a cozy home"
    ]
    
    for user_input in test_inputs:
        print(f"\nTesting: {user_input}")
        print("-" * 60)
        
        try:
            result = run_pipeline(user_input)
            print(f"✓ Success! Generated design with {len(result['elements']['rooms'])} rooms")
            
            # Save test output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_output_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Saved to: {output_file}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print()


if __name__ == "__main__":
    test_pipeline()
