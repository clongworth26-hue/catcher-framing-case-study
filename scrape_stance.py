#!/usr/bin/env python3
"""
Scrape Baseball Savant Catcher Stance leaderboard (knee-down rate + stance-split
framing/blocking/throwing run values). Data available 2020+.
Joins to framing data to build the knee-down "stolen strikes" case study.
"""
import csv
import io
import json
import os
import time
import urllib.request

URL = ("https://baseballsavant.mlb.com/leaderboard/catcher-stance"
       "?type=catcher&seasonStart={y}&seasonEnd={y}&team=&min=q"
       "&sortColumn=num_pitches&sortDirection=desc&csv=true")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Referer": "https://baseballsavant.mlb.com/",
}

YEARS = list(range(2020, 2026))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

import math

FLOAT_COLS = [
    "pitches", "knee_down_pct", "l_down_r_up_pct", "r_down_l_up_pct",
    "both_down_pct", "both_up_pct", "extended_leg_pct", "inside_down_pct",
    "outside_down_pct", "one_knee_framing_rv", "other_framing_rv",
    "one_knee_calledstr_pct", "other_calledstr_pct", "one_knee_blocking_rv",
    "other_blocking_rv", "one_knee_pbwp100", "other_pbwp100",
    "one_knee_throwing_rv", "other_throwing_rv", "one_knee_csaa100",
    "other_csaa100", "catching_rv", "one_knee_pitching_rv", "other_pitching_rv",
]


def fetch(year):
    url = URL.format(y=year)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8-sig")


def main():
    all_rows = []
    for y in YEARS:
        raw = fetch(y)
        rows = list(csv.DictReader(io.StringIO(raw)))
        year_rows = []
        for row in rows:
            rec = {}
            for k, v in row.items():
                if k in FLOAT_COLS:
                    s = (v or "").strip()
                    try:
                        val = float(s) if s else None
                        if val is not None and not math.isfinite(val):
                            val = None
                        rec[k] = val
                    except ValueError:
                        rec[k] = None
                else:
                    rec[k] = v
                if k == "year" and (v or "") == "":
                    rec[k] = y
            rec["season"] = y
            year_rows.append(rec)
            all_rows.append(rec)
        with open(os.path.join(OUT_DIR, f"stance_{y}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(year_rows[0].keys()))
            w.writeheader()
            w.writerows(year_rows)
        print(f"{y}: {len(year_rows)} catchers")
        time.sleep(0.5)

    with open(os.path.join(OUT_DIR, "stance_all.json"), "w") as f:
        json.dump(all_rows, f, indent=1)
    print(f"\nTOTAL: {len(all_rows)} catcher-seasons -> stance_all.json")


if __name__ == "__main__":
    main()
