"""Build the two 3D models KiCad has no library model for. Needs OpenCascade (pip install cadquery-ocp).

- lib/3d/XIAO-ESP32S3.step: Seeed's official STEP, re-oriented into the
  Seeed_Studio_XIAO_Series:XIAO-ESP32-S3-SMD footprint frame (origin = XIAO
  bottom-left corner, USB-C toward +Y in model space, underside at Z=0).
- lib/3d/SparkFun_Micro_6DoF.step: envelope model of the SparkFun Micro 6DoF
  (1.6 mm PCB 19.05x7.62, LSM6DSV16X LGA, JST-SH Qwiic connector), in the
  swing-pod:SparkFun_Micro_6DoF_LSM6DSV16X_Flat footprint frame. Dimensions
  from SparkFun's Eagle board + ordering notes; KiCad's JST-SH model for height.

Usage: python tools/make_3d_models.py <Seeed 'XIAO-ESP32S3 v2.step'>
"""
import os
import sys

from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound

OUT = os.path.join(os.path.dirname(__file__), "..", "lib", "3d")


def write(shape, name):
    os.makedirs(OUT, exist_ok=True)
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    assert w.Write(os.path.join(OUT, name)) == IFSelect_RetDone


def xiao(src):
    r = STEPControl_Reader()
    assert r.ReadFile(src) == IFSelect_RetDone
    r.TransferRoots()
    shape = r.OneShape()
    # Seeed model: X = length (USB-C at +X, PCB x -8.67..12.28), Y = up
    # (PCB underside -0.25), Z = width (-15.0..2.78, D0 castellation side at
    # Z=-15, matches the U.FL sitting 4 mm from that edge).
    # Wanted: X' = Z + 15, Y' = X + 8.695, Z' = Y + 0.25. That is the cyclic
    # axis permutation (a proper rotation) plus a translation.
    rot1 = gp_Trsf()
    rot1.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 1, 1)), 2.0943951023931953)  # +120 deg: x->y, y->z, z->x
    move = gp_Trsf()
    move.SetTranslation(gp_Vec(15.0, 8.695, 0.25))
    t = move.Multiplied(rot1)
    write(BRepBuilderAPI_Transform(shape, t, True).Shape(), "XIAO-ESP32S3.step")


def box(x1, y1, z1, x2, y2, z2):
    return BRepPrimAPI_MakeBox(gp_Pnt(x1, y1, z1), gp_Pnt(x2, y2, z2)).Shape()


def sparkfun():
    # Footprint frame: module centred on origin, test-pad end at PCB +Y, i.e.
    # model -Y (KiCad model Y = -PCB Y).
    parts = [
        box(-3.81, -9.525, 0.0, 3.81, 9.525, 1.6),        # PCB
        box(-1.25, -1.5, 1.6, 1.25, 1.5, 2.43),           # LSM6DSV16X LGA-14 2.5x3x0.83
        box(-3.0, -6.925, 1.6, 3.0, -1.965, 4.56),        # JST-SH SM04B, 2.96 tall
    ]
    comp = TopoDS_Compound()
    bld = BRep_Builder()
    bld.MakeCompound(comp)
    for p in parts:
        bld.Add(comp, p)
    write(comp, "SparkFun_Micro_6DoF.step")


if __name__ == "__main__":
    xiao(sys.argv[1])
    sparkfun()
    print("ok")
