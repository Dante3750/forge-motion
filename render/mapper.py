import json, re, sys, collections

def has(n, *ws): return any(w in n for w in ws)

def classify(e):
    n = " " + e["name"].lower().replace("-", " ") + " "
    eq = (e.get("equipment") or "body only").lower()
    cat = (e.get("category") or "").lower()
    pm = (e.get("primaryMuscles") or ["?"])[0]
    bb = eq in ("barbell", "e-z curl bar") or has(n, "barbell", "smith", "ez bar", "e z bar", "trap bar")
    db = eq == "dumbbell" or has(n, "dumbbell")
    kb = eq == "kettlebells" or has(n, "kettlebell")
    cable = eq == "cable" or has(n, "cable", "pulley")
    if has(n, "foam roll", " smr", "roller") or eq == "foam roll": return "foam_roll"
    if cat == "stretching" or has(n, " stretch"):
        return {"hamstrings": "stretch_hamstring", "quadriceps": "stretch_quad", "chest": "stretch_chest", "shoulders": "stretch_shoulder",
                "triceps": "stretch_triceps", "calves": "stretch_calf", "glutes": "stretch_hip_flexor", "abductors": "stretch_hip_flexor",
                "adductors": "stretch_butterfly", "lats": "stretch_child", "middle back": "stretch_child", "lower back": "stretch_child",
                "abdominals": "stretch_side", "neck": "stretch_neck", "traps": "stretch_neck", "biceps": "stretch_chest",
                "forearms": "stretch_chest"}.get(pm, "stretch_side")
    if has(n, "snatch"): return "snatch"
    if has(n, " clean") and not has(n, "clean and press"): return "clean"
    if has(n, "jerk", "push press", "thruster", "clean and press"): return "push_press"
    if has(n, "farmer", "carry", "yoke", "suitcase"): return "farmer_walk"
    if has(n, "sled", "prowler", "car push", "truck", "drag"): return "sled_push"
    if has(n, "tire flip", "log lift"): return "deadlift_bb"
    if has(n, "atlas", "keg", "sandbag"): return "deadlift_kb"
    if has(n, "bicycl", " bike", "cycling", "recumbent"): return "bike" if not has(n, "crunch", "air bike") or has(n, "stationary") else "russian_twist"
    if has(n, "rowing, stationary", "rowing machine", "stationary row", "erg"): return "row_erg"
    if has(n, "rope jump", "jump rope", "rope skipping"): return "jump_rope"
    if has(n, "jumping jack", "star jump", "jack"): return "jumping_jack"
    if has(n, "treadmill", "elliptical", "jog", "running", " run ", "sprint", "stair", "trail run", "skating", "high knee", "butt kick", "skip"): return "run"
    if has(n, "walking, treadmill", " walk "): return "walk"
    if has(n, "box jump", "depth jump", "box squat jump", "jump onto"): return "box_jump"
    if has(n, "slam", "throw", "toss", "chest pass", "medicine ball scoop"): return "push_press"
    if has(n, "hanging") and has(n, "leg raise", "knee raise", "leg lift", "knee"): return "hanging_leg_raise"
    if has(n, "pull up", "pullup", "chin up", "chinup", "muscle up", "pull ups", "chin ups"): return "pullup"
    if has(n, "pulldown", "pull down", "lat pull", "straight arm"): return "pulldown"
    if has(n, "leg raise", "knee raise", "flutter", "scissor", "leg lift", "reverse crunch", "knee tuck", "leg pull in"): return "leg_raise"
    if has(n, "pallof", "cable lift", "judo flip", "landmine 180"): return "russian_twist"
    if has(n, "pull through"): return "kb_swing"
    if has(n, "step mill"): return "step_up"
    if has(n, " chins", " chin "): return "pullup"
    if has(n, "russian twist", "twist", "oblique", "wood chop", "woodchop", "side bend", "windmill"): return "russian_twist"
    if has(n, "mountain climber", "climber"): return "mountain_climber"
    if has(n, "rollout", "ab roller", "roll out", "wheel"): return "ab_rollout"
    if has(n, "crunch"): return "crunch"
    if has(n, "sit up", "situp", "jackknife", "v up", "toe touch", "ab bench", "sit ups"): return "situp"
    if has(n, "plank", "hollow", "dead bug", "bird dog"): return "plank"
    if has(n, "hyperextension", "back extension", "superman", "reverse hyper"): return "back_ext"
    if has(n, "hip thrust", "hip lift"): return "hip_thrust_bb"
    if has(n, "glute bridge", "bridge", "butt lift", "hip raise", "glute kickback", "donkey", "fire hydrant", "clam"): return "glute_bridge"
    if has(n, "good morning"): return "good_morning"
    if has(n, "romanian", "stiff leg", "stiff legged", " rdl", "single leg deadlift"): return "rdl_db" if (db or not bb) else "rdl_bb"
    if has(n, "swing"): return "kb_swing"
    if has(n, "deadlift", "rack pull"):
        if has(n, "sumo") or kb: return "deadlift_kb"
        return "deadlift_db" if db else "deadlift_bb"
    if has(n, "leg press", "hack squat", "sled 45"): return "leg_press"
    if has(n, "leg extension"): return "leg_extension"
    if has(n, "leg curl", "hamstring curl", "glute ham", "nordic"): return "leg_curl"
    if has(n, "calf", "calves", "heel raise", "toe raise"): return "calf_raise_seated" if has(n, "seated") else "calf_raise"
    if has(n, "step up", "stepup"): return "step_up"
    if has(n, "split squat", "bulgarian"): return "split_squat"
    if has(n, "lunge"): return "lunge_bb" if bb else "lunge_db" if (db or kb) else "lunge"
    if has(n, "jump squat", "squat jump", "tuck jump", "frog jump", "jump", "hop", "bound", "split jump", "lateral jump", "plyo"): return "jump_squat"
    if has(n, "front squat", "zercher"): return "squat_front_bb"
    if has(n, "goblet"): return "squat_goblet"
    if has(n, "squat"):
        if bb: return "squat_bb"
        if db or kb: return "squat_goblet"
        return "squat_bw"
    if has(n, "pullover", "pull over"): return "pullover"
    if has(n, "fly", "flye", "pec deck", "crossover", "butterfly"):
        if has(n, "reverse", "rear"): return "rear_fly"
        return "cable_fly" if (cable or eq == "machine") else "fly_db"
    if has(n, "push up", "pushup", "push ups", "pushups", "press up"): return "pushup"
    if has(n, "dip"): return "bench_dip" if has(n, "bench") else "dips"
    if has(n, "skull", "lying triceps", "french press", "tate press", "jm press", "lying close grip triceps"): return "skullcrusher"
    if has(n, "pushdown", "push down", "pressdown"): return "pushdown"
    if has(n, "kickback", "kick back"): return "kickback"
    if pm == "triceps" and has(n, "extension", "overhead"): return "oh_ext"
    if has(n, "bench press", "floor press", "chest press", "board press", "pin press", "close grip bench", "close grip press"):
        inc = has(n, "incline")
        if db and not bb: return "incline_db" if inc else "bench_db"
        return "incline_bb" if inc else "bench_bb"
    if has(n, "lateral raise", "side raise", "side lateral", "lateral delt", "y raise", "lu raise"): return "lateral_raise" if not has(n, "rear", "bent over") else "rear_fly"
    if has(n, "front raise", "front plate raise") or (has(n, "front", "incline shoulder", "deltoid", "scaption", "straight raises") and has(n, "raise")): return "front_raise"
    if has(n, "rotation") and pm == "shoulders": return "lateral_raise"
    if has(n, "rear delt", "reverse fly", "rear lateral", "bent over lateral", "reverse flye"): return "rear_fly"
    if has(n, "upright row"): return "upright_row"
    if has(n, "face pull"): return "face_pull"
    if has(n, "shrug"): return "shrug"
    if has(n, " row", "rows"):
        if cable or has(n, "seated"): return "row_cable"
        return "row_bb" if (bb or has(n, "t bar", "inverted", "pendlay")) else "row_db"
    if has(n, "preacher", "scott", "spider curl"): return "preacher_curl"
    if has(n, "wrist", "finger curl", "reverse curl" if pm == "forearms" else "@@", "wrist roller"): return "wrist_curl"
    if has(n, "hammer"): return "hammer_curl"
    if has(n, "curl"):
        if cable: return "cable_curl"
        if bb: return "curl_bb"
        return "curl_db"
    if has(n, "press", "military", "arnold"):
        if pm in ("shoulders", "triceps"):
            if has(n, "seated", "arnold"): return "seated_ohp_db"
            return "ohp_bb" if bb else "ohp_db"
        if pm == "chest": return "incline_bb" if has(n, "incline") else ("bench_db" if db else "bench_bb")
    # fallbacks by muscle
    fb = {"quadriceps": "squat_bb" if bb else "squat_bw", "hamstrings": "rdl_bb" if bb else "rdl_db", "glutes": "glute_bridge",
          "calves": "calf_raise", "chest": "pushup" if eq == "body only" else ("bench_bb" if bb else "bench_db"),
          "shoulders": "ohp_bb" if bb else "lateral_raise" if cable else "ohp_db", "triceps": "pushdown" if cable else "oh_ext",
          "biceps": "curl_bb" if bb else "cable_curl" if cable else "curl_db", "lats": "pulldown" if (cable or eq == "machine") else "pullup",
          "middle back": "row_cable" if cable else "row_bb" if bb else "row_db", "lower back": "back_ext", "traps": "shrug",
          "abdominals": "crunch", "forearms": "wrist_curl", "neck": "stretch_neck", "adductors": "squat_goblet", "abductors": "glute_bridge"}
    return fb.get(pm, "squat_bw") + "|fb"

if __name__ == "__main__":
    ex = json.load(open(sys.argv[1]))
    m = {}; fbs = []
    for e in ex:
        r = classify(e)
        if r.endswith("|fb"): r = r[:-3]; fbs.append((e["name"], e.get("equipment"), r))
        m[e["id"]] = r
    c = collections.Counter(m.values())
    print(len(c), c.most_common())
    print("fallbacks", len(fbs))
    for f in fbs: print("  ", f)
    json.dump(m, open(sys.argv[2], "w"), indent=0, sort_keys=True)
