import os
import bpy, math, mathutils
from mathutils import Vector, Matrix
exec(open("boot.py").read())

def rest_coords(h):
    states = [(m, m.show_viewport) for m in h.modifiers]
    for m, _ in states: m.show_viewport = False
    dg = bpy.context.evaluated_depsgraph_get()
    ev = h.evaluated_get(dg)
    me = ev.to_mesh()
    co = [v.co.copy() for v in me.vertices]
    ev.to_mesh_clear()
    for m, s in states: m.show_viewport = s
    return co

def mat(name, color, rough=0.5, sss=0.0, sheen=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        p.inputs["Subsurface Scale"].default_value = 0.01
    if sheen: p.inputs["Sheen Weight"].default_value = sheen
    p.inputs["Specular IOR Level"].default_value = spec
    return m

EYES = os.path.join(os.path.dirname(os.path.abspath('scene.py')), '..', 'assets', 'eyes', 'high-poly', 'high-poly.mhclo')
def make_human(female):
    h = HumanService.create_human()
    HOP.set_value("gender", 0.0 if female else 1.0, entity_reference=h)
    HOP.set_value("muscle", 0.7 if female else 0.85, entity_reference=h)
    HOP.set_value("weight", 0.45 if female else 0.5, entity_reference=h)
    HOP.set_value("height", 0.5, entity_reference=h)
    TargetService.reapply_macro_details(h)
    rig = HumanService.add_builtin_rig(h, "default")
    co = rest_coords(h)
    me = h.data
    def ss(e0, e1, x):
        t = min(max((x - e0) / (e1 - e0), 0.0), 1.0); return t * t * (3 - 2 * t)
    ah = me.attributes.new("hairw", "FLOAT", "POINT"); ac = me.attributes.new("clothw", "FLOAT", "POINT"); aa = me.attributes.new("accw", "FLOAT", "POINT")
    B = rig.data.bones
    top = B["head"].tail_local.z; hy = B["head"].head_local.y
    hip = B["upperleg01.L"].head_local.z; knee = B["lowerleg01.L"].head_local.z
    waist = B["root"].head_local.z + 0.10 * (top / 1.73)
    sh = B["upperarm01.L"].head_local.z
    thigh = hip + (knee - hip) * 0.42
    k = top / 1.73
    for i, v in enumerate(co):
        x, y, z = abs(v.x), v.y - hy, v.z
        line = top - 0.03 * k - 0.13 * k * ss(-0.05, 0.11, y)
        if x > 0.055 * k and y < 0.04: line = max(line, top - 0.07 * k)
        hw = ss(line - 0.004, line + 0.010, z) if z > top - 0.3 else 0.0
        cw = 0.0
        if x < 0.30: cw = ss(thigh - 0.01, thigh + 0.01, z) * (1 - ss(waist - 0.005, waist + 0.01, z))
        if female and x < 0.15 * k: cw = max(cw, ss(sh - 0.215 * k, sh - 0.20 * k, z) * (1 - ss(sh - 0.06 * k, sh - 0.045 * k, z)))
        aw = 0.0
        if x < 0.30: aw = ss(waist - 0.03, waist - 0.024, z) * (1 - ss(waist - 0.005, waist + 0.002, z))
        ah.data[i].value = hw; ac.data[i].value = cw; aa.data[i].value = aw
    skin_col = (0.24, 0.115, 0.065) if female else (0.20, 0.09, 0.05)
    m = bpy.data.materials.new("body"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    p = N["Principled BSDF"]
    def attr(n):
        a = N.new("ShaderNodeAttribute"); a.attribute_name = n; a.attribute_type = "GEOMETRY"; return a.outputs["Fac"]
    def mixc(fac, a, b):
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; Lk.new(fac, mx.inputs["Factor"])
        mx.inputs[6].default_value = (*a, 1) if isinstance(a, tuple) else (0,0,0,1)
        if not isinstance(a, tuple): Lk.new(a, mx.inputs[6])
        mx.inputs[7].default_value = (*b, 1); return mx.outputs[2]
    def mixf(fac, a, b):
        mx = N.new("ShaderNodeMix"); mx.data_type = "FLOAT"; Lk.new(fac, mx.inputs["Factor"])
        if isinstance(a, float): mx.inputs[2].default_value = a
        else: Lk.new(a, mx.inputs[2])
        mx.inputs[3].default_value = b; return mx.outputs[0]
    # subtle skin variation
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 6
    skv = N.new("ShaderNodeMix"); skv.data_type = "RGBA"; skv.inputs["Factor"].default_value = 0.08
    Lk.new(nz.outputs["Color"], skv.inputs[7]); skv.inputs[6].default_value = (*skin_col, 1)
    hw, cw, aw = attr("hairw"), attr("clothw"), attr("accw")
    c = mixc(cw, skv.outputs[2], (0.018, 0.02, 0.024))
    c = mixc(aw, c, (0.42, 0.75, 0.02))
    c = mixc(hw, c, (0.012, 0.009, 0.007))
    Lk.new(c, p.inputs["Base Color"])
    r = mixf(cw, 0.52, 0.85); r = mixf(hw, r, 0.9)
    sp = mixf(cw, 0.32, 0.12); sp = mixf(hw, sp, 0.05)
    Lk.new(sp, p.inputs["Specular IOR Level"])
    Lk.new(r, p.inputs["Roughness"])
    sss = mixf(cw, 0.12, 0.0); sss = mixf(hw, sss, 0.0)
    Lk.new(sss, p.inputs["Subsurface Weight"])
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2); p.inputs["Subsurface Scale"].default_value = 0.008
    Lk.new(cw, p.inputs["Sheen Weight"]); p.inputs["Sheen Roughness"].default_value = 0.4
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
    hn = N.new("ShaderNodeTexNoise"); hn.inputs["Scale"].default_value = 900
    Lk.new(hn.outputs["Fac"], bump.inputs["Height"]); Lk.new(bump.outputs["Normal"], p.inputs["Normal"])
    me.materials.clear(); me.materials.append(m)
    if female:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 0, 0), segments=32, ring_count=16)
        bun = bpy.context.object; bun.scale = (1.0, 0.85, 0.9)
        hm = bpy.data.materials.new("bunm"); hm.use_nodes = True
        hp = hm.node_tree.nodes["Principled BSDF"]; hp.inputs["Base Color"].default_value = (0.012, 0.009, 0.007, 1); hp.inputs["Roughness"].default_value = 0.55
        hp.inputs["Sheen Weight"].default_value = 0.6
        bn = hm.node_tree.nodes.new("ShaderNodeBump"); bn.inputs["Strength"].default_value = 0.4
        wv = hm.node_tree.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 40; wv.inputs["Distortion"].default_value = 6
        hm.node_tree.links.new(wv.outputs["Fac"], bn.inputs["Height"]); hm.node_tree.links.new(bn.outputs["Normal"], hp.inputs["Normal"])
        bun.data.materials.append(hm); bpy.ops.object.shade_smooth()
        hb = rig.data.bones["head"]
        bl = Vector((0, hb.head_local.y + 0.10, hb.tail_local.z - 0.06))
        bun.location = bl
        bun.parent = rig; bun.parent_type = "BONE"; bun.parent_bone = "head"
        bun.matrix_parent_inverse = (rig.matrix_world @ hb.matrix_local @ Matrix.Translation((0, hb.length, 0))).inverted()
    for p in me.polygons: p.use_smooth = True
    try:
        eyes = HumanService.add_mhclo_asset(EYES, h, asset_type="Eyes", material_type="MAKESKIN")
        eyes.data.materials.clear()
        em = mat("eye", (0.9, 0.9, 0.88), rough=0.1)
        em2 = mat("iris", (0.05, 0.025, 0.012), rough=0.15)
        eyes.data.materials.append(em); eyes.data.materials.append(em2)
        import mathutils as _mu
        ec = [v.co for v in eyes.data.vertices]
        cy = min(v.y for v in ec)
        for p in eyes.data.polygons:
            vy = sum(ec[i].y for i in p.vertices)/len(p.vertices)
            p.material_index = 1 if vy < cy + 0.006 else 0
    except Exception as e:
        print("EYES FAIL", repr(e))
    sub = h.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    return h, rig

def ik_setup(rig):
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    tg = {}
    def empty(n, loc):
        e = bpy.data.objects.new(n, None); bpy.context.scene.collection.objects.link(e); e.location = loc; tg[n] = e; return e
    pb = rig.pose.bones
    for s in ("L", "R"):
        f = rig.data.bones["foot." + s]
        empty("foot." + s, f.head_local.copy())
        empty("knee." + s, f.head_local + Vector((0, -0.6, 0.45)))
        c = pb["lowerleg02." + s].constraints.new("IK"); c.target = tg["foot." + s]; c.pole_target = tg["knee." + s]; c.chain_count = 4; c.pole_angle = math.radians(-90)
        w = rig.data.bones["wrist." + s]
        empty("hand." + s, w.head_local.copy())
        sx = 1 if s == "L" else -1
        empty("elbow." + s, w.head_local + Vector((sx * 0.3, 0.5, 0)))
        c = pb["lowerarm02." + s].constraints.new("IK"); c.target = tg["hand." + s]; c.pole_target = tg["elbow." + s]; c.chain_count = 4; c.pole_angle = math.radians(0)
        fc = pb["foot." + s].constraints.new("COPY_ROTATION"); fc.target = tg["foot." + s]
    bpy.ops.object.mode_set(mode="OBJECT")
    return tg

def stage(female=False):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = 48; sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 640
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.013, 0.016, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1
    bpy.ops.mesh.primitive_plane_add(size=30); fl = bpy.context.object
    fl.data.materials.append(mat("floor", (0.006, 0.0065, 0.0075), rough=0.8, spec=0.12))
    def light(n, loc, energy, color, size, rot_to=(0, 0, 1.0)):
        l = bpy.data.lights.new(n, "AREA"); l.energy = energy; l.color = color; l.size = size
        o = bpy.data.objects.new(n, l); sc.collection.objects.link(o); o.location = loc
        d = Vector(rot_to) - Vector(loc); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    light("key", (-2.2, -2.6, 3.0), 420, (1, 0.98, 0.95), 2.0)
    light("fill", (2.8, -1.8, 1.2), 120, (0.85, 0.9, 1.0), 3.0)
    light("rim", (1.6, 2.6, 2.4), 500, (0.85, 1.0, 0.45), 1.0)
    light("rim2", (-2.0, 2.4, 1.6), 400, (0.9, 0.95, 1.0), 1.0)
    cam = bpy.data.cameras.new("cam"); cam.lens = 55
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    return co

def aim(cam, loc, target):
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
