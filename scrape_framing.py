#!/usr/bin/env python3
"""
Scrape Baseball Savant Catcher Framing leaderboard (Statcast/TrackMan era).
Pulls per-catcher framing runs-saved data for every year 2015-2025.
Columns: rv_tot (total framing runs, i.e. "stolen strikes" value in runs),
pitches, and 8 shadow-zone zone-level runs + strike-call percentages.

Truth rule: this only WRITES what Savant actually returns. No fabricated numbers.
"""
import csv
import io
import json
import os
import time
import urllib.request

URL = ("https://baseballsavant.mlb.com/leaderboard/catcher-framing"
       "?type=catcher&seasonStart={y}&seasonEnd={y}&team=&min=q"
       "&sortColumn=rv_tot&sortDirection=asc&csv=true")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Referer": "https://baseballsavant.mlb.com/",
}

YEARS = list(range(2015, 2026))

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)


def fetch(year: int):
    url = URL.format(y=year)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main():
    all_rows = []
    for y in YEARS:
        raw = fetch(y)
        reader = csv.DictReader(io.StringIO(raw))
        year_rows = []
        for row in reader:
            row = {k: v for k, v in row.items() if k}
            row["season"] = y
            year_rows.append(row)
            all_rows.append(row)
        # per-year file
        with open(os.path.join(OUT_DIR, f"framing_{y}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(year_rows[0].keys()))
            w.writeheader()
            w.writerows(year_rows)
        print(f"{y}: {len(year_rows)} catchers")
        time.sleep(0.5)

    # combined JSON
    with open(os.path.join(OUT_DIR, "framing_all.json"), "w") as f:
        json.dump(all_rows, f, indent=1)
    # combined CSV
    if all_rows:
        cols = list(all_rows[0].keys())
        with open(os.path.join(OUT_DIR, "framing_all.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(all_rows)
    print(f"\nTOTAL: {len(all_rows)} catcher-seasons written to {OUT_DIR}")


if __name__ == "__main__":
    main()
