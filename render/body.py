import math
from mathutils import Vector, Quaternion
exec(open("poser.py").read())

SPINE = ["spine05", "spine04", "spine03", "spine02", "spine01"]
NECK = ["neck01", "neck02", "neck03"]

def pitch_dir(deg, yaw=0.0):
    t = math.radians(deg); y = math.radians(yaw)
    return Vector((math.sin(y) * math.sin(t), -math.cos(y) * math.sin(t), math.cos(t)))

def resolve(v, posed, P, anchor=None):
    if isinstance(v, tuple) and len(v) == 4 and v[0] == "mix":
        pa, pb, t = resolve(v[1], posed, P), resolve(v[2], posed, P), v[3]
        if anchor is None: return pa.lerp(pb, t)
        ra, rb = pa - anchor, pb - anchor
        if ra.length < 1e-4 or rb.length < 1e-4: return pa.lerp(pb, t)
        dn = ra.normalized().slerp(rb.normalized(), t, ra.normalized().orthogonal())
        return anchor + dn * (ra.length + (rb.length - ra.length) * t)
    if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], str):
        kind, off = v
        off = Vector(off)
        if kind == "torso":
            q = Quaternion((1, 0, 0), math.radians(-P.get("torso", 0.0)))
            return posed["neck01"].translation + q @ off
        if kind == "neckw":
            return posed["neck01"].translation + off
        if kind == "pelvis":
            q = Quaternion((1, 0, 0), math.radians(-P.get("pelvis_tilt", 0.0)))
            return posed["root"].translation + q @ off
    return Vector(v)

POS_KEYS = ("pelvis", "feet", "hands", "knee_pos")
def scale_pose(P, k):
    def sc(v):
        if isinstance(v, dict): return {a: sc(c) for a, c in v.items()}
        if isinstance(v, tuple) and len(v) == 4 and v[0] == "mix": return ("mix", sc(v[1]), sc(v[2]), v[3])
        if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], str): return (v[0], tuple(x * k for x in v[1]))
        return tuple(x * k for x in v)
    Q = dict(P)
    for key in POS_KEYS:
        if key in Q: Q[key] = sc(Q[key])
    return Q

def pose_body(poser, P):
    """P keys: pelvis (xyz), pelvis_tilt (deg fwd), torso (deg fwd), torso_side (deg), head (deg fwd rel to torso),
       feet {L,R: xyz ankle}, toes {L,R: deg outwards}, knee {L,R: hint xyz}, hands {L,R: xyz wrist},
       elbow {L,R: hint xyz}, palm {L,R: twist deg}, lie (deg: whole body rotation about X, for floor work)."""
    b = poser.bones
    k = b["head"].tail_local.z / 1.734
    P = scale_pose(P, k)
    root_rest = b["root"].head_local
    pel = Vector(P.get("pelvis", root_rest))
    tilt = P.get("pelvis_tilt", 0.0)
    rr = Quaternion((1, 0, 0), math.radians(-tilt))
    torso = P.get("torso", 0.0); side = P.get("torso_side", 0.0)
    dirs = {}
    n = len(SPINE)
    for i, s in enumerate(SPINE):
        a = tilt + (torso - tilt) * (i + 1) / n
        d = pitch_dir(a)
        d.x += math.sin(math.radians(side)) * (i + 1) / n
        dirs[s] = d
    hd = torso + P.get("head", 0.0) - 8
    for s in NECK: dirs[s] = pitch_dir(torso * 0.7 + hd * 0.3)
    dirs["head"] = pitch_dir(hd)
    if P.get("head_side"):
        hs = math.sin(math.radians(P["head_side"]))
        for s in NECK[1:]: dirs[s] = dirs[s] + Vector((hs * 0.5, 0, 0))
        dirs["head"] = dirs["head"] + Vector((hs, 0, 0))
    if "shrug" in P:
        qt = Quaternion((1, 0, 0), math.radians(-torso))
        for s, sx in (("L", 1), ("R", -1)):
            dirs["clavicle." + s] = qt @ Vector((sx * 0.086, 0.0, 0.014 + 0.07 * P["shrug"]))
    root_loc = pel - root_rest
    lie = P.get("lie")
    posed = poser.apply(root_loc, dirs, root_rot=rr)
    if P.get("plant") and "hands" in P:
        # hands must reach their target (floor, bench): lower the body until the arms are long enough
        for _ in range(4):
            worst = 0.0
            for s in ("L", "R"):
                shp = posed["upperarm01." + s].translation
                tgt = resolve(P["hands"][s], posed, P, shp)
                reach = (poser.L["uarm" + s] + poser.L["farm" + s]) * 0.97
                worst = max(worst, (tgt - shp).length - reach)
            if worst < 0.004: break
            root_loc = root_loc + Vector((0, 0, -worst * 1.15))
            posed = poser.apply(root_loc, dirs, root_rot=rr)
    tw = {}
    for s, sx in (("L", 1), ("R", -1)):
        hip = posed["upperleg01." + s].translation
        ank = resolve(P["feet"][s], posed, P, hip) if "feet" in P else poser.rest["foot." + s][0] + root_loc * Vector((1, 1, 0))
        hint = Vector(P.get("knee", {}).get(s, (sx * 0.15, -1, 0)))
        knee, ank = two_bone(hip, ank, poser.L["thigh" + s], poser.L["shin" + s], hint)
        dirs["upperleg01." + s] = dirs["upperleg02." + s] = knee - hip
        dirs["lowerleg01." + s] = dirs["lowerleg02." + s] = ank - knee
        toe = math.radians(P.get("toes", {}).get(s, 8) * sx)
        fp = P.get("foot_pitch", {}).get(s, 30)
        fd = Vector((math.sin(toe), -math.cos(toe), 0)) * math.cos(math.radians(fp)) + Vector((0, 0, -math.sin(math.radians(fp))))
        dirs["foot." + s] = fd
        sh = posed["upperarm01." + s].translation
        wr = resolve(P["hands"][s], posed, P, sh) if "hands" in P else None
        if wr is not None:
            eh = Vector(P.get("elbow", {}).get(s, (sx * 0.3, 0.3, -1)))
            el, wr = two_bone(sh, wr, poser.L["uarm" + s], poser.L["farm" + s], eh)
            dirs["upperarm01." + s] = dirs["upperarm02." + s] = el - sh
            dirs["lowerarm01." + s] = dirs["lowerarm02." + s] = wr - el
            wd = P.get("wrist_dir", {}).get(s)
            dirs["wrist." + s] = Vector(wd) if wd else (wr - el)
        if s in P.get("palm", {}):
            tw["lowerarm02." + s] = P["palm"][s] * sx
    loc = {}
    for s, sx in (("L", 1), ("R", -1)):
        g = P.get("grip", {}).get(s, 0.35)
        for f in range(2, 6):
            for j, k in ((1, 1.0), (2, 1.1), (3, 0.9)):
                loc["finger%d-%d.%s" % (f, j, s)] = ("X", 75 * g * k)
        loc["finger1-2.%s" % s] = ("X", 30 * g); loc["finger1-3.%s" % s] = ("X", 30 * g)
    poser.apply(root_loc, dirs, twists=tw, root_rot=rr, local=loc)
