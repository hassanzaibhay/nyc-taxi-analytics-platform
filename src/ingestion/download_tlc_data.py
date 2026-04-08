"""Download NYC TLC parquet files from the public CloudFront mirror."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("download_tlc")

BASE_URL = os.environ.get("TLC_BASE_URL", "https://d37ci6vzurychx.cloudfront.net/trip-data")


def file_url(taxi_type: str, year: int, month: int) -> str:
    return f"{BASE_URL}/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet"


def download_one(url: str, dest: Path) -> bool:
    """Download a single file with resume support. Returns True on success."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    log.info("HEAD %s", url)
    head = requests.head(url, allow_redirects=True, timeout=30)
    if head.status_code != 200:
        log.error("File not available: %s (HTTP %s)", url, head.status_code)
        return False

    remote_size = int(head.headers.get("Content-Length", "0"))
    if dest.exists() and dest.stat().st_size == remote_size:
        log.info("Already downloaded: %s", dest.name)
        return True

    log.info("Downloading %s -> %s", url, dest)
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as fh, tqdm(
            total=remote_size, unit="B", unit_scale=True, desc=dest.name
        ) as bar:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)
                    bar.update(len(chunk))

    if dest.stat().st_size != remote_size and remote_size > 0:
        log.error("Size mismatch for %s", dest)
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=int(os.environ.get("TLC_START_YEAR", "2024")))
    parser.add_argument("--start-month", type=int, default=int(os.environ.get("TLC_START_MONTH", "1")))
    parser.add_argument("--end-month", type=int, default=int(os.environ.get("TLC_END_MONTH", "3")))
    parser.add_argument("--taxi-type", default=os.environ.get("TLC_TAXI_TYPE", "yellow"))
    parser.add_argument("--output-dir", default="data/raw", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = 0
    for month in range(args.start_month, args.end_month + 1):
        url = file_url(args.taxi_type, args.year, month)
        dest = args.output_dir / f"{args.taxi_type}_tripdata_{args.year:04d}-{month:02d}.parquet"
        if not download_one(url, dest):
            failures += 1
    if failures:
        log.error("%s downloads failed", failures)
        return 1
    log.info("All downloads complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
