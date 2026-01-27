"""
Updated Agent Pipeline for Multi-Format Output
"""

import json
from datetime import datetime
from config import Config
from agents import (
    IntentAgent,
    RequirementAgent,
    RulesAgent,
    LayoutAgent
)

class Agent5_DualOutputGenerator:
    """
    Generates both JSON (for web) and structure layout data
    replacing the old AutoLISP agent logic
    """
    
    def __init__(self, layout_data):
        self.layout_data = layout_data
        
    def generate_json(self):
        """Convert layout to JSON for frontend/storage"""
        
        # Build elements structure from layout data
        elements = {
            "external_boundary": {
                "type": "polyline",
                "points": self._get_boundary_points(),
                "closed": True,
                "layer": "walls"
            },
            "walls": [],
            "doors": [],
            "windows": [],
            "rooms": []
        }
        
        # Add internal walls
        for room in self.layout_data.get('rooms', []):
            x1, y1 = room.get('x1', 0), room.get('y1', 0)
            x2, y2 = room.get('x2', 0), room.get('y2', 0)
            
            # Simple box walls for each room (could be optimized to avoid duplicates)
            elements['walls'].extend([
                {"start": (x1, y1), "end": (x2, y1)},
                {"start": (x2, y1), "end": (x2, y2)},
                {"start": (x2, y2), "end": (x1, y2)},
                {"start": (x1, y2), "end": (x1, y1)}
            ])
            
            # Add room metadata
            elements['rooms'].append({
                "name": room.get('name', 'Room'),
                "area": room.get('area', 0),
                "label_position": ((x1+x2)/2, (y1+y2)/2)
            })
            
        # Add basic doors (placeholders based on logic)
        # This part would ideally come from the LayoutAgent, but we infer for now
        for room in self.layout_data.get('rooms', []):
             x1, y1 = room.get('x1', 0), room.get('y1', 0)
             # Add a door on the first wall
             elements['doors'].append({
                 "position": (x1 + 100, y1),
                 "width": 900,
                 "orientation": "horizontal"
             })

        return {
            "metadata": {
                "units": "mm",
                "building_type": "residential", # Should come from intent
                "total_area": self.layout_data.get('total_area', 0),
                "timestamp": datetime.now().isoformat()
            },
            "elements": elements
        }
    
    def generate_autolisp(self):
        """Convert layout directly to AutoLISP code (Legacy support)"""
        # This delegates to the converter utility
        from converters.json_to_autolisp import convert_json_to_autolisp
        design_data = self.generate_json()
        return convert_json_to_autolisp(design_data)

    def _get_boundary_points(self):
        """Get external boundary from layout bbox"""
        bbox = self.layout_data.get('bounding_box', {'width_mm': 10000, 'height_mm': 10000})
        w = bbox.get('width_mm', 10000)
        h = bbox.get('height_mm', 10000)
        return [(0,0), (w,0), (w,h), (0,h)]


def run_pipeline(user_input: str) -> dict:
    """
    Run the multi-agent pipeline from Intent to Layout
    Returns: Layout Data
    """
    Config.validate()
    
    # Initialize agents
    intent_agent = IntentAgent(
        api_key=Config.GOOGLE_API_KEY,
        model_name=Config.MODEL_NAME
    )
    req_agent = RequirementAgent(
        api_key=Config.GOOGLE_API_KEY,
        model_name=Config.MODEL_NAME
    )
    rules_agent = RulesAgent(
        api_key=Config.GOOGLE_API_KEY,
        model_name=Config.MODEL_NAME
    )
    layout_agent = LayoutAgent(
        api_key=Config.GOOGLE_API_KEY,
        model_name=Config.MODEL_NAME
    )
    
    print(f"Pipeline Input: {user_input}")
    
    try:
        # Agent 1: Intent
        print("→ Agent 1: Parsing intent...")
        intent_data = intent_agent.parse(user_input)
        
        # Agent 2: Requirements
        print("→ Agent 2: Expanding requirements...")
        requirements = req_agent.expand(intent_data)
        
        # Agent 3: Rules
        print("→ Agent 3: Validating rules...")
        dimensions = rules_agent.validate(requirements)
        
        # Agent 4: Layout
        print("→ Agent 4: Generating layout...")
        layout_data = layout_agent.plan(dimensions)
        
        print("✓ Pipeline structure generated")
        return layout_data
        
    except Exception as e:
        print(f"Pipeline Error: {e}")
        # Fallback layout for error resilience
        return {
            "bounding_box": {"width_mm": 5000, "height_mm": 5000},
            "rooms": [
                {"name": "Living Room", "x1": 0, "y1": 0, "x2": 5000, "y2": 5000}
            ]
        }
