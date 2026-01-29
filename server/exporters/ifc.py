"""
IFC (Industry Foundation Classes) Exporter
Exports geometry to BIM-compatible IFC format
"""

import ifcopenshell
from ifcopenshell import guid
from schemas.geometry import GeometryOutput
import time
from typing import Optional

def export_to_ifc(geometry: GeometryOutput, project_name: str = "Generated Design") -> bytes:
    """
    Exports GeometryOutput to IFC 4 format
    Returns: IFC file as bytes
    """
    
    # Create IFC file
    timestamp = int(time.time())
    filename = f"design_{timestamp}.ifc"
    schema = "IFC4"
    
    ifc_file = ifcopenshell.file(schema=schema)
    
    # Create basic hierarchy
    project, context = create_project(ifc_file, project_name, geometry)
    site = create_site(ifc_file, project, geometry)
    building = create_building(ifc_file, site)
    storey = create_building_storey(ifc_file, building)
    
    # Convert geometry based on domain
    if geometry.domain == "industrial":
        export_industrial_geometry(ifc_file, storey, geometry, context)
    else:
        export_building_geometry(ifc_file, storey, geometry, context)
    
    # Write to bytes
    return ifc_file.wrapped_data.to_string().encode('utf-8')

def create_project(ifc_file, project_name: str, geometry: GeometryOutput):
    """Create IFC project structure and context"""
    
    # Create owner history
    person = ifc_file.createIfcPerson(
        None, None, "Engineer", None, None, None, None, None
    )
    organization = ifc_file.createIfcOrganization(
        None, "Morphogen AI", "AI-Generated Design", None, None
    )
    person_org = ifc_file.createIfcPersonAndOrganization(
        person, organization, None
    )
    application = ifc_file.createIfcApplication(
        organization, "1.0", "Morphogen", "AI Generative Design System"
    )
    owner_history = ifc_file.createIfcOwnerHistory(
        person_org, application, None, "ADDED", None, None, None, timestamp()
    )
    
    # Create Geometric Representation Context
    context = ifc_file.createIfcGeometricRepresentationContext(
        guid.new(),
        "Model",
        "Model",
        3,
        0.00001,
        ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0]),
            ifc_file.createIfcDirection([0.0, 0.0, 1.0]),
            ifc_file.createIfcDirection([1.0, 0.0, 0.0])
        ),
        ifc_file.createIfcDirection([0.0, 1.0])
    )

    # Create project
    project = ifc_file.createIfcProject(
        guid.new(),
        owner_history,
        project_name,
        f"Generated design - {geometry.domain}",
        None, None, None,
        [context], # RepresentationContexts
        ifc_file.createIfcUnitAssignment([
            create_si_unit(ifc_file, "LENGTHUNIT", geometry.units)
        ])
    )
    
    return project, context

def create_site(ifc_file, project, geometry: GeometryOutput):
    """Create site container"""
    
    site = ifc_file.createIfcSite(
        guid.new(),
        project.OwnerHistory,
        "Site",
        "Design site",
        None, None, None, None,
        "ELEMENT", None, None, None, None, None
    )
    
    # Create relationship
    ifc_file.createIfcRelAggregates(
        guid.new(),
        project.OwnerHistory,
        "ProjectSite",
        None,
        project,
        [site]
    )
    
    return site

def create_building(ifc_file, site):
    """Create building container"""
    
    building = ifc_file.createIfcBuilding(
        guid.new(),
        site.OwnerHistory,
        "Building",
        "Main building",
        None, None, None, None,
        "ELEMENT", None, None, None
    )
    
    ifc_file.createIfcRelAggregates(
        guid.new(),
        site.OwnerHistory,
        "SiteBuilding",
        None,
        site,
        [building]
    )
    
    return building

def create_building_storey(ifc_file, building):
    """Create building storey (floor)"""
    
    storey = ifc_file.createIfcBuildingStorey(
        guid.new(),
        building.OwnerHistory,
        "Ground Floor",
        "Ground level",
        None, None, None, None,
        "ELEMENT", 0.0
    )
    
    ifc_file.createIfcRelAggregates(
        guid.new(),
        building.OwnerHistory,
        "BuildingStorey",
        None,
        building,
        [storey]
    )
    
    return storey

def export_industrial_geometry(ifc_file, storey, geometry: GeometryOutput, context):
    """Export industrial piping and equipment to IFC"""
    
    owner_history = storey.OwnerHistory
    
    # Export equipment
    for equip in geometry.equipment:
        element = create_equipment_element(ifc_file, owner_history, equip, geometry.units, context)
        relate_to_storey(ifc_file, storey, element)
    
    # Export pipes
    for pipe in geometry.pipes:
        element = create_pipe_element(ifc_file, owner_history, pipe, geometry.units)
        relate_to_storey(ifc_file, storey, element)
    
    # Export valves
    for valve in geometry.valves:
        element = create_valve_element(ifc_file, owner_history, valve, geometry.units)
        relate_to_storey(ifc_file, storey, element)

def export_building_geometry(ifc_file, storey, geometry: GeometryOutput, context):
    """Export building walls, doors, windows to IFC"""
    
    owner_history = storey.OwnerHistory
    
    # Export walls
    for wall in geometry.walls:
        element = create_wall_element(ifc_file, owner_history, wall, geometry.units)
        relate_to_storey(ifc_file, storey, element)
    
    # Export doors
    for door in geometry.doors:
        element = create_door_element(ifc_file, owner_history, door, geometry.units)
        relate_to_storey(ifc_file, storey, element)

def create_equipment_element(ifc_file, owner_history, equip, units, context):
    """Create IFC equipment element (IfcFlowTerminal or IfcFlowSegment)"""
    
    # Create placement
    placement = create_placement(ifc_file, equip.position[0], equip.position[1], 0)
    
    # Create representation
    representation = create_box_representation(
        ifc_file, context, equip.width, equip.length, equip.height or 2.0
    )
    
    # Map equipment type to IFC type
    if equip.equipment_type in ["pump"]:
        element = ifc_file.createIfcPump(
            guid.new(),
            owner_history,
            equip.id,
            f"{equip.equipment_type} - {equip.capacity}",
            None,
            placement,
            representation,
            None,
            None
        )
    elif equip.equipment_type in ["tank"]:
        element = ifc_file.createIfcTank(
            guid.new(),
            owner_history,
            equip.id,
            f"{equip.equipment_type} - {equip.capacity}",
            None,
            placement,
            representation,
            None,
            None
        )
    else:
        # Generic flow terminal for other equipment
        element = ifc_file.createIfcFlowTerminal(
            guid.new(),
            owner_history,
            equip.id,
            equip.equipment_type,
            None,
            placement,
            representation,
            None
        )
    
    # Add properties
    add_property_set(ifc_file, element, "Equipment Properties", {
        "Type": equip.equipment_type,
        "Capacity": str(equip.capacity) if equip.capacity else "N/A",
        "Power": str(equip.power) if equip.power else "N/A"
    })
    
    return element

def create_pipe_element(ifc_file, owner_history, pipe, units, context):
    """Create IFC pipe segment"""
    # ... (existing body, simplified for brevity in this replacement) ...
    start_x, start_y = pipe.start
    end_x, end_y = pipe.end
    length = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
    placement = create_placement(ifc_file, start_x, start_y, 0)
    
    element = ifc_file.createIfcPipeSegment(guid.new(), owner_history, pipe.id, f"{pipe.pipe_type} - {pipe.diameter}mm", None, placement, None, None, None)
    
    add_property_set(ifc_file, element, "Pipe Properties", {
        "Diameter": f"{pipe.diameter} mm",
        "Material": pipe.material,
        "Pipe Type": pipe.pipe_type,
        "Flow Rate": str(pipe.flow_rate) if pipe.flow_rate else "N/A",
        "Length": f"{length:.2f} {units}"
    })
    return element

def create_valve_element(ifc_file, owner_history, valve, units, context):
    placement = create_placement(ifc_file, valve.position[0], valve.position[1], 0)
    element = ifc_file.createIfcValve(guid.new(), owner_history, valve.id, f"{valve.valve_type} valve - {valve.size}mm", None, placement, None, None, None)
    add_property_set(ifc_file, element, "Valve Properties", {
        "Valve Type": valve.valve_type,
        "Size": f"{valve.size} mm",
        "Normally Open": "Yes" if valve.normally_open else "No"
    })
    return element

def create_wall_element(ifc_file, owner_history, wall, units, context):
    placement = create_placement(ifc_file, wall.start[0], wall.start[1], 0)
    length = ((wall.end[0] - wall.start[0])**2 + (wall.end[1] - wall.start[1])**2)**0.5
    element = ifc_file.createIfcWall(guid.new(), owner_history, f"Wall_{wall.start}_{wall.end}", "External wall", None, placement, None, None, None)
    add_property_set(ifc_file, element, "Wall Properties", {
        "Thickness": f"{wall.thickness} mm",
        "Height": f"{wall.height} mm",
        "Length": f"{length:.2f} {units}"
    })
    return element

def create_door_element(ifc_file, owner_history, door, units, context):
    placement = create_placement(ifc_file, door.start[0], door.start[1], 0)
    element = ifc_file.createIfcDoor(guid.new(), owner_history, f"Door_{door.wall}", "Door", None, placement, None, None, door.height, door.width)
    return element

def create_placement(ifc_file, x, y, z):
    """Create 3D placement"""
    
    point = ifc_file.createIfcCartesianPoint([float(x), float(y), float(z)])
    direction = ifc_file.createIfcDirection((0.0, 0.0, 1.0))
    axis = ifc_file.createIfcDirection((1.0, 0.0, 0.0))
    
    axis_placement = ifc_file.createIfcAxis2Placement3D(
        point, direction, axis
    )
    
    return ifc_file.createIfcLocalPlacement(
        None, axis_placement
    )

def create_box_representation(ifc_file, width, length, height):
    """Create simple box shape representation"""
    
    point = ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0])
    direction = ifc_file.createIfcDirection((0.0, 0.0, 1.0))
    axis = ifc_file.createIfcDirection((1.0, 0.0, 0.0))
    
    axis_placement = ifc_file.createIfcAxis2Placement3D(point, direction, axis)
    
    box = ifc_file.createIfcBlock(axis_placement, width, length, height)
    
    shape = ifc_file.createIfcShapeRepresentation(
        None, "Body", "SweptSolid", [box]
    )
    
    return ifc_file.createIfcProductDefinitionShape(None, None, [shape])

def create_si_unit(ifc_file, unit_type, prefix):
    """Create SI unit"""
    
    # Convert units
    unit_map = {
        "mm": "MILLI",
        "cm": "CENTI",
        "m": None
    }
    
    return ifc_file.createIfcSIUnit(
        None,
        unit_type,
        unit_map.get(prefix),
        "METRE" if unit_type == "LENGTHUNIT" else None
    )

def add_property_set(ifc_file, element, pset_name, properties):
    """Add property set to element"""
    
    property_values = []
    for key, value in properties.items():
        prop = ifc_file.createIfcPropertySingleValue(
            key,
            None,
            ifc_file.create_entity("IfcText", value),
            None
        )
        property_values.append(prop)
    
    property_set = ifc_file.createIfcPropertySet(
        guid.new(),
        element.OwnerHistory,
        pset_name,
        None,
        property_values
    )
    
    ifc_file.createIfcRelDefinesByProperties(
        guid.new(),
        element.OwnerHistory,
        None,
        None,
        [element],
        property_set
    )

def relate_to_storey(ifc_file, storey, element):
    """Relate element to building storey"""
    
    ifc_file.createIfcRelContainedInSpatialStructure(
        guid.new(),
        storey.OwnerHistory,
        "StoreyElements",
        None,
        [element],
        storey
    )

def timestamp():
    """Get current timestamp for IFC"""
    return int(time.time())
