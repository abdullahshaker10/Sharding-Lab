import argparse
from collections import defaultdict

from db import row_counts, shard, truncate_all
from router import SHARDS, shard_for

BATCH = 5_000


def seed(n_users: int) -> None:
    truncate_all(SHARDS)
    buckets: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for user_id in range(1, n_users + 1):
        buckets[shard_for(user_id)].append((user_id, f"user-{user_id}"))
    for n, rows in buckets.items():
        with shard(n) as conn, conn.cursor() as cur:
            with cur.copy("COPY users (id, name) FROM STDIN") as copy:
                for row in rows:
                    copy.write_row(row)
            with cur.copy("COPY accounts (user_id, balance) FROM STDIN") as copy:
                for user_id, _ in rows:
                    copy.write_row((user_id, 1_000))
    print(row_counts(SHARDS))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=200_000)
    seed(parser.parse_args().users)
