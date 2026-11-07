"""Photo-real muscle map for the app's Explore > 3D Body tab.
python bodymap.py <m|f> <outdir> [samples]
Renders the realistic human standing, turning through 24 angles (beauty, transparent background), plus a matching
"muscle ID" image per angle in which every pixel's red value says which muscle is there. The app spins through the
frames, hit-tests taps on the ID image and paints the selected/trained muscles over the photo.
Muscle regions come from the same muscle layout the app's old body map used (metres, x right, y up, z forward)."""
import os, sys, json, math
g, outdir = sys.argv[1], os.path.abspath(sys.argv[2])
samples = int(sys.argv[3]) if len(sys.argv) > 3 else 64
female = g == "f"
os.environ["FORGE_BODYMAP"] = "1"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
exec(open("scene.py").read()); exec(open("body.py").read()); exec(open("anim.py").read()); exec(open("patterns.py").read())
import bpy, numpy as np
from mathutils import Vector
from PIL import Image

MUSCLES = ["neck", "traps", "shoulders", "chest", "abdominals", "lats", "middle back", "lower back", "glutes",
           "biceps", "triceps", "forearms", "abductors", "adductors", "quadriceps", "hamstrings", "calves"]
FRAMES = int(os.environ.get("BM_FRAMES", 24))
W, H = 540, 900

def ell(m, x, y, z, a, b, c): return ("e", m, (x, y, z), (a, b, c))
def cap(m, x1, y1, z1, x2, y2, z2, r): return ("c", m, (x1, y1, z1), (x2, y2, z2), r)
def sym(f): return [f(1.0), f(-1.0)]
parts = []
parts += [cap("neck", 0, 1.60, .005, 0, 1.53, .005, .046)]
parts += sym(lambda s: ell("traps", s * .075, 1.51, -.03, .075, .045, .055))
parts += sym(lambda s: ell("shoulders", s * .215, 1.45, 0, .062, .065, .062))
parts += sym(lambda s: ell("chest", s * .075, 1.35, .065, .082, .065, .05))
parts += [ell("abdominals", 0, 1.24, .082, .075, .045, .03), ell("abdominals", 0, 1.15, .082, .075, .045, .03),
          ell("abdominals", 0, 1.06, .082, .07, .045, .03)]
parts += sym(lambda s: ell("abdominals", s * .125, 1.14, .05, .034, .10, .04))
parts += sym(lambda s: ell("lats", s * .135, 1.30, -.07, .062, .13, .045))
parts += [ell("middle back", 0, 1.34, -.09, .09, .06, .03), ell("lower back", 0, 1.10, -.085, .09, .06, .03)]
parts += sym(lambda s: ell("glutes", s * .075, .94, -.075, .08, .08, .06))
parts += sym(lambda s: ell("biceps", s * .252, 1.30, .035, .04, .085, .034))
parts += sym(lambda s: ell("triceps", s * .252, 1.30, -.035, .04, .085, .034))
parts += sym(lambda s: cap("forearms", s * .272, 1.16, 0, s * .312, .93, 0, .033))
parts += sym(lambda s: ell("abductors", s * .165, .96, 0, .04, .07, .05))
parts += sym(lambda s: ell("adductors", s * .045, .74, 0, .04, .10, .045))
parts += sym(lambda s: ell("quadriceps", s * .088, .72, .048, .062, .165, .045))
parts += sym(lambda s: ell("hamstrings", s * .088, .72, -.048, .062, .165, .045))
parts += sym(lambda s: ell("calves", s * .09, .33, -.038, .046, .10, .04))

h, rig = make_human(female)
poser = Poser(rig)
k = rig.data.bones["head"].tail_local.z / 1.734
# neutral stance: feet under the hips, arms hanging a little away from the body so every muscle shows
base = dict(P["curl_db"]["keys"][0])
base.pop("hands", None); base.pop("elbow", None); base.pop("palm", None); base.pop("grip", None)
base["hands"] = {"L": ("hang", (0.085, 0.01, -0.52)), "R": ("hang", (-0.085, 0.01, -0.52))}
base["palm"] = {"L": 40, "R": 40}
base["grip"] = {"L": 0.15, "R": 0.15}
base["feet"] = {"L": (0.115, -0.01, 0.075), "R": (-0.115, -0.01, 0.075)}
base["toes"] = {"L": 10, "R": 10}
pose_body(poser, base)
bpy.context.view_layer.update()

# --- which muscle is under each face of the (posed) body ---
sub = h.modifiers.get("sub")
# evaluate with only the armature on, so vertex indices match the mesh (masks remove hidden-under-clothes verts)
was = {m.name: m.show_viewport for m in h.modifiers}
for m in h.modifiers: m.show_viewport = m.type == "ARMATURE"
dg = bpy.context.evaluated_depsgraph_get()
ev = h.evaluated_get(dg); me = ev.to_mesh()
mw = h.matrix_world
V = np.array([tuple(mw @ v.co) for v in me.vertices], np.float32)
ev.to_mesh_clear()
for m in h.modifiers: m.show_viewport = was[m.name]
# Blender (x, y fwd=-y, z up) -> map frame (x, y up, z fwd)
Q = np.stack([V[:, 0], V[:, 2] / k, -V[:, 1] / k], 1)
Q[:, 0] /= k
# only real skin (not the hidden helper meshes) and the torso centred front-to-back like the muscle layout
vg = h.vertex_groups["body"]
inb = np.zeros(len(V), bool)
for v in h.data.vertices:
    for ge in v.groups:
        if ge.group == vg.index and ge.weight > 0.5: inb[v.index] = True
band = inb & (Q[:, 1] > 1.0) & (Q[:, 1] < 1.4) & (np.abs(Q[:, 0]) < 0.12)
Q[:, 2] -= 0.5 * (Q[band, 2].max() + Q[band, 2].min())
best = np.full(len(Q), 9.0, np.float32); bid = np.zeros(len(Q), np.int32)
for p in parts:
    mid = MUSCLES.index(p[1]) + 1
    if p[0] == "e":
        c = np.array(p[2]); ax = np.array(p[3]) * np.array([1.9, 1.35, 2.6])
        d = np.sqrt((((Q - c) / ax) ** 2).sum(1))
    else:
        a = np.array(p[2]); b = np.array(p[3]); r = p[4] * 2.0
        ab = b - a; t = np.clip(((Q - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(Q - (a + t[:, None] * ab), axis=1) / r
    upd = d < best
    best[upd] = d[upd]; bid[upd] = mid
bid[(best > 2.2) | ~inb] = 0
gl = bid == MUSCLES.index("glutes") + 1
front_gl = gl & (Q[:, 2] > -0.03)
bid[front_gl] = np.where(np.abs(Q[front_gl, 0]) > 0.11, MUSCLES.index("abductors") + 1, MUSCLES.index("abdominals") + 1)
# legs: front vs back measured from each leg's own centre line at that height
def leg_front(mask):
    out = np.zeros(len(Q), np.float32)
    for sx in (-1, 1):
        for y0 in np.arange(0.0, 1.0, 0.04):
            sel = mask & inb & (np.sign(Q[:, 0]) == sx) & (Q[:, 1] >= y0) & (Q[:, 1] < y0 + 0.04)
            if sel.sum() < 4: continue
            mid = 0.5 * (Q[sel, 2].max() + Q[sel, 2].min())
            out[sel] = Q[sel, 2] - mid
    return out
legs = (Q[:, 1] < 0.90) & (np.abs(Q[:, 0]) < 0.21)
fr = leg_front(legs)
low = legs & (Q[:, 1] < 0.50)
bid[low] = np.where(fr[low] < 0.0, MUSCLES.index("calves") + 1, 0)
thigh = legs & (Q[:, 1] >= 0.50) & np.isin(bid, [MUSCLES.index(m) + 1 for m in ("hamstrings", "quadriceps", "calves")])
bid[thigh] = np.where(fr[thigh] < -0.005, MUSCLES.index("hamstrings") + 1, MUSCLES.index("quadriceps") + 1)
for i, m in enumerate(MUSCLES):
    sel = bid == i + 1
    if sel.any(): print("MUS", m, sel.sum(), Q[sel].mean(0).round(3))
print("Q range", Q.min(0).round(2), Q.max(0).round(2))
if os.environ.get("BM_DEBUG"):
    vg = h.vertex_groups.get("body"); print("groups", [g.name for g in h.vertex_groups][:12], len(h.vertex_groups))
    print("mods", [(m.name, m.type, getattr(m, "vertex_group", None), getattr(m, "invert_vertex_group", None)) for m in h.modifiers])
    if vg:
        inb = np.zeros(len(V), bool)
        for v in h.data.vertices:
            for ge in v.groups:
                if ge.group == vg.index and ge.weight > 0.5: inb[v.index] = True
        for i, m in enumerate(MUSCLES):
            sel = bid == i + 1; print("in body", m, sel.sum(), (sel & inb).sum())
    sys.exit(0)
wl = poser.posed["wrist.L"].translation.z; head_z = poser.posed["neck01"].translation.z + 0.05 * k
bid[(V[:, 2] < wl) & (np.abs(Q[:, 0]) > 0.21)] = 0                                    # hands
bid[V[:, 2] > head_z + 0.06 * k] = 0                                                  # head
bid[V[:, 2] < 0.12 * k] = 0                                                           # feet
fid = np.zeros(len(h.data.polygons), np.int32)
for i, poly in enumerate(h.data.polygons):
    ids = [bid[v] for v in poly.vertices]
    fid[i] = max(set(ids), key=ids.count)
attr = h.data.attributes.get("mus") or h.data.attributes.new("mus", "FLOAT_COLOR", "FACE")
def srgb_to_lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
for i, f in enumerate(fid):
    r = srgb_to_lin(f * 12 / 255.0)
    attr.data[i].color = (r, 0.0, 0.0, 1.0)

# --- stage: transparent background, studio key + rims, fixed camera, body turns ---
sc = bpy.context.scene
cam = stage(female)
for o in list(sc.objects):
    if o.type == "MESH" and o.name.startswith("Plane"): bpy.data.objects.remove(o)
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = W, H
cam.data.lens = 50; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24
aim(cam, (0, -5.0 * k, 0.93 * k), (0, 0, 0.90 * k))
cam.data.lens = 50 * (5.0 * k) / (2.0 * 0.98 * k / (24 / 50)) if False else 50
# fit: vertical fov = 2 atan(12/50) -> height covered at distance d = 2 d * 12/50; we want ~1.95 m * k
d = 1.98 * k / (2 * 12 / 50)
aim(cam, (0, -d - 0.0, 0.92 * k), (0, 0, 0.92 * k))
os.makedirs(outdir, exist_ok=True)
pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
rig.parent = pivot

others = [o for o in sc.objects if o.type == "MESH" and o != h]
idmat = bpy.data.materials.new("idpass"); idmat.use_nodes = True
N = idmat.node_tree.nodes; L = idmat.node_tree.links
for n in list(N): N.remove(n)
at = N.new("ShaderNodeAttribute"); at.attribute_name = "mus"; at.attribute_type = "GEOMETRY"
em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
outn = N.new("ShaderNodeOutputMaterial")
L.new(at.outputs["Color"], em.inputs["Color"]); L.new(em.outputs["Emission"], outn.inputs["Surface"])

def beauty_mode():
    sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.filter_size = 1.5
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_layers[0].material_override = None
    for o in others: o.hide_render = False
    for m in h.modifiers:
        if m.type == "MASK" and m.name.startswith("Delete."): m.show_render = True
def id_mode():
    sc.cycles.samples = 1; sc.cycles.use_denoising = False
    sc.render.filter_size = 0.01
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
    sc.view_settings.exposure = 0; sc.view_settings.gamma = 1
    sc.view_layers[0].material_override = idmat
    for o in others: o.hide_render = True
    for m in h.modifiers:   # the muscle map needs the skin that clothes normally hide
        if m.type == "MASK" and m.name.startswith("Delete."): m.show_render = False
    if sub: sub.render_levels = 0

for f in range(FRAMES):
    pivot.rotation_euler = (0, 0, math.radians(360.0 * f / FRAMES))
    beauty_mode()
    if sub: sub.render_levels = 2
    sc.render.filepath = os.path.join(outdir, "b%02d.png" % f); bpy.ops.render.render(write_still=True)
    id_mode()
    sc.render.filepath = os.path.join(outdir, "i%02d.png" % f); bpy.ops.render.render(write_still=True)
    print("FRAME", f, flush=True)

# pack: 6 x 4 sheets
cols, rows = 6, 4
bs = Image.new("RGBA", (W * cols, H * rows)); ms = Image.new("L", (W * cols, H * rows))
for f in range(FRAMES):
    x, y = (f % cols) * W, (f // cols) * H
    bs.paste(Image.open(os.path.join(outdir, "b%02d.png" % f)).convert("RGBA"), (x, y))
    im = np.asarray(Image.open(os.path.join(outdir, "i%02d.png" % f)).convert("RGBA")).astype(np.int32)
    idv = np.where(im[..., 3] > 127, np.clip(np.rint(im[..., 0] / 12.0), 0, len(MUSCLES)), 0).astype(np.uint8)
    ms.paste(Image.fromarray(idv, "L"), (x, y))
bs.save(os.path.join(outdir, "bodymap_%s.webp" % g), quality=86, method=6)
ms.save(os.path.join(outdir, "bodymask_%s.png" % g), optimize=True)
json.dump({"muscles": MUSCLES, "frames": FRAMES, "cols": cols, "w": W, "h": H}, open(os.path.join(outdir, "bodymap.json"), "w"))
print("BODYMAP DONE")
