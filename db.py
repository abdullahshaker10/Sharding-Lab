from contextlib import contextmanager

import psycopg

SHARD_PORTS = {0: 5440, 1: 5441, 2: 5442, 3: 5443, 4: 5444}
DIRECTORY_PORT = 5449
DSN = "host=localhost port={port} user=lab password=lab dbname=lab"


@contextmanager
def shard(n: int):
    with psycopg.connect(DSN.format(port=SHARD_PORTS[n]), autocommit=True) as conn:
        yield conn


@contextmanager
def directory():
    with psycopg.connect(DSN.format(port=DIRECTORY_PORT), autocommit=True) as conn:
        yield conn


def truncate_all(shards: list[int]) -> None:
    for n in shards:
        with shard(n) as conn:
            conn.execute("TRUNCATE users, accounts, posts")


def row_counts(shards: list[int]) -> dict[int, int]:
    counts = {}
    for n in shards:
        with shard(n) as conn:
            counts[n] = conn.execute("SELECT count(*) FROM users").fetchone()[0]
    return counts
