import math, os, sys, time, json
from mathutils import Vector, Matrix, Quaternion

LIMB_KEYS = ("hands", "feet")
KEYFRAME_HOOK = None  # export mode: called per frame instead of rendering

def lerp(a, b, t, key=None):
    if isinstance(a, dict) and key in LIMB_KEYS:
        # hands/feet swing around the shoulder/hip instead of travelling in a straight line
        return {s: (a[s] if a[s] == b.get(s, a[s]) else ("mix", a[s], b.get(s, a[s]), t)) for s in a}
    if isinstance(a, dict) and key is None:
        out = {}
        for k in a:
            out[k] = lerp(a[k], b[k], t, k if k in LIMB_KEYS else "_") if k in b else a[k]
        for k in b:
            if k not in a: out[k] = b[k]
        return out
    if isinstance(a, dict):
        return {k: lerp(a[k], b.get(k, a[k]), t) if k in b else a[k] for k in a} | {k: b[k] for k in b if k not in a}
    ta = isinstance(a, tuple) and len(a) >= 2 and isinstance(a[0], str)
    tb = isinstance(b, tuple) and len(b) >= 2 and isinstance(b[0], str)
    if ta and tb and a[0] == b[0] and a[0] != "mix":
        return (a[0], lerp(a[1], b[1], t))
    if ta or tb:
        return ("mix", a, b, t)
    if isinstance(a, (tuple, list)):
        return tuple(lerp(x, y, t) for x, y in zip(a, b))
    if isinstance(a, (int, float)):
        return a + (b - a) * t
    return a

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * t)

def bezier_ease(x, x1, x2):
    """CSS-style cubic-bezier(x1, 0, x2, 1): x1/x2 set how gently the move leaves / arrives."""
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    u = x
    for _ in range(8):
        bx = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3
        dx = 3 * (1 - u) ** 2 * x1 + 6 * (1 - u) * u * (x2 - x1) + 3 * u * u * (1 - x2)
        if abs(dx) < 1e-6: break
        u = min(max(u - (bx - x) / dx, 0.0), 1.0)
    return 3 * (1 - u) * u * u + u ** 3

# How each kind of key is passed through. A lockout (standing tall, arms straight) is a real stop:
# the body settles and pauses. A turnaround (bottom of a squat, top of a curl) is a quick reversal:
# no dead stop, the muscles load and change direction - that rhythm is what reads as "human".
FEEL = {
    "lift":    {"lock": (0.58, 0.10), "turn": (0.30, 0.025)},
    "rhythm":  {"lock": (0.30, 0.0), "turn": (0.30, 0.0)},
    "stretch": {"lock": (0.62, 0.16), "turn": (0.62, 0.16)},
}

def pose_at(keys, t, tempo=None, hold=None, style="lift"):
    """keys: poses visited in order and back to the first (loop). t in [0,1). keys[0] is the start/lockout
    position, the others are turnarounds. tempo: relative duration of each segment."""
    n = len(keys)
    if n == 1: return keys[0]
    seq = keys + [keys[0]] if n > 2 else [keys[0], keys[1], keys[0]]
    segs = len(seq) - 1
    w = list(tempo) if tempo and len(tempo) == segs else [1.0] * segs
    feel = FEEL.get(style, FEEL["lift"])
    def kind(i): return "lock" if i % (segs) == 0 else "turn"
    tot = sum(w); acc = 0.0
    for i in range(segs):
        d = w[i] / tot
        if t < acc + d or i == segs - 1:
            x = min(max((t - acc) / d, 0.0), 1.0)
            s0, h0 = feel[kind(i)]; s1, h1 = feel[kind(i + 1)]
            if hold is not None: h0 = h1 = hold
            x = min(max((x - h0) / (1 - h0 - h1), 0.0), 1.0)
            return lerp(seq[i], seq[i + 1], bezier_ease(x, s0, 1 - s1))
        acc += d
    return seq[-1]

# Overlapping action: in a real body the hips start the movement, the trunk follows, and the loose ends
# (hands, head) arrive a beat later. Fractions of the loop; negative = later.
PHASE = {"pelvis": 0.022, "pelvis_tilt": 0.018, "torso": 0.008, "torso_side": 0.008,
         "head": -0.03, "head_side": -0.03,
         "hands": -0.018, "elbow": -0.018, "palm": -0.018, "wrist_dir": -0.018, "grip": -0.012, "shrug": -0.01,
         "feet": -0.01, "knee": -0.01, "foot_pitch": -0.01}
NO_BAL = ("pullbar", "dipbars", "cable", "bench", "swissball", "roller")
LOAD = {"barbell": 0.55, "ezbar": 0.25, "dumbbells": 0.2, "dumbbells_R": 0.1, "dumbbell": 0.18,
        "kettlebell": 0.18, "kettlebells": 0.3, "medball": 0.06}

def frame_pose(spec, t):
    """The pose at loop time t with the human layer on top: staggered body parts, a slightly unequal
    left/right side, breathing, small postural sway and (via _bal) centre-of-mass balance."""
    keys, tempo = spec["keys"], spec.get("tempo")
    style = spec.get("style", "lift")
    planted = any(k.get("plant") for k in keys)
    props = spec.get("props", [])
    rigid = planted or any(k.get("pelvis_tilt", 0) <= -60 or k.get("lie") for k in keys)
    cache = {}
    def at(dt):
        if dt not in cache: cache[dt] = pose_at(keys, (t + dt) % 1.0, tempo, style=style)
        return cache[dt]
    P = dict(at(0.0))
    for key, dt in PHASE.items():
        if key not in P: continue
        if rigid and key in ("pelvis", "pelvis_tilt", "torso", "hands", "elbow", "feet", "knee", "foot_pitch"): continue
        src = at(round(dt, 4))
        if key in src: P[key] = src[key]
    # the two sides of a body never move in perfect lockstep (only when the hands are not tied by one bar)
    if not rigid and "hands" in P and not ({"barbell", "ezbar", "dumbbell", "kettlebell", "medball"} & set(props)):
        lagL = at(round(PHASE["hands"] - 0.012, 4))
        P["hands"] = dict(P["hands"]); P["hands"]["L"] = lagL["hands"]["L"]
        if "elbow" in P and "elbow" in lagL: P["elbow"] = dict(P["elbow"]); P["elbow"]["L"] = lagL["elbow"]["L"]
    br = math.sin(2 * math.pi * t)
    P["torso"] = P.get("torso", 0.0) + 0.8 * br
    P["head"] = P.get("head", 0.0) + 0.7 * math.sin(2 * math.pi * t + 1.0) + 0.4 * math.sin(4 * math.pi * t + 0.3)
    if not rigid and "pelvis" in P and not spec.get("nobal"):
        p = P["pelvis"]
        if not (isinstance(p, tuple) and isinstance(p[0], str)):
            P["pelvis"] = (p[0] + 0.004 * math.sin(2 * math.pi * t + 0.7), p[1], p[2])
    if spec.get("air"):
        # airborne moves: a ballistic hop between the two landings (whole body leaves the floor)
        segs = 2 if len(keys) == 2 else len(keys)
        ph = (t * segs) % 1.0
        P["_lift"] = spec["air"] * max(0.0, math.sin(math.pi * min(max((ph - 0.12) / 0.76, 0), 1)))
    if not planted and not spec.get("nobal") and not (set(NO_BAL) & set(props)) and not spec.get("benches") and not spec.get("follow"):
        P["_bal"] = max([LOAD.get(p, 0.0) for p in props] + [0.0])
    return P

# ---------- props ----------
def pmat(name, col, rough=0.35, metal=0.0):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    return m

def cyl(r, depth, mat, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts)
    o = bpy.context.object; o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o

def box(size, loc, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
    o.scale = size; o.data.materials.append(mat)
    bev = o.modifiers.new("b", "BEVEL"); bev.width = 0.015; bev.segments = 3
    return o

def join(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); return bpy.context.object

def make_barbell(plates=True):
    steel = pmat("steel", (0.75, 0.76, 0.78), 0.25, 1.0)
    rub = pmat("plate", (0.02, 0.022, 0.025), 0.6)
    accent = pmat("plate_acc", (0.55, 0.85, 0.05), 0.5)
    parts = [cyl(0.0145, 2.0, steel)]
    for sx in (-1, 1):
        sl = cyl(0.025, 0.42, steel); sl.location.z = sx * 0.78; parts.append(sl)
        if plates:
            for i, w in enumerate((0.055, 0.04)):
                pl = cyl(0.225 if i == 0 else 0.19, w, rub, 64); pl.location.z = sx * (0.62 + i * 0.05 + w / 2); parts.append(pl)
            rim = cyl(0.226, 0.012, accent, 64); rim.location.z = sx * 0.615; parts.append(rim)
        col = cyl(0.04, 0.03, steel); col.location.z = sx * 0.57; parts.append(col)
    o = join(parts)
    o.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    return o

def make_dumbbell():
    steel = pmat("steel", (0.75, 0.76, 0.78), 0.25, 1.0)
    rub = pmat("plate", (0.02, 0.022, 0.025), 0.6)
    parts = [cyl(0.016, 0.30, steel)]
    for sx in (-1, 1):
        h = cyl(0.07, 0.07, rub, 6); h.location.z = sx * 0.115; parts.append(h)
    o = join(parts); o.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    return o

def make_bench(y0=0.0, length=1.2, height=0.45, incline=0.0, x0=0.0, rot=0.0, back=None):
    pad = pmat("pad", (0.015, 0.016, 0.018), 0.55)
    fr = pmat("frame", (0.08, 0.085, 0.09), 0.35, 0.8)
    parts = [box((0.30, length, 0.08), (0, y0, height - 0.04), pad)]
    for yy in (y0 - length / 2 + 0.12, y0 + length / 2 - 0.12):
        parts.append(box((0.05, 0.05, height - 0.08), (0, yy, (height - 0.08) / 2), fr))
        parts.append(box((0.42, 0.06, 0.04), (0, yy, 0.02), fr))
    o = join(parts)
    if back is not None:
        bp = box((0.30, 0.08, 0.75), (0, 0, 0), pad)
        bp.rotation_euler.x = -math.radians(back[0]); bp.location = back[1]
    o.location.x = x0; o.rotation_euler.z = math.radians(rot)
    return o

def make_pullbar(z=2.15):
    steel = pmat("steel", (0.75, 0.76, 0.78), 0.25, 1.0)
    fr = pmat("frame", (0.08, 0.085, 0.09), 0.35, 0.8)
    b = cyl(0.016, 1.3, steel); b.rotation_euler = (0, math.radians(90), 0); b.location = (0, 0, z)
    posts = []
    for sx in (-1, 1):
        p = box((0.06, 0.06, z + 0.1), (sx * 0.62, 0, (z + 0.1) / 2), fr); posts.append(p)
    return [b] + posts

def make_kettlebell():
    iron = pmat("iron", (0.025, 0.026, 0.028), 0.45, 0.6)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.095, segments=48, ring_count=24, location=(0, 0, -0.14)); b = bpy.context.object
    b.data.materials.append(iron); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.013, location=(0, 0, -0.03), rotation=(math.radians(90), 0, 0)); t = bpy.context.object
    t.scale = (1, 1.15, 1); t.data.materials.append(iron); bpy.ops.object.shade_smooth()
    o = join([b, t])
    bpy.context.scene.cursor.location = (0, 0, 0); bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return o

def make_ball(r, col):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=48, ring_count=24); b = bpy.context.object
    b.data.materials.append(pmat("ball%.2f" % r, col, 0.55)); bpy.ops.object.shade_smooth(); return b

def make_box(h=0.5, y=-0.55):
    return box((0.6, 0.45, h), (0, y, h / 2), pmat("boxm", (0.04, 0.035, 0.03), 0.7))

def make_dipbars():
    fr = pmat("frame", (0.08, 0.085, 0.09), 0.35, 0.8); steel = pmat("steel", (0.75, 0.76, 0.78), 0.25, 1.0)
    parts = []
    for sx in (-1, 1):
        b = cyl(0.02, 0.6, steel); b.rotation_euler = (math.radians(90), 0, 0); b.location = (sx * 0.30, -0.1, 1.25); parts.append(b)
        for yy in (-0.38, 0.18): parts.append(box((0.05, 0.05, 1.25), (sx * 0.30, yy, 0.625), fr))
    return parts

def make_cable(z=1.9, y=-0.9, x=0.0):
    y = y + (-0.08 if y <= 0 else 0.08)
    fr = pmat("frame", (0.08, 0.085, 0.09), 0.35, 0.8)
    post = box((0.12, 0.12, 2.2), (x, y, 1.1), fr)
    return post

def make_roller():
    o = cyl(0.075, 0.9, pmat("roller", (0.02, 0.025, 0.03), 0.8)); o.rotation_euler = (0, math.radians(90), 0); return o

def make_mat():
    m = pmat("mat", (0.012, 0.013, 0.015), 0.9)
    return box((0.65, 1.9, 0.012), (0, 0.0, 0.006), m)

# ---------- driver ----------
_cable = {}
def cable_line(P, poser, spec):
    if "cable" not in spec.get("props", []): return
    pul = spec.get("pulley", (0, -0.85, 1.95))
    lines = []
    if isinstance(pul, dict):
        for s in ("L", "R"): lines.append((Vector(pul[s]), grip_point(poser, s), s))
    else:
        lines.append((Vector(pul), (grip_point(poser, "L") + grip_point(poser, "R")) / 2, "C"))
    for pv, tgt, key in lines:
        d = tgt - pv
        if key not in _cable:
            _cable[key] = cyl(0.004, 1.0, pmat("cablem", (0.02, 0.02, 0.02), 0.4), 12)
            _cable[key + "h"] = cyl(0.016, 0.16 if key == "C" else 0.10, pmat("steel", (0.75, 0.76, 0.78), 0.25, 1.0))
            if key != "C": make_cable(z=pv.z, y=pv.y, x=pv.x)
        _cable[key].matrix_world = Matrix.Translation(pv + d / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4() @ Matrix.Diagonal((1, 1, d.length, 1))
        _cable[key + "h"].matrix_world = Matrix.Translation(tgt) @ Vector((0, 0, 1)).rotation_difference(Vector((1, 0, 0))).to_matrix().to_4x4()

def grip_point(poser, s):
    M = poser.posed["wrist." + s]
    return M.translation + (M.to_3x3() @ Vector((0, 1, 0))).normalized() * 0.075

CAMS = {
    "side": ((3.4, -1.5, 1.05), (0, 0.05, 0.78), 50),
    "side_low": ((3.4, -1.3, 0.75), (0, 0.15, 0.55), 50),
    "front34": ((2.2, -3.0, 1.2), (0, 0, 0.85), 50),
    "front": ((0.6, -3.6, 1.2), (0, 0, 0.9), 50),
    "lying": ((2.6, -2.2, 1.5), (0, 0.15, 0.45), 45),
    "hang": ((2.5, -3.1, 1.75), (0, 0, 1.30), 40),
    "side_hang": ((3.6, -1.1, 1.6), (0, 0.05, 1.30), 40),
    "front34_low": ((1.9, -2.9, 0.95), (0, 0.10, 0.38), 45),
    "lying_b": ((2.3, 2.3, 1.7), (0, 0.15, 0.62), 45),
    "bar34": ((2.4, -2.7, 1.25), (0, 0.05, 0.85), 48),
    "floor": ((3.0, -1.6, 1.1), (0, 0.15, 0.3), 45),
    "front_low": ((1.0, -3.4, 0.9), (0, 0, 0.7), 48),
    "back34": ((2.4, 2.6, 1.3), (0, 0.0, 0.9), 48),
}

ALT = {"side": "front34", "front34": "side", "bar34": "side", "lying": "lying_b", "floor": "front34_low", "front": "side",
       "hang": "side_hang", "side_low": "front34", "front_low": "side", "back34": "side"}

FRAME_BONES = ("root", "spine03", "spine01", "neck01", "head", "upperarm01.L", "upperarm01.R", "lowerarm01.L", "lowerarm01.R",
               "wrist.L", "wrist.R", "upperleg01.L", "upperleg01.R", "lowerleg01.L", "lowerleg01.R", "foot.L", "foot.R")

def fit_camera(cam, preset, pts, margin=0.84):
    """Keep the preset's viewing direction and lens, but move/aim the camera so every point fills the frame."""
    cl, ct, lens = preset
    d = (Vector(cl) - Vector(ct)).normalized()
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    t = (lo + hi) / 2
    up0 = Vector((0, 0, 1))
    R = d.cross(up0).normalized(); U = R.cross(d).normalized()
    R = -R
    k = math.tan(math.atan(18.0 / lens)) * margin
    need = 0.5
    for p in pts:
        r = p - t
        need = max(need, abs(r.dot(R)) / k + r.dot(d), abs(r.dot(U)) / k + r.dot(d))
    cam.data.lens = lens
    aim(cam, tuple(t + d * need), tuple(t))

def render_pattern(name, spec, female, outdir, frames=24, res=400, samples=24, only=None, angles=("a",)):
    h, rig = make_human(female)
    cam = stage(female)
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = res; sc.cycles.samples = samples
    poser = Poser(rig)
    props = spec.get("props", [])
    bar = make_barbell(spec.get("plates", True)) if "barbell" in props else None
    if bar is not None and not spec.get("plates", True): bar.scale = (0.62, 1, 1)
    if "pullbar" in props:
        for o in make_pullbar(spec.get("pullbar_z", 2.15)): pass
    ez = make_barbell(False) if "ezbar" in props else None
    dbs = [make_dumbbell(), make_dumbbell()] if "dumbbells" in props else []
    if "dumbbells_R" in props: dbs = [None, make_dumbbell()]
    if "bench" in props: make_bench(**spec.get("bench", {}))
    if "mat" in props: make_mat()
    if "box" in props: make_box(**spec.get("box", {}))
    if "dipbars" in props: make_dipbars()
    if "cable" in props and not isinstance(spec.get("pulley"), dict):
        pv = spec.get("pulley", (0, -0.85, 1.95)); make_cable(z=pv[2], y=pv[1] - 0.08 * (1 if pv[1] <= 0 else -1), x=pv[0])
    kbs = [make_kettlebell() for _ in range(2 if "kettlebells" in props else 1 if "kettlebell" in props else 0)]
    mball = make_ball(0.12, (0.05, 0.06, 0.05)) if "medball" in props else None
    sball = make_ball(0.32, (0.08, 0.09, 0.1)) if "swissball" in props else None
    roller = make_roller() if "roller" in props else None
    for extra in spec.get("benches", []): make_bench(**extra)
    single_db = make_dumbbell() if "dumbbell" in props else None
    follows = []
    for fd in spec.get("follow", []):
        o = box(fd["size"], (0, 0, 0), pmat(fd.get("mat", "frame"), (0.08, 0.085, 0.09) if fd.get("mat", "frame") == "frame" else (0.015, 0.016, 0.018), 0.4, 0.6 if fd.get("mat", "frame") == "frame" else 0.0))
        follows.append((o, fd))
    cam_names = {"a": spec.get("cam", "side")}
    cam_names["b"] = spec.get("cam_b", ALT.get(cam_names["a"], "front34"))
    for ang in angles: os.makedirs(os.path.join(outdir, ang) if len(angles) > 1 else outdir, exist_ok=True)
    # sample the whole loop to frame it tightly
    pts = []
    for f in range(0, frames, 2):
        pose_body(poser, frame_pose(spec, f / frames))
        for b in FRAME_BONES:
            M = poser.posed[b]; pts.append(M.translation.copy())
        hb = poser.posed["head"]; pts.append(hb.translation + (hb.to_3x3() @ Vector((0, 1, 0))).normalized() * 0.26)
        for s in ("L", "R"):
            g = grip_point(poser, s); pts.append(g)
            fb = poser.posed["foot." + s]; pts.append(fb.translation + Vector((0, 0, -0.08)))
        if bar is not None or ez is not None:
            gl, gr = grip_point(poser, "L"), grip_point(poser, "R"); c = (gl + gr) / 2; ax = (gl - gr).normalized()
            half = 1.0 if spec.get("plates", True) else 0.62
            for sgn in (-1, 1):
                for dz in (-0.23, 0.23):
                    pts.append(c + ax * half * sgn + Vector((0, 0, dz if spec.get("plates", True) else 0)))
    for o in bpy.context.scene.objects:
        if o.type == "MESH" and o.name not in ("Plane",) and not o.name.startswith(("Human", "cablem")) and o.dimensions.length < 4:
            if o.parent is None and o.data.name.startswith(("Cube",)):
                pts.extend(o.matrix_world @ Vector(c) for c in o.bound_box)
    pts = [p for p in pts if p.length < 6]
    for f in range(frames):
        if only is not None and f not in only: continue
        P = frame_pose(spec, f / frames)
        pose_body(poser, P)
        gl, gr = grip_point(poser, "L"), grip_point(poser, "R")
        for o in (bar, ez):
            if o is None: continue
            c = (gl + gr) / 2; ax = (gl - gr).normalized()
            o.matrix_world = Matrix.Translation(c) @ Vector((1, 0, 0)).rotation_difference(ax).to_matrix().to_4x4()
        dbax = P.get("db_axis")
        for o, s in zip(dbs, ("L", "R")):
            if o is None: continue
            M = poser.posed["wrist." + s]
            ax = Vector(dbax).normalized() if dbax else (M.to_3x3() @ Vector((1, 0, 0))).normalized()
            o.matrix_world = Matrix.Translation(grip_point(poser, s)) @ Vector((1, 0, 0)).rotation_difference(ax).to_matrix().to_4x4()
        cable_line(P, poser, spec)
        if single_db is not None:
            ax = Vector(P.get("db_axis", (0, 0, 1))).normalized()
            single_db.matrix_world = Matrix.Translation((gl + gr) / 2 + Vector(P.get("db_off", (0, 0, 0)))) @ Vector((1, 0, 0)).rotation_difference(ax).to_matrix().to_4x4()
        for o, fd in follows:
            at = fd["at"]
            if at == "feet": c = (poser.posed["foot.L"].translation + poser.posed["foot.R"].translation) / 2
            elif at == "grip": c = (gl + gr) / 2
            elif at == "knees": c = (poser.posed["lowerleg01.L"].translation + poser.posed["lowerleg01.R"].translation) / 2
            else: c = Vector((0, 0, 0))
            o.location = c + Vector(fd.get("off", (0, 0, 0))); o.rotation_euler = tuple(math.radians(r) for r in fd.get("rot", (0, 0, 0)))
        if len(kbs) == 1:
            c = (gl + gr) / 2; kbs[0].matrix_world = Matrix.Translation(c)
        elif len(kbs) == 2:
            kbs[0].matrix_world = Matrix.Translation(gl); kbs[1].matrix_world = Matrix.Translation(gr)
        if mball is not None: mball.location = (gl + gr) / 2 + Vector(P.get("ball_off", (0, -0.06, 0)))
        if sball is not None: sball.location = Vector(P.get("sball", (0, 0.0, 0.32)))
        if roller is not None: roller.location = Vector(P.get("roller", (0, 0.4, 0.075)))
        if KEYFRAME_HOOK is not None:
            KEYFRAME_HOOK(f, rig)
            continue
        for ang in angles:
            fit_camera(cam, CAMS[cam_names[ang]], pts)
            sc.render.filepath = os.path.join(outdir, ang, "%02d.png" % f) if len(angles) > 1 else os.path.join(outdir, "%02d.png" % f)
            bpy.ops.render.render(write_still=True)
