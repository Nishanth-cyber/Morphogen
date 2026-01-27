"""
Complete Ollama-based pipeline - 100% FREE
Uses local AI models via Docker
"""

import json
import requests
from datetime import datetime


def run_ollama_pipeline(user_input: str, model_name: str = "llama3.2") -> dict:
    """
    Run complete design pipeline using Ollama (FREE)
    
    Args:
        user_input: Natural language construction request
        model_name: Ollama model to use
        
    Returns:
        Dictionary with design data in JSON format
    """
    
    print(f"\n{'='*60}")
    print(f"OLLAMA PIPELINE (FREE)")
    print(f"{'='*60}")
    print(f"Model: {model_name}")
    print(f"Input: {user_input}\n")
    
    base_url = "http://localhost:11434"
    
    # Check if Ollama is available
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code != 200:
            raise Exception("Ollama not responding")
    except Exception as e:
        print(f"⚠️ Ollama not available: {e}")
        print("Falling back to simple generation...")
        from simple_pipeline import run_simple_pipeline
        return run_simple_pipeline(user_input)
    
    try:
        # Agent 1: Intent Understanding
        print("→ Agent 1: Understanding intent...")
        intent_data = ollama_intent_agent(base_url, model_name, user_input)
        print(f"  ✓ Type: {intent_data['building_type']}, Bedrooms: {intent_data['bedroom_count']}")
        
        # Agent 2: Requirement Expansion  
        print("→ Agent 2: Expanding requirements...")
        requirements = ollama_requirement_agent(base_url, model_name, intent_data)
        print(f"  ✓ Rooms: {len(requirements['rooms'])}, Area: {requirements['total_area_sqft']} sqft")
        
        # Agent 3: Engineering Rules (no AI needed)
        print("→ Agent 3: Applying rules...")
        dimensions = apply_engineering_rules(requirements)
        print(f"  ✓ Dimensions validated")
        
        # Agent 4: Layout Planning
        print("→ Agent 4: Creating layout...")
        layout = create_layout(dimensions)
        print(f"  ✓ Layout created")
        
        # Convert to JSON
        design_json = convert_to_json(layout, intent_data, requirements)
        
        print(f"\n{'='*60}")
        print(f"✅ PIPELINE COMPLETED")
        print(f"{'='*60}\n")
        
        return design_json
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("Falling back to simple generation...\n")
        from simple_pipeline import run_simple_pipeline
        return run_simple_pipeline(user_input)


def ollama_generate(base_url: str, model: str, prompt: str, temperature: float = 0.3) -> str:
    """Call Ollama API"""
    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 800
            }
        },
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.status_code}")
    
    return response.json()['response']


def extract_json(text: str) -> dict:
    """Extract JSON from text"""
    import re
    
    # Remove markdown
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except:
        # Find JSON in text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("No JSON found")


def ollama_intent_agent(base_url: str, model: str, user_input: str) -> dict:
    """Agent 1: Understand intent"""
    
    prompt = f"""You are an architect. Extract info from this request.

Request: "{user_input}"

Return ONLY this JSON format:
{{
  "building_type": "residential",
  "bedroom_count": 2,
  "floor_count": 1
}}

Extract bedroom count from request. If not mentioned, use 2.
No explanation, only JSON."""

    try:
        response = ollama_generate(base_url, model, prompt, 0.2)
        data = extract_json(response)
        
        # Validate
        if 'bedroom_count' not in data:
            data['bedroom_count'] = 2
        if 'building_type' not in data:
            data['building_type'] = 'residential'
        if 'floor_count' not in data:
            data['floor_count'] = 1
            
        return data
    except Exception as e:
        print(f"  ⚠️ Agent 1 error: {e}, using defaults")
        # Parse bedroom count manually
        bedroom_count = 2
        if "3" in user_input or "three" in user_input.lower():
            bedroom_count = 3
        elif "1" in user_input or "one" in user_input.lower():
            bedroom_count = 1
        elif "4" in user_input or "four" in user_input.lower():
            bedroom_count = 4
            
        return {
            "building_type": "residential",
            "bedroom_count": bedroom_count,
            "floor_count": 1
        }


def ollama_requirement_agent(base_url: str, model: str, intent: dict) -> dict:
    """Agent 2: Expand requirements"""
    
    bedroom_count = intent['bedroom_count']
    bathroom_count = max(1, (bedroom_count + 1) // 2)
    
    prompt = f"""Create room list for {bedroom_count}-bedroom house.

Requirements:
- {bedroom_count} bedrooms
- 1 living room  
- 1 kitchen
- {bathroom_count} bathrooms

Return ONLY this JSON:
{{
  "building_type": "residential",
  "total_area_sqft": 1000,
  "floor_count": 1,
  "rooms": [
    {{"name": "Living Room", "area_sqft": 150, "type": "living"}},
    {{"name": "Kitchen", "area_sqft": 80, "type": "kitchen"}},
    {{"name": "Bedroom 1", "area_sqft": 120, "type": "bedroom"}},
    {{"name": "Bathroom 1", "area_sqft": 30, "type": "bathroom"}}
  ]
}}

Room sizes:
- Living: 150-200 sqft
- Bedroom: 100-140 sqft  
- Kitchen: 80-100 sqft
- Bathroom: 25-35 sqft

Total area = sum(rooms) * 1.2

Only JSON, no explanation."""

    try:
        response = ollama_generate(base_url, model, prompt, 0.3)
        data = extract_json(response)
        
        if 'rooms' not in data or not data['rooms']:
            raise ValueError("No rooms")
            
        return data
    except Exception as e:
        print(f"  ⚠️ Agent 2 error: {e}, using defaults")
        return get_default_requirements(bedroom_count)


def get_default_requirements(bedroom_count: int) -> dict:
    """Default room layout"""
    rooms = [
        {"name": "Living Room", "area_sqft": 150, "type": "living"},
        {"name": "Kitchen", "area_sqft": 80, "type": "kitchen"},
    ]
    
    for i in range(bedroom_count):
        rooms.append({
            "name": f"Bedroom {i+1}",
            "area_sqft": 120 if i == 0 else 100,
            "type": "bedroom"
        })
    
    bathroom_count = max(1, (bedroom_count + 1) // 2)
    for i in range(bathroom_count):
        rooms.append({
            "name": f"Bathroom {i+1}",
            "area_sqft": 30 if i == 0 else 25,
            "type": "bathroom"
        })
    
    total = sum(r['area_sqft'] for r in rooms) * 1.2
    
    return {
        "building_type": "residential",
        "total_area_sqft": int(total),
        "floor_count": 1,
        "rooms": rooms
    }


def apply_engineering_rules(requirements: dict) -> dict:
    """Agent 3: Apply rules"""
    dimensions = {
        "building_type": requirements['building_type'],
        "wall_thickness_mm": 230,
        "door_width_mm": 900,
        "rooms": []
    }
    
    for room in requirements['rooms']:
        area_sqft = room['area_sqft']
        area_m2 = area_sqft * 0.092903
        side_m = (area_m2 ** 0.5)
        
        width_mm = int(side_m * 1000)
        height_mm = int(side_m * 1000)
        
        # Minimums
        room_type = room.get('type', 'other')
        if room_type == 'bedroom':
            width_mm = max(width_mm, 3000)
            height_mm = max(height_mm, 3000)
        elif room_type == 'bathroom':
            width_mm = max(width_mm, 1500)
            height_mm = max(height_mm, 2000)
        elif room_type == 'kitchen':
            width_mm = max(width_mm, 2500)
        
        dimensions['rooms'].append({
            "name": room['name'],
            "type": room_type,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "area_sqft": area_sqft
        })
    
    return dimensions


def create_layout(dimensions: dict) -> dict:
    """Agent 4: Create layout"""
    rooms = dimensions['rooms']
    
    x, y = 0, 0
    max_width = 0
    
    layout_rooms = []
    walls = []
    doors = []
    
    for i, room in enumerate(rooms):
        w, h = room['width_mm'], room['height_mm']
        
        layout_rooms.append({
            "id": f"room_{i}",
            "name": room['name'],
            "x_mm": x,
            "y_mm": y,
            "width_mm": w,
            "height_mm": h,
            "area_sqft": room['area_sqft']
        })
        
        # Walls
        walls.append({
            "id": f"wall_{i}_top",
            "x1_mm": x, "y1_mm": y,
            "x2_mm": x + w, "y2_mm": y,
            "thickness_mm": 230
        })
        
        walls.append({
            "id": f"wall_{i}_right",
            "x1_mm": x + w, "y1_mm": y,
            "x2_mm": x + w, "y2_mm": y + h,
            "thickness_mm": 230
        })
        
        # Doors
        if i == 0:
            doors.append({
                "id": f"door_{i}",
                "x_mm": x + w//2 - 450,
                "y_mm": y,
                "width_mm": 900,
                "orientation": "horizontal"
            })
        else:
            doors.append({
                "id": f"door_{i}",
                "x_mm": x,
                "y_mm": y + h//2 - 450,
                "width_mm": 900,
                "orientation": "vertical"
            })
        
        y += h
        max_width = max(max_width, w)
    
    return {
        "bounding_box": {"width_mm": max_width, "height_mm": y},
        "rooms": layout_rooms,
        "walls": walls,
        "doors": doors,
        "windows": []
    }


def convert_to_json(layout: dict, intent: dict, requirements: dict) -> dict:
    """Convert to frontend JSON"""
    bbox = layout['bounding_box']
    
    boundary = [
        [0, 0],
        [bbox['width_mm'], 0],
        [bbox['width_mm'], bbox['height_mm']],
        [0, bbox['height_mm']]
    ]
    
    rooms_data = []
    for r in layout['rooms']:
        rooms_data.append({
            "id": r['id'],
            "name": r['name'],
            "bounds": {
                "x": r['x_mm'],
                "y": r['y_mm'],
                "width": r['width_mm'],
                "height": r['height_mm']
            },
            "area": r['area_sqft'],
            "label_position": [
                r['x_mm'] + r['width_mm']/2,
                r['y_mm'] + r['height_mm']/2
            ]
        })
    
    walls_data = []
    for w in layout['walls']:
        walls_data.append({
            "id": w['id'],
            "type": "line",
            "start": [w['x1_mm'], w['y1_mm']],
            "end": [w['x2_mm'], w['y2_mm']],
            "layer": "walls",
            "thickness": w['thickness_mm']
        })
    
    doors_data = []
    for d in layout['doors']:
        doors_data.append({
            "id": d['id'],
            "type": "door",
            "position": [d['x_mm'], d['y_mm']],
            "width": d['width_mm'],
            "orientation": d['orientation'],
            "layer": "doors"
        })
    
    return {
        "metadata": {
            "units": "mm",
            "building_type": intent.get('building_type', 'residential'),
            "total_area": requirements.get('total_area_sqft', 1000),
            "bedroom_count": intent.get('bedroom_count', 2),
            "timestamp": datetime.now().isoformat(),
            "generator": "Ollama (FREE)"
        },
        "elements": {
            "external_boundary": {
                "type": "polyline",
                "points": boundary,
                "closed": True,
                "layer": "walls"
            },
            "walls": walls_data,
            "doors": doors_data,
            "windows": [],
            "rooms": rooms_data
        }
    }
