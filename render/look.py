# Realistic look: MakeHuman CC0 skin textures, hair, brows, lashes, sportswear and sneakers (falls back to the painted look).
import os, glob
A = None
def _asset(sub, name, ext=".mhclo"):
    for root in AssetService.get_asset_roots(sub):
        for f in glob.glob(os.path.join(root, "**", name + ext), recursive=True): return f
    return None

AssetService = imp("services.assetservice", "AssetService")

def fabric(name, col, tex=None, normal=None, rough=0.75, sheen=0.5, keep_tex=0.0, spec=0.25):
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
    h.data.materials.clear(); h.data.materials.append(m)
    return m

TONES = {"medium": (0.5, 1.22, 0.47), "light": (0.5, 1.0, 0.92), "deep": (0.5, 1.15, 0.42)}

def dress(h, rig, female, tone="medium"):
    skin_mat(h, female, TONES[tone])
    add_item(h, "eyebrow010" if female else "eyebrow001", "Eyebrows")
    add_item(h, "eyelashes02" if female else "eyelashes01", "Eyelashes")
    if female:
        add_item(h, "ponytail01", "Hair", col=(0.035, 0.025, 0.02), keep=0.2, rough=0.55, sheen=0.3)
        add_item(h, "female_sportsuit01", "Clothes", col=(0.018, 0.02, 0.024), keep=0.0, rough=0.72, sheen=0.2)
    else:
        add_item(h, "short02", "Hair", col=(0.03, 0.022, 0.018), keep=0.2, rough=0.6, sheen=0.3)
        add_item(h, "elvs_crude_t-shirt_male", "Clothes", col=(0.016, 0.018, 0.021), keep=0.0, rough=0.8, sheen=0.2)
        add_item(h, "cortu_jeans_shorts", "Clothes", col=(0.03, 0.033, 0.038), keep=0.0, rough=0.8, sheen=0.2)
    add_item(h, "shoes06", "Clothes", col=(0.75, 0.78, 0.8), keep=0.15, rough=0.6, sheen=0.2)
