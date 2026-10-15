"""Pack rendered frames into a sprite sheet + animated preview.  python pack.py <frames_dir> <out_dir> <name>"""
import glob, json, os, sys
from PIL import Image
src, out, name = sys.argv[1], sys.argv[2], sys.argv[3]
fs = sorted(glob.glob(os.path.join(src, "*.png")))
ims = [Image.open(f).convert("RGB") for f in fs]
n = len(ims); w, h = ims[0].size
cols = 8; rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
os.makedirs(out, exist_ok=True)
sheet.save(os.path.join(out, name + ".webp"), quality=78, method=6)
small = [im.resize((w // 2, h // 2), Image.LANCZOS) for im in ims]
small[0].save(os.path.join(out, name + ".preview.webp"), save_all=True, append_images=small[1:], duration=75, loop=0, quality=70)
json.dump({"frames": n, "cols": cols, "rows": rows, "w": w, "h": h}, open(os.path.join(out, name + ".json"), "w"))
print(name, n, os.path.getsize(os.path.join(out, name + ".webp")))
