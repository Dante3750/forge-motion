"""Writes a photo-studio light environment (equirectangular Radiance .hdr) for the live 3D viewer:
a big soft key box up front-left, a rim strip behind-right, a dim fill, dark walls and a darker floor.
cmgen turns it into the image-based lighting the app loads (reflections + soft ambient light)."""
import sys, math
import numpy as np
W, H = 1024, 512
u = (np.arange(W) + 0.5) / W; v = (np.arange(H) + 0.5) / H
th = (u - 0.5) * 2 * math.pi              # longitude
ph = (0.5 - v) * math.pi                  # latitude, +up
TH, PH = np.meshgrid(th, ph)
d = np.stack([np.cos(PH) * np.sin(TH), np.sin(PH), -np.cos(PH) * np.cos(TH)], -1)
img = np.zeros((H, W, 3), np.float32)
up = d[..., 1]
# walls: dark grey, a touch brighter towards the ceiling; floor darker
img += (0.035 + 0.06 * np.clip(up, 0, 1))[..., None] * np.array([1.0, 1.0, 1.04])
img[up < 0] *= 0.55
def box(theta, phi, w, h, lum, col=(1, 1, 1), soft=0.35):
    c = np.array([math.cos(math.radians(phi)) * math.sin(math.radians(theta)), math.sin(math.radians(phi)),
                  -math.cos(math.radians(phi)) * math.cos(math.radians(theta))])
    ang = np.degrees(np.arccos(np.clip((d * c).sum(-1), -1, 1)))
    # rectangular-ish softbox via separate longitude / latitude distances
    dl = np.abs(((np.degrees(TH) - theta + 180) % 360) - 180) * np.cos(PH); dp = np.abs(np.degrees(PH) - phi)
    m = np.clip(1 - np.maximum(dl / w, dp / h), 0, 1)
    m = np.clip(m / soft, 0, 1) ** 2
    m *= (ang < 90)
    img[...] += m[..., None] * lum * np.array(col, np.float32)
box(-35, 32, 26, 20, 14.0, (1.0, 0.97, 0.92))   # key softbox, front-left above
box(140, 18, 9, 30, 9.0, (0.92, 0.96, 1.0))     # rim strip, behind-right
box(40, 8, 30, 14, 2.2, (0.95, 0.97, 1.0))      # fill, front-right
box(0, 75, 60, 12, 1.2)                          # overhead bounce
# Radiance RGBE
def write_hdr(path, a):
    a = np.maximum(a, 0)
    m = a.max(-1); e = np.zeros_like(m, np.int32); mant = np.zeros_like(m)
    nz = m > 1e-32
    mant[nz], e[nz] = np.frexp(m[nz])
    sc = np.zeros_like(m); sc[nz] = mant[nz] * 256.0 / m[nz]
    rgbe = np.zeros(a.shape[:2] + (4,), np.uint8)
    rgbe[..., :3] = np.clip(a * sc[..., None], 0, 255).astype(np.uint8)
    rgbe[..., 3] = np.where(nz, e + 128, 0).astype(np.uint8)
    with open(path, "wb") as f:
        f.write(b"#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y %d +X %d\n" % (H, W)); f.write(rgbe.tobytes())
write_hdr(sys.argv[1] if len(sys.argv) > 1 else "studio.hdr", img)
print("ok")
