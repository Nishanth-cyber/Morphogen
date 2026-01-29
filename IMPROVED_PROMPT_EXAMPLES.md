# IMPROVED PROMPTS FOR MORPHOGEN

## Residential Building Prompts

### Basic House (Working Example)
```
Design a single-story residential house with the following specifications:

Plot dimensions: 20 meters × 30 meters

Rooms required:
- 3 bedrooms (master: 5m × 4m, bedroom 2: 4m × 4m, bedroom 3: 4m × 3.5m)
- 1 living room (6m × 5m)
- 1 kitchen (4m × 4m)
- 2 bathrooms (3m × 2.5m each)
- 1 entrance hallway (2m wide)

Construction specifications:
- All exterior walls: 200mm thick
- All interior walls: 150mm thick
- Wall height: 3000mm
- Standard door width: 900mm (bedrooms/bathrooms), 1000mm (living room)
- Window dimensions: 1500mm wide × 1200mm tall
- Window sill height: 900mm from floor

Layout preferences:
- Main entrance on the south side
- Living room near entrance
- Kitchen adjacent to living room
- Bedrooms in private zone
- Adequate natural lighting with windows on exterior walls
```

### Apartment (2BHK)
```
Create a 2BHK apartment layout:

Total area: 850 square feet
Dimensions: 12m × 8m

Rooms:
- 2 bedrooms (3.5m × 3.5m each)
- 1 living room (4m × 4m)
- 1 kitchen (3m × 2.5m)
- 2 bathrooms (2m × 2m each)
- 1 balcony (2m × 1.5m)

Requirements:
- Wall thickness: 200mm (exterior), 100mm (interior)
- Efficient space utilization
- Proper ventilation in all rooms
- Balcony accessible from living room
```

### Villa (Luxury)
```
Design a luxury villa with:

Plot: 40m × 30m (1200 sq m)
Floors: 2

Ground Floor:
- Grand entrance foyer (4m × 4m)
- Living room (8m × 6m)
- Dining room (5m × 4m)
- Modern kitchen (6m × 4m)
- Guest bedroom with attached bathroom (4m × 4m + 2m × 2m)
- Powder room (1.5m × 2m)
- Home office (3m × 3m)

First Floor:
- Master bedroom suite (6m × 5m) with walk-in closet and attached bathroom
- 2 additional bedrooms (4m × 4m each)
- 2 bathrooms (3m × 2.5m each)
- Family lounge (5m × 4m)

Specifications:
- Wall thickness: 230mm (exterior), 150mm (interior)
- Floor height: 3.5m (ground), 3m (first floor)
- Large windows for natural light
- Balconies on first floor
```

## Industrial Plant Prompts

### Desalination Plant (Basic)
```
Design a reverse osmosis desalination plant:

Capacity: 50 MLD (Million Liters per Day)
Technology: Reverse Osmosis (RO)
Site dimensions: 120m × 60m

Process units required:
1. Seawater intake system with screens
2. Pretreatment section:
   - Multimedia filters (6 units)
   - Cartridge filters (4 units)
3. High pressure pumps (3 units, 250 kW each)
4. RO membrane units (8 trains, 6.25 MLD each)
5. Post-treatment:
   - Remineralization
   - Chlorination
6. Product water storage tanks (2 × 5000 m³)
7. Brine discharge system

Specifications:
- Recovery rate: 45%
- Operating pressure: 65-70 bar
- Pipe diameters: Inlet 800mm, HP piping 600mm, Product 500mm
- Linear flow configuration
- Maintenance access: 2m clearance around all equipment
```

### Water Treatment Plant
```
Create a municipal water treatment facility:

Capacity: 100 MLD
Population served: 500,000 people
Site: 150m × 80m

Treatment processes:
1. Raw water intake
2. Screening and grit removal
3. Coagulation and flocculation
4. Sedimentation tanks (4 units)
5. Rapid sand filters (8 units)
6. Chlorination and disinfection
7. Clear water reservoir (10,000 m³)
8. High service pumping station

Layout requirements:
- Sequential flow arrangement
- Gravity flow where possible
- Equipment redundancy for reliability
- Chemical storage area (separate zone)
- Administration building
- Laboratory facilities
```

### Chemical Processing Plant (Compact)
```
Design a chemical processing facility:

Capacity: 50 tons/day
Site: 80m × 50m

Process units:
1. Raw material storage (3 tanks, 20 m³ each)
2. Reactor section (2 reactors, 15 m³ each)
3. Heat exchangers (4 units)
4. Separation units (distillation columns)
5. Product storage (2 tanks, 30 m³ each)
6. Cooling water system
7. Utility connections

Safety requirements:
- Hazardous area classification
- Emergency shutdown systems
- Fire protection equipment
- Proper ventilation
- Containment areas
```

## Key Improvements in These Prompts

1. **Specific Dimensions**: Always provide exact measurements
2. **Wall Thickness**: Explicitly state 200mm (not 0.2mm) to avoid validation errors
3. **Room Count**: Clear number of each room type
4. **Layout Preferences**: Mention spatial relationships
5. **Technical Details**: Include engineering specifications
6. **Proper Units**: Use meters (m) for large dimensions, millimeters (mm) for details

## Common Mistakes to Avoid

❌ "20m x 30m with 3 bedrooms and a kitchen"
✅ "Design on a 20m × 30m plot with 3 bedrooms (each 4m × 4m), 1 kitchen (4m × 3m), walls 200mm thick"

❌ "Design a desalination plant"
✅ "Design a 50 MLD reverse osmosis desalination plant with seawater intake, pretreatment, RO units, and post-treatment on a 120m × 60m site"

❌ "Make walls thinner"
✅ "Reduce interior wall thickness from 200mm to 150mm while keeping exterior walls at 200mm"

## Troubleshooting Common Errors

### "Wall has unusually thin thickness"
**Problem**: Wall thickness specified as 0.2mm instead of 200mm
**Solution**: Always specify "200mm thick" or "0.2m thick" for standard walls

### "Found open wall endpoints"
**Problem**: Walls don't connect to form closed rooms
**Solution**: Use prompts that emphasize complete room enclosures: "Ensure all walls form enclosed rooms with proper connections"

### "DXF Export Failed"
**Problem**: Missing geometry data or invalid coordinates
**Solution**: Use complete prompts with all required room specifications

## Testing Your Prompts

After updating your prompt, check for:
1. ✅ No validation warnings
2. ✅ DXF export works (blue button)
3. ✅ IFC export works (green button)
4. ✅ Preview shows complete layout
5. ✅ All rooms are properly enclosed

## Quick Reference: Minimum Working Prompt

```
Design a house on a 20m × 30m plot:
- 3 bedrooms (4m × 4m each)
- 1 living room (6m × 5m)
- 1 kitchen (4m × 3m)
- 2 bathrooms (2.5m × 2m each)
- Walls: 200mm thick exterior, 150mm interior
- Doors: 900mm wide
- Ensure all rooms are fully enclosed with connected walls
```

This prompt should work without validation errors!
