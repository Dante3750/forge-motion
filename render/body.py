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
        pa, pb, t = resolve(v[1], posed, P, anchor), resolve(v[2], posed, P, anchor), v[3]
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
        if kind == "hang":
            # a loaded hand hangs straight down under the shoulder whatever the torso does (gravity)
            return (anchor if anchor is not None else posed["neck01"].translation) + off
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

def bone_tail(poser, posed, n):
    M = posed[n]
    return M.translation + M.to_3x3() @ Vector((0, poser.bones[n].length, 0))

# body-segment masses (fraction of body mass, de Leva 1996) and where along the segment their centre sits
SEGMENTS = [("trunk", "root", "neck01", 0.497, 0.50), ("headseg", "neck01", "@head", 0.081, 0.55)]
for _s in ("L", "R"):
    SEGMENTS += [("uarm", "upperarm01." + _s, "lowerarm01." + _s, 0.028, 0.44),
                 ("farm", "lowerarm01." + _s, "wrist." + _s, 0.016, 0.43),
                 ("hand", "wrist." + _s, "@wrist." + _s, 0.006, 0.80),
                 ("thigh", "upperleg01." + _s, "lowerleg01." + _s, 0.100, 0.43),
                 ("shank", "lowerleg01." + _s, "foot." + _s, 0.0465, 0.43),
                 ("footseg", "foot." + _s, "@foot." + _s, 0.0145, 0.50)]

def centre_of_mass(poser, posed, load=0.0):
    def pt(n): return bone_tail(poser, posed, n[1:]) if n.startswith("@") else posed[n].translation
    c = Vector((0, 0, 0)); m = 0.0
    for _, a, b, w, f in SEGMENTS:
        pa, pb = pt(a), pt(b); c += (pa + (pb - pa) * f) * w; m += w
    if load:
        for s in ("L", "R"): c += posed["wrist." + s].translation * (load / 2); m += load
    return c / m

def support_point(poser, posed, k):
    """Mid-foot of the planted foot/feet (the base of support), or None if the body isn't standing on its feet."""
    pts = []
    for s in ("L", "R"):
        a = posed["foot." + s].translation; t = bone_tail(poser, posed, "foot." + s)
        fwd = Vector((t.x - a.x, t.y - a.y, 0))
        fwd = fwd.normalized() if fwd.length > 1e-4 else Vector((0, -1, 0))
        pts.append((a.z, a + fwd * 0.065 * k))
    lo = min(z for z, _ in pts)
    planted = [p for z, p in pts if z < lo + 0.06 * k]
    return sum(planted, Vector((0, 0, 0))) / len(planted), len(planted)

def scap_dirs(poser, posed, P, dirs, hands_w):
    """Scapulohumeral rhythm: the shoulder girdle rises when the arm goes overhead and slides forward on a reach,
    instead of the arm pivoting from a fixed socket like a robot."""
    top = Vector(dirs[SPINE[-1]]).normalized()
    qt = Vector((0, 0, 1)).rotation_difference(top)
    qi = qt.inverted()
    shrug = P.get("shrug", 0.0)
    for s, sx in (("L", 1), ("R", -1)):
        base = Vector((sx * 0.086, 0.0, 0.014 + 0.07 * shrug))
        wr = hands_w.get(s)
        if wr is not None:
            sh = posed["upperarm01." + s].translation
            d = qi @ (wr - sh)
            reach = poser.L["uarm" + s] + poser.L["farm" + s]
            ext = min(d.length / reach, 1.0)
            dn = d.normalized()
            elev = math.degrees(math.acos(max(-1.0, min(1.0, -dn.z))))  # 0 = arm hanging, 180 = straight overhead
            up = min(max((elev - 50) / 120, 0.0), 1.0)
            up = up * up * (3 - 2 * up)
            base.z += 0.045 * up
            fwd = max(0.0, -dn.y) * ext * min(elev / 90, 1.0)
            base.y -= 0.03 * fwd                      # protraction on a reach / press lockout
            back = max(0.0, dn.y) * (1 - ext)
            base.y += 0.02 * back                     # retraction when the elbow drives back (rows)
        dirs["clavicle." + s] = qt @ base

def pose_body(poser, P):
    """P keys: pelvis (xyz), pelvis_tilt (deg fwd), torso (deg fwd), torso_side (deg), head (deg fwd rel to torso),
       feet {L,R: xyz ankle}, toes {L,R: deg outwards}, knee {L,R: hint xyz}, hands {L,R: xyz wrist},
       elbow {L,R: hint xyz}, palm {L,R: twist deg}. _bal: carried load (fraction of body mass) to balance over the feet."""
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
    root_loc = pel - root_rest
    air = P.get("_lift", 0.0) * k
    root_loc = root_loc + Vector((0, 0, air))
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

    def limbs(root_loc):
        posed = poser.apply(root_loc, dirs, root_rot=rr)
        if "hands" in P:
            hw = {s: resolve(P["hands"][s], posed, P, posed["upperarm01." + s].translation) for s in ("L", "R")}
            scap_dirs(poser, posed, P, dirs, hw)
            posed = poser.apply(root_loc, dirs, root_rot=rr)
        elif "shrug" in P:
            scap_dirs(poser, posed, P, dirs, {})
            posed = poser.apply(root_loc, dirs, root_rot=rr)
        tw = {}
        for s, sx in (("L", 1), ("R", -1)):
            hip = posed["upperleg01." + s].translation
            ank = resolve(P["feet"][s], posed, P, hip) if "feet" in P else poser.rest["foot." + s][0] + root_loc * Vector((1, 1, 0))
            ank = ank + Vector((0, 0, air))
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
                for j, kk in ((1, 1.0), (2, 1.1), (3, 0.9)):
                    loc["finger%d-%d.%s" % (f, j, s)] = ("X", 75 * g * kk)
            loc["finger1-2.%s" % s] = ("X", 30 * g); loc["finger1-3.%s" % s] = ("X", 30 * g)
        return poser.apply(root_loc, dirs, twists=tw, root_rot=rr, local=loc)

    posed = limbs(root_loc)
    bal = P.get("_bal")
    if bal is not None and not P.get("plant") and "feet" in P:
        # Balance: a standing body keeps its centre of mass over the mid-foot. Shift the hips (not the feet,
        # not hands that hold a fixed path) until it does - this is what makes hinges sit back and
        # loaded reaches counter-lean like a real person instead of a puppet hanging in the air.
        start = root_loc.copy()
        for _ in range(4):
            sup, nfeet = support_point(poser, posed, k)
            com = centre_of_mass(poser, posed, bal)
            if com.z - sup.z < 0.40 * k: break
            dz_y = 0.035 * k
            dz_x = (0.03 if nfeet == 1 else 0.20) * k
            ey = sup.y - com.y; ex = sup.x - com.x
            ey = (ey - dz_y if ey > dz_y else ey + dz_y if ey < -dz_y else 0.0)
            ex = (ex - dz_x if ex > dz_x else ex + dz_x if ex < -dz_x else 0.0)
            if abs(ey) < 0.002 and abs(ex) < 0.002: break
            root_loc = root_loc + Vector((ex, ey, 0)) * 1.25
            off = root_loc - start
            cap = 0.12 * k
            if off.length > cap: root_loc = start + off.normalized() * cap
            posed = limbs(root_loc)
    poser.last_root = root_loc
