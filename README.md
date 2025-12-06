# GIMPmeasure

GIMP 3.x plugin for drawing annotated measurement lines on images. Select a rectangular region, trigger a shortcut, and get a labeled dimension line.

![GIMP 3.x](https://img.shields.io/badge/GIMP-3.x-blue)
![Python 3](https://img.shields.io/badge/Python-3.x-yellow)
![License](https://img.shields.io/badge/license-GPL--3.0-green)

## Features

- **Three measurement modes**:
  - **Horizontal** — Measures selection width
  - **Vertical** — Measures selection height  
  - **Diagonal** — Measures corner-to-corner distance (Euclidean)

- **Non-destructive** — Each measurement creates a new layer
- **Single undo** — Ctrl+Z removes entire annotation
- **Clean workflow** — Selection auto-clears after measurement
- **Auto-detection** — Makefile finds native or Flatpak GIMP installs

## Requirements

- **GIMP 3.x** (3.0 or later) — Will not work with GIMP 2.10
- **Python 3.x** (included with GIMP 3.x)
- **Linux** (tested on Fedora; macOS/Windows may need path adjustments)

## Installation

### Quick Install

```bash
git clone https://github.com/hamiltonia/GIMPmeasure.git
cd GIMPmeasure
make install
```

Then restart GIMP.

### Development Install (symlink)

For plugin development, use a symlink so edits take effect on GIMP restart:

```bash
make dev
```

### Verify Installation

```bash
make check
```

This confirms GIMP 3.x config directory exists.

### Uninstall

```bash
make uninstall
```

### Supported GIMP Locations

The Makefile auto-detects:
| Install Type | Config Path |
|--------------|-------------|
| Native | `~/.config/GIMP/3.0/plug-ins/` |
| Flatpak | `~/.var/app/org.gimp.GIMP/config/GIMP/3.0/plug-ins/` |

## Usage

1. **Open an image** in GIMP
2. **Make a rectangular selection** using the Rectangle Select tool (`R`)
3. **Run measurement** via menu:
   - `Filters → Render → Measure → Measure Horizontal`
   - `Filters → Render → Measure → Measure Vertical`
   - `Filters → Render → Measure → Measure Diagonal`

The measurement appears on a new layer named `"Measure: Xpx"`.

### Keyboard Shortcuts (Recommended)

For fastest workflow, assign shortcuts:

1. Go to **Edit → Preferences → Interface → Keyboard Shortcuts**
2. Search for "measure"
3. Assign shortcuts:

| Mode | Suggested Shortcut |
|------|-------------------|
| Horizontal | `Ctrl+Shift+H` |
| Vertical | `Ctrl+Shift+V` |
| Diagonal | `Ctrl+Shift+D` |

### Workflow Example

```
1. Press R (Rectangle Select)
2. Drag selection around area to measure
3. Press Ctrl+Shift+H (horizontal measurement)
4. Result: red line with "347px" label on new layer
```

## Visual Example

```
         408px
    ←─────────────→           ↑
                              │
                            280px
      ╲                       │
       ╲  217.8px             ↓
        ╲
         ╲

(Diagonal)        (Horizontal & Vertical)
```

## Troubleshooting

### Plugin doesn't appear in menu
- Ensure GIMP 3.x (not 2.10) — check `Help → About`
- Restart GIMP after installation
- Check file is executable: `chmod +x src/measure-annotate/measure-annotate.py`

### "No selection found" error
- Make a selection first with Rectangle Select tool (`R`)
- Ensure selection is on the active image

### GIMP 3.x config not found
- Run GIMP once to create config directory
- For Flatpak: `flatpak run org.gimp.GIMP`

### Check for errors
Launch GIMP from terminal to see Python errors:
```bash
gimp
```

## Project Structure

```
GIMPmeasure/
├── src/
│   └── measure-annotate/
│       └── measure-annotate.py   # Main plugin
├── memory/
│   └── plan.md                   # Development notes
├── Makefile                      # Build/install automation
├── README.md
└── LICENSE
```

## Contributing

1. Fork the repository
2. Use `make dev` for development install
3. Edit `src/measure-annotate/measure-annotate.py`
4. Restart GIMP to test changes
5. Submit a pull request

## Future Enhancements

- [ ] Configurable line color
- [ ] Configurable line width
- [ ] Dockable toolbar for quick mode switching
- [ ] Arrow endpoints option
- [ ] Angle measurement mode

## License

GPL-3.0 — See [LICENSE](LICENSE) for details.

## Author

Eric Hamilton — [@hamiltonia](https://github.com/hamiltonia)
