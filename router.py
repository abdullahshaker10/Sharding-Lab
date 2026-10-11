SHARDS = [0, 1, 2, 3]


def shard_for(user_id: int) -> int:
    
    return SHARDS[user_id % len(SHARDS)]
