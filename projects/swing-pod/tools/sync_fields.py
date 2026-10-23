"""Copy what the MCP schematic->PCB sync leaves out, so DRC schematic parity is clean.

- All symbol fields (Description, Datasheet, MPN, ...) and exclude-from-BOM flags from the netlist.
- "unconnected-(...)" net names on intentionally unused pads.
- GND pours drop isolated islands.

Usage (KiCad Python):
  kicad-cli sch export netlist -o /tmp/n.net swing-pod.kicad_sch
  python tools/sync_fields.py swing-pod.kicad_pcb /tmp/n.net
"""
import re
import sys

import pcbnew


def components(netlist):
    for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)(.*?)\n\t\t\)', netlist, re.S):
        body = m.group(2)
        fields = dict(re.findall(r'\(field\s*\(name "([^"]+)"\)\s*"([^"]*)"\)', body))
        desc = re.search(r'\(description "([^"]*)"\)', body)
        ds = re.search(r'\(datasheet "([^"]*)"\)', body)
        if desc:
            fields.setdefault("Description", desc.group(1))
        if ds:
            fields.setdefault("Datasheet", ds.group(1))
        excluded = re.search(r'\(property\s*\(name "exclude_from_bom"\)', body) is not None
        yield m.group(1), fields, excluded


def main(board_path, netlist_path):
    b = pcbnew.LoadBoard(board_path)
    netlist = open(netlist_path).read()

    for ref, fields, excluded in components(netlist):
        fp = b.FindFootprintByReference(ref)
        if fp is None:
            continue
        for name, text in fields.items():
            if name == "Footprint":
                continue
            if fp.HasField(name):
                fp.GetField(name).SetText(text)
            else:
                fp.SetField(name, text)
                fp.GetField(name).SetVisible(False)
        attrs = fp.GetAttributes()
        fp.SetAttributes(attrs | pcbnew.FP_EXCLUDE_FROM_BOM if excluded else attrs & ~pcbnew.FP_EXCLUDE_FROM_BOM)

    for m in re.finditer(r'\(name "(unconnected-[^"]+)"\)\s*\(class "[^"]*"\)\s*\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', netlist):
        name, ref, pin = m.groups()
        fp = b.FindFootprintByReference(ref)
        net = b.FindNet(name)
        if net is None:
            net = pcbnew.NETINFO_ITEM(b, name)
            b.Add(net)
        for pad in fp.Pads():
            if pad.GetNumber() == pin:
                pad.SetNet(net)

    for i in range(b.GetAreaCount()):
        z = b.GetArea(i)
        if not z.GetIsRuleArea() and z.GetNetname() == "GND":
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)

    b.Save(board_path)
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
