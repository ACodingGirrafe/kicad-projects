"""Board edits the KiCad MCP server has no tool for. Idempotent.

- Antenna keep-out rule area (both copper layers, no tracks/vias/pour) around
  the XIAO U.FL corner and the board strip below it.
- 1.0/0.5 mm plated vias inside the XIAO BAT+/BAT- underside pads so they can
  be soldered from the bottom of the board (the pads are hidden under the XIAO).

Run with KiCad's Python: <kicad python> tools/board_extras.py swing-pod.kicad_pcb
"""
import sys

import pcbnew

# name: (rect x1, y1, x2, y2 in board mm, copper layers)
KEEPOUTS = {
    # Board-local x 17.2..27 / y 18..28 (board origin at 100,100): XIAO
    # bottom-left corner with the U.FL at (121.24, 120.26), down to the edge.
    "ANTENNA_KEEPOUT": ((117.2, 118.0, 127.0, 128.0), (pcbnew.F_Cu, pcbnew.B_Cu)),
    # Under the flat-soldered SparkFun module body: no top copper touching its
    # underside. Its own pads (edge pads, PTH) are still allowed.
    "IMU_UNDERSIDE": ((100.79, 100.775, 108.41, 117.9), (pcbnew.F_Cu,)),
}


def mm(v):
    return pcbnew.FromMM(v)


def add_keepout(board, name, rect, layers):
    if any(z.GetIsRuleArea() and z.GetZoneName() == name for z in board.Zones()):
        return
    x1, y1, x2, y2 = rect
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    ls = pcbnew.LSET()
    for layer in layers:
        ls.AddLayer(layer)
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)       # XIAO castellation D6 pad sits inside
    z.SetDoNotAllowFootprints(False)  # XIAO body overlaps the area
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        o.Append(mm(x), mm(y))
    board.Add(z)


def add_pad_vias(board):
    xiao = board.FindFootprintByReference("U1")
    for pad in xiao.Pads():
        if pad.GetNumber() not in ("23", "24"):
            continue
        pos = pad.GetPosition()
        v = next((t for t in board.GetTracks() if isinstance(t, pcbnew.PCB_VIA) and t.GetPosition() == pos), None)
        if v is None:
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pos)
            v.SetWidth(mm(1.0))
            v.SetDrill(mm(0.5))
            v.SetNet(pad.GetNet())
            board.Add(v)
        # Open mask on the bottom so solder can be fed through from below.
        v.SetBackTentingMode(pcbnew.TENTING_MODE_NOT_TENTED)


if __name__ == "__main__":
    b = pcbnew.LoadBoard(sys.argv[1])
    for name, (rect, layers) in KEEPOUTS.items():
        add_keepout(b, name, rect, layers)
    add_pad_vias(b)
    b.Save(sys.argv[1])
    print("ok")
