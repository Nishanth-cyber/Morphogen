def convert_json_to_autolisp(design_data):
    """
    Convert JSON design data to AutoLISP code
    """
    
    metadata = design_data.get('metadata', {})
    elements = design_data.get('elements', {})
    
    code = [
        "(defun c:GENPLAN ( / )",
        f"  ;; Project ID: {metadata.get('project_id', 'Unknown')}",
        f"  ;; Building Type: {metadata.get('building_type', 'Unknown')}",
        f"  ;; Last Modified: {metadata.get('last_modified', 'Unknown')}",
        f"  ;; Version: {metadata.get('version', 1)}",
        "  ",
        "  ;; Create layers",
        '  (command "._LAYER" "N" "WALLS" "C" "7" "WALLS" "")',
        '  (command "._LAYER" "N" "DOORS" "C" "3" "DOORS" "")',
        '  (command "._LAYER" "N" "WINDOWS" "C" "5" "WINDOWS" "")',
        '  (command "._LAYER" "N" "TEXT" "C" "2" "TEXT" "")',
        "  ",
        "  ;; Set WALLS layer current",
        '  (command "._LAYER" "S" "WALLS" "")',
        "  "
    ]
    
    # External boundary
    if 'external_boundary' in elements:
        points = elements['external_boundary'].get('points', [])
        if points:
            points_str = " ".join([f'"{x},{y}"' for x, y in points])
            code.append("  ;; External boundary")
            code.append(f'  (command "._PLINE" {points_str} "C")')
            code.append("  ")
    
    # Internal walls
    if 'walls' in elements and elements['walls']:
        code.append("  ;; Internal walls")
        for wall in elements['walls']:
            x1, y1 = wall['start']
            x2, y2 = wall['end']
            code.append(f'  (command "._LINE" "{x1},{y1}" "{x2},{y2}" "")')
        code.append("  ")
    
    # Doors
    if 'doors' in elements and elements['doors']:
        code.append("  ;; Doors")
        code.append('  (command "._LAYER" "S" "DOORS" "")')
        for door in elements['doors']:
            x, y = door['position']
            width = door.get('width', 900)
            orientation = door.get('orientation', 'horizontal')
            
            if orientation == 'horizontal':
                code.append(f'  (command "._LINE" "{x},{y}" "{x+width},{y}" "")')
                # Add door arc (swing)
                code.append(f'  (command "._ARC" "C" "{x},{y}" "{x+width},{y}" "{x},{y+width}" "")')
            else:
                code.append(f'  (command "._LINE" "{x},{y}" "{x},{y+width}" "")')
                code.append(f'  (command "._ARC" "C" "{x},{y}" "{x},{y+width}" "{x+width},{y}" "")')
        code.append("  ")
    
    # Windows (if present)
    if 'windows' in elements and elements['windows']:
        code.append("  ;; Windows")
        code.append('  (command "._LAYER" "S" "WINDOWS" "")')
        for window in elements['windows']:
            x, y = window['position']
            width = window.get('width', 1200)
            orientation = window.get('orientation', 'horizontal')
            
            if orientation == 'horizontal':
                code.append(f'  (command "._LINE" "{x},{y}" "{x+width},{y}" "")')
            else:
                code.append(f'  (command "._LINE" "{x},{y}" "{x},{y+width}" "")')
        code.append("  ")
    
    # Room labels
    if 'rooms' in elements and elements['rooms']:
        code.append("  ;; Room labels")
        code.append('  (command "._LAYER" "S" "TEXT" "")')
        for room in elements['rooms']:
            x, y = room.get('label_position', [0, 0])
            name = room.get('name', 'Room')
            area = room.get('area', 0)
            
            # Room name
            code.append(f'  (command "._TEXT" "J" "MC" "{x},{y}" "300" "0" "{name}")')
            
            # Room area below name
            if area > 0:
                code.append(f'  (command "._TEXT" "J" "MC" "{x},{y-500}" "200" "0" "{area} sq.ft")')
        code.append("  ")
    
    # Zoom extents
    code.append('  (command "._ZOOM" "E")')
    code.append('  (princ "\\nFloor plan generated successfully!")')
    code.append('  (princ)')
    code.append(')')
    code.append('')
    code.append('(princ "\\nType GENPLAN to generate the floor plan.")')
    code.append('(princ)')
    
    return "\n".join(code)
