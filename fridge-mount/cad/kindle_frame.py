"""Kindle Paperwhite fridge frame — Concept A (top-slot sleeve).
Fits the 169 x 117 x 9.1 mm body shared by the Paperwhite 1, 2 and 3.

Parts (each exported in its print orientation):
  tray  - back + side/bottom walls, Kindle slides in from the top. Prints back-down.
  face  - red front with screen window and raised label. Prints face-up;
          pause at the top of the plate and swap to white for the text.
  knob  - x2, white. Prints top-down, peg up.

All dimensions in mm. Measure your Kindle and adjust the KINDLE/SCREEN values.
"""
import cadquery as cq

# --- Kindle Paperwhite 2 --------------------------------------------------
K_W, K_H, K_D = 117.0, 169.0, 9.1
CLEAR = 0.5                      # side/height clearance
SCREEN_W, SCREEN_H = 92.0, 124.0 # window = e-paper active area + small margin
SCREEN_BOTTOM = 27.0             # Kindle bottom edge -> bottom of active area (measure!)

# --- Frame ----------------------------------------------------------------
WALL = 5.0
BACK = 3.0                       # back wall (magnet pockets cut into it)
POCKET_D = 9.8
FACE_T = 2.4
OUT_W = K_W + CLEAR + 2 * WALL   # ~128
OUT_H = 180.0
CORNER_R = 10.0

MAG_D, MAG_H = 8.3, 2.1          # 8x2 mm magnets, press/glue fit, flush with back
MAG_X = 48.0
MAG_Y = [18.0, 66.0, 114.0, 162.0]

PIN_D, PIN_H, PIN_HOLE_D, PIN_HOLE_H = 2.5, 1.4, 2.8, 1.7
PIN_POS = [(sx * (OUT_W / 2 - WALL / 2), y) for sx in (-1, 1) for y in (40.0, 140.0)]

USB_SLOT_W = 50.0                # opening in bottom wall for charging cable/button

KNOB_D, KNOB_H = 22.0, 6.0
KNOB_POS = [(-45.0, 17.0), (45.0, 17.0)]
KNOB_PEG_D, KNOB_PEG_H, KNOB_HOLE_D, KNOB_HOLE_H = 4.0, 1.6, 4.3, 1.8

LABEL = "FAMILY CALENDAR"
LABEL_SIZE = 5.0
LABEL_RAISE = 0.6
LABEL_Y = 17.0

TRAY_T = BACK + POCKET_D
win_y0 = WALL + SCREEN_BOTTOM
win_y1 = win_y0 + SCREEN_H


def rounded_plate(t):
    return (cq.Workplane("XY").center(0, OUT_H / 2)
            .rect(OUT_W, OUT_H).extrude(t).edges("|Z").fillet(CORNER_R))


def make_tray():
    t = rounded_plate(TRAY_T)
    pocket_w = K_W + CLEAR
    t = t.cut(cq.Workplane("XY").workplane(offset=BACK).center(0, WALL + (OUT_H + 5) / 2)
              .rect(pocket_w, OUT_H + 5).extrude(POCKET_D + 1))
    t = t.cut(cq.Workplane("XY").workplane(offset=BACK).center(0, WALL / 2 - 0.5)
              .rect(USB_SLOT_W, WALL + 1.2).extrude(POCKET_D + 1))
    mags = cq.Workplane("XY").workplane(offset=-0.01).pushPoints(
        [(sx * MAG_X, y) for sx in (-1, 1) for y in MAG_Y]).circle(MAG_D / 2).extrude(MAG_H + 0.01)
    t = t.cut(mags)
    pins = cq.Workplane("XY").workplane(offset=TRAY_T).pushPoints(PIN_POS).circle(PIN_D / 2).extrude(PIN_H)
    return t.union(pins)


def make_face():
    f = rounded_plate(FACE_T).faces(">Z").edges().chamfer(0.8)
    # window with chamfered front edge
    cx, cy = 0, (win_y0 + win_y1) / 2
    win = (cq.Workplane("XY").workplane(offset=-0.1).center(cx, cy).rect(SCREEN_W, SCREEN_H)
           .workplane(offset=FACE_T - 0.7).rect(SCREEN_W, SCREEN_H)
           .loft())
    win_ch = (cq.Workplane("XY").workplane(offset=FACE_T - 0.8).center(cx, cy).rect(SCREEN_W, SCREEN_H)
              .workplane(offset=0.9).rect(SCREEN_W + 1.8, SCREEN_H + 1.8).loft())
    f = f.cut(win).cut(win_ch)
    # finger notch at top to grab the Kindle bezel
    f = f.cut(cq.Workplane("XY").workplane(offset=-0.1).center(0, OUT_H + 4).circle(18).extrude(FACE_T + 1))
    # knob sockets (front) and alignment holes (back)
    f = f.cut(cq.Workplane("XY").workplane(offset=FACE_T - KNOB_HOLE_H).pushPoints(KNOB_POS)
              .circle(KNOB_HOLE_D / 2).extrude(KNOB_HOLE_H + 0.1))
    f = f.cut(cq.Workplane("XY").workplane(offset=-0.01).pushPoints(PIN_POS)
              .circle(PIN_HOLE_D / 2).extrude(PIN_HOLE_H))
    return f


def make_label():
    return (cq.Workplane("XY").workplane(offset=FACE_T).center(0, LABEL_Y)
            .text(LABEL, LABEL_SIZE, LABEL_RAISE, kind="bold", halign="center", valign="center"))


def make_knob():
    k = cq.Workplane("XY").circle(KNOB_D / 2).extrude(KNOB_H)
    k = k.faces("<Z").edges().chamfer(0.6)          # this face is the knob's top (prints on the bed)
    ridges = cq.Workplane("XY").workplane(offset=1.5).polarArray(KNOB_D / 2 + 0.3, 0, 360, 30) \
        .circle(0.8).extrude(KNOB_H)
    k = k.cut(ridges)
    peg = cq.Workplane("XY").workplane(offset=KNOB_H).circle(KNOB_PEG_D / 2).extrude(KNOB_PEG_H)
    return k.union(peg)


if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    tray, face, label, knob = make_tray(), make_face(), make_label(), make_knob()
    cq.exporters.export(tray, f"{out}/A_tray_red.stl")
    cq.exporters.export(face.union(label), f"{out}/A_face_red_white-text.stl")
    cq.exporters.export(face, f"{out}/A_face_red_plate-only.stl")
    cq.exporters.export(label, f"{out}/A_face_label_white.stl")
    cq.exporters.export(knob, f"{out}/A_knob_white_x2.stl")
    # assembled preview, in place
    asm = (cq.Assembly()
           .add(tray, name="tray", color=cq.Color(0.78, 0.13, 0.18))
           .add(face, name="face", loc=cq.Location((0, 0, TRAY_T)), color=cq.Color(0.78, 0.13, 0.18))
           .add(label, name="label", loc=cq.Location((0, 0, TRAY_T)), color=cq.Color(0.97, 0.97, 0.95)))
    for i, (x, y) in enumerate(KNOB_POS):
        asm.add(knob, name=f"knob{i}", color=cq.Color(0.97, 0.97, 0.95),
                loc=cq.Location((x, y, TRAY_T + FACE_T + KNOB_H), (1, 0, 0), 180))
    asm.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "A_assembly.step"))
    print("tray bbox", tray.val().BoundingBox().xlen, tray.val().BoundingBox().ylen, tray.val().BoundingBox().zlen)
    print("face bbox", face.val().BoundingBox().xlen, face.val().BoundingBox().ylen, face.val().BoundingBox().zlen)
    print("label bbox", label.val().BoundingBox().xlen, label.val().BoundingBox().ylen)
