"""How many users move when a 5th shard joins: modulo vs a consistent-hash ring."""
import bisect
import hashlib

USERS = range(1, 200_001)
VNODES = 100


def h(key: str) -> int:
    return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")


def ring(shards: list[int]) -> tuple[list[int], list[int]]:
    points = sorted((h(f"shard{s}-{v}"), s) for s in shards for v in range(VNODES))
    return [p for p, _ in points], [s for _, s in points]


def lookup(r: tuple[list[int], list[int]], user_id: int) -> int:
    keys, owners = r
    return owners[bisect.bisect(keys, h(str(user_id))) % len(keys)]


old, new = ring([0, 1, 2, 3]), ring([0, 1, 2, 3, 4])
moved = [u for u in USERS if lookup(old, u) != lookup(new, u)]
to_new = sum(1 for u in moved if lookup(new, u) == 4)
mod_moved = sum(1 for u in USERS if u % 4 != u % 5)
counts = [0] * 5
for u in USERS:
    counts[lookup(new, u)] += 1

print(f"modulo 4->5:     {mod_moved:,} moved ({mod_moved / len(USERS):.0%})")
print(f"consistent 4->5: {len(moved):,} moved ({len(moved) / len(USERS):.0%}), {to_new:,} of them to the new shard")
print(f"ring balance ({VNODES} vnodes/shard): {counts}")
