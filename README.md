# Sharding Lab

    docker compose up -d                 # shard0..3 + directory
    uv sync
    uv run seed.py                       # needs router.shard_for
    uv run load.py                       # uniform load
    uv run load.py --celebrity-share 0.3 # 30% of traffic on user 42
    docker compose --profile grow up -d  # brings up shard4
    docker stop shard2                   # break things

## Experiments (you write each one in experiments/)

1. Modulo routing. Seed, then switch to 5 shards. How many rows are now on the wrong shard?
2. Consistent hashing. Same question, same numbers. Compare.
3. Hot key. Run load with a celebrity. Find the hot shard from the numbers alone, then fix it.
4. Range on created_at. Show where every write lands.
5. Scatter-gather. Top 10 posts by likes across all shards. Measure it, then make it cheap.
6. Cross-shard transfer. Move money from a user on one shard to a user on another.
   Kill the second shard mid-transfer. No money may be created or destroyed.
7. Bonus: run the same schema on Citus and compare what it does for you.
