"""Compare a KiCad netlist (kicadsexpr) against the swing-pod connection spec.

Usage:
  kicad-cli sch export netlist -o /tmp/n.net swing-pod.kicad_sch
  python3 tools/check_netlist.py /tmp/n.net
Exit code 0 = every spec line matches and no extra pins sit on spec nets.
"""
import re
import sys

# Spec from the task brief, as (net, {ref.pin, ...}). XIAO pin numbers per
# Seeed symbol: 2=D1/GPIO2, 3=D2/GPIO3, 5=D4/GPIO5, 6=D5/GPIO6, 12=3V3,
# 13/18/24=GND, 14=VUSB(5V), 23=VBAT pad.
SPEC = {
    "VBAT": {"U1.23", "J1.1", "J2.1", "R1.1", "TP5.1"},
    "GND": {"U1.13", "U1.18", "U1.24", "J1.2", "J2.2", "J3.2", "U2.2", "U2.6",
            "R2.2", "C1.2", "TP2.1"},
    "POGO_P": {"J3.1", "D1.2"},          # D1 pin 2 = anode
    "VUSB": {"D1.1", "U1.14", "TP6.1"},  # D1 pin 1 = cathode
    "VBAT_SENSE": {"R1.2", "R2.1", "C1.1", "U1.3", "TP7.1"},
    "+3V3": {"U1.12", "U2.1", "R3.1", "R4.1", "TP1.1"},
    "I2C_SDA": {"U2.3", "U1.5", "R3.2", "TP3.1"},
    "I2C_SCL": {"U2.4", "U1.6", "R4.2", "TP4.1"},
    "IMU_INT1": {"U2.5", "U1.2"},
}


def parse(path):
    text = open(path).read()
    nets = {}
    for block in re.split(r"\(net\s*\n?\s*\(code", text)[1:]:
        name = re.search(r'\(name "([^"]*)"\)', block).group(1).lstrip("/")
        nodes = re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', block)
        nets[name] = {f"{r}.{p}" for r, p in nodes}
    return nets


def main(path):
    nets = parse(path)
    ok = True
    for net, want in SPEC.items():
        got = nets.get(net, set())
        missing, extra = want - got, got - want
        status = "OK  " if not (missing or extra) else "FAIL"
        ok &= status == "OK  "
        print(f"{status} {net:11} {' '.join(sorted(got))}")
        if missing:
            print(f"     missing: {' '.join(sorted(missing))}")
        if extra:
            print(f"     extra:   {' '.join(sorted(extra))}")
    others = {n: p for n, p in nets.items() if n not in SPEC and not n.startswith("unconnected")}
    for n, p in others.items():
        ok = False
        print(f"FAIL unexpected net {n}: {' '.join(sorted(p))}")
    print("RESULT:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) else 1)
