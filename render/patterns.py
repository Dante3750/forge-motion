# Male-unit poses (body height 1.73 m). Front of body faces -Y. Positions in metres.
def LR(l, r=None):
    if r is None: r = (-l[0], *l[1:]) if isinstance(l, tuple) else l
    return {"L": l, "R": r}
def tor(x, y, z): return {"L": ("torso", (x, y, z)), "R": ("torso", (-x, y, z))}
def pel(x, y, z): return {"L": ("pelvis", (x, y, z)), "R": ("pelvis", (-x, y, z))}

STAND = dict(pelvis=(0, 0.05, 0.905), pelvis_tilt=0, torso=2, head=0,
             feet=LR((0.12, 0.0, 0.075)), toes=LR(10), knee=LR((0.1, -1, 0)))
def st(**kw):
    d = dict(STAND); d.update(kw); return d
def mk(base, **kw):
    d = dict(base); d.update(kw); return d

SIDES = {"L": ("hang", (0.045, 0.0, -0.53)), "R": ("hang", (-0.045, 0.0, -0.53))}  # weights hang straight down under the shoulders
HIPS = pel(0.17, -0.03, 0.10)          # hands on hips
BACKBAR = tor(0.32, 0.07, -0.05)       # bar on traps
P = {}

# ---------------- legs ----------------
sq_top = st(feet=LR((0.2, 0.0, 0.075)), toes=LR(22), knee=LR((0.45, -1, 0)), torso=6)
sq_bot = mk(sq_top, pelvis=(0, 0.24, 0.52), pelvis_tilt=30, torso=44, head=-32)
bb = dict(hands=BACKBAR, elbow=LR((0.5, 0.8, -1)), grip=LR(0.8))
P["squat_bb"] = dict(cam="bar34", props=["barbell"], keys=[mk(sq_top, **bb), mk(sq_bot, **bb)])
fr = dict(hands=tor(0.19, -0.17, -0.10), elbow=LR((0.15, -1, 0.35)), grip=LR(0.5))
P["squat_front_bb"] = dict(cam="bar34", props=["barbell"], keys=[mk(sq_top, **fr), mk(sq_bot, torso=24, pelvis_tilt=20, pelvis=(0, 0.18, 0.50), **{k: v for k, v in sq_bot.items() if k not in ("torso", "pelvis_tilt", "pelvis")}, **fr)])
gb = dict(hands=tor(0.07, -0.13, -0.30), elbow=LR((0.3, 0.2, -1)), grip=LR(0.8), db_axis=(0, 0, 1), db_off=(0, 0.05, 0.02))
P["squat_goblet"] = dict(cam="side", props=["dumbbell"], keys=[mk(sq_top, **gb), mk(sq_bot, torso=30, **{k: v for k, v in sq_bot.items() if k != "torso"}, **gb)])
P["squat_bw"] = dict(cam="side", props=[], keys=[
    mk(sq_top, hands=LR((0.17, -0.58, 1.30)), elbow=LR((0.4, 0.3, -1)), grip=LR(0.2)),
    mk(sq_bot, hands=LR((0.17, -0.62, 0.92)), elbow=LR((0.4, 0.3, -1)), grip=LR(0.2))])

lg_top = st(feet=LR((0.12, -0.42, 0.075), (-0.12, 0.42, 0.11)), foot_pitch=LR(30, 65) if False else {"L": 30, "R": 65},
            pelvis=(0, 0.03, 0.83), knee=LR((0.1, -1, 0)), toes=LR(6))
lg_bot = mk(lg_top, pelvis=(0, 0.04, 0.50), torso=4)
P["lunge"] = dict(cam="side", props=[], keys=[mk(lg_top, hands=HIPS, elbow=LR((1, 0.3, 0))), mk(lg_bot, hands=HIPS, elbow=LR((1, 0.3, 0)))])
P["lunge_db"] = dict(cam="side", props=["dumbbells"], keys=[mk(lg_top, hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8)), mk(lg_bot, hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8))])
P["lunge_bb"] = dict(cam="bar34", props=["barbell"], keys=[mk(lg_top, **bb), mk(lg_bot, **bb)])
bs_top = st(feet={"L": (0.12, -0.32, 0.075), "R": (-0.12, 0.62, 0.50)}, foot_pitch={"L": 30, "R": -10}, pelvis=(0, 0.10, 0.86), knee=LR((0.1, -1, 0)))
bs_bot = mk(bs_top, pelvis=(0, 0.14, 0.55), torso=12, pelvis_tilt=8)
P["split_squat"] = dict(cam="side", props=["dumbbells"], benches=[dict(y0=0.72, length=0.5, height=0.45)],
    keys=[mk(bs_top, hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8)), mk(bs_bot, hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8))])

dl_bot = st(pelvis=(0, 0.28, 0.64), pelvis_tilt=48, torso=58, head=-45, feet=LR((0.14, 0.0, 0.075)), knee=LR((0.2, -1, 0)),
            hands=LR((0.24, -0.06, 0.24)), elbow=LR((0.3, 0.5, 0)), grip=LR(0.85))
dl_top = st(feet=LR((0.14, 0.0, 0.075)), hands=LR((0.24, -0.04, 0.76)), elbow=LR((0.3, 0.5, 0)), grip=LR(0.85))
P["deadlift_bb"] = dict(cam="bar34", props=["barbell"], keys=[dl_top, dl_bot])
P["deadlift_db"] = dict(cam="side", props=["dumbbells"], keys=[mk(dl_top, hands=LR((0.22, 0.0, 0.76)), db_axis=(0, 1, 0)), mk(dl_bot, hands=LR((0.20, -0.02, 0.18)), db_axis=(0, 1, 0))])
sumo_top = st(feet=LR((0.27, 0.0, 0.075)), toes=LR(30), knee=LR((0.6, -1, 0)), hands=LR((0.035, -0.04, 0.72)), elbow=LR((0.3, 0.3, 0)), grip=LR(0.85))
sumo_bot = mk(sumo_top, pelvis=(0, 0.16, 0.58), pelvis_tilt=30, torso=38, head=-30, hands=LR((0.035, -0.06, 0.30)))
P["deadlift_kb"] = dict(cam="side", props=["kettlebell"], keys=[sumo_top, sumo_bot])
rdl_top = st(hands=LR((0.24, -0.04, 0.76)), elbow=LR((0.3, 0.5, 0)), grip=LR(0.85), knee=LR((0.1, -1, 0)))
rdl_bot = mk(rdl_top, pelvis=(0, 0.24, 0.86), pelvis_tilt=60, torso=78, head=-55, hands=LR((0.24, -0.16, 0.40)))
P["rdl_bb"] = dict(cam="bar34", props=["barbell"], keys=[rdl_top, rdl_bot])
P["rdl_db"] = dict(cam="side", props=["dumbbells"], keys=[mk(rdl_top, hands=LR((0.22, -0.02, 0.76)), db_axis=(1, 0, 0)), mk(rdl_bot, hands=LR((0.20, -0.16, 0.40)), db_axis=(1, 0, 0))])
P["good_morning"] = dict(cam="bar34", props=["barbell"], keys=[mk(STAND, **bb), mk(STAND, pelvis=(0, 0.22, 0.87), pelvis_tilt=62, torso=82, head=-60, **bb)])

ht_top = dict(pelvis=(0, -0.02, 0.62), pelvis_tilt=-88, torso=-92, head=40, feet=LR((0.17, -0.38, 0.075)), toes=LR(12),
              knee=LR((0.3, -0.5, 1)), hands=pel(0.30, -0.15, 0.04), elbow=LR((1, 0, 0.3)), grip=LR(0.8))
ht_bot = mk(ht_top, pelvis=(0, 0.10, 0.24), pelvis_tilt=-40, torso=-55, head=30)
P["hip_thrust_bb"] = dict(cam="front34", cam_b="side_low", props=["barbell"], plates=True, benches=[dict(y0=0.62, length=0.42, height=0.42)], keys=[ht_bot, ht_top])
gbr_bot = dict(pelvis=(0, 0.05, 0.12), pelvis_tilt=-90, torso=-92, head=0, feet=LR((0.15, -0.32, 0.075)), toes=LR(8),
               knee=LR((0.2, -0.3, 1)), hands=LR((0.26, 0.12, 0.035)), elbow=LR((1, 0, 0.2)), grip=LR(0.1), wrist_dir=LR((0, -1, 0)))
gbr_top = mk(gbr_bot, pelvis=(0, 0.02, 0.36), pelvis_tilt=-120, torso=-128, head=20)
P["glute_bridge"] = dict(cam="floor", props=["mat"], keys=[gbr_bot, gbr_top])

lp_bent = dict(pelvis=(0, 0.12, 0.48), pelvis_tilt=-40, torso=-48, head=30, feet=LR((0.15, -0.42, 0.88)), foot_pitch=LR(-35), toes=LR(10),
               knee=LR((0.3, -0.2, 1)), hands=LR((0.27, 0.12, 0.42)), elbow=LR((1, 0, 0)), grip=LR(0.8))
lp_ext = mk(lp_bent, feet=LR((0.15, -0.70, 1.20)))
P["leg_press"] = dict(cam="side", props=[], benches=[dict(y0=0.25, length=0.55, height=0.38, back=(45, (0, 0.55, 0.62)))],
    follow=[dict(size=(0.7, 0.05, 0.55), at="feet", off=(0, -0.10, 0.05), rot=(-45, 0, 0))], keys=[lp_ext, lp_bent])
le_bot = dict(pelvis=(0, 0.10, 0.60), pelvis_tilt=-8, torso=-12, head=10, feet=LR((0.10, -0.40, 0.14)), foot_pitch=LR(0), toes=LR(0),
              knee=LR((0.1, -1, 0.4)), hands=LR((0.24, 0.05, 0.52)), elbow=LR((1, 0.3, 0)), grip=LR(0.8))
le_top = mk(le_bot, feet=LR((0.10, -0.92, 0.56)))
P["leg_extension"] = dict(cam="side", props=[], benches=[dict(y0=0.15, length=0.6, height=0.50, back=(12, (0, 0.47, 0.88)))],
    follow=[dict(size=(0.5, 0.09, 0.09), at="feet", off=(0, -0.07, 0.05), mat="pad")], keys=[le_bot, le_top])
lc_bot = dict(pelvis=(0, 0.22, 0.60), pelvis_tilt=92, torso=90, head=20, feet=LR((0.10, 1.07, 0.60)), foot_pitch=LR(80), toes=LR(0),
              knee=LR((0, 0.2, -1)), hands=LR((0.18, -0.66, 0.44)), elbow=LR((1, 0, -0.3)), grip=LR(0.8))
lc_top = mk(lc_bot, feet=LR((0.10, 0.62, 1.04)))
P["leg_curl"] = dict(cam="side", props=[], benches=[dict(y0=0.0, length=1.4, height=0.45)],
    follow=[dict(size=(0.5, 0.09, 0.09), at="feet", off=(0, 0.05, 0.06), mat="pad")], keys=[lc_bot, lc_top])
cr_bot = mk(STAND, hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8))
cr_top = mk(cr_bot, pelvis=(0, 0.05, 0.99), feet=LR((0.12, 0.0, 0.16)), foot_pitch=LR(72))
P["calf_raise"] = dict(cam="side", props=["dumbbells"], keys=[cr_bot, cr_top])
sc_bot = dict(pelvis=(0, 0.10, 0.55), pelvis_tilt=0, torso=4, feet=LR((0.12, -0.40, 0.075)), foot_pitch=LR(30), knee=LR((0.1, -1, 0)),
              hands=LR((0.10, -0.38, 0.62)), elbow=LR((1, 0, 0)), grip=LR(0.6))
sc_top = mk(sc_bot, feet=LR((0.12, -0.40, 0.16)), foot_pitch=LR(70), hands=LR((0.10, -0.38, 0.70)))
P["calf_raise_seated"] = dict(cam="side", props=[], benches=[dict(y0=0.15, length=0.55, height=0.45)],
    follow=[dict(size=(0.45, 0.14, 0.05), at="knees", off=(0, 0.04, 0.10), mat="pad")], keys=[sc_bot, sc_top])
su1 = st(feet=LR((0.12, 0.10, 0.075)), hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8))
su2 = st(feet={"L": (0.12, -0.36, 0.52), "R": (-0.12, 0.10, 0.075)}, foot_pitch={"L": 30, "R": 30}, pelvis=(0, -0.04, 0.95), torso=14, hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8))
su3 = st(feet=LR((0.12, -0.38, 0.52)), pelvis=(0, -0.33, 1.36), hands=SIDES, db_axis=(0, 1, 0), grip=LR(0.8))
P["step_up"] = dict(cam="side", props=["dumbbells", "box"], box=dict(h=0.45, y=-0.42), keys=[su1, su2, su3, su2])
js_bot = mk(sq_bot, hands=tor(0.24, 0.25, -0.50), elbow=LR((0.3, -0.5, -1)), grip=LR(0.2))
js_air = st(pelvis=(0, 0.05, 1.18), feet=LR((0.14, 0.02, 0.33)), foot_pitch=LR(75), hands=tor(0.25, -0.05, 0.62), elbow=LR((0.5, 0, 0)), grip=LR(0.1))
P["jump_squat"] = dict(cam="side", props=[], keys=[js_bot, js_air])
bj_land = mk(sq_bot, pelvis=(0, -0.38, 1.12), feet=LR((0.2, -0.55, 0.575)), torso=36, hands=tor(0.2, -0.45, -0.2), grip=LR(0.2))
bj_stand = st(pelvis=(0, -0.55, 1.41), feet=LR((0.14, -0.6, 0.575)), hands=tor(0.22, 0.0, -0.58), elbow=LR((0.3, 0.3, -1)), grip=LR(0.2))
bj_step = st(pelvis=(0, -0.25, 1.18), torso=8, feet={"L": (0.14, -0.6, 0.575), "R": (-0.14, 0.02, 0.075)}, foot_pitch={"L": 30, "R": 40},
             knee=LR((0.1, -1, 0)), hands=tor(0.22, 0.0, -0.58), elbow=LR((0.3, 0.3, -1)), grip=LR(0.2))
bj_floor = st(feet=LR((0.14, 0.02, 0.075)), hands=tor(0.22, 0.0, -0.58), elbow=LR((0.3, 0.3, -1)), grip=LR(0.2))
P["box_jump"] = dict(cam="side", props=["box"], box=dict(h=0.5, y=-0.6), tempo=[0.9, 0.7, 0.8, 1.0, 1.1, 1.0, 0.9],
    keys=[js_bot, mk(js_air, pelvis=(0, -0.25, 1.35), feet=LR((0.14, -0.3, 0.60))), bj_land, bj_stand, bj_step, bj_floor, js_bot])
kb_bot = st(pelvis=(0, 0.22, 0.83), pelvis_tilt=45, torso=62, head=-50, feet=LR((0.2, 0.0, 0.075)), toes=LR(18), knee=LR((0.3, -1, 0)),
            hands=LR((0.03, 0.18, 0.56)), elbow=LR((0.3, 0, 0)), grip=LR(0.85))
kb_top = st(feet=LR((0.2, 0.0, 0.075)), toes=LR(18), hands=LR((0.03, -0.58, 1.25)), elbow=LR((0.3, 0, 0)), grip=LR(0.85))
P["kb_swing"] = dict(cam="side", props=["kettlebell"], keys=[kb_bot, kb_top])

def nw(x, y, z): return {"L": ("neckw", (x, y, z)), "R": ("neckw", (-x, y, z))}
# ---------------- push ----------------
FLAT = dict(pelvis=(0, -0.05, 0.56), pelvis_tilt=-88, torso=-90, head=8, feet=LR((0.30, -0.42, 0.075)), toes=LR(20),
            knee=LR((0.4, -0.2, 1)), grip=LR(0.8))
FLATB = [dict(y0=0.25, length=1.25, height=0.45)]
P["bench_bb"] = dict(cam="lying", props=["barbell"], benches=FLATB, keys=[
    mk(FLAT, hands=LR((0.40, 0.42, 1.18)), elbow=LR((1, 0, -0.4))), mk(FLAT, hands=LR((0.40, 0.40, 0.74)), elbow=LR((1, 0, -0.4)))])
P["bench_db"] = dict(cam="lying", props=["dumbbells"], benches=FLATB, keys=[
    mk(FLAT, hands=LR((0.18, 0.42, 1.17)), elbow=LR((1, 0, -0.4)), db_axis=(1, 0, 0)), mk(FLAT, hands=LR((0.34, 0.40, 0.76)), elbow=LR((1, 0, -0.4)), db_axis=(1, 0, 0))])
INC = dict(pelvis=(0, 0.06, 0.56), pelvis_tilt=-30, torso=-52, head=20, feet=LR((0.28, -0.45, 0.075)), toes=LR(20), knee=LR((0.4, -1, 0.5)), grip=LR(0.8))
INCB = [dict(y0=0.12, length=0.45, height=0.45, back=(52, (0, 0.40, 0.78)))]
P["incline_bb"] = dict(cam="lying", props=["barbell"], benches=INCB, keys=[
    mk(INC, hands=LR((0.38, 0.30, 1.42)), elbow=LR((1, 0.3, -0.4))), mk(INC, hands=LR((0.38, 0.22, 1.04)), elbow=LR((1, 0.3, -0.4)))])
P["incline_db"] = dict(cam="lying", props=["dumbbells"], benches=INCB, keys=[
    mk(INC, hands=LR((0.17, 0.30, 1.42)), elbow=LR((1, 0.3, -0.4)), db_axis=(1, 0, 0)), mk(INC, hands=LR((0.34, 0.24, 1.06)), elbow=LR((1, 0.3, -0.4)), db_axis=(1, 0, 0))])
P["pushup"] = dict(cam="side", props=["mat"], keys=[
    dict(pelvis=(0, 0.30, 0.43), pelvis_tilt=78, torso=76, head=8, feet=LR((0.12, 1.12, 0.10)), toes=LR(0),
         foot_pitch=LR(95), knee=LR((0, 0, -1)), hands=LR((0.24, -0.38, 0.06)), elbow=LR((0.6, 0.6, 0.6)), grip=LR(0.05)),
    dict(pelvis=(0, 0.30, 0.25), pelvis_tilt=88, torso=88, head=10, feet=LR((0.12, 1.15, 0.10)), toes=LR(0),
         foot_pitch=LR(95), knee=LR((0, 0, -1)), hands=LR((0.24, -0.38, 0.06)), elbow=LR((0.8, 0.6, 0.6)), grip=LR(0.05))])
DIP = dict(pelvis=(0, 0.04, 1.30), pelvis_tilt=0, torso=6, head=0, feet=LR((0.10, 0.30, 0.78)), foot_pitch=LR(50), knee=LR((0.1, -1, 0)),
           hands=LR((0.30, -0.10, 1.29)), elbow=LR((0.2, 1, 0)), grip=LR(0.8))
P["dips"] = dict(cam="front34", props=["dipbars"], keys=[DIP, mk(DIP, pelvis=(0, 0.10, 0.98), torso=22, pelvis_tilt=10, feet=LR((0.10, 0.36, 0.46)))])
BD = dict(pelvis=(0, 0.10, 0.56), pelvis_tilt=0, torso=0, head=0, feet=LR((0.14, -0.62, 0.075)), foot_pitch=LR(-10), knee=LR((0.1, -1, 0.5)),
          hands=LR((0.20, 0.26, 0.48)), elbow=LR((0.2, 1, 0)), grip=LR(0.6), wrist_dir=LR((0, -1, 0)))
P["bench_dip"] = dict(cam="side", props=[], benches=[dict(y0=0.52, length=0.55, height=0.45)], keys=[BD, mk(BD, pelvis=(0, 0.14, 0.30), torso=8)])
OH = st(grip=LR(0.8), feet=LR((0.15, 0.0, 0.075)))
P["ohp_bb"] = dict(cam="bar34", props=["barbell"], keys=[
    mk(OH, hands=tor(0.26, -0.15, -0.06), elbow=LR((0.3, -0.6, -1))), mk(OH, hands=tor(0.26, -0.03, 0.56), elbow=LR((1, 0, 0)))])
P["ohp_db"] = dict(cam="front34", props=["dumbbells"], keys=[
    mk(OH, hands=tor(0.31, -0.06, -0.02), elbow=LR((1, 0.1, -1)), db_axis=(1, 0, 0)), mk(OH, hands=tor(0.17, -0.03, 0.57), elbow=LR((1, 0, 0)), db_axis=(1, 0, 0))])
SEAT = dict(pelvis=(0, 0.10, 0.56), pelvis_tilt=0, torso=0, head=0, feet=LR((0.25, -0.40, 0.075)), toes=LR(15), knee=LR((0.3, -1, 0)), grip=LR(0.8))
P["seated_ohp_db"] = dict(cam="front34", props=["dumbbells"], benches=[dict(y0=0.15, length=0.45, height=0.45, back=(5, (0, 0.40, 0.85)))], keys=[
    mk(SEAT, hands=tor(0.31, -0.06, -0.02), elbow=LR((1, 0.1, -1)), db_axis=(1, 0, 0)), mk(SEAT, hands=tor(0.17, -0.03, 0.57), elbow=LR((1, 0, 0)), db_axis=(1, 0, 0))])
P["lateral_raise"] = dict(cam="front34", props=["dumbbells"], keys=[
    mk(OH, hands=tor(0.22, -0.03, -0.56), elbow=LR((0.3, 0.6, 0)), db_axis=(0, 1, 0)), mk(OH, hands=tor(0.70, -0.05, -0.10), elbow=LR((0, 0.6, 1)), db_axis=(0, 1, 0))])
P["front_raise"] = dict(cam="side", props=["dumbbells"], keys=[
    mk(OH, hands=tor(0.18, -0.08, -0.56), elbow=LR((0.3, 0.6, 0)), db_axis=(1, 0, 0)), mk(OH, hands=tor(0.18, -0.62, -0.08), elbow=LR((0.4, 0, -1)), db_axis=(1, 0, 0))])
BO = st(pelvis=(0, 0.20, 0.86), pelvis_tilt=50, torso=72, head=-50, knee=LR((0.15, -1, 0)), feet=LR((0.14, 0.0, 0.075)), grip=LR(0.8))
P["rear_fly"] = dict(cam="front34", props=["dumbbells"], keys=[
    mk(BO, hands=nw(0.15, -0.02, -0.56), elbow=LR((1, 0.3, 0)), db_axis=(0, 1, 0)), mk(BO, hands=nw(0.64, 0.0, -0.10), elbow=LR((0.2, 0.2, 1)), db_axis=(0, 1, 0))])
P["fly_db"] = dict(cam="lying", props=["dumbbells"], benches=FLATB, keys=[
    mk(FLAT, hands=LR((0.10, 0.42, 1.14)), elbow=LR((1, 0, -0.1)), db_axis=(0, 1, 0)), mk(FLAT, hands=LR((0.66, 0.42, 0.66)), elbow=LR((0.2, 0, -1)), db_axis=(0, 1, 0))])
P["cable_fly"] = dict(cam="front34", props=["cable"], pulley={"L": (0.85, 0.10, 1.85), "R": (-0.85, 0.10, 1.85)}, keys=[
    mk(OH, torso=12, feet={"L": (0.12, -0.25, 0.075), "R": (-0.12, 0.25, 0.075)}, hands=LR((0.72, -0.05, 1.42)), elbow=LR((0.3, 1, -0.5))),
    mk(OH, torso=12, feet={"L": (0.12, -0.25, 0.075), "R": (-0.12, 0.25, 0.075)}, hands=LR((0.07, -0.52, 1.05)), elbow=LR((1, 0.3, -0.3)))])
P["pushdown"] = dict(cam="side", props=["cable"], pulley=(0, -0.55, 2.05), keys=[
    mk(OH, torso=8, hands=tor(0.10, -0.32, -0.24), elbow=LR((0.15, 0.6, -1))), mk(OH, torso=8, hands=tor(0.11, -0.16, -0.62), elbow=LR((0.15, 0.6, -1)))])
P["oh_ext"] = dict(cam="side", props=["dumbbell"], keys=[
    mk(OH, hands=tor(0.04, 0.02, 0.58), elbow=LR((0.2, -0.3, 1)), db_axis=(0, 0, 1), db_off=(0, 0, -0.04)),
    mk(OH, hands=tor(0.04, 0.24, 0.16), elbow=LR((0.2, -0.3, 1)), db_axis=(0, 0, 1), db_off=(0, 0, -0.04))])
P["skullcrusher"] = dict(cam="lying", props=["barbell"], plates=False, benches=FLATB, keys=[
    mk(FLAT, hands=LR((0.14, 0.44, 1.12)), elbow=LR((0.3, 0, 1))), mk(FLAT, hands=LR((0.14, 0.70, 0.74)), elbow=LR((0.3, -0.4, 1)))])
P["kickback"] = dict(cam="side", props=["dumbbells"], keys=[
    mk(BO, torso=65, hands=nw(0.17, 0.30, -0.42), elbow=LR((0.1, 1, 0.4)), db_axis=(0, 0, 1)),
    mk(BO, torso=65, hands=nw(0.17, 0.62, -0.12), elbow=LR((0.1, 0, 1)), db_axis=(0, 0, 1))])

# ---------------- pull & arms ----------------
HANG = dict(pelvis=(0, 0.06, 1.12), pelvis_tilt=0, torso=4, head=0, feet=LR((0.10, 0.22, 0.36)), foot_pitch=LR(60), knee=LR((0.1, -1, 0)),
            hands=LR((0.34, 0.0, 2.17)), elbow=LR((1, 0.2, -0.3)), grip=LR(0.85))
P["pullup"] = dict(cam="hang", props=["pullbar"], keys=[HANG, mk(HANG, pelvis=(0, 0.10, 1.50), torso=10, feet=LR((0.10, 0.28, 0.74)))])
PD = mk(SEAT, torso=-10, pelvis=(0, 0.10, 0.56), feet=LR((0.16, -0.45, 0.075)))
P["pulldown"] = dict(cam="front34", props=["cable", "barbell"], plates=False, pulley=(0, 0.0, 2.35), benches=[dict(y0=0.15, length=0.45, height=0.45)], keys=[
    mk(PD, hands=LR((0.42, -0.08, 1.62)), elbow=LR((1, 0.2, -0.3))), mk(PD, hands=LR((0.34, -0.02, 1.08)), elbow=LR((1, 0.6, -1)))])
P["row_bb"] = dict(cam="bar34", props=["barbell"], keys=[
    mk(BO, hands=nw(0.25, -0.03, -0.58), elbow=LR((0.4, 1, 0))), mk(BO, hands=nw(0.25, 0.20, -0.32), elbow=LR((0.4, 1, 0.5)))])
P["row_db"] = dict(cam="side", props=["dumbbells"], keys=[
    mk(BO, hands=nw(0.20, -0.03, -0.58), elbow=LR((0.2, 1, 0)), db_axis=(0, 1, 0)), mk(BO, hands=nw(0.21, 0.24, -0.32), elbow=LR((0.2, 1, 0.5)), db_axis=(0, 1, 0))])
CR = dict(pelvis=(0, 0.25, 0.45), pelvis_tilt=0, torso=0, head=0, feet=LR((0.15, -0.55, 0.30)), foot_pitch=LR(-20), knee=LR((0.2, -0.3, 1)), grip=LR(0.85))
P["row_cable"] = dict(cam="side", props=["cable"], pulley=(0, -0.95, 0.45), benches=[dict(y0=0.30, length=0.65, height=0.35)],
    follow=[dict(size=(0.5, 0.05, 0.3), at="none", off=(0, -0.66, 0.22), rot=(-20, 0, 0))], keys=[
    mk(CR, torso=18, hands=LR((0.10, -0.62, 0.78)), elbow=LR((0.4, 0.3, -1))), mk(CR, torso=-6, hands=LR((0.13, -0.10, 0.82)), elbow=LR((0.4, 1, 0)))])
SH = mk(OH, hands=tor(0.24, -0.10, -0.62), elbow=LR((0.3, 0.6, 0)))
P["shrug"] = dict(cam="bar34", props=["barbell"], keys=[mk(SH, shrug=0.0), mk(SH, shrug=1.0, hands=tor(0.24, -0.10, -0.56))])
P["upright_row"] = dict(cam="bar34", props=["barbell"], keys=[
    mk(OH, hands=tor(0.12, -0.12, -0.60), elbow=LR((1, 0, 0))), mk(OH, hands=tor(0.12, -0.15, -0.12), elbow=LR((1, 0.2, 1)))])
P["face_pull"] = dict(cam="front34", props=["cable"], pulley=(0, -1.05, 1.62), keys=[
    mk(OH, torso=-4, feet={"L": (0.12, -0.18, 0.075), "R": (-0.12, 0.2, 0.075)}, hands=LR((0.07, -0.55, 1.46)), elbow=LR((1, 0, 0.3))),
    mk(OH, torso=-4, feet={"L": (0.12, -0.18, 0.075), "R": (-0.12, 0.2, 0.075)}, hands=LR((0.22, -0.20, 1.58)), elbow=LR((1, 0.3, 0.4)))])
CURL = dict(elbow=LR((0.0, 0.4, -1)), grip=LR(0.85))
P["curl_bb"] = dict(cam="side", props=["barbell"], plates=False, keys=[mk(OH, hands=tor(0.20, -0.05, -0.56), **CURL), mk(OH, hands=tor(0.20, -0.17, -0.12), **CURL)])
P["hammer_curl"] = dict(cam="front34", props=["dumbbells"], keys=[
    mk(OH, hands=tor(0.21, -0.02, -0.56), db_axis=(0, 1, 0), **CURL), mk(OH, hands=tor(0.21, -0.16, -0.11), db_axis=(0, 0.3, 1), **CURL)])
P["cable_curl"] = dict(cam="side", props=["cable"], pulley=(0, -0.75, 0.15), keys=[mk(OH, hands=tor(0.18, -0.07, -0.56), **CURL), mk(OH, hands=tor(0.18, -0.17, -0.12), **CURL)])
PC = mk(SEAT, torso=18, feet=LR((0.2, -0.30, 0.075)))
P["preacher_curl"] = dict(cam="side", props=["barbell"], plates=False, benches=[dict(y0=0.15, length=0.45, height=0.45)],
    follow=[dict(size=(0.55, 0.30, 0.06), at="none", off=(0, -0.36, 0.86), rot=(-50, 0, 0), mat="pad")], keys=[
    mk(PC, hands=LR((0.17, -0.70, 0.66)), elbow=LR((0.1, -0.2, -1))), mk(PC, hands=LR((0.17, -0.42, 1.12)), elbow=LR((0.1, -0.6, -1)))])
WC = mk(SEAT, torso=28, feet=LR((0.15, -0.42, 0.075)))
P["wrist_curl"] = dict(cam="side", props=["barbell"], plates=False, benches=[dict(y0=0.15, length=0.45, height=0.45)], keys=[
    mk(WC, hands=LR((0.12, -0.60, 0.58)), elbow=LR((0.2, 0.5, -1)), wrist_dir=LR((0, -0.4, -1))),
    mk(WC, hands=LR((0.12, -0.60, 0.58)), elbow=LR((0.2, 0.5, -1)), wrist_dir=LR((0, -0.4, 1)))])
P["pullover"] = dict(cam="lying", props=["dumbbell"], benches=FLATB, keys=[
    mk(FLAT, hands=LR((0.05, 0.40, 1.10)), elbow=LR((1, 0, 0.2)), db_axis=(0, 0, 1), db_off=(0, 0, 0.06)),
    mk(FLAT, hands=LR((0.05, 1.08, 0.66)), elbow=LR((1, 0, 0.2)), db_axis=(0, 1, 0), db_off=(0, 0.06, 0))])

# ---------------- core ----------------
SUP = dict(pelvis=(0, 0.05, 0.11), pelvis_tilt=-90, torso=-92, head=0, feet=LR((0.15, -0.36, 0.075)), toes=LR(8),
           knee=LR((0.2, -0.3, 1)), grip=LR(0.3))
HEADH = tor(0.14, 0.05, 0.18)
P["crunch"] = dict(cam="floor", props=["mat"], keys=[mk(SUP, hands=HEADH, elbow=LR((1, 0, 0.3))), mk(SUP, torso=-58, head=12, hands=HEADH, elbow=LR((1, 0, 0.3)))])
P["situp"] = dict(cam="floor", props=["mat"], keys=[mk(SUP, hands=tor(0.08, -0.12, -0.12), elbow=LR((1, 0, 0))), mk(SUP, torso=-12, pelvis_tilt=-40, pelvis=(0, 0.05, 0.12), hands=tor(0.08, -0.12, -0.12), elbow=LR((1, 0, 0)))])
LRB = dict(pelvis=(0, 0.05, 0.11), pelvis_tilt=-90, torso=-92, head=0, feet=LR((0.08, -0.93, 0.08)), foot_pitch=LR(-60), knee=LR((0, 0, 1)),
           hands=LR((0.26, 0.05, 0.035)), elbow=LR((1, 0, 0.2)), grip=LR(0.1), wrist_dir=LR((0, -1, 0)))
P["leg_raise"] = dict(cam="floor", props=["mat"], keys=[LRB, mk(LRB, feet=LR((0.08, -0.08, 0.95)), foot_pitch=LR(-10))])
P["hanging_leg_raise"] = dict(cam="hang", props=["pullbar"], keys=[mk(HANG, feet=LR((0.10, 0.06, 0.28)), foot_pitch=LR(40)),
    mk(HANG, pelvis=(0, 0.10, 1.16), pelvis_tilt=-20, feet=LR((0.10, -0.78, 1.10)), foot_pitch=LR(-40), knee=LR((0, 0, 1)))])
PL = dict(pelvis=(0, 0.30, 0.30), pelvis_tilt=86, torso=86, head=20, feet=LR((0.10, 1.12, 0.10)), foot_pitch=LR(95), knee=LR((0, 0, -1)),
          hands=LR((0.09, -0.46, 0.05)), elbow=LR((0.05, 0.25, -1)), grip=LR(0.4), wrist_dir=LR((0, -1, 0)))
P["plank"] = dict(cam="side", props=["mat"], keys=[PL, mk(PL, pelvis=(0, 0.30, 0.34))])
RT = dict(pelvis=(0, 0.10, 0.11), pelvis_tilt=-30, torso=-38, head=20, feet=LR((0.14, -0.50, 0.24)), foot_pitch=LR(-10), knee=LR((0.2, -0.3, 1)), grip=LR(0.7))
P["russian_twist"] = dict(cam="front_low", props=["mat", "medball"], keys=[
    mk(RT, torso_side=-12, hands=LR((0.30, -0.30, 0.34), (0.04, -0.42, 0.34)), elbow=LR((1, 0, -0.6))),
    mk(RT, torso_side=12, hands=LR((-0.04, -0.42, 0.34), (-0.30, -0.30, 0.34)), elbow=LR((1, 0, -0.6)))])
MC = dict(pelvis=(0, 0.30, 0.50), pelvis_tilt=72, torso=72, head=10, feet=LR((0.12, 1.08, 0.10)), toes=LR(0), foot_pitch=LR(95), knee=LR((0, 0, -1)),
          hands=LR((0.24, -0.36, 0.06)), elbow=LR((0.2, 0.6, 0.3)), grip=LR(0.05))
P["mountain_climber"] = dict(cam="side", props=["mat"], keys=[
    mk(MC, feet={"L": (0.12, 0.36, 0.30), "R": (-0.12, 1.08, 0.10)}, knee={"L": (0, -1, -0.15), "R": (0, 0, -1)}),
    mk(MC, feet={"L": (0.12, 1.08, 0.10), "R": (-0.12, 0.36, 0.30)}, knee={"L": (0, 0, -1), "R": (0, -1, -0.15)})])
BE = dict(pelvis=(0, -0.02, 0.86), pelvis_tilt=92, torso=165, head=0, feet=LR((0.10, 0.84, 0.82)), foot_pitch=LR(170), knee=LR((0, 0, -1)),
          hands=tor(0.10, -0.16, -0.16), elbow=LR((1, -0.5, 0)), grip=LR(0.6))
P["back_ext"] = dict(cam="side", props=[], benches=[dict(y0=0.42, length=0.9, height=0.76)], keys=[BE, mk(BE, torso=92, head=-10)])
AR = dict(pelvis=(0, 0.02, 0.55), pelvis_tilt=28, torso=55, head=-30, feet=LR((0.12, 0.48, 0.08)), foot_pitch=LR(160), knee=LR((0.05, -0.2, -1)),
          hands=LR((0.12, -0.42, 0.12)), elbow=LR((0.3, 0.5, 0)), grip=LR(0.8), ball_off=(0, 0, -0.03))
P["ab_rollout"] = dict(cam="side", props=["mat", "medball"], keys=[AR, mk(AR, pelvis=(0, -0.20, 0.34), pelvis_tilt=72, torso=86, head=-10, hands=LR((0.12, -1.02, 0.12)))])

# ---------------- olympic / strongman ----------------
cl_pull = st(pelvis=(0, 0.02, 0.97), torso=-4, pelvis_tilt=-4, head=5, feet=LR((0.14, 0.0, 0.15)), foot_pitch=LR(62),
             hands=LR((0.24, -0.08, 0.92)), elbow=LR((1, 0.3, 0.4)), grip=LR(0.85), shrug=1.0)
cl_catch = mk(sq_top, pelvis=(0, 0.14, 0.70), pelvis_tilt=14, torso=16, head=-10, **fr)
cl_stand = mk(sq_top, **fr)
P["clean"] = dict(cam="bar34", props=["barbell"], keys=[dl_bot, mk(dl_top, hands=LR((0.24, -0.05, 0.62))), cl_pull, cl_catch, cl_stand])
sn_bot = mk(dl_bot, hands=LR((0.43, -0.06, 0.24)), pelvis=(0, 0.28, 0.60))
sn_pull = mk(cl_pull, hands=LR((0.43, -0.06, 1.00)))
sn_catch = mk(sq_bot, pelvis=(0, 0.16, 0.58), pelvis_tilt=20, torso=24, head=-10, hands=tor(0.45, 0.06, 0.52), elbow=LR((1, 0, 0)), grip=LR(0.85))
sn_stand = mk(sq_top, hands=tor(0.45, 0.04, 0.55), elbow=LR((1, 0, 0)), grip=LR(0.85))
P["snatch"] = dict(cam="bar34", props=["barbell"], keys=[sn_bot, sn_pull, sn_catch, sn_stand])
pp_rack = mk(OH, hands=tor(0.24, -0.16, -0.08), elbow=LR((0.2, -0.8, -1)))
pp_dip = mk(pp_rack, pelvis=(0, 0.08, 0.80), torso=4)
pp_top = mk(OH, hands=tor(0.25, -0.02, 0.56), elbow=LR((1, 0, 0)))
P["push_press"] = dict(cam="bar34", props=["barbell"], keys=[pp_rack, pp_dip, pp_top])
def gait(base, stride=0.30, lift=0.18, arm=0.25, armz=-0.58, side_hands=None, run=False):
    keys = []
    for ph in (0, 1, 2, 3):
        fL = [(0.12, -stride, 0.075), (0.12, 0.0, 0.075 + lift), (0.12, stride, 0.10), (0.12, 0.0, 0.075)][ph]
        fR = [(-0.12, stride, 0.10), (-0.12, 0.0, 0.075), (-0.12, -stride, 0.075), (-0.12, 0.0, 0.075 + lift)][ph]
        fpL = [20, 40, 55, 30][ph]; fpR = [55, 30, 20, 40][ph]
        k = mk(base, feet={"L": fL, "R": fR}, foot_pitch={"L": fpL, "R": fpR}, pelvis=(0, base["pelvis"][1], base["pelvis"][2] - (0.04 if ph in (0, 2) else 0.0)))
        if side_hands is None:
            sw = [1, 0, -1, 0][ph] * arm
            k["hands"] = {"L": ("torso", (0.20, sw if not run else sw, armz if not run else -0.30)), "R": ("torso", (-0.20, -sw, armz if not run else -0.30))}
            k["elbow"] = LR((0.2, 1, -0.3)) if run else LR((0.2, 0.2, -1))
        keys.append(k)
    return keys
P["farmer_walk"] = dict(cam="front34", props=["kettlebells"], keys=gait(mk(OH, hands=tor(0.24, 0.0, -0.58), grip=LR(0.9)), side_hands=True))
P["run"] = dict(cam="side", props=[], keys=gait(st(torso=10, grip=LR(0.5)), stride=0.42, lift=0.30, arm=0.22, run=True))
P["walk"] = dict(cam="side", props=[], keys=gait(st(grip=LR(0.3)), stride=0.28, lift=0.10, arm=0.16))
SLED = st(torso=52, pelvis_tilt=40, pelvis=(0, 0.20, 0.80), head=-35, hands=LR((0.25, -0.62, 0.98)), elbow=LR((0.4, 0.3, -1)), grip=LR(0.8))
P["sled_push"] = dict(cam="side", props=[], follow=[dict(size=(0.7, 0.45, 0.42), at="grip", off=(0, -0.26, -0.80)), dict(size=(0.62, 0.05, 0.85), at="grip", off=(0, -0.05, -0.45))], keys=gait(SLED, stride=0.35, lift=0.12, side_hands=True))
BK = dict(pelvis=(0, 0.12, 0.98), pelvis_tilt=20, torso=28, head=-15, hands=LR((0.20, -0.50, 1.08)), elbow=LR((0.6, 0.3, -1)), grip=LR(0.8), knee=LR((0.15, -1, 0.2)))
def pedal(a):
    import math
    c = (0.0, -0.18, 0.32); r = 0.17
    def f(ang, x): return (x, c[1] + r * math.cos(ang), c[2] + r * math.sin(ang))
    return {"L": f(a, 0.12), "R": f(a + math.pi, -0.12)}
P["bike"] = dict(cam="side", props=[], follow=[dict(size=(0.18, 0.30, 0.05), at="none", off=(0, 0.13, 0.86), mat="pad"),
    dict(size=(0.06, 0.06, 0.85), at="none", off=(0, 0.06, 0.43)), dict(size=(0.5, 0.05, 0.05), at="none", off=(0, -0.52, 1.06)),
    dict(size=(0.06, 0.06, 1.0), at="none", off=(0, -0.42, 0.55), rot=(-15, 0, 0)), dict(size=(0.12, 0.7, 0.12), at="none", off=(0, -0.18, 0.06))],
    keys=[mk(BK, feet=pedal(a * 1.5708), foot_pitch=LR(25)) for a in range(4)])
ER = dict(pelvis=(0, 0.20, 0.42), pelvis_tilt=0, torso=0, head=0, feet=LR((0.12, -0.62, 0.28)), foot_pitch=LR(-30), knee=LR((0.15, -0.3, 1)), grip=LR(0.85))
P["row_erg"] = dict(cam="side", props=["cable"], pulley=(0, -1.0, 0.55),
    follow=[dict(size=(0.3, 0.35, 0.06), at="none", off=(0, 0.0, 0.0), mat="pad"), dict(size=(0.12, 2.0, 0.08), at="none", off=(0, -0.2, 0.2))], keys=[
    mk(ER, pelvis=(0, -0.20, 0.42), torso=30, pelvis_tilt=20, hands=LR((0.14, -0.75, 0.60)), elbow=LR((0.3, 0.2, -1))),
    mk(ER, pelvis=(0, 0.25, 0.42), torso=-18, pelvis_tilt=-10, feet=LR((0.12, -0.62, 0.28)), hands=LR((0.14, -0.05, 0.86)), elbow=LR((0.5, 1, -0.2)))])
P["jump_rope"] = dict(cam="front34", props=[], keys=[
    st(hands=tor(0.30, -0.08, -0.50), elbow=LR((0.4, 0.4, -1)), feet=LR((0.10, 0.0, 0.10)), foot_pitch=LR(55), pelvis=(0, 0.05, 0.89)),
    st(hands=tor(0.30, -0.04, -0.48), elbow=LR((0.4, 0.4, -1)), feet=LR((0.10, 0.0, 0.22)), foot_pitch=LR(65), pelvis=(0, 0.05, 1.02))])
P["jumping_jack"] = dict(cam="front", props=[], keys=[
    st(hands=tor(0.24, 0.0, -0.58), elbow=LR((0.3, 0.3, -1)), grip=LR(0.2)),
    st(feet=LR((0.42, 0.0, 0.075)), toes=LR(18), pelvis=(0, 0.05, 0.86), hands=tor(0.24, 0.0, 0.62), elbow=LR((1, 0, 0)), grip=LR(0.2))])

# ---------------- stretches & mobility ----------------
SIT = dict(pelvis=(0, 0.10, 0.11), pelvis_tilt=0, torso=0, head=0, feet=LR((0.10, -0.86, 0.08)), foot_pitch=LR(-60), knee=LR((0, 0, 1)), grip=LR(0.3))
P["stretch_hamstring"] = dict(cam="floor", props=["mat"], keys=[mk(SIT, torso=30, pelvis_tilt=10, hands=LR((0.12, -0.45, 0.20)), elbow=LR((1, 0, 0))),
    mk(SIT, torso=62, pelvis_tilt=25, head=-10, hands=LR((0.12, -0.78, 0.14)), elbow=LR((1, 0, 0)))])
QS = st(feet={"L": (0.11, 0.0, 0.075), "R": (-0.13, 0.36, 0.66)}, foot_pitch={"L": 30, "R": -70}, knee={"L": (0.1, -1, 0), "R": (0, 0, -1)},
        hands={"L": ("torso", (0.45, -0.10, -0.30)), "R": (-0.14, 0.38, 0.64)}, elbow=LR((1, 0, -0.3)), grip=LR(0.6))
P["stretch_quad"] = dict(cam="side", props=[], keys=[QS, mk(QS, feet={"L": (0.11, 0.0, 0.075), "R": (-0.13, 0.30, 0.74)}, hands={"L": ("torso", (0.45, -0.10, -0.30)), "R": (-0.14, 0.33, 0.72)})])
P["stretch_chest"] = dict(cam="side", props=[], keys=[mk(OH, hands=tor(0.06, 0.28, -0.52), elbow=LR((1, 0.3, 0)), grip=LR(0.6)),
    mk(OH, hands=tor(0.05, 0.42, -0.45), elbow=LR((1, 0.3, 0)), grip=LR(0.6), head=-12)])
SS = mk(OH, hands={"L": (-0.22, -0.22, 1.33), "R": (-0.02, -0.26, 1.22)}, elbow={"L": (0, -1, -0.3), "R": (-0.2, -0.3, -1)}, grip=LR(0.3))
P["stretch_shoulder"] = dict(cam="front", props=[], keys=[SS, mk(SS, hands={"L": (-0.30, -0.18, 1.33), "R": (-0.06, -0.22, 1.24)})])
TS = mk(OH, hands={"L": ("torso", (-0.03, 0.14, 0.12)), "R": ("torso", (0.04, 0.0, 0.30))}, elbow={"L": (0.2, -0.2, 1), "R": (-0.4, -0.3, 0.3)}, grip=LR(0.3))
P["stretch_triceps"] = dict(cam="front34", props=[], keys=[TS, mk(TS, hands={"L": ("torso", (-0.06, 0.16, 0.08)), "R": ("torso", (0.02, 0.0, 0.32))})])
CS = st(feet={"L": (0.12, -0.20, 0.075), "R": (-0.12, 0.45, 0.075)}, foot_pitch=LR(30), pelvis=(0, 0.02, 0.84), torso=22, pelvis_tilt=18,
        hands=LR((0.24, -0.74, 1.40)), elbow=LR((1, 0, -0.3)), grip=LR(0.1), wrist_dir=LR((0, 0, 1)))
P["stretch_calf"] = dict(cam="side", props=[], follow=[dict(size=(1.2, 0.1, 2.2), at="none", off=(0, -0.86, 1.1), mat="pad")],
    keys=[CS, mk(CS, pelvis=(0, -0.04, 0.80), torso=26)])
HF = dict(pelvis=(0, 0.12, 0.56), pelvis_tilt=-6, torso=-2, head=0, feet={"L": (0.12, -0.42, 0.075), "R": (-0.12, 0.62, 0.08)}, foot_pitch={"L": 30, "R": 165},
          knee={"L": (0.1, -1, 0), "R": (0, 0, -1)}, hands=HIPS, elbow=LR((1, 0.3, 0)), grip=LR(0.4))
P["stretch_hip_flexor"] = dict(cam="side", props=["mat"], keys=[HF, mk(HF, pelvis=(0, 0.02, 0.50), pelvis_tilt=-10)])
SB = mk(OH, feet=LR((0.18, 0, 0.075)), hands={"L": ("torso", (0.10, 0.0, 0.58)), "R": ("torso", (-0.22, 0.0, -0.45))}, elbow={"L": (1, 0, 0), "R": (-0.3, 0.3, -1)}, grip=LR(0.2))
P["stretch_side"] = dict(cam="front", props=[], keys=[mk(SB, torso_side=-4), mk(SB, torso_side=-28, hands={"L": ("torso", (-0.15, 0.0, 0.58)), "R": ("torso", (-0.30, 0.0, -0.40))})])
CH = dict(pelvis=(0, 0.30, 0.26), pelvis_tilt=70, torso=96, head=-10, feet=LR((0.10, 0.62, 0.06)), foot_pitch=LR(170), knee=LR((0.05, -0.3, -1)),
          hands=LR((0.18, -0.70, 0.05)), elbow=LR((1, 0, 0)), grip=LR(0.1), wrist_dir=LR((0, -1, 0)))
P["stretch_child"] = dict(cam="side", props=["mat"], keys=[mk(CH, pelvis=(0, 0.22, 0.34), torso=80, pelvis_tilt=50), CH])
BF = dict(pelvis=(0, 0.10, 0.11), pelvis_tilt=0, torso=8, head=0, feet={"L": (0.03, -0.30, 0.07), "R": (-0.03, -0.30, 0.07)}, toes={"L": -80, "R": -80},
          foot_pitch=LR(10), knee=LR((1, -0.2, 0.3)), hands=LR((0.05, -0.30, 0.14)), elbow=LR((1, 0, 0)), grip=LR(0.7))
P["stretch_butterfly"] = dict(cam="front_low", props=["mat"], keys=[BF, mk(BF, torso=30, pelvis_tilt=10)])
NK = mk(OH, hands={"L": ("torso", (0.20, 0.0, -0.58)), "R": ("torso", (-0.02, 0.0, 0.26))}, elbow={"L": (0.3, 0.3, -1), "R": (-1, 0, 0.3)}, grip=LR(0.3))
P["stretch_neck"] = dict(cam="front", props=[], keys=[mk(NK, head_side=-8), mk(NK, head_side=-32, head=6)])
FR = dict(pelvis=(0, -0.10, 0.30), pelvis_tilt=-95, torso=-98, head=20, feet=LR((0.16, -0.42, 0.075)), toes=LR(8), knee=LR((0.2, -0.3, 1)),
          hands=tor(0.10, -0.12, 0.08), elbow=LR((1, 0, 0.4)), grip=LR(0.6), roller=(0, 0.40, 0.075))
P["foam_roll"] = dict(cam="floor", props=["roller"], keys=[FR, mk(FR, pelvis=(0, -0.28, 0.30), roller=(0, 0.25, 0.075))])
P["curl_db"] = dict(cam="front34", props=["dumbbells"], keys=[
    mk(OH, hands=tor(0.2, -0.02, -0.55), elbow=LR((0.0, 0.4, -1)), grip=LR(0.85), db_axis=(1, 0, 0)),
    mk(OH, hands=tor(0.19, -0.17, -0.11), elbow=LR((0.0, 0.4, -1)), grip=LR(0.85), db_axis=(1, 0, 0))])

# ---------------- home-friendly variants ----------------
P["floor_press_db"] = dict(cam="floor", props=["mat", "dumbbells"], keys=[
    mk(SUP, hands=LR((0.18, 0.40, 0.72)), elbow=LR((1, 0, -0.5)), grip=LR(0.85), db_axis=(1, 0, 0)),
    mk(SUP, hands=LR((0.30, 0.36, 0.34)), elbow=LR((1, 0, -0.6)), grip=LR(0.85), db_axis=(1, 0, 0))])
PI = dict(pelvis=(0, 0.32, 0.70), pelvis_tilt=58, torso=56, head=8, feet=LR((0.12, 0.98, 0.10)), toes=LR(0), foot_pitch=LR(70),
          knee=LR((0, 0, -1)), hands=LR((0.25, -0.46, 0.48)), elbow=LR((0.6, 0.6, 0.4)), grip=LR(0.05), wrist_dir=LR((0, -1, 0.2)))
P["pushup_incline"] = dict(cam="side", props=[], benches=[dict(y0=-0.55, length=0.42, height=0.45)], keys=[PI, mk(PI, pelvis=(0, 0.30, 0.55), pelvis_tilt=66, torso=66, elbow=LR((0.8, 0.6, 0.6)))])
PK = dict(pelvis=(0, 0.20, 0.98), pelvis_tilt=110, torso=140, head=10, feet=LR((0.14, 0.62, 0.10)), toes=LR(0), foot_pitch=LR(60),
          knee=LR((0, -1, 0)), hands=LR((0.22, -0.38, 0.06)), elbow=LR((0.6, 0.6, 0.4)), grip=LR(0.05), wrist_dir=LR((0, -1, 0)))
P["pike_pushup"] = dict(cam="side", props=["mat"], keys=[PK, mk(PK, pelvis=(0, 0.16, 0.86), torso=152, elbow=LR((0.8, 0.6, 0.3)))])
PU = P["pushup"]["keys"]
P["diamond_pushup"] = dict(cam="front34", props=["mat"], keys=[mk(PU[0], pelvis=(0, 0.30, 0.42), hands=LR((0.06, -0.36, 0.06)), elbow=LR((0.3, 1, 0.4))),
    mk(PU[1], hands=LR((0.06, -0.36, 0.06)), elbow=LR((0.3, 1, 0.5)))])
P["pushup_knee"] = dict(cam="side", props=["mat"], keys=[
    dict(pelvis=(0, 0.24, 0.26), pelvis_tilt=63, torso=63, head=10, feet=LR((0.12, 0.92, 0.30)), foot_pitch=LR(-40), knee=LR((0, 0, -1)),
         hands=LR((0.25, -0.22, 0.05)), elbow=LR((0.6, 0.6, 0.6)), grip=LR(0.05)),
    dict(pelvis=(0, 0.21, 0.15), pelvis_tilt=79, torso=79, head=12, feet=LR((0.12, 0.94, 0.26)), foot_pitch=LR(-40), knee=LR((0, 0, -1)),
         hands=LR((0.25, -0.22, 0.05)), elbow=LR((0.8, 0.6, 0.6)), grip=LR(0.05))])
R1 = dict(pelvis=(0, 0.28, 0.86), pelvis_tilt=86, torso=90, head=-10, feet={"L": (0.10, 0.62, 0.50), "R": (-0.26, 0.20, 0.075)},
          foot_pitch={"L": 170, "R": 30}, knee={"L": (0, 0, -1), "R": (-0.2, -1, 0)}, grip=LR(0.85))
P["row_db_single"] = dict(cam="side", props=["dumbbells_R"], benches=[dict(y0=0.15, length=1.0, height=0.45)], keys=[
    mk(R1, hands={"L": (0.14, -0.36, 0.47), "R": ("neckw", (-0.20, 0.0, -0.56))}, elbow={"L": (0.3, 0.3, 0), "R": (-0.2, 1, 0)}, db_axis=(0, 1, 0)),
    mk(R1, hands={"L": (0.14, -0.36, 0.47), "R": ("neckw", (-0.21, 0.24, -0.30))}, elbow={"L": (0.3, 0.3, 0), "R": (-0.2, 1, 0.6)}, db_axis=(0, 1, 0))])
WS = dict(pelvis=(0, 0.14, 0.50), pelvis_tilt=0, torso=-3, head=0, feet=LR((0.15, -0.38, 0.075)), foot_pitch=LR(30), knee=LR((0.1, -1, 0)),
          hands=LR((0.14, -0.30, 0.56)), elbow=LR((1, 0.3, 0)), grip=LR(0.3))
P["wall_sit"] = dict(cam="side", props=[], follow=[dict(size=(1.4, 0.1, 2.2), at="none", off=(0, 0.33, 1.1), mat="pad")], keys=[WS, mk(WS, pelvis=(0, 0.14, 0.49))])
P["cable_lateral"] = dict(cam="front34", props=["cable"], pulley={"L": (-0.55, 0.05, 0.25), "R": (0.55, 0.05, 0.25)}, keys=[
    mk(OH, hands=tor(0.20, -0.06, -0.56), elbow=LR((0.3, 0.6, 0)), grip=LR(0.85)), mk(OH, hands=tor(0.68, -0.05, -0.10), elbow=LR((0, 0.6, 1)), grip=LR(0.85))])
P["goblet_lunge"] = dict(cam="side", props=["dumbbell"], keys=[mk(lg_top, **gb), mk(lg_bot, **gb)])
P["glute_bridge_single"] = dict(cam="floor", props=["mat"], keys=[
    mk(gbr_bot, feet={"L": (0.12, -0.32, 0.075), "R": (-0.12, -0.70, 0.40)}, foot_pitch={"L": 30, "R": -20}, knee={"L": (0.2, -0.3, 1), "R": (0, 0, 1)}),
    mk(gbr_top, feet={"L": (0.12, -0.32, 0.075), "R": (-0.12, -0.80, 0.62)}, foot_pitch={"L": 30, "R": -20}, knee={"L": (0.2, -0.3, 1), "R": (0, 0, 1)})])

# lifting first (start at the bottom): quicker up, slower down. Everything else lowers first.
LIFT_FIRST = {"curl_bb", "curl_db", "hammer_curl", "cable_curl", "preacher_curl", "wrist_curl", "row_bb", "row_db", "row_db_single", "row_cable",
              "pullup", "pulldown", "lateral_raise", "cable_lateral", "front_raise", "rear_fly", "shrug", "upright_row", "face_pull",
              "hip_thrust_bb", "glute_bridge", "glute_bridge_single", "leg_extension", "leg_curl", "calf_raise", "calf_raise_seated",
              "crunch", "situp", "leg_raise", "hanging_leg_raise", "kickback", "pushdown", "back_ext", "cable_fly", "kb_swing"}
for _n, _s in P.items():
    if len(_s["keys"]) == 2 and "tempo" not in _s and not _n.startswith("stretch") and _n not in ("plank", "wall_sit", "foam_roll", "jump_rope", "jumping_jack", "mountain_climber", "russian_twist"):
        _s["tempo"] = [0.42, 0.58] if _n in LIFT_FIRST else [0.58, 0.42]

for _n in ("pushup", "diamond_pushup", "pushup_knee", "pushup_incline", "pike_pushup", "plank", "mountain_climber", "bench_dip", "ab_rollout", "stretch_child"):
    for _k in P[_n]["keys"]: _k["plant"] = True

# ---------------- added after the mapping review ----------------
_FLR = mk(STAND, hands=HIPS, elbow=LR((1, 0.3, 0)), grip=LR(0.4))
P["front_leg_raise"] = dict(cam="side", props=[], tempo=[0.45, 0.55], keys=[
    mk(_FLR, feet={"L": (0.11, 0.0, 0.075), "R": (-0.12, -0.02, 0.075)}),
    mk(_FLR, feet={"L": (0.11, 0.0, 0.075), "R": (-0.12, -0.80, 0.55)}, foot_pitch={"L": 30, "R": -20}, knee={"L": (0.1, -1, 0), "R": (0, 0, 1)})])
P["side_leg_raise"] = dict(cam="front", props=[], tempo=[0.45, 0.55], keys=[
    mk(_FLR, feet={"L": (0.11, 0.0, 0.075), "R": (-0.13, 0.0, 0.075)}),
    mk(_FLR, torso_side=6, feet={"L": (0.11, 0.0, 0.075), "R": (-0.62, 0.0, 0.40)}, knee={"L": (0.1, -1, 0), "R": (0, -1, 0)})])
_GK = dict(pelvis=(0, 0.25, 0.60), pelvis_tilt=85, torso=88, head=10, hands=LR((0.20, -0.36, 0.05)), elbow=LR((0.2, 0.3, -1)), grip=LR(0.1),
           wrist_dir=LR((0, -1, 0)), knee={"L": (0, 0, -1), "R": (0, 0, -1)}, plant=True)
P["glute_kickback"] = dict(cam="side", props=["mat"], tempo=[0.42, 0.58], keys=[
    mk(_GK, feet={"L": (0.12, 0.62, 0.06), "R": (-0.12, 0.55, 0.12)}, foot_pitch={"L": 165, "R": 150}, knee={"L": (0, 0, -1), "R": (0, -1, -0.6)}),
    mk(_GK, feet={"L": (0.12, 0.62, 0.06), "R": (-0.12, 1.02, 0.78)}, foot_pitch={"L": 165, "R": -60}, knee={"L": (0, 0, -1), "R": (0, 0.3, -1)})])
_FK = mk(LRB, head=14)
P["flutter_kick"] = dict(cam="floor", props=["mat"], keys=[
    mk(_FK, feet={"L": (0.08, -0.86, 0.42), "R": (-0.08, -0.90, 0.20)}, foot_pitch=LR(-50)),
    mk(_FK, feet={"L": (0.08, -0.90, 0.20), "R": (-0.08, -0.86, 0.42)}, foot_pitch=LR(-50))])
_RC = dict(pelvis=(0, 0.05, 0.11), pelvis_tilt=-90, torso=-92, head=10, hands=LR((0.26, 0.05, 0.035)), elbow=LR((1, 0, 0.2)), grip=LR(0.1),
           wrist_dir=LR((0, -1, 0)), knee=LR((0.05, -0.5, 1)))
P["reverse_crunch"] = dict(cam="floor", props=["mat"], tempo=[0.42, 0.58], keys=[
    mk(_RC, feet=LR((0.10, -0.55, 0.40)), foot_pitch=LR(-10)),
    mk(_RC, pelvis=(0, 0.08, 0.16), pelvis_tilt=-120, feet=LR((0.10, -0.05, 0.62)), foot_pitch=LR(-40))])
_SP = dict(pelvis=(0, 0.0, 0.42), pelvis_tilt=0, torso=0, torso_side=-62, head=0, lie=None,
           feet={"L": (0.62, 0.0, 0.13), "R": (0.70, -0.06, 0.08)}, foot_pitch=LR(10), knee=LR((0, -1, 0)),
           hands={"L": ("torso", (0.10, -0.05, -0.30)), "R": (-0.50, -0.05, 0.05)}, elbow={"L": (0.3, 0.3, -1), "R": (-0.3, 0, -1)}, grip=LR(0.2))
P["superman"] = dict(cam="side", props=["mat"], tempo=[0.45, 0.55], keys=[
    dict(pelvis=(0, 0.20, 0.13), pelvis_tilt=90, torso=92, head=10, feet=LR((0.12, 1.02, 0.07)), foot_pitch=LR(170), knee=LR((0, 0, -1)),
         hands=LR((0.22, -0.92, 0.05)), elbow=LR((0.3, 0, -1)), grip=LR(0.1), wrist_dir=LR((0, -1, 0))),
    dict(pelvis=(0, 0.20, 0.13), pelvis_tilt=90, torso=80, head=-6, feet=LR((0.12, 1.00, 0.26)), foot_pitch=LR(150), knee=LR((0, 0, -1)),
         hands=LR((0.22, -0.88, 0.32)), elbow=LR((0.3, 0, -1)), grip=LR(0.1), wrist_dir=LR((0, -1, 0)))])
P["side_bend"] = dict(cam="front", props=["dumbbells_R"], keys=[
    mk(OH, torso_side=0, hands={"L": ("torso", (0.10, 0.05, 0.16)), "R": ("torso", (-0.22, -0.02, -0.58))}, elbow={"L": (1, 0, 0.5), "R": (-0.3, 0.3, -1)}, db_axis=(0, 1, 0), grip=LR(0.85)),
    mk(OH, torso_side=-45, hands={"L": ("torso", (0.10, 0.05, 0.16)), "R": ("torso", (-0.22, -0.02, -0.58))}, elbow={"L": (1, 0, 0.5), "R": (-0.3, 0.3, -1)}, db_axis=(0, 1, 0), grip=LR(0.85))])

# ---------------- movement feel ----------------
for _n in ("jumping_jack", "jump_rope", "mountain_climber", "high_knees", "russian_twist", "burpee", "skater", "butt_kick", "box_jump"):
    if _n in P: P[_n]["style"] = "rhythm"
for _n, _s in P.items():
    if _n.startswith("stretch") or _n in ("foam_roll",): _s["style"] = "stretch"
P["jumping_jack"]["air"] = 0.07
