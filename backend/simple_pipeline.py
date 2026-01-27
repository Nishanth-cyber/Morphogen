"""
Simple fallback pipeline for testing without AI
Generates a basic 2BHK design instantly
"""

def run_simple_pipeline(user_input: str) -> dict:
    """
    Generate a simple 2BHK layout without AI (instant)
    """
    
    print("\n[FALLBACK MODE] Generating simple 2BHK layout...")
    
    # Parse bedroom count from input
    bedroom_count = 2
    if "3" in user_input or "three" in user_input.lower():
        bedroom_count = 3
    elif "1" in user_input or "one" in user_input.lower():
        bedroom_count = 1
    
    # Simple room layout
    rooms = [
        {
            "id": "room_0",
            "name": "Living Room",
            "x_mm": 0,
            "y_mm": 0,
            "width_mm": 4000,
            "height_mm": 5000,
            "area_sqft": 215
        },
        {
            "id": "room_1",
            "name": "Kitchen",
            "x_mm": 0,
            "y_mm": 5000,
            "width_mm": 4000,
            "height_mm": 5000,
            "area_sqft": 215
        }
    ]
    
    # Add bedrooms
    x_offset = 4000
    for i in range(bedroom_count):
        y_pos = i * 3333
        rooms.append({
            "id": f"room_{len(rooms)}",
            "name": f"Bedroom {i+1}",
            "x_mm": x_offset,
            "y_mm": y_pos,
            "width_mm": 3500,
            "height_mm": 3333,
            "area_sqft": 125
        })
    
    # Add bathrooms
    bathroom_count = max(1, (bedroom_count + 1) // 2)
    for i in range(bathroom_count):
        rooms.append({
            "id": f"room_{len(rooms)}",
            "name": f"Bathroom {i+1}",
            "x_mm": 7500,
            "y_mm": i * 2500,
            "width_mm": 2500,
            "height_mm": 2500,
            "area_sqft": 67
        })
    
    # Generate walls
    walls = [
        {"id": "wall_0", "x1_mm": 0, "y1_mm": 5000, "x2_mm": 4000, "y2_mm": 5000, "thickness_mm": 230},
        {"id": "wall_1", "x1_mm": 4000, "y1_mm": 0, "x2_mm": 4000, "y2_mm": 10000, "thickness_mm": 230},
        {"id": "wall_2", "x1_mm": 7500, "y1_mm": 0, "x2_mm": 7500, "y2_mm": 10000, "thickness_mm": 230},
    ]
    
    # Add bedroom dividers
    for i in range(bedroom_count - 1):
        walls.append({
            "id": f"wall_{len(walls)}",
            "x1_mm": 4000,
            "y1_mm": (i + 1) * 3333,
            "x2_mm": 7500,
            "y2_mm": (i + 1) * 3333,
            "thickness_mm": 230
        })
    
    # Generate doors
    doors = [
        {"id": "door_0", "x_mm": 1800, "y_mm": 0, "width_mm": 900, "orientation": "horizontal"},
        {"id": "door_1", "x_mm": 2000, "y_mm": 5000, "width_mm": 900, "orientation": "horizontal"},
        {"id": "door_2", "x_mm": 4000, "y_mm": 2000, "width_mm": 900, "orientation": "vertical"},
    ]
    
    # Build layout structure
    layout = {
        "bounding_box": {
            "width_mm": 10000,
            "height_mm": 10000
        },
        "rooms": rooms,
        "walls": walls,
        "doors": doors,
        "windows": []
    }
    
    # Convert to JSON format
    from pipeline import convert_layout_to_json
    
    intent_data = {
        "building_type": "residential",
        "bedroom_count": bedroom_count
    }
    
    requirements = {
        "total_area_sqft": sum(r.get('area_sqft', 0) for r in rooms)
    }
    
    design_json = convert_layout_to_json(layout, intent_data, requirements)
    
    print("✓ Simple layout generated instantly!")
    
    return design_json
