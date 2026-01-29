"""
Enhanced Geometry Validators with Engineering Rules
"""

from schemas.geometry import GeometryOutput, Pipe, Equipment
from typing import List, Dict, Tuple
import math

class ValidationError(Exception):
    """Custom validation error"""
    pass

class ValidationWarning:
    """Validation warning (non-fatal)"""
    def __init__(self, message: str, severity: str = "warning"):
        self.message = message
        self.severity = severity

def validate_geometry(geometry: GeometryOutput) -> Tuple[bool, List[ValidationWarning]]:
    """
    Comprehensive geometry validation
    Returns: (is_valid, warnings_list)
    """
    warnings = []
    
    # Basic validation
    if not geometry.walls and not geometry.pipes and not geometry.equipment:
        raise ValidationError("Geometry must contain at least walls, pipes, or equipment")
    
    # Domain-specific validation
    if geometry.domain == "industrial":
        warnings.extend(validate_industrial_geometry(geometry))
    elif geometry.domain in ["residential", "commercial"]:
        warnings.extend(validate_building_geometry(geometry))
    
    return True, warnings

# ============================================================
# INDUSTRIAL VALIDATION
# ============================================================

def validate_industrial_geometry(geometry: GeometryOutput) -> List[ValidationWarning]:
    """Validate industrial piping and equipment layout"""
    
    warnings = []
    
    # Validate equipment
    if geometry.equipment:
        warnings.extend(validate_equipment(geometry.equipment))
        warnings.extend(validate_equipment_clearances(geometry.equipment))
    
    # Validate piping
    if geometry.pipes:
        warnings.extend(validate_pipes(geometry.pipes))
        warnings.extend(validate_pipe_spacing(geometry.pipes))
        warnings.extend(validate_flow_continuity(geometry.pipes, geometry.equipment))
    
    # Validate valves
    if geometry.valves:
        warnings.extend(validate_valves(geometry.valves, geometry.pipes))
    
    return warnings

def validate_equipment(equipment_list: List[Equipment]) -> List[ValidationWarning]:
    """Validate individual equipment items"""
    
    warnings = []
    
    for equip in equipment_list:
        # Check dimensions
        if equip.width <= 0 or equip.length <= 0:
            raise ValidationError(f"Equipment {equip.id} has invalid dimensions")
        
        # Check for unrealistic dimensions (too large)
        if equip.width > 50 or equip.length > 50:  # meters
            warnings.append(ValidationWarning(
                f"Equipment {equip.id} has unusually large dimensions: {equip.width}m × {equip.length}m",
                "warning"
            ))
        
        # Type-specific validation
        if equip.equipment_type == "pump":
            if not equip.power:
                warnings.append(ValidationWarning(
                    f"Pump {equip.id} missing power specification",
                    "info"
                ))
        
        elif equip.equipment_type == "tank":
            if not equip.capacity:
                warnings.append(ValidationWarning(
                    f"Tank {equip.id} missing capacity specification",
                    "warning"
                ))
    
    return warnings

def validate_equipment_clearances(equipment_list: List[Equipment]) -> List[ValidationWarning]:
    """Validate clearances between equipment (minimum 1.5m)"""
    
    warnings = []
    MIN_CLEARANCE = 1.5  # meters
    
    for i, equip1 in enumerate(equipment_list):
        for equip2 in equipment_list[i+1:]:
            clearance = calculate_equipment_clearance(equip1, equip2)
            
            if clearance < MIN_CLEARANCE:
                warnings.append(ValidationWarning(
                    f"Insufficient clearance between {equip1.id} and {equip2.id}: "
                    f"{clearance:.2f}m (minimum {MIN_CLEARANCE}m required)",
                    "warning"
                ))
    
    return warnings

def calculate_equipment_clearance(equip1: Equipment, equip2: Equipment) -> float:
    """Calculate minimum clearance between two equipment pieces"""
    
    # Simple rectangular collision detection
    x1_min, y1_min = equip1.position[0] - equip1.width/2, equip1.position[1] - equip1.length/2
    x1_max, y1_max = equip1.position[0] + equip1.width/2, equip1.position[1] + equip1.length/2
    
    x2_min, y2_min = equip2.position[0] - equip2.width/2, equip2.position[1] - equip2.length/2
    x2_max, y2_max = equip2.position[0] + equip2.width/2, equip2.position[1] + equip2.length/2
    
    # Calculate minimum distance
    dx = max(0, max(x1_min - x2_max, x2_min - x1_max))
    dy = max(0, max(y1_min - y2_max, y2_min - y1_max))
    
    return math.sqrt(dx**2 + dy**2)

def validate_pipes(pipes: List[Pipe]) -> List[ValidationWarning]:
    """Validate individual pipes"""
    
    warnings = []
    
    for pipe in pipes:
        # Check for zero-length pipes
        length = calculate_pipe_length(pipe)
        if length < 0.1:  # Less than 100mm
            raise ValidationError(f"Pipe {pipe.id} has invalid length: {length:.3f}m")
        
        # Check for very long unsupported pipes
        if length > 6.0:  # More than 6 meters
            warnings.append(ValidationWarning(
                f"Pipe {pipe.id} is very long ({length:.2f}m) - may need support",
                "info"
            ))
        
        # Validate diameter
        if pipe.diameter < 25 or pipe.diameter > 3000:
            warnings.append(ValidationWarning(
                f"Pipe {pipe.id} has unusual diameter: {pipe.diameter}mm",
                "warning"
            ))
        
        # Validate flow rate vs diameter
        if pipe.flow_rate:
            max_velocity = calculate_pipe_velocity(pipe.diameter, pipe.flow_rate)
            if max_velocity > 3.0:  # 3 m/s is typical max for liquid
                warnings.append(ValidationWarning(
                    f"Pipe {pipe.id} has high velocity ({max_velocity:.2f} m/s) - "
                    f"consider larger diameter",
                    "warning"
                ))
    
    return warnings

def validate_pipe_spacing(pipes: List[Pipe]) -> List[ValidationWarning]:
    """Validate spacing between parallel pipes"""
    
    warnings = []
    MIN_SPACING = 0.5  # 500mm minimum between pipe centerlines
    
    # Check for pipes that are too close
    for i, pipe1 in enumerate(pipes):
        for pipe2 in pipes[i+1:]:
            # Check if pipes are parallel and close
            if are_pipes_parallel(pipe1, pipe2):
                spacing = calculate_pipe_spacing(pipe1, pipe2)
                if spacing < MIN_SPACING:
                    warnings.append(ValidationWarning(
                        f"Pipes {pipe1.id} and {pipe2.id} are too close: "
                        f"{spacing:.2f}m (minimum {MIN_SPACING}m)",
                        "warning"
                    ))
    
    return warnings

def validate_flow_continuity(pipes: List[Pipe], equipment: List[Equipment]) -> List[ValidationWarning]:
    """Validate flow continuity in piping network"""
    
    warnings = []
    
    # Build connection graph
    pipe_graph = build_pipe_graph(pipes)
    
    # Check for disconnected pipes
    for pipe in pipes:
        connections = pipe_graph.get(pipe.id, [])
        if len(connections) == 0:
            warnings.append(ValidationWarning(
                f"Pipe {pipe.id} is not connected to any other pipe or equipment",
                "warning"
            ))
    
    # Check flow balance at junctions
    # (Simplified - just check if inlet ≈ outlet)
    junction_flows = calculate_junction_flows(pipes)
    for junction_id, (inlet_flow, outlet_flow) in junction_flows.items():
        if abs(inlet_flow - outlet_flow) > 0.1 * inlet_flow:  # 10% tolerance
            warnings.append(ValidationWarning(
                f"Flow imbalance at junction {junction_id}: "
                f"inlet {inlet_flow:.1f} ≠ outlet {outlet_flow:.1f}",
                "warning"
            ))
    
    return warnings

def validate_valves(valves, pipes: List[Pipe]) -> List[ValidationWarning]:
    """Validate valve placement"""
    
    warnings = []
    
    for valve in valves:
        # Check if valve is on an existing pipe
        pipe = next((p for p in pipes if p.id == valve.pipe_id), None)
        if not pipe:
            warnings.append(ValidationWarning(
                f"Valve {valve.id} references non-existent pipe {valve.pipe_id}",
                "error"
            ))
        else:
            # Check if valve size matches pipe size
            if abs(valve.size - pipe.diameter) > 50:  # 50mm tolerance
                warnings.append(ValidationWarning(
                    f"Valve {valve.id} size ({valve.size}mm) doesn't match "
                    f"pipe {valve.pipe_id} diameter ({pipe.diameter}mm)",
                    "warning"
                ))
    
    return warnings

# ============================================================
# BUILDING VALIDATION
# ============================================================

def validate_building_geometry(geometry: GeometryOutput) -> List[ValidationWarning]:
    """Validate building layout"""
    
    warnings = []
    
    if geometry.walls:
        warnings.extend(validate_walls(geometry.walls))
        warnings.extend(validate_wall_continuity(geometry.walls))
    
    if geometry.doors:
        warnings.extend(validate_doors(geometry.doors, geometry.walls))
    
    return warnings

def validate_walls(walls) -> List[ValidationWarning]:
    """Validate individual walls"""
    
    warnings = []
    
    for wall in walls:
        # Check for zero-length walls
        length = math.sqrt(
            (wall.end[0] - wall.start[0])**2 + 
            (wall.end[1] - wall.start[1])**2
        )
        
        if length < 0.1:
            raise ValidationError(f"Wall from {wall.start} to {wall.end} has zero length")
        
        # Check for very thin walls (considering different unit systems)
        # Wall thickness could be in mm or m depending on geometry.units
        thickness_mm = wall.thickness
        
        # If thickness is less than 10, it's probably in meters, convert to mm
        if wall.thickness < 10:
            thickness_mm = wall.thickness * 1000
        
        if thickness_mm < 50:  # Less than 50mm is very thin
            warnings.append(ValidationWarning(
                f"Wall has unusually thin thickness: {wall.thickness:.1f}mm",
                "warning"
            ))
        elif thickness_mm > 500:  # More than 500mm is very thick
            warnings.append(ValidationWarning(
                f"Wall has unusually thick thickness: {thickness_mm:.0f}mm",
                "info"
            ))
    
    return warnings

def validate_wall_continuity(walls) -> List[ValidationWarning]:
    """Check if walls form closed boundaries"""
    
    warnings = []
    
    # Build endpoint graph
    endpoints = {}
    for wall in walls:
        start = tuple(wall.start)
        end = tuple(wall.end)
        
        endpoints[start] = endpoints.get(start, 0) + 1
        endpoints[end] = endpoints.get(end, 0) + 1
    
    # Check for open ends (points connected to only 1 wall)
    open_ends = [pt for pt, count in endpoints.items() if count == 1]
    
    if open_ends:
        warnings.append(ValidationWarning(
            f"Found {len(open_ends)} open wall endpoints - "
            f"walls may not form closed boundaries",
            "info"
        ))
    
    return warnings

def validate_doors(doors, walls) -> List[ValidationWarning]:
    """Validate door placement"""
    
    warnings = []
    
    for door in doors:
        # Check if door is actually on a wall
        # (Simplified - just warn if no walls exist)
        if not walls:
            warnings.append(ValidationWarning(
                f"Door specified but no walls exist",
                "warning"
            ))
    
    return warnings

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_pipe_length(pipe: Pipe) -> float:
    """Calculate pipe length"""
    return math.sqrt(
        (pipe.end[0] - pipe.start[0])**2 + 
        (pipe.end[1] - pipe.start[1])**2
    )

def calculate_pipe_velocity(diameter_mm: float, flow_rate_m3h: float) -> float:
    """
    Calculate flow velocity in pipe
    Returns: velocity in m/s
    """
    diameter_m = diameter_mm / 1000
    area = math.pi * (diameter_m / 2) ** 2
    flow_rate_m3s = flow_rate_m3h / 3600
    return flow_rate_m3s / area

def are_pipes_parallel(pipe1: Pipe, pipe2: Pipe) -> bool:
    """Check if two pipes are roughly parallel"""
    
    # Calculate direction vectors
    dx1, dy1 = pipe1.end[0] - pipe1.start[0], pipe1.end[1] - pipe1.start[1]
    dx2, dy2 = pipe2.end[0] - pipe2.start[0], pipe2.end[1] - pipe2.start[1]
    
    # Normalize
    len1 = math.sqrt(dx1**2 + dy1**2)
    len2 = math.sqrt(dx2**2 + dy2**2)
    
    if len1 < 0.001 or len2 < 0.001:
        return False
    
    dx1, dy1 = dx1/len1, dy1/len1
    dx2, dy2 = dx2/len2, dy2/len2
    
    # Dot product close to 1 or -1 means parallel
    dot = abs(dx1*dx2 + dy1*dy2)
    return dot > 0.9

def calculate_pipe_spacing(pipe1: Pipe, pipe2: Pipe) -> float:
    """Calculate minimum spacing between two parallel pipes"""
    
    # Simplified: distance between midpoints
    mid1 = ((pipe1.start[0] + pipe1.end[0])/2, (pipe1.start[1] + pipe1.end[1])/2)
    mid2 = ((pipe2.start[0] + pipe2.end[0])/2, (pipe2.start[1] + pipe2.end[1])/2)
    
    return math.sqrt((mid2[0] - mid1[0])**2 + (mid2[1] - mid1[1])**2)

def build_pipe_graph(pipes: List[Pipe]) -> Dict[str, List[str]]:
    """Build connectivity graph of pipes"""
    
    graph = {pipe.id: [] for pipe in pipes}
    
    # Find connections (pipes that share endpoints)
    for i, pipe1 in enumerate(pipes):
        for pipe2 in pipes[i+1:]:
            if pipes_connected(pipe1, pipe2):
                graph[pipe1.id].append(pipe2.id)
                graph[pipe2.id].append(pipe1.id)
    
    return graph

def pipes_connected(pipe1: Pipe, pipe2: Pipe, tolerance: float = 0.1) -> bool:
    """Check if two pipes are connected (share an endpoint)"""
    
    endpoints1 = [pipe1.start, pipe1.end]
    endpoints2 = [pipe2.start, pipe2.end]
    
    for p1 in endpoints1:
        for p2 in endpoints2:
            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            if dist < tolerance:
                return True
    
    return False

def calculate_junction_flows(pipes: List[Pipe]) -> Dict[str, Tuple[float, float]]:
    """Calculate flow balance at pipe junctions"""
    
    # Simplified implementation
    # Group pipes by shared endpoints to find junctions
    junctions = {}
    
    # This is a placeholder - full implementation would be more complex
    # Would need to track flow directions and sum inlet vs outlet flows
    
    return junctions
