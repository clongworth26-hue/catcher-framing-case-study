# Stolen Strikes — The One-Knee-Down Catching Revolution

A data-grounded case study of how the knee-down receiving setup took over MLB and became
the dominant framing weapon of the TrackMan/Statcast era — measured in **stolen strikes**
and the **runs they save**.

**Live report:** https://clongworth26-hue.github.io/catcher-framing-case-study/

## The question
> "When did knee-down setups become popular, and what did they do for catcher framing —
> from a runs-saved perspective, across the entire TrackMan era?"

## Key findings (all computed from Baseball Savant data)

| Metric | Value |
|---|---|
| Knee-down rate, 2020 → 2025 | **23.7% → 95.3%** |
| Called-strike rate (knee-down vs traditional) | **+2.25 pts** |
| Framing runs / 1,000 pitches (knee-down vs traditional) | **+0.056 vs −0.051** |
| League aggregate framing value, 2020–25 (knee-down vs traditional) | **+244.4 vs −168.4 runs** |
| Best single-season framing | Patrick Bailey, 2025 (+25.05 runs) |
| Career framing leader, 2018–25 | Austin Hedges (+72.1 runs) |

## Data sources
- **Baseball Savant — Catcher Framing leaderboard** (`rv_tot` framing runs, 2015–2025).
  Run-value totals fill in starting 2018 (early TrackMan years report zone strike rates only).
- **Baseball Savant — Catcher Stance leaderboard** (knee-down rate + stance-split
  framing/blocking/throwing run values, 2020–2025).

## Supporting context (cited, not scraped)
- Strike → runs conversion: ~**+0.125 runs per extra called strike** (Savant).
- Runs → wins: ~**10 runs ≈ 1 win**.

## Reproduce
```bash
python3 scrape_framing.py   # -> framing_YYYY.csv, framing_all.json
python3 scrape_stance.py    # -> stance_YYYY.csv, stance_all.json
python3 analyze.py          # -> analysis.json
python3 build_report.py     # -> index.html
```

## Honest caveat
Dropping a knee does **not** automatically make a catcher a good framer. Correlating a
catcher's knee-down *rate* against their framing value yields only a weak relationship
(r ≈ 0.05). Knee-down is the *platform* that lets already-skilled receivers maximize low-pitch
framing — glove work and body quietness remain the causal driver.

---
*All figures match the source CSVs; no numbers are estimated or fabricated. Data pulled 2026-10-16.*
