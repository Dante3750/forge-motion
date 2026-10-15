"""Print the render jobs for shard i of n:  python jobs.py i n"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
exec(open("patterns.py").read())
jobs = [(p, g) for p in sorted(P) for g in ("m", "f")]
i, n = int(sys.argv[1]), int(sys.argv[2])
only = os.environ.get("ONLY", "").split(",") if os.environ.get("ONLY") else None
if only: jobs = [j for j in jobs if j[0] in only]
for k, (p, g) in enumerate(jobs):
    if k % n == i: print(p, g)
