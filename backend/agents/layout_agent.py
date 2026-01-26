"""
Agent 4: Layout Planning Agent
Converts dimensions into 2D spatial coordinates
"""

import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from templates.prompts import LAYOUT_AGENT_PROMPT


class LayoutAgent:
    """
    Plans spatial layout and generates 2D coordinates
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )
        self.prompt_template = PromptTemplate(
            input_variables=["dimensions"],
            template=LAYOUT_AGENT_PROMPT
        )
    
    def plan(self, dimensions: dict) -> dict:
        """
        Generate 2D spatial layout
        
        Args:
            dimensions: Output from RulesAgent
            
        Returns:
            Dictionary with room coordinates and geometry
        """
        try:
            # Format prompt with dimensions
            prompt = self.prompt_template.format(
                dimensions=json.dumps(dimensions, indent=2)
            )
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response
            layout = self._extract_json(response.content)
            
            # Validate structure
            self._validate_layout(layout)
            
            return layout
            
        except Exception as e:
            print(f"Error in LayoutAgent: {e}")
            # Return default layout on error
            return self._get_default_layout()
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Could not extract valid JSON from response")
    
    def _validate_layout(self, layout: dict):
        """Validate layout structure"""
        required_keys = ["bounding_box", "rooms", "walls", "doors"]
        
        for key in required_keys:
            if key not in layout:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate bounding box
        if "width_mm" not in layout["bounding_box"] or "height_mm" not in layout["bounding_box"]:
            raise ValueError("bounding_box must have width_mm and height_mm")
        
        # Validate rooms
        if not isinstance(layout["rooms"], list):
            raise ValueError("rooms must be a list")
        
        for room in layout["rooms"]:
            required_keys = ["name", "x1", "y1", "x2", "y2"]
            for key in required_keys:
                if key not in room:
                    raise ValueError(f"Each room must have '{key}'")
    
    def _get_default_layout(self) -> dict:
        """Return default layout for error cases"""
        return {
            "bounding_box": {
                "width_mm": 10000,
                "height_mm": 10000
            },
            "rooms": [
                {
                    "name": "Living Room",
                    "x1": 0,
                    "y1": 0,
                    "x2": 4000,
                    "y2": 5000
                },
                {
                    "name": "Kitchen",
                    "x1": 0,
                    "y1": 5000,
                    "x2": 4000,
                    "y2": 7500
                },
                {
                    "name": "Bedroom 1",
                    "x1": 4000,
                    "y1": 0,
                    "x2": 7500,
                    "y2": 3500
                },
                {
                    "name": "Bedroom 2",
                    "x1": 7500,
                    "y1": 5000,
                    "x2": 10000,
                    "y2": 8500
                },
                {
                    "name": "Bathroom 1",
                    "x1": 4000,
                    "y1": 3500,
                    "x2": 6000,
                    "y2": 5500
                },
                {
                    "name": "Bathroom 2",
                    "x1": 7500,
                    "y1": 8500,
                    "x2": 9300,
                    "y2": 10000
                }
            ],
            "walls": [
                {"x1": 0, "y1": 0, "x2": 10000, "y2": 0, "type": "external"},
                {"x1": 10000, "y1": 0, "x2": 10000, "y2": 10000, "type": "external"},
                {"x1": 10000, "y1": 10000, "x2": 0, "y2": 10000, "type": "external"},
                {"x1": 0, "y1": 10000, "x2": 0, "y2": 0, "type": "external"}
            ],
            "doors": [
                {
                    "room1": "Living Room",
                    "room2": "entrance",
                    "x": 2000,
                    "y": 0,
                    "width": 900,
                    "orientation": "horizontal"
                }
            ]
        }
