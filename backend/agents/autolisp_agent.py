"""
Agent 5: AutoLISP Generation Agent
Converts layout geometry into executable AutoCAD code
"""

import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from templates.prompts import AUTOLISP_AGENT_PROMPT


class AutoLispAgent:
    """
    Generates executable AutoLISP code from layout geometry
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )
        self.prompt_template = PromptTemplate(
            input_variables=["layout_data"],
            template=AUTOLISP_AGENT_PROMPT
        )
    
    def generate(self, layout_data: dict) -> str:
        """
        Generate AutoLISP code
        
        Args:
            layout_data: Output from LayoutAgent
            
        Returns:
            String containing executable AutoLISP code
        """
        try:
            # Format prompt with layout data
            prompt = self.prompt_template.format(
                layout_data=json.dumps(layout_data, indent=2)
            )
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Extract AutoLISP code
            autolisp_code = self._extract_code(response.content)
            
            # Validate code structure
            self._validate_code(autolisp_code)
            
            return autolisp_code
            
        except Exception as e:
            print(f"Error in AutoLispAgent: {e}")
            # Return default code on error
            return self._get_default_code(layout_data)
    
    def _extract_code(self, text: str) -> str:
        """Extract AutoLISP code from LLM response"""
        # Remove markdown code blocks if present
        text = re.sub(r'```lisp\s*', '', text)
        text = re.sub(r'```autolisp\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Return cleaned text
        return text.strip()
    
    def _validate_code(self, code: str):
        """Validate AutoLISP code structure"""
        # Check for required elements
        if "(defun c:GENPLAN" not in code:
            raise ValueError("Code must define c:GENPLAN command")
        
        if "(command" not in code:
            raise ValueError("Code must contain AutoCAD commands")
        
        # Check for balanced parentheses
        if code.count('(') != code.count(')'):
            raise ValueError("Unbalanced parentheses in AutoLISP code")
    
    def _get_default_code(self, layout_data: dict) -> str:
        """Generate basic AutoLISP code as fallback"""
        
        bbox = layout_data.get("bounding_box", {"width_mm": 10000, "height_mm": 10000})
        rooms = layout_data.get("rooms", [])
        
        code = """(defun c:GENPLAN (/ wall-thickness door-width)
  
  ;; Set units and variables
  (setq wall-thickness 230)
  (setq door-width 900)
  
  ;; Create layers
  (command "._LAYER" "N" "WALLS" "C" "7" "WALLS" "")
  (command "._LAYER" "N" "DOORS" "C" "3" "DOORS" "")
  (command "._LAYER" "N" "TEXT" "C" "2" "TEXT" "")
  
  ;; Set WALLS layer current
  (command "._LAYER" "S" "WALLS" "")
  
  ;; External walls - bounding box
  (command "._PLINE" "0,0" "{},{}" "{},{}" "0,{}" "C")
  
""".format(
            bbox["width_mm"], 0,
            bbox["width_mm"], bbox["height_mm"],
            bbox["height_mm"]
        )
        
        # Add internal walls for each room
        for room in rooms:
            x1, y1 = room.get("x1", 0), room.get("y1", 0)
            x2, y2 = room.get("x2", 0), room.get("y2", 0)
            
            # Draw room boundaries
            code += f'  ;; {room.get("name", "Room")}\n'
            code += f'  (command "._LINE" "{x1},{y1}" "{x2},{y1}" "")\n'
            code += f'  (command "._LINE" "{x2},{y1}" "{x2},{y2}" "")\n'
            code += f'  (command "._LINE" "{x2},{y2}" "{x1},{y2}" "")\n'
            code += f'  (command "._LINE" "{x1},{y2}" "{x1},{y1}" "")\n'
            code += '\n'
        
        code += """  ;; Set TEXT layer current
  (command "._LAYER" "S" "TEXT" "")
  
"""
        
        # Add room labels
        for room in rooms:
            x1, y1 = room.get("x1", 0), room.get("y1", 0)
            x2, y2 = room.get("x2", 0), room.get("y2", 0)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            name = room.get("name", "Room").replace(" ", "")
            
            code += f'  (command "._TEXT" "J" "MC" "{center_x},{center_y}" "300" "0" "{name}")\n'
        
        code += """
  ;; Zoom extents
  (command "._ZOOM" "E")
  
  (princ "\\nFloor plan generated successfully!")
  (princ)
)

(princ "\\nType GENPLAN to generate the plan.")
(princ)
"""
        
        return code
