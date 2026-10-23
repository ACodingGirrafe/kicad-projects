# kicad-projects

My KiCad PCB projects. Each one lives in its own folder under `projects/` and is self-contained:
its custom symbols, footprints and 3D models sit in that project's `lib/` folder, so cloning
the repo and opening the `.kicad_pro` just works.

## Projects

| Project | Status | Description |
|---|---|---|
| [swing-pod](projects/swing-pod/) | v1.0, fab files ready | Badminton swing-tracker pod: XIAO ESP32-S3 + LSM6DSV16X IMU, 36 × 28 mm |
| [js-drone](projects/js-drone/) | Schematic | Flight controller schematic and PCB for an ESP32-based drone |
| [atfd](projects/atfd/) | Not started | A Tamagotchi for Daniela |

## Layout

```
projects/<name>/
├── <name>.kicad_pro / .kicad_sch / .kicad_pcb
├── sym-lib-table, fp-lib-table   # project libraries, paths relative to ${KIPRJMOD}
├── lib/                          # custom symbols (.kicad_sym), footprints (.pretty/), 3D models
├── outputs/                      # Gerbers, BOM, pick-and-place, schematic PDF, reports, renders
├── tools/                        # helper scripts, if any
└── README.md
```

## Starting a new project

1. Make `projects/<new-name>/` and create the KiCad project inside it.
2. Put any custom symbols/footprints in `projects/<new-name>/lib/` and add them under
   **Preferences → Manage Symbol/Footprint Libraries → Project Specific Libraries**
   with a path starting `${KIPRJMOD}/lib/...` (never an absolute `C:\Users\...` path).
3. Add a row to the table above.

## Versions

Use git tags (e.g. `swing-pod-v1.0`) for each board revision you send to fab,
rather than separate branches. Branches are for trying out changes you may throw away.
