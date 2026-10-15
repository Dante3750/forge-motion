"""Build README media from the rendered sheets: animated GIFs for a few moves and a gallery of every movement.
python tools/showcase.py <media_dir>   (media_dir has v1/ or v2/ with <move>_<g>.webp sprite sheets)"""
import glob, json, os, sys
from PIL import Image, ImageDraw, ImageFont

media = sys.argv[1]
ver = "v2" if glob.glob(os.path.join(media, "v2", "*_m.webp")) else "v1"
src = os.path.join(media, ver)
out = os.path.join(media, "showcase"); os.makedirs(out, exist_ok=True)

def frames(name):
    p = os.path.join(src, name + ".webp")
    if not os.path.exists(p): return None
    sheet = Image.open(p).convert("RGB")
    meta = json.load(open(os.path.join(src, name + ".json"))) if os.path.exists(os.path.join(src, name + ".json")) else {"frames": 32, "cols": 8, "w": sheet.width // 8, "h": sheet.width // 8}
    w, h, c = meta["w"], meta["h"], meta["cols"]
    return [sheet.crop(((i % c) * w, (i // c) * h, (i % c + 1) * w, (i // c + 1) * h)) for i in range(meta["frames"])]

def gif(names, path, size=300):
    seqs = [frames(n) for n in names]
    seqs = [s for s in seqs if s]
    if not seqs: return False
    n = min(len(s) for s in seqs)
    out_frames = []
    for i in range(n):
        W = Image.new("RGB", (size * len(seqs), size))
        for k, s in enumerate(seqs): W.paste(s[i].resize((size, size), Image.LANCZOS), (k * size, 0))
        out_frames.append(W.convert("P", palette=Image.ADAPTIVE, colors=200))
    out_frames[0].save(path, save_all=True, append_images=out_frames[1:], duration=85, loop=0, optimize=True)
    return True

HERO = [("hero_gym", ["squat_bb_m", "deadlift_bb_f", "bench_bb_m"]),
        ("hero_home", ["squat_goblet_f", "row_db_single_m", "floor_press_db_f"]),
        ("hero_bodyweight", ["pushup_m", "pike_pushup_f", "lunge_m"]),
        ("hero_angles", ["squat_goblet_f", "squat_goblet_f_b"])]
made = [n for n, ns in HERO if gif(ns, os.path.join(out, n + ".gif"))]

# gallery: one mid-rep frame of every movement (men's), labelled
names = sorted({os.path.basename(p)[:-7] for p in glob.glob(os.path.join(src, "*_m.webp"))})
cols, cell = 6, 200
rows = (len(names) + cols - 1) // cols
G = Image.new("RGB", (cols * cell, rows * (cell + 22)), (10, 11, 13))
d = ImageDraw.Draw(G)
for i, n in enumerate(names):
    fr = frames(n + "_m")
    if not fr: continue
    x, y = (i % cols) * cell, (i // cols) * (cell + 22)
    G.paste(fr[len(fr) // 3].resize((cell, cell), Image.LANCZOS), (x, y))
    d.text((x + 6, y + cell + 4), n.replace("_", " "), fill=(201, 255, 47))
G.save(os.path.join(out, "gallery.jpg"), quality=82)
print("made", made, "gallery", len(names), "from", ver)
