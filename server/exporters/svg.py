from schemas.geometry import GeometryOutput

def export_to_svg(geometry: GeometryOutput, scale: float = 10.0) -> str:
    """
    Exports geometry to a simple SVG string.
    Scale determines pixels per unit.
    """
    # Calculate bounding box
    all_x = []
    all_y = []
    
    # Building domain
    for w in geometry.walls:
        all_x.extend([w.start[0], w.end[0]])
        all_y.extend([w.start[1], w.end[1]])
        
    # Industrial domain
    for p in geometry.pipes:
        all_x.extend([p.start[0], p.end[0]])
        all_y.extend([p.start[1], p.end[1]])
    
    for e in geometry.equipment:
        all_x.extend([e.position[0], e.position[0] + e.width])
        all_y.extend([e.position[1], e.position[1] + e.length])

    if not all_x:
        return "<svg width='100' height='100'><text x='10' y='50'>No geometry</text></svg>"
        
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Add margin
    margin = 5
    width_units = max_x - min_x + 2 * margin
    height_units = max_y - min_y + 2 * margin
    
    width_px = width_units * scale
    height_px = height_units * scale
    
    viewbox_x = (min_x - margin) * scale
    viewbox_y = (min_y - margin) * scale
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox_x} {viewbox_y} {width_px} {height_px}" width="100%" height="100%" style="background-color:white; border:1px solid #eee">'
    ]
    
    # Draw Grid (Optional, for visual context)
    svg_lines.append(f'<defs><pattern id="grid" width="{10*scale}" height="{10*scale}" patternUnits="userSpaceOnUse"><path d="M {10*scale} 0 L 0 0 0 {10*scale}" fill="none" stroke="gray" stroke-width="0.5"/></pattern></defs>')
    svg_lines.append(f'<rect x="{viewbox_x}" y="{viewbox_y}" width="{width_px}" height="{height_px}" fill="url(#grid)" />')

    # --- Industrial ---
    
    # Draw Pipes
    for p in geometry.pipes:
        x1, y1 = p.start[0] * scale, p.start[1] * scale
        x2, y2 = p.end[0] * scale, p.end[1] * scale
        color = "blue" if p.pipe_type == "main_feed" else "gray"
        width = max(1, (p.diameter / 100)) # Scale thickness
        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" />')
        
    # Draw Equipment
    for e in geometry.equipment:
        x = e.position[0] * scale
        y = e.position[1] * scale
        w = e.width * scale
        h = e.length * scale
        color = "orange" if e.equipment_type == "pump" else "teal"
        svg_lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"  opacity="0.5" stroke="black" />')
        svg_lines.append(f'<text x="{x + w/2}" y="{y + h/2}" font-size="{12}" text-anchor="middle" fill="black">{e.id}</text>')

    # --- Building ---
    
    # Draw Walls
    for w in geometry.walls:
        x1, y1 = w.start[0] * scale, w.start[1] * scale
        x2, y2 = w.end[0] * scale, w.end[1] * scale
        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="4" />')
        
    # Draw Doors (Red)
    for d in geometry.doors:
        x1, y1 = d.start[0] * scale, d.start[1] * scale
        x2, y2 = d.end[0] * scale, d.end[1] * scale
        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="red" stroke-width="4" />')
        
    svg_lines.append('</svg>')
    return "\n".join(svg_lines)
