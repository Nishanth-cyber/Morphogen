from pydantic import BaseModel, Field
from typing import List, Tuple, Literal, Optional
from enum import Enum

# Basic types
Point = Tuple[float, float]
Point3D = Tuple[float, float, float]

# Enums for standardization
class PipeType(str, Enum):
    MAIN_FEED = "main_feed"
    BRINE_DISCHARGE = "brine_discharge"
    PERMEATE = "permeate"
    CHEMICAL = "chemical"
    CLEANING = "cleaning"
    DRAIN = "drain"

class EquipmentType(str, Enum):
    PUMP = "pump"
    TANK = "tank"
    RO_UNIT = "ro_unit"
    FILTER = "filter"
    HEAT_EXCHANGER = "heat_exchanger"
    VALVE = "valve"
    MIXER = "mixer"

class ValveType(str, Enum):
    GATE = "gate"
    BALL = "ball"
    BUTTERFLY = "butterfly"
    CHECK = "check"
    PRESSURE_RELIEF = "pressure_relief"

class FlowDirection(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

# Building/Residential Geometry
class Wall(BaseModel):
    start: Point
    end: Point
    thickness: float = Field(default=200, description="Wall thickness in mm")
    height: Optional[float] = Field(default=3000, description="Wall height in mm")

class Door(BaseModel):
    wall: Literal["north", "south", "east", "west"]
    start: Point
    end: Point
    width: float = Field(default=900, description="Door width in mm")
    height: float = Field(default=2100, description="Door height in mm")

class Window(BaseModel):
    wall: Literal["north", "south", "east", "west"]
    start: Point
    end: Point
    width: float
    height: float = Field(default=1200, description="Window height in mm")
    sill_height: float = Field(default=900, description="Height from floor in mm")

# Industrial Piping Components
class Pipe(BaseModel):
    id: str = Field(description="Unique pipe identifier")
    start: Point
    end: Point
    diameter: float = Field(description="Pipe diameter in mm", ge=25, le=3000)
    pipe_type: PipeType
    material: str = Field(default="HDPE", description="Pipe material")
    flow_direction: FlowDirection
    flow_rate: Optional[float] = Field(default=None, description="Flow rate in m³/h")
    pressure_rating: Optional[float] = Field(default=None, description="Pressure rating in bar")
    
    class Config:
        use_enum_values = True

class Equipment(BaseModel):
    id: str = Field(description="Unique equipment identifier")
    equipment_type: EquipmentType
    position: Point
    width: float = Field(description="Equipment width in mm")
    length: float = Field(description="Equipment length in mm")
    height: Optional[float] = Field(default=2000, description="Equipment height in mm")
    capacity: Optional[float] = Field(default=None, description="Capacity (units vary by type)")
    power: Optional[float] = Field(default=None, description="Power consumption in kW")
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    
    class Config:
        use_enum_values = True

class Valve(BaseModel):
    id: str = Field(description="Unique valve identifier")
    valve_type: ValveType
    position: Point
    size: float = Field(description="Valve size (diameter) in mm")
    pipe_id: str = Field(description="Associated pipe ID")
    normally_open: bool = Field(default=True)
    
    class Config:
        use_enum_values = True

class ProcessUnit(BaseModel):
    """Represents a complete process unit (e.g., pretreatment section)"""
    id: str
    name: str = Field(description="Process unit name, e.g., 'Pretreatment'")
    boundary: List[Point] = Field(description="Boundary polygon of the unit area")
    equipment: List[str] = Field(default_factory=list, description="List of equipment IDs in this unit")
    inlet_pipes: List[str] = Field(default_factory=list, description="List of inlet pipe IDs")
    outlet_pipes: List[str] = Field(default_factory=list, description="List of outlet pipe IDs")

class Annotation(BaseModel):
    """Text labels for drawings"""
    text: str
    position: Point
    font_size: float = Field(default=12)
    layer: str = Field(default="ANNOTATIONS")

# Complete Geometry Output
class GeometryOutput(BaseModel):
    """
    Complete geometry representation supporting both building and industrial layouts
    """
    units: Literal["mm", "cm", "m"] = Field(default="mm")
    
    # Building components
    walls: List[Wall] = Field(default_factory=list)
    doors: List[Door] = Field(default_factory=list)
    windows: List[Window] = Field(default_factory=list)
    
    # Industrial piping components
    pipes: List[Pipe] = Field(default_factory=list)
    equipment: List[Equipment] = Field(default_factory=list)
    valves: List[Valve] = Field(default_factory=list)
    process_units: List[ProcessUnit] = Field(default_factory=list)
    
    # Common
    annotations: List[Annotation] = Field(default_factory=list)
    
    # Metadata
    domain: Optional[str] = Field(default=None, description="Design domain: industrial, residential, commercial")
    project_name: Optional[str] = None
    capacity: Optional[float] = Field(default=None, description="Plant capacity (e.g., MLD for desalination)")
    site_dimensions: Optional[Tuple[float, float]] = Field(default=None, description="Site dimensions [length, width]")

# Industrial Planning Schema
class IndustrialPlan(BaseModel):
    """
    Structured plan for industrial facilities (e.g., desalination plants)
    """
    domain: str = Field(default="industrial")
    subdomain: str = Field(description="e.g., desalination_plant, water_treatment")
    capacity: float = Field(description="Facility capacity (units depend on subdomain)")
    capacity_unit: str = Field(default="MLD", description="e.g., MLD, m³/day, MW")
    
    site_dimensions: Tuple[float, float] = Field(description="Site dimensions [length, width] in meters")
    
    process_units: List[str] = Field(
        description="Ordered list of process units",
        example=["intake", "pretreatment", "reverse_osmosis", "post_treatment"]
    )
    
    flow_configuration: Literal["linear", "compact", "distributed"] = Field(
        default="linear",
        description="Overall plant layout configuration"
    )
    
    # Detailed specifications
    inlet_flow_rate: Optional[float] = Field(default=None, description="Inlet flow rate in m³/h")
    outlet_flow_rate: Optional[float] = Field(default=None, description="Product water flow rate in m³/h")
    recovery_rate: Optional[float] = Field(default=None, description="Recovery rate as percentage")
    
    # Additional constraints
    equipment_specs: Optional[dict] = Field(default=None, description="Specific equipment requirements")
    piping_specs: Optional[dict] = Field(default=None, description="Piping specifications")
    
class BuildingPlan(BaseModel):
    """
    Structured plan for buildings (residential/commercial)
    """
    domain: str = Field(default="residential")
    subdomain: str = Field(description="e.g., single_family_house, apartment")
    
    floors: int = Field(default=1, ge=1, le=10)
    plot_dimensions: Tuple[float, float] = Field(description="Plot dimensions [length, width] in meters")
    
    rooms: List[dict] = Field(
        description="List of rooms with type and area",
        example=[{"type": "living_room", "area": 25}, {"type": "bedroom", "area": 15}]
    )
    
    bathrooms: int = Field(default=1, ge=1)
    parking: Optional[int] = Field(default=0, description="Number of parking spaces")
    
    # Additional features
    features: List[str] = Field(
        default_factory=list,
        description="Additional features like balcony, terrace, etc."
    )
