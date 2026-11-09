import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
import cadquery as cq
import kindle_frame as kf

RED, WHITE, SCREEN = (0.80, 0.12, 0.17), (0.96, 0.96, 0.94), (0.88, 0.87, 0.84)
BG = np.array([238, 235, 230]) / 255


def tris(shape, loc=None):
    s = shape.val() if hasattr(shape, "val") else shape
    if loc is not None:
        s = s.moved(loc)
    v, f = s.tessellate(0.1, 0.2)
    v = np.array([[p.x, p.y, p.z] for p in v])
    return v[np.array(f)]


def rot(elev, azim):
    a, e = np.radians(azim), np.radians(elev)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return Rx @ Rz


def render(parts, elev, azim, size=600):
    R = rot(elev, azim)
    allv = np.concatenate([t.reshape(-1, 3) for t, _ in parts]) @ R.T
    mn, mx = allv[:, :2].min(0), allv[:, :2].max(0)
    scale = 0.86 * size / (mx - mn).max()
    off = size / 2 - scale * (mn + mx) / 2
    img = np.ones((size, size, 3)) * BG
    zb = np.full((size, size), -np.inf)
    L = np.array([-0.35, 0.55, 0.76]); L /= np.linalg.norm(L)
    for t, col in parts:
        p = t @ R.T
        n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        nn = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
        nn[nn[:, 2] < 0] *= -1
        k = 0.35 + 0.65 * np.clip(nn @ L, 0, 1)
        xy = p[:, :, :2] * scale + off
        xy[:, :, 1] = size - xy[:, :, 1]
        for i in range(len(p)):
            a, b, c = xy[i]
            x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
            x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
            x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, size - 1), min(y1, size - 1)
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(d) < 1e-9:
                continue
            w0 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / d
            w1 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / d
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any():
                continue
            z = w0 * p[i, 0, 2] + w1 * p[i, 1, 2] + w2 * p[i, 2, 2]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            upd = m & (z > sub)
            sub[upd] = z[upd]
            img[y0:y1 + 1, x0:x1 + 1][upd] = np.array(col) * k[i]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


tray, face, label, knob = kf.make_tray(), kf.make_face(), kf.make_label(), kf.make_knob()
for n, s in [("tray", tray), ("face+label", face.union(label)), ("knob", knob)]:
    print(n, "valid:", s.val().isValid(), "solids:", len(s.solids().vals()))
up = cq.Location(cq.Vector(0, 0, kf.TRAY_T))
screen = cq.Workplane("XY").workplane(offset=kf.BACK + 1).center(0, (kf.win_y0 + kf.win_y1) / 2) \
    .rect(kf.SCREEN_W + 4, kf.SCREEN_H + 4).extrude(kf.POCKET_D - 1.5)
asm = [(tris(tray), RED), (tris(face, up), RED), (tris(label, up), WHITE), (tris(screen), SCREEN)]
for x, y in kf.KNOB_POS:
    loc = cq.Location(cq.Vector(x, y, kf.TRAY_T + kf.FACE_T + kf.KNOB_H), cq.Vector(1, 0, 0), 180)
    asm.append((tris(knob, loc), WHITE))

views = [
    (render(asm, -25, 15), "Assembled — front"),
    (render([(tris(tray), RED)], -55, 200), "Back tray — Kindle slides in from top"),
    (render([(tris(tray), RED)], 150, 10), "Back — 8 flush magnet pockets"),
]
W = 600
sheet = Image.new("RGB", (W * 3, W + 50), tuple((BG * 255).astype(int)))
dr = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 22)
except Exception:
    font = ImageFont.load_default()
for i, (im, t) in enumerate(views):
    sheet.paste(im, (i * W, 50))
    dr.text((i * W + 20, 14), t, fill=(40, 37, 35), font=font)
sheet.save(sys.argv[1])
