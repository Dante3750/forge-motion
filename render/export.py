"""Export one movement as a self-contained animated 3D model (GLB) for the in-app 3D viewer.
python export.py <movement> <m|f> <out.glb> [frames]
The human, clothes, hair and equipment are baked into simple PBR materials that any glTF viewer can draw."""
import os, sys, json, struct
args = sys.argv[1:]
name, g, out = args[0], args[1], os.path.abspath(args[2])
frames = int(args[3]) if len(args) > 3 else 40
os.chdir(os.path.dirname(os.path.abspath(__file__)))
TEXDIR = os.path.abspath(os.path.join(os.path.dirname(out), "_tex_" + g))
os.makedirs(TEXDIR, exist_ok=True)
exec(open("scene.py").read()); exec(open("body.py").read()); exec(open("anim.py").read()); exec(open("patterns.py").read())
import numpy as np
from PIL import Image

def _lin(a): return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
def _srgb(a): a = np.clip(a, 0, 1); return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)

def bake(fx, key, size):
    """Bake the look's colour tweaks into a plain texture (cached per look)."""
    keep_alpha = fx["kind"] == "hair"
    path = os.path.join(TEXDIR, key + (".png" if keep_alpha else ".jpg"))
    if os.path.exists(path): return path
    im = Image.open(fx["tex"]); has_a = im.mode == "RGBA" and keep_alpha
    im = im.convert("RGBA").resize((size, size), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    rgb = _lin(a[..., :3]); v = rgb.max(axis=2, keepdims=True)
    if fx["kind"] == "skin":
        h, s, val = fx["hsv"]
        rgb = (v - (v - rgb) * s) * val
    else:
        rgb = (v - (v - rgb) * fx["keep"]) * np.array(fx["col"], dtype=np.float32)
    outa = np.concatenate([_srgb(rgb), a[..., 3:4]], axis=2) if has_a else _srgb(rgb)
    img = Image.fromarray((outa * 255).round().astype(np.uint8), "RGBA" if has_a else "RGB")
    img.save(path, quality=88) if path.endswith(".jpg") else img.save(path)
    return path

def plain(name, base=None, color=(0.8, 0.8, 0.8), normal=None, rough=0.6, metal=0.0, alpha=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; L = m.node_tree.links; p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    if base:
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(base, check_existing=True)
        L.new(t.outputs["Color"], p.inputs["Base Color"])
        if alpha: L.new(t.outputs["Alpha"], p.inputs["Alpha"])
    else:
        p.inputs["Base Color"].default_value = (*color, 1)
    if normal and os.path.exists(normal):
        nim = os.path.join(TEXDIR, os.path.basename(normal))
        if not os.path.exists(nim): Image.open(normal).convert("RGB").resize((1024, 1024), Image.LANCZOS).save(nim)
        tn = N.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(nim, check_existing=True); tn.image.colorspace_settings.name = "Non-Color"
        nm = N.new("ShaderNodeNormalMap"); L.new(tn.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], p.inputs["Normal"])
    if alpha:
        try: m.surface_render_method = "DITHERED"
        except Exception: pass
    return m

def eye_materials(o):
    """Eyes: glossy white sclera with a dark brown iris on the front of each eyeball."""
    white = plain("eye_white_gl", color=(0.82, 0.8, 0.78), rough=0.15)
    iris = plain("eye_iris_gl", color=(0.03, 0.015, 0.008), rough=0.1)
    o.data.materials.clear(); o.data.materials.append(white); o.data.materials.append(iris)
    co = [v.co for v in o.data.vertices]
    cy = min(v.y for v in co)
    for p in o.data.polygons:
        vy = sum(co[i].y for i in p.vertices) / len(p.vertices)
        p.material_index = 1 if vy < cy + 0.006 else 0

def convert_materials(human_objs):
    for o in human_objs:
        if o.type != "MESH": continue
        if "high-poly" in o.name or "low-poly" in o.name:
            eye_materials(o); continue
        for i, m in enumerate(list(o.data.materials)):
            if m is None: continue
            if "fx" in m.keys():
                fx = json.loads(m["fx"])
                if fx["kind"] == "fabric" and any(k in m.name.lower() for k in ("short0", "ponytail", "hair", "bob", "braid")): fx["kind"] = "hair"
                if fx.get("tex") and os.path.exists(fx["tex"]):
                    size = 2048 if fx["kind"] == "skin" else 1024
                    key = m.name.replace(".", "_")
                    base = bake(fx, key, size)
                    nm = plain(m.name + "_gl", base, normal=fx.get("normal"), rough=0.5 if fx["kind"] == "skin" else fx.get("rough", 0.75),
                               alpha=fx["kind"] == "hair")
                else:
                    nm = plain(m.name + "_gl", color=tuple(fx.get("col", (0.5, 0.5, 0.5))), rough=fx.get("rough", 0.75))
                o.data.materials[i] = nm
                continue
            # MakeHuman materials (brows, lashes, eyes): keep their diffuse image, with alpha
            imgs = [n for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and n.image.colorspace_settings.name != "Non-Color"] if m.use_nodes else []
            if imgs:
                src = bpy.path.abspath(imgs[0].image.filepath)
                im = Image.open(src); cut = any(k in m.name.lower() for k in ("eyebrow", "eyelash"))
                dst = os.path.join(TEXDIR, os.path.splitext(os.path.basename(src))[0] + (".png" if cut else ".jpg"))
                if not os.path.exists(dst):
                    im = im.resize((min(im.width, 1024), min(im.height, 1024)), Image.LANCZOS)
                    (im.save(dst) if cut else im.convert("RGB").save(dst, quality=88))
                o.data.materials[i] = plain(m.name + "_gl", dst, rough=0.6, alpha=cut)

human_set = set()
def hook(f, rig):
    for pb in rig.pose.bones:
        # the rig's bones are Euler-mode: switch to quaternions (keeping the pose) so the rotation is what gets keyed
        if pb.rotation_mode != "QUATERNION":
            mb = pb.matrix_basis.copy(); pb.rotation_mode = "QUATERNION"; pb.matrix_basis = mb
        pb.keyframe_insert("location", frame=f + 1); pb.keyframe_insert("rotation_quaternion", frame=f + 1)
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or o.name in human_set or o.parent is not None: continue
        mw = o.matrix_world.copy()
        o.rotation_mode = "QUATERNION"
        o.location, o.rotation_quaternion, o.scale = mw.to_translation(), mw.to_quaternion(), mw.to_scale()
        for path in ("location", "rotation_quaternion", "scale"): o.keyframe_insert(path, frame=f + 1)

# build the scene (posing + props) through the normal pipeline, with keyframing instead of rendering
_orig_make_human = make_human
def make_human_tracked(female):
    h, rig = _orig_make_human(female)
    for o in bpy.context.scene.objects: human_set.add(o.name)
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            for md in o.modifiers:
                if md.type == "SUBSURF": md.levels = 1
    return h, rig
make_human = make_human_tracked
KEYFRAME_HOOK = hook
render_pattern(name, P[name], g == "f", "/tmp/_unused", frames=frames, res=64, samples=1, angles=("a",))

MODE = os.environ.get("EXPORT_MODE", "anim")
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, frames
sc.render.fps = max(1, round(frames / 2.8))
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA") or o.name.startswith("Plane"):
        bpy.data.objects.remove(o, do_unlink=True)
rig_obj = next(o for o in sc.objects if o.type == "ARMATURE")
if MODE == "model":
    # rest pose, no props: the shared, cached human
    rig_obj.animation_data_clear()
    for pb in rig_obj.pose.bones: pb.matrix_basis.identity()
    for o in list(sc.objects):
        if o.name not in human_set: bpy.data.objects.remove(o, do_unlink=True)
    convert_materials([o for o in sc.objects if o.name in human_set])
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=0.02, vertices=96, location=(0, 0, -0.01))
    fl = bpy.context.object; fl.name = "floor"; fl.data.materials.append(plain("floor_gl", color=(0.02, 0.022, 0.026), rough=0.85))
else:
    # skeleton + equipment + motion only: tiny, loaded per exercise
    for o in list(sc.objects):
        if o.name in human_set and o.type == "MESH": bpy.data.objects.remove(o, do_unlink=True)
for o in sc.objects:
    if o.type == "MESH" and o.name not in human_set:
        for m in o.data.materials:
            if m and m.use_nodes and any(n.type in ("TEX_NOISE", "ATTRIBUTE") for n in m.node_tree.nodes):
                p = m.node_tree.nodes.get("Principled BSDF")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True, export_animations=(MODE != "model"), export_skins=True,
                          export_morph=False, export_image_format="AUTO", export_jpeg_quality=86, export_yup=True,
                          export_frame_range=True, export_force_sampling=True, export_optimize_animation_size=True,
                          export_lights=False, export_cameras=False, export_extras=False, use_visible=True)

# hair, brows and lashes are cut-outs: use alpha masking (sharp, no sorting artefacts)
with open(out, "rb") as fh: data = fh.read()
jl = struct.unpack("<I", data[12:16])[0]
js = json.loads(data[20:20 + jl])
for m in js.get("materials", []):
    if m.get("alphaMode") == "BLEND" or any(k in m.get("name", "").lower() for k in ("eyebrow", "eyelash", "short0", "ponytail", "hair")):
        if m.get("alphaMode"): m["alphaMode"] = "MASK"; m["alphaCutoff"] = 0.4
        m["doubleSided"] = True
nj = json.dumps(js, separators=(",", ":")).encode()
nj += b" " * ((4 - len(nj) % 4) % 4)
rest = data[20 + jl:]
total = 12 + 8 + len(nj) + len(rest)
with open(out, "wb") as fh:
    fh.write(struct.pack("<III", 0x46546C67, 2, total)); fh.write(struct.pack("<II", len(nj), 0x4E4F534A)); fh.write(nj); fh.write(rest)
print("EXPORTED", out, os.path.getsize(out) // 1024, "KB", len(js.get("animations", [])), "animations", len(js.get("meshes", [])), "meshes")
