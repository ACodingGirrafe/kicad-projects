# swing-pod v1.0

PCB for a badminton swing-tracker pod. A Seeed XIAO ESP32-S3 and a SparkFun Micro 6DoF IMU (LSM6DSV16X) sit on a 36 x 28 mm, 2-layer, 0.8 mm board. It charges through USB-C or through magnetic pogo pads. Made in KiCad 10.0.7.

## Files

| Path | What |
|---|---|
| `swing-pod.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad project |
| `outputs/swing-pod-schematic.pdf` | Schematic |
| `outputs/swing-pod-gerbers-jlcpcb.zip` | Gerbers + Excellon drill (PTH/NPTH), upload to JLCPCB as-is |
| `outputs/gerbers/` | Same files unzipped, plus drill maps |
| `outputs/swing-pod-bom.csv` | BOM with manufacturer + MPN |
| `outputs/swing-pod-pos.csv` | Pick-and-place, mm, absolute coordinates (board top-left = 100,100) |
| `outputs/swing-pod-assembly.pdf` | Top assembly drawing (fab layer, all refdes) |
| `outputs/swing-pod-assembled.step` | Assembled 3D model for the housing fit check |
| `outputs/renders/` | Top, bottom, 3D renders and outline SVG |
| `outputs/erc-report.rpt`, `drc-report.rpt` | Final check reports |
| `lib/` | Project libraries (Seeed XIAO library, custom footprints, 3D models) |
| `tools/` | Scripts for the steps the KiCad MCP server can't do (see below) |

## Coordinate convention

- **+Y** is the board's top edge as drawn in KiCad, the edge with the USB-C connector. KiCad's own Y numbers get smaller toward it.
- **+X** is to the right, looking at the top side.
- The bottom silkscreen has a "+Y ^ USB-C" arrow.
- The USB-C shell overhangs the +Y edge by about 0.5 mm, so it reaches toward the housing wall opening.
- The board outline runs from (100,100) to (136,128) with 1 mm corner radii.

## Measured stack-up height (from the STEP models)

| From bottom of PCB to top of | Height |
|---|---|
| JST PH side-entry J1 (tallest part) | **5.65 mm** |
| SparkFun module (1.6 mm PCB + Qwiic connector) | 5.36 mm |
| XIAO USB-C shell | 5.26 mm |
| XIAO shield | 4.05 mm |
| U.FL + mated plug (Hirose spec, 2.5 mm max mated) | about 4.6 mm |

**5.65 mm is under the 6.0 mm budget.** That assumes the through-hole leads (J1, D1, wire pads) are trimmed flush on the bottom. Untrimmed, the JST pins stick out 2.6 mm below the board.

## Design rules (JLCPCB, conservative)

- 0.2 mm track and clearance, 0.6/0.3 mm vias, 0.3 mm copper-to-edge.
- `Power` netclass (VBAT, VUSB, POGO_P, GND): 0.5 mm tracks, 0.8/0.4 mm vias.
- GND pour on both layers.
- Keep-outs:
  - `ANTENNA_KEEPOUT` (both layers, no copper): x 117.2–127, y 118–128. That is the XIAO's U.FL corner and the strip below it.
  - `IMU_UNDERSIDE` (top layer only, no copper): under the flat-mounted SparkFun module's body.
- Mounting: **H1** (M2, bottom-right corner) plus the **SparkFun module's own M2 hole** (2.2 mm NPTH in footprint U2), which also clamps the module.

## Check results

- **ERC:** 0 violations.
- **DRC:** 0 errors, 0 unconnected items, 0 schematic-parity issues. 22 waived warnings, all from Seeed's XIAO footprint artwork:
  - 18 × silk over copper: the module outline is drawn across its own castellated pads. JLCPCB clips silkscreen off pads automatically.
  - 4 × silk past board edge: the outline around the USB-C overhang.
- **Netlist vs. spec** (`tools/check_netlist.py`, plus a separate check of the PCB pad nets): all 9 nets PASS.

| Spec line | Net | Pins |
|---|---|---|
| Battery + to XIAO BAT+ | VBAT | U1.23 (BAT+ pad), J1.1, J2.1, R1.1, TP5 |
| Battery − to XIAO BAT− | GND | U1.24 (BAT− pad), U1.13, U1.18, J1.2, J2.2, J3.2, U2.2, U2.6, R2.2, C1.2, TP2 |
| Pogo + to Schottky anode | POGO_P | J3.1 to D1.2 (A) |
| Schottky cathode to XIAO 5V | VUSB | D1.1 (K) to U1.14 (5V/VBUS), TP6 |
| Divider node to D2, 100 nF to GND | VBAT_SENSE | R1.2, R2.1, C1.1, U1.3 (D2/GPIO3), TP7 |
| IMU 3V3 and pull-ups to XIAO 3V3 | +3V3 | U1.12 (3V3), U2.1, R3.1, R4.1, TP1 |
| SDA | I2C_SDA | U2.3 to U1.5 (D4/GPIO5), R3.2, TP3 |
| SCL | I2C_SCL | U2.4 to U1.6 (D5/GPIO6), R4.2, TP4 |
| INT1 (deep-sleep wake) | IMU_INT1 | U2.5 to U1.2 (D1/GPIO2) |

XIAO pins used: D1 (GPIO2), D2 (GPIO3), D4 (GPIO5), D5 (GPIO6), 3V3, 5V, GND, plus the BAT+ and BAT− underside pads. Every other pin is marked no-connect. The GPIO mapping is checked against Seeed's wiki pin table.

## Verify by hand before you order or assemble

1. **Battery polarity.** J1 pin 1 (marked "+" on the silkscreen, rounded-rect pad) and J2's square pad are BAT+. JST-PH battery plugs come wired both ways. Measure your battery's plug with a meter and compare it to the board before you plug it in. Reversed polarity will destroy the XIAO's charger.
2. **XIAO BAT pads are underneath.** The XIAO is soldered flat by its castellations. Its BAT+ and BAT− pads face down onto this board, so an iron can't reach them. Each mating pad here has a 0.5 mm plated hole that is open on the bottom: feed solder through from below, or reflow or hot-plate the XIAO. Check continuity from J2 to the XIAO BAT pads afterwards.
3. **IMU module mounting.** The SparkFun board sits flat on footprint U2:
   - Its four underside test pads (GND, 3V3, SDA, SCL) land on pads that extend 1 mm past the module edge, so you can drag-solder them with an iron.
   - INT1 and GND use the module's two through-holes. Push a short wire or pin through both boards and solder both sides.
   - **The INT1 hole** is the one nearer the module's left long edge (looking at the board top, test pads toward you), about 5 mm from the far end. The GND hole is the matching one on the right. Confirm against the silkscreen on your module before soldering.
4. **SparkFun module jumpers:**
   - It already has 2.2 kΩ I2C pull-ups (jumper `I2C_PU`). Your 4.7 kΩ R3/R4 in parallel give about 1.5 kΩ, which works fine. Either cut `I2C_PU` or leave R3/R4 unfitted.
   - Cut the `LED` jumper to save about 0.7 mA in sleep.
   - Default I2C address is 0x6B.
5. **Diode, fit ONE of two:**
   - 1N5819 in DO-41, laid flat in the through-holes, **or**
   - a SOD-123 1 A Schottky on the centre pads, such as **B5819W**. SS14 is in SMA (DO-214AC) and does **not** fit SOD-123 pads.
   - The band (cathode) goes to the square pad, on the left.
6. **Battery plug clearance.** J1 is side-entry with its mouth facing −Y, toward the middle of the board. The mated plug and its wires lie over the J2/R1 area. Check in the STEP model that the wires have a path down to the battery.
7. **Antenna.** Route the U.FL cable and FPC antenna away from the battery and pogo wires. No copper is under the keep-out area.

## Footprints and models I made (not from a vendor library)

- `swing-pod:SparkFun_Micro_6DoF_LSM6DSV16X_Flat`: built from SparkFun's Eagle board file (19.05 × 7.62 mm, test pads at 1.905 mm pitch, 0.7 mm holes enlarged to 0.8 mm).
- `swing-pod:D_DO-41_P10.16mm_Horizontal_SOD-123_Alt`: KiCad's DO-41 and SOD-123 land patterns merged into one footprint.
- `swing-pod:WirePads_1x02_P3.0mm_D0.7mm`: two plated wire pads for 26–30 AWG wire.
- `lib/3d/SparkFun_Micro_6DoF.step`: a simple box model, not SparkFun's.
- `lib/3d/XIAO-ESP32S3.step`: Seeed's official model, re-oriented to fit the footprint.
- The XIAO symbol and footprint (`XIAO-ESP32-S3-SMD`) are **Seeed's official** files from their OPL KiCad library. They're unchanged except for the attached 3D model.

## Assumptions and open questions

- The board grew from about 34 × 26 to **36 × 28 mm** (your decision) to fit the side-entry JST. That leaves about 0.6 mm per side in the 37.2 × 29.3 bay, so check your print tolerance.
- The housing bay is assumed rectangular. Two M2 holes are provided: H1 at (133.6, 125.0) and the module hole at (104.6, 103.3).
- 1N5819 forward drop is about 0.3–0.45 V, so the XIAO charger sees about 4.6 V from a 5 V dock. That's fine for a single-cell LiPo.
- The divider draws about 4.5 µA from the battery at all times (470k + 470k).
- The BOM doesn't list LCSC numbers. Use JLCPCB's BOM matcher on the MPN column.
- The XIAO and the SparkFun module are hand-soldered modules, so leave them out of JLCPCB assembly if you order SMT assembly.

## Regenerating

`tools/` holds the steps the KiCad MCP server couldn't do. Run them with KiCad's Python (or a venv built with `--system-site-packages` on top of it):

- `board_extras.py`: keep-outs, and the BAT-pad vias open on the bottom.
- `sync_fields.py`: copies symbol fields, BOM flags and unconnected-net names to the PCB (the MCP sync skips them).
- `make_3d_models.py`: builds the XIAO and SparkFun 3D models. Needs `pip install cadquery-ocp`.
- `check_netlist.py`: compares the exported netlist against the connection spec. Run with any Python 3.
