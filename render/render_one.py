"""Render one movement loop for one body.  python render_one.py <pattern> <m|f> <outdir> [frames] [res] [samples]"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:]]
name, g, out = args[0], args[1], os.path.abspath(args[2])
frames = int(args[3]) if len(args) > 3 else 32
res = int(args[4]) if len(args) > 4 else 400
samples = int(args[5]) if len(args) > 5 else 28
exec(open("scene.py").read()); exec(open("body.py").read()); exec(open("anim.py").read()); exec(open("patterns.py").read())
angles = tuple(os.environ.get("ANGLES", "a,b").split(","))
render_pattern(name, P[name], g == "f", out, frames=frames, res=res, samples=samples, angles=angles)
