import ezdxf
from ezdxf.enums import TextEntityAlignment
from pathlib import Path

def convert_json_to_dxf(design_data, output_path):
    """
    Convert JSON design data to DXF format
    """
    
    # Create DXF document
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Create layers
    doc.layers.add('WALLS', color=7)
    doc.layers.add('DOORS', color=3)
    doc.layers.add('WINDOWS', color=5)
    doc.layers.add('TEXT', color=2)
    doc.layers.add('DIMENSIONS', color=1)
    
    elements = design_data.get('elements', {})
    
    # Draw external boundary
    if 'external_boundary' in elements:
        points = elements['external_boundary'].get('points', [])
        if points:
            msp.add_lwpolyline(
                points,
                dxfattribs={'layer': 'WALLS', 'closed': True}
            )
    
    # Draw walls
    if 'walls' in elements:
        for wall in elements['walls']:
            msp.add_line(
                tuple(wall['start']),
                tuple(wall['end']),
                dxfattribs={'layer': 'WALLS'}
            )
    
    # Draw doors
    if 'doors' in elements:
        for door in elements['doors']:
            pos = door['position']
            width = door.get('width', 900)
            orientation = door.get('orientation', 'horizontal')
            
            if orientation == 'horizontal':
                # Draw door opening
                msp.add_line(
                    (pos[0], pos[1]),
                    (pos[0] + width, pos[1]),
                    dxfattribs={'layer': 'DOORS', 'color': 3, 'lineweight': 50}
                )
                # Draw door arc (swing)
                msp.add_arc(
                    center=(pos[0], pos[1]),
                    radius=width,
                    start_angle=0,
                    end_angle=90,
                    dxfattribs={'layer': 'DOORS', 'color': 3}
                )
            else:
                # Vertical door
                msp.add_line(
                    (pos[0], pos[1]),
                    (pos[0], pos[1] + width),
                    dxfattribs={'layer': 'DOORS', 'color': 3, 'lineweight': 50}
                )
                msp.add_arc(
                    center=(pos[0], pos[1]),
                    radius=width,
                    start_angle=0,
                    end_angle=90,
                    dxfattribs={'layer': 'DOORS', 'color': 3}
                )
    
    # Draw windows
    if 'windows' in elements:
        for window in elements['windows']:
            pos = window['position']
            width = window.get('width', 1200)
            orientation = window.get('orientation', 'horizontal')
            
            if orientation == 'horizontal':
                # Window line
                msp.add_line(
                    (pos[0], pos[1]),
                    (pos[0] + width, pos[1]),
                    dxfattribs={'layer': 'WINDOWS', 'color': 5, 'lineweight': 35}
                )
                # Window panes (vertical divider)
                msp.add_line(
                    (pos[0] + width/2, pos[1] - 100),
                    (pos[0] + width/2, pos[1] + 100),
                    dxfattribs={'layer': 'WINDOWS', 'color': 5}
                )
            else:
                # Vertical window
                msp.add_line(
                    (pos[0], pos[1]),
                    (pos[0], pos[1] + width),
                    dxfattribs={'layer': 'WINDOWS', 'color': 5, 'lineweight': 35}
                )
                # Window panes (horizontal divider)
                msp.add_line(
                    (pos[0] - 100, pos[1] + width/2),
                    (pos[0] + 100, pos[1] + width/2),
                    dxfattribs={'layer': 'WINDOWS', 'color': 5}
                )
    
    # Add room labels
    if 'rooms' in elements:
        for room in elements['rooms']:
            label_pos = room.get('label_position', [0, 0])
            name = room.get('name', 'Room')
            area = room.get('area', 0)
            
            # Room name
            msp.add_text(
                name,
                dxfattribs={
                    'layer': 'TEXT',
                    'height': 300,
                    'color': 2
                }
            ).set_placement(label_pos, align=TextEntityAlignment.MIDDLE_CENTER)
            
            # Room area (below name)
            if area > 0:
                area_text = f"{area} sq.ft"
                area_pos = (label_pos[0], label_pos[1] - 500)
                msp.add_text(
                    area_text,
                    dxfattribs={
                        'layer': 'TEXT',
                        'height': 200,
                        'color': 8
                    }
                ).set_placement(area_pos, align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Save DXF
    doc.saveas(output_path)
    
    return output_path
