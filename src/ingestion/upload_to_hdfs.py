"""Upload local parquet files to HDFS using the hdfs CLI.

Idempotent: skips files that already exist with the same size.
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("upload_to_hdfs")

FILENAME_RE = re.compile(r"(?P<type>\w+)_tripdata_(?P<year>\d{4})-(?P<month>\d{2})\.parquet")


def hdfs(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["hdfs", "dfs", *args], capture_output=True, text=True, check=False)


def ensure_dir(path: str) -> None:
    hdfs("-mkdir", "-p", path)


def remote_size(path: str) -> int | None:
    res = hdfs("-stat", "%b", path)
    if res.returncode != 0:
        return None
    try:
        return int(res.stdout.strip())
    except ValueError:
        return None


def upload(local: Path, hdfs_root: str) -> bool:
    match = FILENAME_RE.match(local.name)
    if not match:
        log.warning("Skipping unrecognized filename: %s", local.name)
        return True

    year = match.group("year")
    month = match.group("month")
    target_dir = f"{hdfs_root}/year={year}/month={month}"
    target_path = f"{target_dir}/{local.name}"

    ensure_dir(target_dir)

    rsize = remote_size(target_path)
    if rsize is not None and rsize == local.stat().st_size:
        log.info("Already uploaded: %s", target_path)
        return True

    log.info("Uploading %s -> %s", local, target_path)
    res = hdfs("-put", "-f", str(local), target_path)
    if res.returncode != 0:
        log.error("Upload failed: %s", res.stderr)
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data/raw", type=Path)
    parser.add_argument("--hdfs-root", default="/data/nyc-taxi/raw")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = sorted(args.input_dir.glob("*.parquet"))
    if not files:
        log.error("No parquet files found in %s", args.input_dir)
        return 1
    failures = sum(1 for f in files if not upload(f, args.hdfs_root))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
