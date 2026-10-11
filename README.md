# Sharding Lab

A hands-on lab for database sharding: 4 Postgres shards in Docker, a router, and a load
generator. One database is taken step by step to a sharded cluster, and each step is measured.

## Run it

    docker compose up -d                             # shard0..3 (5440-5443) + directory (5449)
    uv sync
    uv run seed.py                                   # 200K users, placed by router.shard_for
    uv run load.py --workers 32                      # one load generator
    uv run experiments/bench.py --procs 4            # several generators at once, results summed
    uv run experiments/bench.py --procs 8 --celebrity-share 0.3   # 30% of traffic on user 42
    uv run experiments/consistent_hashing.py         # key movement: modulo vs hash ring
    docker compose --profile grow up -d              # brings up shard4

All routing goes through `router.shard_for(user_id)`. Each load operation is one `INSERT`
plus one indexed `count(*)`.

## Results

Measured on a laptop (10 cores given to Docker), so treat the throughput numbers as relative.

### 1. One database

| Clients | ops/s | p50 |
|---|---|---|
| 1 process × 24 workers | 3,192 | 5.9 ms |
| 2 processes × 24 workers | 6,169 | 6.1 ms |
| 4 processes × 24 workers | 6,171 | 11.1 ms |

- The single-node ceiling is about **6.2K ops/s**. Past that point, extra clients only add latency.
- The first measurement said 4.2K. That was the limit of one Python load generator (GIL), not
  Postgres. `bench.py` runs several generators so the client isn't the bottleneck.
- At 128 connections Postgres refuses clients (`max_connections` = 100). Too many connections
  calls for a pooler such as PgBouncer. Too much work calls for sharding.

### 2. Four shards with `user_id % 4`

- A perfectly even split: 50,000 users per shard.
- Total throughput was not reliably higher than one node (3.9K–9.4K ops/s across runs). All four
  shards share the same laptop CPU as the load generators.
- **Hot key:** with 30% of traffic on one user, that shard reached p50 65 ms and p99 760 ms, while
  the others stayed at about 19 ms p50. Cluster throughput fell by about a third.

### 3. Resharding: modulo vs consistent hashing

Users that have to move to a different shard when one shard is added (200K users):

| Change | Modulo | Consistent hashing (100 vnodes/shard) |
|---|---|---|
| 4 → 5 shards | 160,000 (80%) | 40,888 (20%) |
| 16 → 17 shards | 188,225 (94%) | 12,447 (6%) |

- With consistent hashing, every moved user goes to the new shard. None move between old shards.
- The cost is balance: 37.7K–44.4K users per shard instead of an exact 50K.
- Either way, the data still has to be migrated: copy, dual-write, verify, then switch the router.

## Still to do

4. Range on `created_at`: show where every write lands.
5. Scatter-gather: top 10 posts by likes across all shards.
6. Cross-shard transfer: move money between shards, kill one mid-transfer, lose nothing.
7. Bonus: the same schema on Citus.
