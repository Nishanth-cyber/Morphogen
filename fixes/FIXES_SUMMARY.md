# Morphogen Fixes - DXF Export and Prompt Issues

## Issues Fixed

### 1. DXF Export Error
**Problem**: The client was sending incorrect payload to the DXF export endpoint
**Root Cause**: API expects `GenerateRequest` format but client was only sending `{ geometry }`
**Solution**: Updated the export endpoints to accept geometry directly

### 2. Prompt Validation Errors
**Problem**: Walls showing as 0.2mm thick (should be 200mm)
**Root Cause**: Unclear unit specifications in prompts
**Solution**: Created detailed prompt templates with explicit units

### 3. Open Wall Endpoints
**Problem**: Walls not forming closed boundaries
**Root Cause**: Incomplete spatial relationships in prompts
**Solution**: Enhanced prompts to specify complete room enclosures

## Files Modified

1. `server/routes/generate.py` - Fixed export endpoints
2. `client/src/services/api.ts` - Updated API calls
3. `WORKING_PROMPTS.md` - New prompt templates

## How to Apply Fixes

### Step 1: Update Server Routes
```bash
# Backup current file
cp server/routes/generate.py server/routes/generate.py.backup

# Apply the fix
cp fixes/generate.py server/routes/generate.py
```

### Step 2: Update Client API
```bash
# Backup current file
cp client/src/services/api.ts client/src/services/api.ts.backup

# Apply the fix
cp fixes/api.ts client/src/services/api.ts
```

### Step 3: Restart Services
```bash
# Terminal 1: Restart backend
cd server
python main.py

# Terminal 2: Restart frontend
cd client
npm run dev
```

## Testing the Fixes

### Test 1: Working Prompt
Use this prompt in the chat:
```
Design a single-story house on a 20m × 30m plot:

Rooms:
- 3 bedrooms (master: 5m × 4m, bedroom 2: 4m × 4m, bedroom 3: 4m × 3.5m)
- 1 living room (6m × 5m)  
- 1 kitchen (4m × 4m)
- 2 bathrooms (3m × 2.5m each)
- 1 entrance hallway (2m wide)

Wall specifications:
- Exterior walls: 200mm thickness
- Interior walls: 150mm thickness
- Wall height: 3000mm
- All walls must connect to form fully enclosed rooms

Door specifications:
- Bedroom/bathroom doors: 900mm wide
- Living room/kitchen doors: 1000mm wide
- Door height: 2100mm

Window specifications:
- Width: 1500mm
- Height: 1200mm
- Sill height: 900mm from floor
- Install on exterior walls for natural lighting

Layout requirements:
- Main entrance on south side
- Living room near entrance
- Kitchen adjacent to living room
- Bedrooms in private zone away from entrance
- Proper circulation space between all rooms
```

### Test 2: DXF Export
1. After design is generated
2. Click "Export DXF" button
3. File should download without errors
4. Check file contains valid DXF content

### Test 3: Validation
After generation, check for:
- ✅ No "unusually thin thickness" warnings
- ✅ No "open wall endpoints" errors
- ✅ SVG preview shows complete layout
- ✅ DXF export works
- ✅ IFC export works

## Quick Prompt Templates

### Residential House (Minimal)
```
Design a house on a 20m × 30m plot with 3 bedrooms (each 4m × 4m), 1 living room (6m × 5m), 1 kitchen (4m × 3m), 2 bathrooms (each 2.5m × 2m). Use 200mm thick exterior walls, 150mm thick interior walls. All rooms must be fully enclosed with connected walls. Add 900mm wide doors and 1500mm wide windows on exterior walls.
```

### Residential House (Detailed)
```
Create a single-story residential house:

Plot: 20 meters × 30 meters

Room Layout:
- Master bedroom: 5m × 4m (south-east corner)
- Bedroom 2: 4m × 4m (south-west corner)
- Bedroom 3: 4m × 3.5m (north-west corner)
- Living room: 6m × 5m (central, near entrance)
- Kitchen: 4m × 4m (north side, adjacent to living room)
- Bathroom 1: 3m × 2.5m (attached to master bedroom)
- Bathroom 2: 3m × 2.5m (shared between bedroom 2 and 3)
- Entrance hallway: 2m wide × 4m long (south side)

Construction Specifications:
- Exterior walls: 200mm thick concrete
- Interior walls: 150mm thick brick
- Wall height: 3000mm (3 meters)
- Foundation depth: 1500mm

Door Specifications:
- Bedroom doors: 900mm wide × 2100mm tall
- Bathroom doors: 800mm wide × 2100mm tall  
- Living room door: 1000mm wide × 2100mm tall
- Kitchen door: 900mm wide × 2100mm tall
- Main entrance door: 1200mm wide × 2400mm tall

Window Specifications:
- Standard windows: 1500mm wide × 1200mm tall
- Window sill height: 900mm from floor level
- Master bedroom: 2 windows (east and south walls)
- Other bedrooms: 1 window each (exterior walls)
- Living room: 2 large windows (south wall)
- Kitchen: 1 window (north wall)

Critical Requirements:
- All walls must connect to form completely enclosed rooms
- No open endpoints - every wall must connect to another wall or corner
- Ensure proper door swing clearance (at least 1m space)
- Maintain minimum 1m corridor width for circulation
- All exterior walls must have proper load-bearing capacity
```

### Industrial Plant (Desalination)
```
Design a reverse osmosis desalination plant:

Capacity: 50 MLD (Million Liters per Day)
Site: 120m × 60m

Process Flow (left to right):
1. Seawater intake (0m-20m): Inlet pipe 800mm diameter, screens
2. Pretreatment (20m-50m): 
   - Multimedia filters (6 units, 3m diameter each)
   - Cartridge filters (4 units, 2m diameter each)
   - Chemical dosing tanks (3 units, 5m³ each)
3. High Pressure System (50m-70m):
   - HP pumps (3 units, 250 kW each, 2m × 3m footprint)
   - Energy recovery devices (2 units)
4. RO Membrane Area (70m-100m):
   - 8 RO trains (each 6.25 MLD capacity)
   - Membrane vessels (6 vessels per train, 8 inches diameter)
   - Train spacing: 3m between centers
5. Post-Treatment (100m-115m):
   - Remineralization tank (20m³)
   - Chlorination unit
   - pH adjustment
6. Storage (115m-120m):
   - Product water tanks (2 units, 5000 m³ each, 15m diameter)

Piping Specifications:
- Seawater inlet: 800mm diameter, HDPE
- HP feed: 600mm diameter, stainless steel
- Permeate: 500mm diameter, HDPE
- Brine discharge: 700mm diameter, HDPE
- Pressure rating: 75 bar for HP piping
- All pipes must show clear flow direction

Equipment Clearances:
- Minimum 2m maintenance clearance around all equipment
- 3m clearance for major equipment (pumps, tanks)
- 4m wide access roads throughout plant

Safety Requirements:
- Emergency shutdown system
- Fire water ring main
- Chemical containment areas
- Proper grounding and lightning protection
```

## Troubleshooting

### DXF Still Not Exporting
1. Check browser console for errors
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check backend logs for Python errors
4. Try a simpler prompt first

### Validation Warnings Persist
1. Use exact prompt templates above
2. Always specify "200mm" not "0.2m" or "20cm"
3. Mention "fully enclosed rooms" explicitly
4. Check that room dimensions fit within plot size

### Design Looks Incomplete
1. Increase plot size
2. Reduce room sizes
3. Specify exact room positions (north/south/east/west)
4. Mention "connect all walls to form enclosed spaces"

## Additional Resources

- See `IMPROVED_PROMPT_EXAMPLES.md` for more examples
- Check `server/readme.md` for API documentation
- Review `COMPLETE_SYSTEM.md` for architecture details
