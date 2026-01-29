from schemas.geometry import GeometryOutput
import traceback

def export_to_dxf(geometry: GeometryOutput) -> str:
    """
    Exports geometry to a minimal ASCII DXF string.
    Only supports LINE entities.
    
    Enhanced with error handling and validation.
    """
    try:
        lines = [
            "0", "SECTION",
            "2", "HEADER",
            "9", "$INSUNITS",
            "70", "4",  # Millimeters
            "0", "ENDSEC",
            "0", "SECTION",
            "2", "TABLES",
            "0", "TABLE",
            "2", "LAYER",
            "70", "6",  # Number of layers
        ]
        
        # Define layers
        layer_names = ["WALLS", "DOORS", "WINDOWS", "PIPES", "EQUIPMENT", "ANNOTATIONS"]
        for layer_name in layer_names:
            lines.extend([
                "0", "LAYER",
                "2", layer_name,
                "70", "0",  # Standard flags
                "62", "7"   # Color (white)
            ])
        
        lines.extend([
            "0", "ENDTAB",
            "0", "ENDSEC",
            "0", "SECTION",
            "2", "ENTITIES"
        ])
        
        def add_line(layer, x1, y1, x2, y2):
            """Add a LINE entity"""
            try:
                lines.extend([
                    "0", "LINE",
                    "8", str(layer),
                    "10", str(float(x1)),
                    "20", str(float(y1)),
                    "30", "0.0",
                    "11", str(float(x2)),
                    "21", str(float(y2)),
                    "31", "0.0"
                ])
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to add line: {e}")

        def add_rect(layer, x, y, w, h):
            """Add a rectangle using LWPOLYLINE"""
            try:
                lines.extend([
                    "0", "LWPOLYLINE",
                    "8", str(layer),
                    "90", "4",  # Number of vertices
                    "70", "1",  # Closed polyline
                    "10", str(float(x)), 
                    "20", str(float(y)),
                    "10", str(float(x + w)), 
                    "20", str(float(y)),
                    "10", str(float(x + w)), 
                    "20", str(float(y + h)),
                    "10", str(float(x)), 
                    "20", str(float(y + h))
                ])
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to add rectangle: {e}")
        
        def add_text(layer, text, x, y, height=2.5):
            """Add a TEXT entity"""
            try:
                lines.extend([
                    "0", "TEXT",
                    "8", str(layer),
                    "10", str(float(x)),
                    "20", str(float(y)),
                    "30", "0.0",
                    "40", str(float(height)),  # Text height
                    "1", str(text)  # Text string
                ])
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to add text: {e}")

        # Industrial Components
        if hasattr(geometry, 'pipes') and geometry.pipes:
            for p in geometry.pipes:
                try:
                    if hasattr(p, 'start') and hasattr(p, 'end'):
                        add_line("PIPES", p.start[0], p.start[1], p.end[0], p.end[1])
                except Exception as e:
                    print(f"Warning: Failed to export pipe {getattr(p, 'id', 'unknown')}: {e}")
        
        if hasattr(geometry, 'equipment') and geometry.equipment:
            for e in geometry.equipment:
                try:
                    if hasattr(e, 'position') and hasattr(e, 'width') and hasattr(e, 'length'):
                        add_rect("EQUIPMENT", e.position[0], e.position[1], e.width, e.length)
                        # Add equipment label
                        if hasattr(e, 'id'):
                            add_text("ANNOTATIONS", e.id, e.position[0], e.position[1] + e.length + 0.5)
                except Exception as ex:
                    print(f"Warning: Failed to export equipment {getattr(e, 'id', 'unknown')}: {ex}")

        if hasattr(geometry, 'valves') and geometry.valves:
            for v in geometry.valves:
                try:
                    if hasattr(v, 'position') and hasattr(v, 'size'):
                        size = v.size / 1000.0  # Convert mm to m
                        add_rect("EQUIPMENT", v.position[0] - size/2, v.position[1] - size/2, size, size)
                except Exception as ex:
                    print(f"Warning: Failed to export valve {getattr(v, 'id', 'unknown')}: {ex}")

        # Building Components
        if hasattr(geometry, 'walls') and geometry.walls:
            for w in geometry.walls:
                try:
                    if hasattr(w, 'start') and hasattr(w, 'end'):
                        add_line("WALLS", w.start[0], w.start[1], w.end[0], w.end[1])
                except Exception as ex:
                    print(f"Warning: Failed to export wall: {ex}")
        
        if hasattr(geometry, 'doors') and geometry.doors:
            for d in geometry.doors:
                try:
                    if hasattr(d, 'start') and hasattr(d, 'end'):
                        add_line("DOORS", d.start[0], d.start[1], d.end[0], d.end[1])
                except Exception as ex:
                    print(f"Warning: Failed to export door: {ex}")
        
        if hasattr(geometry, 'windows') and geometry.windows:
            for win in geometry.windows:
                try:
                    if hasattr(win, 'start') and hasattr(win, 'end'):
                        add_line("WINDOWS", win.start[0], win.start[1], win.end[0], win.end[1])
                except Exception as ex:
                    print(f"Warning: Failed to export window: {ex}")

        # Annotations
        if hasattr(geometry, 'annotations') and geometry.annotations:
            for ann in geometry.annotations:
                try:
                    if hasattr(ann, 'text') and hasattr(ann, 'position'):
                        height = getattr(ann, 'font_size', 2.5) / 10.0  # Convert to appropriate scale
                        add_text("ANNOTATIONS", ann.text, ann.position[0], ann.position[1], height)
                except Exception as ex:
                    print(f"Warning: Failed to export annotation: {ex}")
        
        # Process Units (draw boundaries)
        if hasattr(geometry, 'process_units') and geometry.process_units:
            for unit in geometry.process_units:
                try:
                    if hasattr(unit, 'boundary') and len(unit.boundary) >= 3:
                        boundary = unit.boundary
                        for i in range(len(boundary)):
                            p1 = boundary[i]
                            p2 = boundary[(i + 1) % len(boundary)]
                            add_line("EQUIPMENT", p1[0], p1[1], p2[0], p2[1])
                        
                        # Add unit name label
                        if hasattr(unit, 'name') and boundary:
                            centroid_x = sum(p[0] for p in boundary) / len(boundary)
                            centroid_y = sum(p[1] for p in boundary) / len(boundary)
                            add_text("ANNOTATIONS", unit.name, centroid_x, centroid_y)
                except Exception as ex:
                    print(f"Warning: Failed to export process unit {getattr(unit, 'id', 'unknown')}: {ex}")
        
        # End of file
        lines.extend([
            "0", "ENDSEC",
            "0", "EOF"
        ])
        
        return "\n".join(lines)
        
    except Exception as e:
        # If everything fails, return a minimal valid DXF
        traceback.print_exc()
        print(f"CRITICAL ERROR in DXF export: {e}")
        return "\n".join([
            "0", "SECTION",
            "2", "HEADER",
            "0", "ENDSEC",
            "0", "SECTION",
            "2", "ENTITIES",
            "0", "ENDSEC",
            "0", "EOF"
        ])
