# GIMP Measurement Annotation Plugin — Implementation Plan

## Overview
GIMP 3.x Python plugin that draws annotated measurement lines based on rectangular selection bounds. Three modes: horizontal, vertical, diagonal.

## Target
- **GIMP Version**: 3.x only (uses GObject Introspection API)
- **Python**: 3.x
- **API**: `gi.repository.Gimp`, `gi.repository.Gegl`

## User Workflow
1. Make rectangular selection on image using Rectangle Select tool
2. Trigger measurement via keyboard shortcut (user-assigned)
3. Plugin draws labeled measurement line on new layer
4. Selection is cleared automatically
5. To undo: Ctrl+Z (single undo step) or delete annotation layer

## Three Measurement Modes

| Mode | Shortcut (suggested) | Line Position | Label |
|------|---------------------|---------------|-------|
| Horizontal | `Ctrl+Shift+H` | Horizontal center of selection | Width in px |
| Vertical | `Ctrl+Shift+V` | Vertical center of selection | Height in px |
| Diagonal | `Ctrl+Shift+D` | Corner to corner (top-left → bottom-right) | Euclidean distance in px |

## Visual Style (MVP)
- **Line**: 2px red (`#FF0000`)
- **Text**: Default font, offset ~10px above line
- **Arrows**: None (simplicity)
- **Layer**: New transparent layer named `"Measure: {distance}px"`

## Installation

### Development (symlink for live editing)
```bash
make dev
```

### Production (copy to plugin dir)
```bash
make install
```

### Remove
```bash
make uninstall
```

## File Structure
```
GIMPmeasure/
├── src/
│   └── measure-annotate/
│       └── measure-annotate.py    # Main plugin
├── memory/
│   └── plan.md                    # This file
├── Makefile                       # Build/install automation
├── README.md                      # User documentation
└── LICENSE                        # GPL-3.0
```

## GIMP Plugin Directory Locations
- **Native**: `~/.config/GIMP/3.0/plug-ins/`
- **Flatpak**: `~/.var/app/org.gimp.GIMP/config/GIMP/3.0/plug-ins/`

Makefile auto-detects which is present.

## Technical Implementation

### Plugin Registration
Three procedures registered via `do_query_procedures()`:
- `python-fu-measure-horizontal`
- `python-fu-measure-vertical`
- `python-fu-measure-diagonal`

Menu path: `<Image>/Filters/Render/Measure/`

### Core Logic (`draw_measurement`)
1. Validate selection exists via `Gimp.Selection.bounds(image)`
2. Create transparent RGBA layer
3. Set foreground color to red via `Gegl.Color`
4. Draw line with `Gimp.pencil(layer, [x1, y1, x2, y2])`
5. Create text layer with distance label, position offset above midpoint
6. Flatten text into annotation layer
7. Clear selection via `Gimp.Selection.none(image)`
8. Wrap all in `image.undo_group_start()` / `image.undo_group_end()`

## Future Enhancements
- [ ] Dockable toolbar for mode selection
- [ ] Configurable line width (1-5px)
- [ ] Configurable color (foreground or custom)
- [ ] Arrow endpoints option
- [ ] Angle measurement mode
- [ ] Export annotations to CSV

## References
- GIMP 3.0 Python API: https://developer.gimp.org/api/3.0/libgimp/
- GIMP Plugin Porting Guide: https://developer.gimp.org/resource/gimp3-plug-in-porting-guide/
