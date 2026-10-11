"""Run several load.py processes at once and sum their results, so the Python client isn't the bottleneck."""
import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--procs", type=int, default=4)
parser.add_argument("--workers", type=int, default=24)
parser.add_argument("--celebrity-share", type=float, default=0.0)
args = parser.parse_args()

cmd = [sys.executable, "load.py", "--workers", str(args.workers), "--celebrity-share", str(args.celebrity_share)]
procs = [subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(args.procs)]
ops: dict[int, float] = defaultdict(float)
p50: dict[int, list[float]] = defaultdict(list)
p99: dict[int, list[float]] = defaultdict(list)
for p in procs:
    out, err = p.communicate()
    if "Error" in err:
        print(err.strip().splitlines()[-1], file=sys.stderr)
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s+\d+\s+(\d+)\s+([\d.]+)\s+([\d.]+)", line)
        if m:
            n = int(m[1])
            ops[n] += float(m[2])
            p50[n].append(float(m[3]))
            p99[n].append(float(m[4]))

print(f"{args.procs} procs x {args.workers} workers, celebrity share {args.celebrity_share}")
print(f"{'shard':>5} {'ops/s':>8} {'p50 ms':>8} {'p99 ms':>8}")
for n in sorted(ops):
    print(f"{n:>5} {ops[n]:>8.0f} {max(p50[n]):>8.2f} {max(p99[n]):>8.2f}")
print(f"total {sum(ops.values()):>8.0f}")
