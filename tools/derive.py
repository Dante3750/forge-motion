"""From the HD sheets, build sharper card sheets (360px frames) and HD list thumbnails.
python tools/derive.py <media_dir>"""
import glob, os, sys
from PIL import Image
v3 = os.path.join(sys.argv[1], "v3")
n = 0
for p0 in sorted(glob.glob(os.path.join(v3, "*_0.webp"))):
    base = p0[:-7]
    p1 = base + "_1.webp"
    if not os.path.exists(p1): continue
    frames = []
    for p in (p0, p1):
        s = Image.open(p).convert("RGB"); w = s.width // 4
        for i in range((s.height // w) * 4): frames.append(s.crop(((i % 4) * w, (i // 4) * w, (i % 4 + 1) * w, (i // 4 + 1) * w)))
    cw, cols = 360, 8
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * cw))
    for i, f in enumerate(frames): sheet.paste(f.resize((cw, cw), Image.LANCZOS), ((i % cols) * cw, (i // cols) * cw))
    sheet.save(base + "_s.webp", quality=84, method=6)
    if not base.endswith("_b"):
        frames[len(frames) // 3].resize((480, 480), Image.LANCZOS).save(base + "_t.webp", quality=86, method=6)
    n += 1
print("derived", n)
