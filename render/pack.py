"""Pack rendered frames.  python pack.py <frames_dir> <out_dir> <name>
Writes  <name>_0.webp, <name>_1.webp  HD sheets (4x4 frames each, frames 0-15 and 16-31)
        <name>_s.webp                small sheet (8 columns, 200px frames) for cards
        <name>.preview.webp          small animated preview
        <name>.json                  layout"""
import glob, json, os, sys
from PIL import Image
src, out, name = sys.argv[1], sys.argv[2], sys.argv[3]
fs = sorted(glob.glob(os.path.join(src, "*.png")))
ims = [Image.open(f).convert("RGB") for f in fs]
n = len(ims); w, h = ims[0].size
os.makedirs(out, exist_ok=True)
per = 16; hc = 4
parts = (n + per - 1) // per
for p in range(parts):
    chunk = ims[p * per:(p + 1) * per]
    rows = (len(chunk) + hc - 1) // hc
    sheet = Image.new("RGB", (hc * w, rows * h))
    for i, im in enumerate(chunk): sheet.paste(im, ((i % hc) * w, (i // hc) * h))
    sheet.save(os.path.join(out, "%s_%d.webp" % (name, p)), quality=86, method=6)
sw = 200; sc = 8
small = [im.resize((sw, sw), Image.LANCZOS) for im in ims]
srows = (n + sc - 1) // sc
ss = Image.new("RGB", (sc * sw, srows * sw))
for i, im in enumerate(small): ss.paste(im, ((i % sc) * sw, (i // sc) * sw))
ss.save(os.path.join(out, name + "_s.webp"), quality=80, method=6)
small[0].save(os.path.join(out, name + ".preview.webp"), save_all=True, append_images=small[1:], duration=75, loop=0, quality=72)
json.dump({"frames": n, "hd": {"size": w, "cols": hc, "perSheet": per, "sheets": parts}, "small": {"size": sw, "cols": sc}},
          open(os.path.join(out, name + ".json"), "w"))
print(name, n, "frames", parts, "hd sheets")
