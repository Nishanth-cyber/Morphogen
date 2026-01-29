from schemas.geometry import GeometryOutput
from typing import List, Tuple

def export_to_svg(geometry: GeometryOutput, scale: float = 10.0, use_dark_mode: bool = False) -> str:
    """
    Exports geometry to SVG with proper error handling and empty geometry support.
    
    IMPROVEMENTS:
    - Better empty geometry handling
    - Proper viewBox calculation
    - Layer styling
    - Annotations support
    - Process units support
    - Fallback for missing data
    
    Args:
        geometry: GeometryOutput object
        scale: Pixels per unit (default: 10)
        use_dark_mode: Use dark background (default: False)
    
    Returns:
        str: Valid SVG content
    """
    try:
        # Helper for coordinate extraction
        def get_coords(pt):
            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                return float(pt[0]), float(pt[1])
            elif isinstance(pt, dict) and 'x' in pt and 'y' in pt:
                return float(pt['x']), float(pt['y'])
            elif hasattr(pt, 'x') and hasattr(pt, 'y'):
                return float(pt.x), float(pt.y)
            return None

        # Collect all coordinates for bounding box
        all_x = []
        all_y = []
        has_geometry = False
        
        print("DEBUG: SVG Export - Starting coordinate collection...")

        # === INDUSTRIAL COMPONENTS ===
        
        # Process Units
        if hasattr(geometry, 'process_units') and geometry.process_units:
            print(f"DEBUG: Processing {len(geometry.process_units)} process units")
            for unit in geometry.process_units:
                if hasattr(unit, 'boundary') and unit.boundary:
                    for pt in unit.boundary:
                        coords = get_coords(pt)
                        if coords:
                            all_x.append(coords[0])
                            all_y.append(coords[1])
                            has_geometry = True
        
        # Equipment
        if hasattr(geometry, 'equipment') and geometry.equipment:
            print(f"DEBUG: Processing {len(geometry.equipment)} equipment items")
            for eq in geometry.equipment:
                if hasattr(eq, 'position') and hasattr(eq, 'width') and hasattr(eq, 'length'):
                    coords = get_coords(eq.position)
                    if coords:
                        x, y = coords
                        w, h = float(eq.width), float(eq.length)
                        all_x.extend([x, x + w])
                        all_y.extend([y, y + h])
                        has_geometry = True
        
        # Pipes
        if hasattr(geometry, 'pipes') and geometry.pipes:
            print(f"DEBUG: Processing {len(geometry.pipes)} pipes")
            for pipe in geometry.pipes:
                start = get_coords(pipe.start)
                end = get_coords(pipe.end)
                if start and end:
                    all_x.extend([start[0], end[0]])
                    all_y.extend([start[1], end[1]])
                    has_geometry = True
        
        # Valves
        if hasattr(geometry, 'valves') and geometry.valves:
            print(f"DEBUG: Processing {len(geometry.valves)} valves")
            for valve in geometry.valves:
                coords = get_coords(valve.position)
                if coords:
                    x, y = coords
                    size = float(getattr(valve, 'size', 500)) / 1000.0
                    all_x.extend([x - size, x + size])
                    all_y.extend([y - size, y + size])
                    has_geometry = True
        
        # === BUILDING COMPONENTS ===
        
        # Walls
        if hasattr(geometry, 'walls') and geometry.walls:
             for wall in geometry.walls:
                start = get_coords(wall.start)
                end = get_coords(wall.end)
                if start and end:
                    all_x.extend([start[0], end[0]])
                    all_y.extend([start[1], end[1]])
                    has_geometry = True
        
        # Doors and Windows (similar logic)
        for comp_list in [getattr(geometry, 'doors', []), getattr(geometry, 'windows', [])]:
            for comp in comp_list:
                start = get_coords(comp.start)
                end = get_coords(comp.end)
                if start and end:
                    all_x.extend([start[0], end[0]])
                    all_y.extend([start[1], end[1]])
                    has_geometry = True

        print(f"DEBUG: SVG Export - Has Geometry: {has_geometry}, Points: {len(all_x)}")
        
        # Check if we have any valid geometry
        if not has_geometry or not all_x or not all_y:
            return generate_empty_svg("No geometry to display")
        
        # Calculate bounding box with margin
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        # Add 10% margin
        width_units = max_x - min_x
        height_units = max_y - min_y
        margin = max(width_units, height_units) * 0.1 if width_units > 0 and height_units > 0 else 5
        
        # Adjust for zero-size designs
        if width_units < 0.1:
            width_units = 10
            margin = 5
        if height_units < 0.1:
            height_units = 10
            margin = 5
        
        viewbox_x = (min_x - margin) * scale
        viewbox_y = (min_y - margin) * scale
        viewbox_w = (width_units + 2 * margin) * scale
        viewbox_h = (height_units + 2 * margin) * scale
        
        # SVG styling
        bg_color = "#1a1a1a" if use_dark_mode else "#ffffff"
        text_color = "#ffffff" if use_dark_mode else "#000000"
        grid_color = "#333333" if use_dark_mode else "#e0e0e0"
        
        # Start SVG
        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" ',
            f'viewBox="{viewbox_x:.2f} {viewbox_y:.2f} {viewbox_w:.2f} {viewbox_h:.2f}" ',
            f'width="100%" height="100%" ',
            f'style="background-color:{bg_color}; border:1px solid {grid_color}">',
            '',
            '<!-- Generated by Morphogen -->',
            ''
        ]
        
        # Define styles
        svg_lines.append('<defs>')
        svg_lines.append(f'<style>')
        svg_lines.append(f'.boundary {{ fill: none; stroke: {text_color}; stroke-width: 2; stroke-dasharray: 5,5; }}')
        svg_lines.append(f'.equipment {{ fill: #4CAF50; fill-opacity: 0.3; stroke: #2E7D32; stroke-width: 1.5; }}')
        svg_lines.append(f'.pipe {{ stroke: #2196F3; stroke-width: 3; }}')
        svg_lines.append(f'.valve {{ fill: #F44336; fill-opacity: 0.6; stroke: #C62828; stroke-width: 1; }}')
        svg_lines.append(f'.wall {{ stroke: {text_color}; stroke-width: 4; }}')
        svg_lines.append(f'.door {{ stroke: #FF5722; stroke-width: 4; }}')
        svg_lines.append(f'.window {{ stroke: #00BCD4; stroke-width: 3; }}')
        svg_lines.append(f'.text {{ fill: {text_color}; font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }}')
        svg_lines.append(f'</style>')
        svg_lines.append('</defs>')
        svg_lines.append('')
        
        # === DRAW COMPONENTS ===
        
        # Draw Process Units (Boundaries)
        if hasattr(geometry, 'process_units') and geometry.process_units:
            svg_lines.append('<!-- Process Units -->')
            svg_lines.append('<g id="process-units">')
            for unit in geometry.process_units:
                if hasattr(unit, 'boundary') and unit.boundary and len(unit.boundary) >= 3:
                    try:
                        points = ' '.join([f"{float(pt[0])*scale:.2f},{float(pt[1])*scale:.2f}" 
                                          for pt in unit.boundary])
                        svg_lines.append(f'<polygon points="{points}" class="boundary" />')
                        
                        # Add label
                        if hasattr(unit, 'name'):
                            centroid_x = sum(float(pt[0]) for pt in unit.boundary) / len(unit.boundary) * scale
                            centroid_y = sum(float(pt[1]) for pt in unit.boundary) / len(unit.boundary) * scale
                            svg_lines.append(f'<text x="{centroid_x:.2f}" y="{centroid_y:.2f}" class="text">{unit.name}</text>')
                    except Exception as e:
                        print(f"Warning: Failed to draw process unit: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Equipment
        if hasattr(geometry, 'equipment') and geometry.equipment:
            svg_lines.append('<!-- Equipment -->')
            svg_lines.append('<g id="equipment">')
            for eq in geometry.equipment:
                if hasattr(eq, 'position') and hasattr(eq, 'width') and hasattr(eq, 'length'):
                    try:
                        x = float(eq.position[0]) * scale
                        y = float(eq.position[1]) * scale
                        w = float(eq.width) * scale
                        h = float(eq.length) * scale
                        svg_lines.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" class="equipment" />')
                        
                        # Add label
                        if hasattr(eq, 'id'):
                            cx, cy = x + w/2, y + h/2
                            svg_lines.append(f'<text x="{cx:.2f}" y="{cy:.2f}" class="text" font-size="10">{eq.id}</text>')
                    except Exception as e:
                        print(f"Warning: Failed to draw equipment: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Pipes
        if hasattr(geometry, 'pipes') and geometry.pipes:
            svg_lines.append('<!-- Pipes -->')
            svg_lines.append('<g id="pipes">')
            for pipe in geometry.pipes:
                if hasattr(pipe, 'start') and hasattr(pipe, 'end'):
                    try:
                        x1, y1 = float(pipe.start[0]) * scale, float(pipe.start[1]) * scale
                        x2, y2 = float(pipe.end[0]) * scale, float(pipe.end[1]) * scale
                        svg_lines.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="pipe" />')
                    except Exception as e:
                        print(f"Warning: Failed to draw pipe: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Valves
        if hasattr(geometry, 'valves') and geometry.valves:
            svg_lines.append('<!-- Valves -->')
            svg_lines.append('<g id="valves">')
            for valve in geometry.valves:
                if hasattr(valve, 'position'):
                    try:
                        x, y = float(valve.position[0]) * scale, float(valve.position[1]) * scale
                        size = float(getattr(valve, 'size', 500)) / 1000.0 * scale
                        svg_lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{size/2:.2f}" class="valve" />')
                    except Exception as e:
                        print(f"Warning: Failed to draw valve: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Walls
        if hasattr(geometry, 'walls') and geometry.walls:
            svg_lines.append('<!-- Walls -->')
            svg_lines.append('<g id="walls">')
            for wall in geometry.walls:
                if hasattr(wall, 'start') and hasattr(wall, 'end'):
                    try:
                        x1, y1 = float(wall.start[0]) * scale, float(wall.start[1]) * scale
                        x2, y2 = float(wall.end[0]) * scale, float(wall.end[1]) * scale
                        svg_lines.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="wall" />')
                    except Exception as e:
                        print(f"Warning: Failed to draw wall: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Doors
        if hasattr(geometry, 'doors') and geometry.doors:
            svg_lines.append('<!-- Doors -->')
            svg_lines.append('<g id="doors">')
            for door in geometry.doors:
                if hasattr(door, 'start') and hasattr(door, 'end'):
                    try:
                        x1, y1 = float(door.start[0]) * scale, float(door.start[1]) * scale
                        x2, y2 = float(door.end[0]) * scale, float(door.end[1]) * scale
                        svg_lines.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="door" />')
                    except Exception as e:
                        print(f"Warning: Failed to draw door: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Windows
        if hasattr(geometry, 'windows') and geometry.windows:
            svg_lines.append('<!-- Windows -->')
            svg_lines.append('<g id="windows">')
            for window in geometry.windows:
                if hasattr(window, 'start') and hasattr(window, 'end'):
                    try:
                        x1, y1 = float(window.start[0]) * scale, float(window.start[1]) * scale
                        x2, y2 = float(window.end[0]) * scale, float(window.end[1]) * scale
                        svg_lines.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="window" />')
                    except Exception as e:
                        print(f"Warning: Failed to draw window: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Draw Annotations
        if hasattr(geometry, 'annotations') and geometry.annotations:
            svg_lines.append('<!-- Annotations -->')
            svg_lines.append('<g id="annotations">')
            for ann in geometry.annotations:
                if hasattr(ann, 'text') and hasattr(ann, 'position'):
                    try:
                        x, y = float(ann.position[0]) * scale, float(ann.position[1]) * scale
                        svg_lines.append(f'<text x="{x:.2f}" y="{y:.2f}" class="text" fill="#FF9800">{ann.text}</text>')
                    except Exception as e:
                        print(f"Warning: Failed to draw annotation: {e}")
            svg_lines.append('</g>')
            svg_lines.append('')
        
        # Close SVG
        svg_lines.append('</svg>')
        
        result = '\n'.join(svg_lines)
        print(f"SVG Export: Generated {len(svg_lines)} lines")
        return result
        
    except Exception as e:
        print(f"Error generating SVG: {e}")
        import traceback
        traceback.print_exc()
        return generate_empty_svg(f"Error: {str(e)}")


def generate_empty_svg(message: str = "No geometry available") -> str:
    """Generate a placeholder SVG when no geometry is available"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" width="400" height="200">
    <rect width="400" height="200" fill="#f5f5f5"/>
    <text x="200" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#666">
        {message}
    </text>
    <text x="200" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#999">
        Try adjusting your design parameters
    </text>
</svg>'''