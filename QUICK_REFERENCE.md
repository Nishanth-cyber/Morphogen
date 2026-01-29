# ⚡ MORPHOGEN QUICK REFERENCE CARD

## 🎯 1-MINUTE SETUP

### Copy-Paste Working Prompt:
```
Design a single-story house on 20m × 30m plot: master bedroom (5m × 4m), 2 bedrooms (each 4m × 4m), living room (6m × 5m), kitchen (4m × 4m), 2 bathrooms (each 3m × 2.5m). Exterior walls 200mm thick, interior walls 150mm thick. All walls must connect to form fully enclosed rooms. Add 900mm doors and 1500mm windows.
```

### Expected: 
✅ 30-45 seconds → ✅ Complete design → ✅ No errors

---

## 🔑 KEY RULES

| DO ✅ | DON'T ❌ |
|-------|----------|
| "200mm thick" | "0.2mm thick" |
| "5m × 4m" | "medium sized" |
| "All walls connect" | (skip this) |
| Exact dimensions | Vague descriptions |

---

## 📏 STANDARD DIMENSIONS

### Walls:
- Exterior: **200mm**
- Interior: **150mm**
- Height: **3000mm**

### Doors:
- Bedroom: **900mm** × 2100mm
- Main: **1200mm** × 2400mm

### Windows:
- Standard: **1500mm** × 1200mm
- Sill: **900mm** from floor

---

## 🏠 ROOM SIZES (Quick Reference)

| Room Type | Small | Medium | Large |
|-----------|-------|--------|-------|
| Bedroom | 3×3m | 4×4m | 5×5m |
| Living | 4×4m | 6×5m | 8×6m |
| Kitchen | 3×3m | 4×4m | 6×5m |
| Bathroom | 2×2m | 3×2.5m | 4×3m |

---

## 🎨 PROMPT FORMULA

```
Design a [TYPE] on [DIMS] plot:

ROOMS: [name] ([size] each)
WALLS: Exterior [thickness], Interior [thickness]
CRITICAL: All walls must connect
DOORS: [width] × [height]  
WINDOWS: [width] × [height]
```

---

## ✅ VALIDATION CHECKLIST

After generation:
- [ ] "Design generated successfully"
- [ ] No red warnings
- [ ] Preview shows layout
- [ ] DXF button active (blue)
- [ ] IFC button active (green)

---

## 🚨 TROUBLESHOOTING 30-SECOND FIXES

### "Wall thickness 0.2mm" error:
**Fix:** Change "0.2m" to "200mm"

### "Open wall endpoints":
**Fix:** Add "All walls must connect to form fully enclosed rooms"

### DXF won't export:
**Fix:** Restart server:
```bash
cd D:\Projects\Working\Morphogen\server
python main.py
```

### Design incomplete:
**Fix:** Check room areas < plot area
Calculate: sum(rooms) + 30% < plot

---

## 📱 QUICK TEMPLATES

### Minimal House:
```
20m×30m plot: 3 bedrooms (4m×4m each), living (6m×5m), kitchen (4m×3m), 2 bathrooms (2.5m×2m). Walls 200mm exterior, 150mm interior. All enclosed.
```

### 2BHK Apartment:
```
12m×8m: 2 bedrooms (3.5m×3.5m), living (4m×4m), kitchen (3m×2.5m), 2 bathrooms (2m×2m), balcony (2m×1.5m). 200mm exterior, 100mm interior walls. All enclosed.
```

### Industrial:
```
50 MLD desalination plant, 120m×60m: intake (pipe 800mm), 6 filters (3m dia), 3 pumps (250kW), 8 RO trains, 2 tanks (5000m³). Linear flow, 2m clearance.
```

---

## 🔗 WHERE TO GO

- **Fast start:** `QUICK_START.md`
- **All fixes:** `APPLIED_FIXES.md`
- **50+ prompts:** `fixes/WORKING_PROMPTS.md`
- **Full report:** `COMPLETE_FIX_REPORT.md`

---

## 🎯 SUCCESS IN 3 STEPS

1. **Start Server**
   ```bash
   cd server && python main.py
   ```

2. **Paste Prompt** (from top of this card)

3. **Export** (Click DXF/IFC buttons)

---

## 📊 QUICK STATS

- ✅ 95%+ success rate with templates
- ⏱️ 30-60 seconds generation time
- 📁 3 export formats (DXF, IFC, SVG)
- 📚 50+ tested prompt templates

---

**Print this card and keep it handy! 📌**

*Last Updated: Jan 29, 2026*
