import math
from mathutils import Vector, Matrix, Quaternion

class Poser:
    """Poses the MakeHuman default rig from world-space joint targets (armature space, metres).
    Each controlled bone is swung (no twist) so head->tail points along a target direction."""
    def __init__(self, rig):
        self.rig = rig
        self.bones = rig.data.bones
        self.order = []
        def walk(b):
            self.order.append(b.name)
            for c in b.children: walk(c)
        for b in self.bones:
            if b.parent is None: walk(b)
        R = lambda n: self.bones[n].head_local.copy()
        self.rest = {n: (self.bones[n].head_local.copy(), self.bones[n].tail_local.copy()) for n in self.order}
        self.L = {}
        for s in "LR":
            self.L["thigh"+s] = (R("lowerleg01."+s) - R("upperleg01."+s)).length
            self.L["shin"+s] = (R("foot."+s) - R("lowerleg01."+s)).length
            self.L["uarm"+s] = (R("lowerarm01."+s) - R("upperarm01."+s)).length
            self.L["farm"+s] = (R("wrist."+s) - R("lowerarm01."+s)).length

    def apply(self, root_loc, dirs, twists=None, root_rot=None, local=None):
        """root_loc: armature-space offset of the root bone head.
        dirs: {bone: Vector direction}. twists: {bone: degrees roll about own axis}.
        root_rot: Quaternion rotation of whole body around root head."""
        twists = twists or {}
        local = local or {}
        posed = {}
        pbs = self.rig.pose.bones
        for n in self.order:
            b = self.bones[n]
            if b.parent is None:
                M0 = b.matrix_local.copy()
                M0.translation = b.head_local + root_loc
                if root_rot is not None:
                    M0 = Matrix.Translation(M0.translation) @ root_rot.to_matrix().to_4x4() @ Matrix.Translation(-M0.translation) @ M0
                rel = Matrix.Identity(4); P = None
            else:
                P = posed[b.parent.name]
                rel = b.parent.matrix_local.inverted() @ b.matrix_local
                M0 = P @ rel
            M = M0
            if n in dirs and dirs[n] is not None:
                cur = (M0.to_3x3() @ Vector((0, 1, 0))).normalized()
                want = Vector(dirs[n]).normalized()
                q = cur.rotation_difference(want)
                head = M0.translation.copy()
                rot = q.to_matrix() @ M0.to_3x3()
                M = rot.to_4x4(); M.translation = head
            if n in twists:
                ax = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
                tq = Quaternion(ax, math.radians(twists[n]))
                head = M.translation.copy()
                M = (tq.to_matrix() @ M.to_3x3()).to_4x4(); M.translation = head
            if n in local:
                ax, deg = local[n]
                head = M.translation.copy()
                M = M @ Matrix.Rotation(math.radians(deg), 4, ax)
                M.translation = head
            posed[n] = M
            if P is None:
                pbs[n].matrix_basis = b.matrix_local.inverted() @ M
            else:
                pbs[n].matrix_basis = rel.inverted() @ P.inverted() @ M
        self.posed = posed
        return posed

def two_bone(a, target, l1, l2, hint):
    """Return middle joint position for chain a->mid->target with lengths l1,l2, bending toward hint."""
    a = Vector(a); t = Vector(target)
    d = t - a; dist = d.length
    dist = min(max(dist, abs(l1 - l2) + 1e-4), l1 + l2 - 1e-4)
    dn = d.normalized()
    t = a + dn * dist
    x = (l1*l1 - l2*l2 + dist*dist) / (2*dist)
    h = math.sqrt(max(l1*l1 - x*x, 0))
    hv = Vector(hint) - dn * Vector(hint).dot(dn)
    if hv.length < 1e-6: hv = Vector((0, -1, 0))
    return a + dn * x + hv.normalized() * h, t
