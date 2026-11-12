# Realistic look: MakeHuman CC0 skin textures, hair, brows, lashes, sportswear and sneakers (falls back to the painted look).
import os, glob
A = None
def _asset(sub, name, ext=".mhclo"):
    for root in AssetService.get_asset_roots(sub):
        for f in glob.glob(os.path.join(root, "**", name + ext), recursive=True): return f
    return None

AssetService = imp("services.assetservice", "AssetService")

def fabric(name, col, tex=None, normal=None, rough=0.75, sheen=0.5, keep_tex=0.0, spec=0.25, weave=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough; p.inputs["Sheen Weight"].default_value = sheen
    p.inputs["Specular IOR Level"].default_value = spec
    if tex and os.path.exists(tex):
        ti = N.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(tex, check_existing=True)
        hsv = N.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = keep_tex
        L.new(ti.outputs["Color"], hsv.inputs["Color"])
        mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
        L.new(hsv.outputs["Color"], mul.inputs[6]); mul.inputs[7].default_value = (*col, 1)
        L.new(mul.outputs[2], p.inputs["Base Color"])
        if "Alpha" in ti.outputs: L.new(ti.outputs["Alpha"], p.inputs["Alpha"])
    else:
        p.inputs["Base Color"].default_value = (*col, 1)
    import json as _j
    m["fx"] = _j.dumps({"kind": "fabric", "tex": tex, "normal": normal, "col": list(col), "keep": keep_tex, "rough": rough, "weave": weave})
    if normal and os.path.exists(normal):
        tn = N.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(normal, check_existing=True); tn.image.colorspace_settings.name = "Non-Color"
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8
        L.new(tn.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], p.inputs["Normal"])
    return m

def _tex(mhclo, kind):
    d = os.path.dirname(mhclo)
    fs = sorted(glob.glob(os.path.join(d, "*_" + kind + ".png")))
    return fs[0] if fs else None

def add_item(h, name, kind, col=None, keep=0.0, rough=0.75, sheen=0.5, subdiv=1):
    path = _asset(kind.lower(), name)
    if path is None:
        print("MISSING", name); return None
    o = HumanService.add_mhclo_asset(path, h, asset_type=kind, subdiv_levels=subdiv, material_type="MAKESKIN")
    if col is not None:
        o.data.materials.clear()
        o.data.materials.append(fabric(name + "_m", col, _tex(path, "diffuse"), _tex(path, "normal"), rough, sheen, keep))
    return o

def skin_mat(h, female, tone):
    """Skin from the MakeHuman texture, shifted to the requested tone, with subsurface scattering and fine pores."""
    sk = "young_caucasian_female" if female else "young_caucasian_male"
    path = _asset("skins", sk, ".mhmat")
    tex = None
    if path:
        fs = glob.glob(os.path.join(os.path.dirname(path), "*diffuse*.png"))
        tex = fs[0] if fs else None
    m = bpy.data.materials.new("skin"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; p = N["Principled BSDF"]
    if tex:
        ti = N.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(tex, check_existing=True)
        hsv = N.new("ShaderNodeHueSaturation")
        hsv.inputs["Hue"].default_value = tone[0]; hsv.inputs["Saturation"].default_value = tone[1]; hsv.inputs["Value"].default_value = tone[2]
        L.new(ti.outputs["Color"], hsv.inputs["Color"]); L.new(hsv.outputs["Color"], p.inputs["Base Color"])
        L.new(hsv.outputs["Color"], p.inputs["Subsurface Radius"]) if False else None
    p.inputs["Roughness"].default_value = 0.5
    p.inputs["Specular IOR Level"].default_value = 0.35
    p.inputs["Subsurface Weight"].default_value = 0.18
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.25); p.inputs["Subsurface Scale"].default_value = 0.012
    p.inputs["Coat Weight"].default_value = 0.04; p.inputs["Coat Roughness"].default_value = 0.35
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.06; bump.inputs["Distance"].default_value = 0.001
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1400; nz.inputs["Detail"].default_value = 4
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    import json as _j
    m["fx"] = _j.dumps({"kind": "skin", "tex": tex, "hsv": list(tone)})
    h.data.materials.clear(); h.data.materials.append(m)
    return m

def sportswear(h, rig, shirt=True):
    """Fitted training tee and shorts cut from a copy of the body's own surface, so they bend exactly like the body
    (no skin poking through, clean hems). Returns the new objects."""
    import bmesh
    B = rig.data.bones; k = B["head"].tail_local.z / 1.734
    names = [g.name for g in h.vertex_groups]; ti = names.index("helper-tights"); bi = names.index("body")
    def cat(n):
        if n.endswith((".L", ".R")):
            s = n[-1]
            if n.startswith(("upperarm", "lowerarm", "wrist", "finger", "metacarpal")): return "arm" + s
            if n.startswith(("upperleg", "lowerleg", "foot", "toe")): return "leg" + s
        return "core"
    bone_ix = {i: cat(n) for i, n in enumerate(names) if n in B}
    def vcat(groups):
        best, bw = "core", 0.0
        for gi, w in groups:
            if gi in bone_ix and w > bw: best, bw = bone_ix[gi], w
        return best
    # cut planes (point, normal pointing to the side that is removed)
    def limb(bone, t):
        b = B[bone]; d = (b.tail_local - b.head_local).normalized()
        return b.head_local.lerp(b.tail_local, t), d
    planes = {"armL": limb("upperarm02.L", 0.50), "armR": limb("upperarm02.R", 0.50),
              "legL": limb("upperleg02.L", 0.40), "legR": limb("upperleg02.R", 0.40)}
    neck = (Vector((0, -0.01 * k, 1.462 * k)), Vector((0, -0.45, 1)).normalized())
    hem, top = 0.995 * k, 1.035 * k
    def sd(co, pl): return (co - pl[0]).dot(pl[1])
    def ss(e0, e1, x):
        t = min(max((x - e0) / (e1 - e0), 0.0), 1.0); return t * t * (3 - 2 * t)

    from mathutils import bvhtree
    bodyv = set(v.index for v in h.data.vertices if any(g.group == bi for g in v.groups))
    spolys = [tuple(p.vertices) for p in h.data.polygons if all(i in bodyv for i in p.vertices)]
    sco = rest_coords(h)      # the body's real shape (its build is stored as shape keys)
    skin = bvhtree.BVHTree.FromPolygons(sco, spolys)
    from mathutils import interpolate
    def top4(d):
        t = sorted(d.items(), key=lambda x: -x[1])[:4]; sm = sum(w for _, w in t) or 1.0
        return {g: w / sm for g, w in t}
    sw = {i: top4({g.group: g.weight for g in h.data.vertices[i].groups if g.group in bone_ix}) for i in bodyv}

    def build(kind):
        bm = bmesh.new(); bm.from_mesh(h.data); dl = bm.verts.layers.deform.verify()
        for v in bm.verts: v.co = sco[v.index]
        for sk in list(bm.verts.layers.shape.values()): bm.verts.layers.shape.remove(sk)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if bi not in v[dl]], context="VERTS")
        cats = {v: vcat(v[dl].items()) for v in bm.verts}
        def cut(pl, pick):
            vs = [v for v in bm.verts if pick(cats.get(v, "new"))]
            vset = set(vs)
            geom = vs + [e for e in bm.edges if e.verts[0] in vset and e.verts[1] in vset] + [f for f in bm.faces if all(v in vset for v in f.verts)]
            before = set(bm.verts)
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=pl[0], plane_no=pl[1], clear_outer=True, dist=1e-5)
            for v in bm.verts:
                if v not in before: cats[v] = "cut"
        if kind == "shirt":
            for a in ("armL", "armR"): cut(planes[a], lambda c, a=a: c == a)
            cut((Vector((0, 0, hem)), Vector((0, 0, -1))), lambda c: not c.startswith("arm"))
            cut(neck, lambda c: True)
        else:
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if cats[v].startswith("arm")], context="VERTS")
            for a in ("legL", "legR"): cut(planes[a], lambda c, a=a: c == a)
            cut((Vector((0, 0, top)), Vector((0, 0, 1))), lambda c: not c.startswith("leg"))
        # stand the cloth off the skin: snug at sleeve and neck (so you can't see inside), looser in between and at
        # the hems; then pull it taut so it spans the dips between muscles instead of looking painted on
        edge = set(v for e in bm.edges if e.is_boundary for v in e.verts)
        inner = [v for v in bm.verts if v not in edge]
        ring = {v: 0 for v in edge}; front = list(edge)
        for r in range(1, 5):
            nxt = []
            for v in front:
                for e in v.link_edges:
                    o = e.other_vert(v)
                    if o not in ring: ring[o] = r; nxt.append(o)
            front = nxt
        def want(v):
            z = v.co.z; t = ring.get(v, 5) / 5.0
            if kind == "shirt":
                free = 0.006 + 0.004 * (1 - ss(hem, hem + 0.06 * k, z))
                if z < hem + 0.05 * k: t = 1.0
                return (0.004 * (1 - t) + free * t) * k
            free = 0.009 + 0.004 * (1 - ss(hem - 0.16 * k, hem - 0.06 * k, z))          # legs of the shorts hang looser
            free *= 0.25 + 0.75 * (1 - ss(hem - 0.04 * k, hem - 0.012 * k, z))            # thin where the tee hangs over
            return free * k if z < hem else (0.0012 * (1 - t) + free * t) * k
        def settle(v, taut):
            loc, nor, fi, dist = skin.find_nearest(v.co)
            d = v.co - loc
            out = d.dot(nor) > 0
            n = d.normalized() if dist > 1e-4 and out else nor
            w = want(v)
            if not taut or not out or dist < w: v.co = loc + n * w
            elif dist > w + 0.02 * k: v.co = loc + n * (w + 0.02 * k)
        for v in bm.verts: settle(v, False)
        for _ in range(3):
            for _ in range(3): bmesh.ops.smooth_vert(bm, verts=inner, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
            for v in inner: settle(v, True)
        for v in bm.verts:
            loc, nor, fi, dist = skin.find_nearest(v.co)
            # bend exactly like the skin underneath: take its bone weights
            pv = spolys[fi]; bw = interpolate.poly_3d_calc([sco[i] for i in pv], loc); acc = {}
            for i, b in zip(pv, bw):
                for g, w in sw[i].items(): acc[g] = acc.get(g, 0.0) + w * b
            for g in list(v[dl].keys()):
                if g in bone_ix: del v[dl][g]
            for g, w in top4(acc).items(): v[dl][g] = w
        me = bpy.data.meshes.new("forge_" + kind); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("Human.forge_" + kind, me); bpy.context.scene.collection.objects.link(o)
        for n in names: o.vertex_groups.new(name=n)
        for p in me.polygons: p.use_smooth = True
        o.parent = rig
        am = o.modifiers.new("Armature", "ARMATURE"); am.object = rig
        sub = o.modifiers.new("Subdivision", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
        return o

    def hide(kind, o):
        """Remove the skin that is safely underneath the garment (well inside its edges), so nothing can poke through."""
        me = o.data
        cloth = bvhtree.BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
        cnt = {}
        for p in me.polygons:
            for e in p.edge_keys: cnt[e] = cnt.get(e, 0) + 1
        import numpy as _np
        be = [e for e, c in cnt.items() if c == 1]
        A = _np.array([me.vertices[a].co[:] for a, _ in be]); Bv = _np.array([me.vertices[b].co[:] for _, b in be]) - A
        L2 = (Bv * Bv).sum(1) + 1e-12
        g = h.vertex_groups.new(name="Delete.forge_" + kind); ix = []
        m = (0.03 if kind == "shirt" else 0.045) * k
        for i in bodyv:
            hit = cloth.find_nearest(sco[i], 0.035 * k)
            if hit[0] is None: continue
            # how far inside the garment's edge is the cloth right above this bit of skin?
            P = _np.array(hit[0][:]) - A
            t = _np.clip((P * Bv).sum(1) / L2, 0, 1)
            d2 = ((P - Bv * t[:, None]) ** 2).sum(1).min()
            if d2 > m * m: ix.append(i)
        g.add(ix, 1.0, "REPLACE")
        md = h.modifiers.new("Delete.forge_" + kind, "MASK"); md.vertex_group = g.name; md.invert_vertex_group = True
        while h.modifiers.find(md.name) > 1: bpy.context.view_layer.objects.active = h; bpy.ops.object.modifier_move_up(modifier=md.name)

    out = []
    for kind in (("shirt", "shorts") if shirt else ("shorts",)):
        o = build(kind); hide(kind, o); out.append(o)
        col = (0.12, 0.127, 0.145) if kind == "shirt" else (0.012, 0.013, 0.016)
        o.data.materials.append(fabric("forge_%s_m" % kind, col, rough=0.78 if kind == "shirt" else 0.72, sheen=0.3 if kind == "shirt" else 0.1, weave=70 if kind == "shirt" else 90))
    return out

TONES = {"medium": (0.5, 1.08, 0.47), "light": (0.5, 1.0, 0.92), "deep": (0.5, 1.15, 0.42)}

def dress(h, rig, female, tone="medium"):
    skin_mat(h, female, TONES[tone])
    add_item(h, "eyebrow010" if female else "eyebrow001", "Eyebrows")
    add_item(h, "eyelashes02" if female else "eyelashes01", "Eyelashes")
    if female:
        add_item(h, "ponytail01", "Hair", col=(0.40, 0.36, 0.34), keep=0.85, rough=0.45, sheen=0.08)
        add_item(h, "female_sportsuit01", "Clothes", col=(0.018, 0.02, 0.024), keep=0.0, rough=0.72, sheen=0.2)
    else:
        add_item(h, "short02", "Hair", col=(0.50, 0.46, 0.44), keep=0.9, rough=0.5, sheen=0.08)
        sportswear(h, rig, shirt=not os.environ.get("FORGE_BODYMAP"))  # the muscle map shows the bare upper body
    add_item(h, "shoes06", "Clothes", col=(0.75, 0.78, 0.8), keep=0.15, rough=0.6, sheen=0.2)
