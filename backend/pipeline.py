"""
Main pipeline orchestrating all agents
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


class GenerativeDesignPipeline:
    """
    Main pipeline that orchestrates all 5 agents
    """
    
    def __init__(self):
        # Validate configuration
        Config.validate()
        
        # Initialize all agents
        self.intent_agent = IntentAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        self.requirement_agent = RequirementAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        self.rules_agent = RulesAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        self.layout_agent = LayoutAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        self.autolisp_agent = AutoLispAgent(
            api_key=Config.GOOGLE_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        self.execution_log = []
    
    def execute(self, user_input: str) -> dict:
        """
        Execute the full pipeline
        
        Args:
            user_input: Natural language construction request
            
        Returns:
            Dictionary with AutoLISP code and execution metadata
        """
        
        print(f"\n{'='*60}")
        print(f"EXECUTING GENERATIVE DESIGN PIPELINE")
        print(f"{'='*60}")
        print(f"Input: {user_input}\n")
        
        self.execution_log = []
        
        try:
            # Agent 1: Intent Understanding
            print("→ Agent 1: Understanding intent...")
            intent_data = self.intent_agent.parse(user_input)
            self._log_step("Intent Understanding", intent_data)
            print(f"  ✓ Extracted intent: {intent_data.get('building_type')} - {intent_data.get('bedroom_count')} bedrooms")
            
            # Agent 2: Requirement Expansion
            print("→ Agent 2: Expanding requirements...")
            requirements = self.requirement_agent.expand(intent_data)
            self._log_step("Requirement Expansion", requirements)
            print(f"  ✓ Generated {len(requirements.get('rooms', []))} rooms - Total area: {requirements.get('total_area_sqft')} sqft")
            
            # Agent 3: Engineering Rules
            print("→ Agent 3: Applying engineering rules...")
            dimensions = self.rules_agent.validate(requirements)
            self._log_step("Engineering Rules", dimensions)
            print(f"  ✓ Validated dimensions - Wall thickness: {dimensions.get('wall_thickness_mm')}mm")
            
            # Agent 4: Layout Planning
            print("→ Agent 4: Planning spatial layout...")
            layout = self.layout_agent.plan(dimensions)
            self._log_step("Layout Planning", layout)
            bbox = layout.get('bounding_box', {})
            print(f"  ✓ Generated layout - Size: {bbox.get('width_mm')}mm × {bbox.get('height_mm')}mm")
            
            # Agent 5: AutoLISP Generation
            print("→ Agent 5: Generating AutoLISP code...")
            autolisp_code = self.autolisp_agent.generate(layout)
            self._log_step("AutoLISP Generation", {"code_length": len(autolisp_code)})
            print(f"  ✓ Generated {len(autolisp_code)} characters of AutoLISP code")
            
            # Save output
            filename = self._save_output(autolisp_code)
            
            print(f"\n{'='*60}")
            print(f"✓ PIPELINE COMPLETED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"Output file: {filename}\n")
            
            return {
                "success": True,
                "autolisp_code": autolisp_code,
                "filename": filename,
                "execution_log": self.execution_log,
                "metadata": {
                    "intent": intent_data,
                    "requirements": requirements,
                    "dimensions": dimensions,
                    "layout": layout
                }
            }
            
        except Exception as e:
            print(f"\n✗ PIPELINE ERROR: {e}\n")
            return {
                "success": False,
                "error": str(e),
                "execution_log": self.execution_log
            }
    
    def _log_step(self, agent_name: str, data: dict):
        """Log execution step"""
        self.execution_log.append({
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    
    def _save_output(self, autolisp_code: str) -> str:
        """Save AutoLISP code to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"floorplan_{timestamp}.lsp"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(autolisp_code)
        
        return filename
    
    def save_execution_log(self, filename: str = None):
        """Save execution log to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"execution_log_{timestamp}.json"
        
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log, f, indent=2)
        
        return filename


# Test function
def test_pipeline():
    """Test the pipeline with sample inputs"""
    pipeline = GenerativeDesignPipeline()
    
    test_inputs = [
        "Build me a 2-bedroom house",
        "I need a small residential building with 3 bedrooms",
        "Design a cozy home"
    ]
    
    for user_input in test_inputs:
        result = pipeline.execute(user_input)
        if result["success"]:
            print(f"Success! Generated: {result['filename']}")
        else:
            print(f"Error: {result['error']}")
        print()


if __name__ == "__main__":
    test_pipeline()
