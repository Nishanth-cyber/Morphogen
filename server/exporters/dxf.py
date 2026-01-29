from schemas.geometry import GeometryOutput
import traceback

def export_to_dxf(geometry: GeometryOutput) -> str:
    """
    Exports geometry to a properly structured ASCII DXF string.
    
    FIXED ISSUES:
    - Proper LWPOLYLINE vertex structure
    - Correct layer table
    - Validation of coordinates
    - Empty geometry handling
    - All required DXF group codes
    
    Returns:
        str: Valid DXF file content
    """
    try:
        # DXF Header
        lines = [
            "0", "SECTION",
            "2", "HEADER",
            "9", "$ACADVER",
            "1", "AC1015",  # AutoCAD 2000 format
            "9", "$INSUNITS",
            "70", "4",  # Millimeters
            "9", "$EXTMIN",
            "10", "0.0",
            "20", "0.0",
            "30", "0.0",
            "9", "$EXTMAX",
            "10", "1000.0",
            "20", "1000.0",
            "30", "0.0",
            "0", "ENDSEC",
        ]
        
        # TABLES Section
        lines.extend([
            "0", "SECTION",
            "2", "TABLES",
            # Layer Table
            "0", "TABLE",
            "2", "LAYER",
            "70", "0",  # Maximum number of entries (0 = unlimited)
        ])
        
        # Define Layer 0 (required by DXF spec)
        lines.extend([
            "0", "LAYER",
            "2", "0",  # Layer name
            "70", "0",  # Standard flags
            "62", "7",  # Color (white)
            "6", "CONTINUOUS"  # Linetype
        ])
        
        # Define additional layers
        layer_definitions = [
            ("BOUNDARIES", "7"),   # White
            ("EQUIPMENT", "3"),    # Green
            ("PIPING", "4"),       # Cyan
            ("VALVES", "1"),       # Red
            ("WALLS", "7"),        # White
            ("DOORS", "1"),        # Red
            ("WINDOWS", "4"),      # Cyan
            ("TEXT", "2"),         # Yellow
            ("ANNOTATIONS", "6"),  # Magenta
        ]
        
        for layer_name, color_code in layer_definitions:
            lines.extend([
                "0", "LAYER",
                "2", layer_name,
                "70", "0",
                "62", color_code,
                "6", "CONTINUOUS"
            ])
        
        lines.extend([
            "0", "ENDTAB",
            "0", "ENDSEC",
        ])
        
        # ENTITIES Section
        lines.extend([
            "0", "SECTION",
            "2", "ENTITIES"
        ])
        
        # Track if any entities were added
        entity_count = 0
        
        # Helper function to add LINE entity
        def add_line(layer, x1, y1, x2, y2):
            """Add a LINE entity with validation"""
            nonlocal entity_count
            try:
                x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
                lines.extend([
                    "0", "LINE",
                    "8", str(layer),
                    "10", f"{x1:.6f}",
                    "20", f"{y1:.6f}",
                    "30", "0.0",
                    "11", f"{x2:.6f}",
                    "21", f"{y2:.6f}",
                    "31", "0.0"
                ])
                entity_count += 1
                return True
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to add line: {e}")
                return False

        def add_polyline(layer, points, closed=True):
            """Add a LWPOLYLINE entity with proper vertex structure"""
            nonlocal entity_count
            try:
                if not points or len(points) < 2:
                    return False
                
                # Validate all points
                validated_points = []
                for pt in points:
                    try:
                        x, y = float(pt[0]), float(pt[1])
                        validated_points.append((x, y))
                    except (ValueError, TypeError, IndexError):
                        print(f"Warning: Invalid point {pt}")
                        continue
                
                if len(validated_points) < 2:
                    return False
                
                lines.extend([
                    "0", "LWPOLYLINE",
                    "8", str(layer),
                    "90", str(len(validated_points)),  # Number of vertices
                    "70", "1" if closed else "0"  # Closed flag
                ])
                
                # Add each vertex
                for x, y in validated_points:
                    lines.extend([
                        "10", f"{x:.6f}",
                        "20", f"{y:.6f}"
                    ])
                
                entity_count += 1
                return True
            except Exception as e:
                print(f"Warning: Failed to add polyline: {e}")
                return False

        def add_text(layer, text, x, y, height=2.5):
            """Add a TEXT entity"""
            nonlocal entity_count
            try:
                x, y, height = float(x), float(y), float(height)
                lines.extend([
                    "0", "TEXT",
                    "8", str(layer),
                    "10", f"{x:.6f}",
                    "20", f"{y:.6f}",
                    "30", "0.0",
                    "40", f"{height:.6f}",
                    "1", str(text)
                ])
                entity_count += 1
                return True
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to add text: {e}")
                return False

        # =================================================================
        # INDUSTRIAL COMPONENTS
        # =================================================================
        
        # Process Units (Boundaries)
        if hasattr(geometry, 'process_units') and geometry.process_units:
            for unit in geometry.process_units:
                try:
                    if hasattr(unit, 'boundary') and unit.boundary and len(unit.boundary) >= 3:
                        if add_polyline("BOUNDARIES", unit.boundary, closed=True):
                            # Add label at centroid
                            if hasattr(unit, 'name') and unit.name:
                                centroid_x = sum(p[0] for p in unit.boundary) / len(unit.boundary)
                                centroid_y = sum(p[1] for p in unit.boundary) / len(unit.boundary)
                                add_text("TEXT", unit.name, centroid_x, centroid_y, 2.0)
                except Exception as e:
                    print(f"Warning: Failed to export process unit {getattr(unit, 'id', 'unknown')}: {e}")
        
        # Equipment
        if hasattr(geometry, 'equipment') and geometry.equipment:
            for eq in geometry.equipment:
                try:
                    if hasattr(eq, 'position') and hasattr(eq, 'width') and hasattr(eq, 'length'):
                        x, y = eq.position[0], eq.position[1]
                        w, h = eq.width, eq.length
                        
                        # Draw equipment as rectangle
                        rect_points = [
                            [x, y],
                            [x + w, y],
                            [x + w, y + h],
                            [x, y + h]
                        ]
                        if add_polyline("EQUIPMENT", rect_points, closed=True):
                            # Add equipment ID label
                            if hasattr(eq, 'id'):
                                add_text("TEXT", eq.id, x + w/2, y + h/2, 1.5)
                except Exception as e:
                    print(f"Warning: Failed to export equipment {getattr(eq, 'id', 'unknown')}: {e}")
        
        # Pipes
        if hasattr(geometry, 'pipes') and geometry.pipes:
            for pipe in geometry.pipes:
                try:
                    if hasattr(pipe, 'start') and hasattr(pipe, 'end'):
                        add_line("PIPING", pipe.start[0], pipe.start[1], 
                                pipe.end[0], pipe.end[1])
                except Exception as e:
                    print(f"Warning: Failed to export pipe {getattr(pipe, 'id', 'unknown')}: {e}")
        
        # Valves
        if hasattr(geometry, 'valves') and geometry.valves:
            for valve in geometry.valves:
                try:
                    if hasattr(valve, 'position') and hasattr(valve, 'size'):
                        x, y = valve.position[0], valve.position[1]
                        size = valve.size / 1000.0  # Convert mm to meters
                        
                        # Draw valve as small square
                        valve_points = [
                            [x - size/2, y - size/2],
                            [x + size/2, y - size/2],
                            [x + size/2, y + size/2],
                            [x - size/2, y + size/2]
                        ]
                        add_polyline("VALVES", valve_points, closed=True)
                except Exception as e:
                    print(f"Warning: Failed to export valve {getattr(valve, 'id', 'unknown')}: {e}")
        
        # =================================================================
        # BUILDING COMPONENTS
        # =================================================================
        
        # Walls
        if hasattr(geometry, 'walls') and geometry.walls:
            for wall in geometry.walls:
                try:
                    if hasattr(wall, 'start') and hasattr(wall, 'end'):
                        add_line("WALLS", wall.start[0], wall.start[1], 
                                wall.end[0], wall.end[1])
                except Exception as e:
                    print(f"Warning: Failed to export wall: {e}")
        
        # Doors
        if hasattr(geometry, 'doors') and geometry.doors:
            for door in geometry.doors:
                try:
                    if hasattr(door, 'start') and hasattr(door, 'end'):
                        add_line("DOORS", door.start[0], door.start[1], 
                                door.end[0], door.end[1])
                except Exception as e:
                    print(f"Warning: Failed to export door: {e}")
        
        # Windows
        if hasattr(geometry, 'windows') and geometry.windows:
            for window in geometry.windows:
                try:
                    if hasattr(window, 'start') and hasattr(window, 'end'):
                        add_line("WINDOWS", window.start[0], window.start[1], 
                                window.end[0], window.end[1])
                except Exception as e:
                    print(f"Warning: Failed to export window: {e}")
        
        # Annotations
        if hasattr(geometry, 'annotations') and geometry.annotations:
            for ann in geometry.annotations:
                try:
                    if hasattr(ann, 'text') and hasattr(ann, 'position'):
                        height = getattr(ann, 'font_size', 10) / 5.0
                        add_text("ANNOTATIONS", ann.text, 
                                ann.position[0], ann.position[1], height)
                except Exception as e:
                    print(f"Warning: Failed to export annotation: {e}")
        
        # If no entities were added, add a placeholder
        if entity_count == 0:
            print("Warning: No valid entities found in geometry")
            # Add a minimal entity to make DXF valid
            add_text("TEXT", "Empty Design", 10, 10, 5)
        
        # End of ENTITIES section
        lines.extend([
            "0", "ENDSEC",
            "0", "EOF"
        ])
        
        result = "\n".join(lines)
        print(f"DXF Export: Generated {entity_count} entities, {len(lines)} lines")
        return result
        
    except Exception as e:
        # Critical error - return minimal valid DXF
        traceback.print_exc()
        print(f"CRITICAL ERROR in DXF export: {e}")
        return generate_minimal_dxf("Error during export")


def generate_minimal_dxf(message="Empty Design"):
    """Generate a minimal valid DXF file"""
    return "\n".join([
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1015",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", "0",
        "0", "LAYER",
        "2", "0",
        "70", "0",
        "62", "7",
        "6", "CONTINUOUS",
        "0", "ENDTAB",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "ENTITIES",
        "0", "TEXT",
        "8", "0",
        "10", "10.0",
        "20", "10.0",
        "30", "0.0",
        "40", "5.0",
        "1", message,
        "0", "ENDSEC",
        "0", "EOF"
    ])