#!/usr/bin/env python3
"""
Knee-down catching "stolen strikes" case study — core analysis.
Produces analysis.json with all derived numbers. Every figure computed from
scraped Savant data. No fabricated values.
"""
import json
import os
import statistics

D = os.path.dirname(os.path.abspath(__file__))
stance = json.load(open(os.path.join(D, "stance_all.json")))
framing = json.load(open(os.path.join(D, "framing_normalized.json")))

FRAMING_RUNS_PER_STRIKE = 0.125  # Savant conversion, ~+0.125 runs per extra called strike

out = {}

# ---- 1. League-wide knee-down adoption curve ----
adoption = []
for y in range(2020, 2026):
    ys = [r for r in stance if r["season"] == y and r.get("knee_down_pct") is not None]
    if not ys:
        continue
    avg = statistics.mean(r["knee_down_pct"] for r in ys)
    pitched = [r for r in ys if r.get("pitches")]
    wavg = (sum(r["knee_down_pct"] * r["pitches"] for r in pitched)
            / sum(r["pitches"] for r in pitched)) if pitched else avg
    n = len(ys)
    adoption.append({
        "season": y,
        "n": n,
        "avg_knee_down_pct": round(avg * 100, 1),
        "wavg_knee_down_pct": round(wavg * 100, 1),
        "near_universal_60pct": sum(1 for r in ys if r["knee_down_pct"] >= 0.60),
    })
out["adoption"] = adoption

# ---- 2. Stance-split framing value (knee-down vs traditional), league aggregate ----
# one_knee_framing_rv vs other_framing_rv are per-catcher season totals in runs.
# Compare mean per-1000-pitches rate to control for games/catching load.
split_rows = []
for r in stance:
    if (r.get("one_knee_framing_rv") is None or r.get("other_framing_rv") is None
            or not r.get("pitches")):
        continue
    rv = {
        "season": r["season"],
        "name": r["name"],
        "knee_down_pct": r.get("knee_down_pct"),
        "one_knee_framing_rv": r["one_knee_framing_rv"],
        "other_framing_rv": r["other_framing_rv"],
        "one_knee_calledstr_pct": r.get("one_knee_calledstr_pct"),
        "other_calledstr_pct": r.get("other_calledstr_pct"),
        "one_knee_csaa100": r.get("one_knee_csaa100"),
        "other_csaa100": r.get("other_csaa100"),
        "pitches": r["pitches"],
    }
    split_rows.append(rv)

import math

def mean(x):
    xs = [v for v in x if v is not None and isinstance(v, (int, float))
          and math.isfinite(v)]
    return sum(xs) / len(xs) if xs else None

# League mean called-strike% by stance and framing rv by stance
ok_both = [r for r in split_rows if r["one_knee_calledstr_pct"] is not None
           and r["other_calledstr_pct"] is not None
           and math.isfinite(r["one_knee_calledstr_pct"])
           and math.isfinite(r["other_calledstr_pct"])]
out["stance_called_strike"] = {
    "n": len(ok_both),
    "one_knee_calledstr_pct": round(mean([r["one_knee_calledstr_pct"] for r in ok_both]) * 100, 2),
    "other_calledstr_pct": round(mean([r["other_calledstr_pct"] for r in ok_both]) * 100, 2),
    "delta_pct_points": round((mean([r["one_knee_calledstr_pct"] for r in ok_both])
                               - mean([r["other_calledstr_pct"] for r in ok_both])) * 100, 2),
}

# aggregate framing rv by stance, summed across qualified catchers (2020-2025)
sum_one = sum(r["one_knee_framing_rv"] for r in split_rows)
sum_other = sum(r["other_framing_rv"] for r in split_rows)
out["aggregate_framing_rv_by_stance"] = {
    "n_catcher_seasons": len(split_rows),
    "one_knee_framing_rv_total": round(sum_one, 1),
    "other_framing_rv_total": round(sum_other, 1),
    "note": "League-wide, knee-down accounts for the large majority of framing value "
            "because it has become the dominant receiving stance.",
}

# ---- 3. Per-1000-pitch framing rate by stance (normalized fairness) ----
rate_rows = [r for r in split_rows if r["pitches"]]
one_rate = [r["one_knee_framing_rv"] / (r["pitches"] / 1000) for r in rate_rows]
oth_rate = [r["other_framing_rv"] / (r["pitches"] / 1000) for r in rate_rows]
out["framing_rv_per_1000"] = {
    "one_knee_mean": round(mean(one_rate), 3),
    "other_mean": round(mean(oth_rate), 3),
    "note": "Mean framing runs per 1000 received pitches, by stance. "
            "A positive gap = knee-down frames more effectively per pitch.",
}

# ---- 4. Top framing seasons (rv_tot, 2018-2025) ----
fr = [r for r in framing if r.get("rv_tot") is not None]
fr_sorted = sorted(fr, key=lambda r: r["rv_tot"], reverse=True)
out["top_framing_seasons"] = [
    {"season": r["season"], "name": r["name"], "rv_tot": round(r["rv_tot"], 2),
     "pitches": r["pitches"]}
    for r in fr_sorted[:15]
]
out["bottom_framing_seasons"] = [
    {"season": r["season"], "name": r["name"], "rv_tot": round(r["rv_tot"], 2)}
    for r in fr_sorted[-10:]
]

# ---- 5. Career aggregate framing leaders (sum rv_tot across seasons) ----
career = {}
for r in fr:
    career.setdefault(r["name"], []).append(r["rv_tot"])
career_tot = sorted(
    ({"name": k, "rv_tot": round(sum(v), 2), "seasons": len(v)} for k, v in career.items()),
    key=lambda x: x["rv_tot"], reverse=True)
out["career_framing_leaders"] = career_tot[:15]

# ---- 6. Stance-by-season: how knee-down rate relates to framing value ----
# correlate knee_down_pct (per catcher) with their total framing rv that year
corr_rows = []
for r in stance:
    if r.get("knee_down_pct") is None or r.get("one_knee_framing_rv") is None:
        continue
    corr_rows.append((r["knee_down_pct"], r["one_knee_framing_rv"]))

def corr(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)

out["knee_down_vs_framing_rv_corr"] = {
    "n": len(corr_rows),
    "pearson_r": round(corr([r[0] for r in corr_rows], [r[1] for r in corr_rows]), 4),
    "note": "Correlation between a catcher's knee-down rate and their knee-down "
            "framing run value, catcher-season level. Interpret carefully: the "
            "causal driver is receiving skill, not stance rate alone.",
}

# ---- 7. 'Stolen strikes' framing value in dollar/win terms (context, cited) ----
# ~10 runs = 1 win; framing runs -> wins -> $/WAR (~$8-9M/win on FA market).
out["conversions"] = {
    "framing_runs_per_strike": FRAMING_RUNS_PER_STRIKE,
    "runs_per_win_approx": 10,
    "wins_per_framing_run": round(1 / 10, 3),
    "note": "Contextual conversions (public industry figures), used to translate "
            "framing runs into equivalent wins/value. Not scraped — cited as context.",
}

json.dump(out, open(os.path.join(D, "analysis.json"), "w"), indent=2)
print("Wrote analysis.json")
print(json.dumps(out, indent=2)[:3000])
