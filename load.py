import argparse
import random
import statistics
import threading
import time
from collections import defaultdict

from db import SHARD_PORTS, DSN
from psycopg_pool import ConnectionPool
from router import SHARDS, shard_for

CELEBRITY_ID = 42


def pick_user(n_users: int, celebrity_share: float) -> int:
    if random.random() < celebrity_share:
        return CELEBRITY_ID
    return random.randint(1, n_users)


def run(n_users: int, seconds: int, workers: int, celebrity_share: float) -> None:
    pools = {
        n: ConnectionPool(DSN.format(port=SHARD_PORTS[n]), min_size=2, max_size=workers, kwargs={"autocommit": True})
        for n in SHARDS
    }
    latencies: dict[int, list[float]] = defaultdict(list)
    lock = threading.Lock()
    deadline = time.monotonic() + seconds

    def worker() -> None:
        while time.monotonic() < deadline:
            user_id = pick_user(n_users, celebrity_share)
            n = shard_for(user_id)
            start = time.perf_counter()
            with pools[n].connection() as conn:
                conn.execute("INSERT INTO posts (id, user_id) VALUES (%s, %s)", (random.getrandbits(62), user_id))
                conn.execute("SELECT count(*) FROM posts WHERE user_id = %s", (user_id,))
            with lock:
                latencies[n].append((time.perf_counter() - start) * 1000)

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"{'shard':>5} {'ops':>8} {'ops/s':>8} {'p50 ms':>8} {'p99 ms':>8}")
    for n in SHARDS:
        samples = sorted(latencies[n]) or [0.0]
        p99 = samples[int(len(samples) * 0.99) - 1] if len(samples) > 1 else samples[0]
        print(f"{n:>5} {len(latencies[n]):>8} {len(latencies[n]) / seconds:>8.0f} {statistics.median(samples):>8.2f} {p99:>8.2f}")
    for pool in pools.values():
        pool.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=200_000)
    parser.add_argument("--seconds", type=int, default=15)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--celebrity-share", type=float, default=0.0)
    args = parser.parse_args()
    run(args.users, args.seconds, args.workers, args.celebrity_share)
