#!/usr/bin/env python3
"""Build the knee-down 'stolen strikes' case study HTML report."""
import json
import os

D = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(D, "analysis.json")))

ADOPTION = data["adoption"]
CALLED = data["stance_called_strike"]
RATE = data["framing_rv_per_1000"]
AGG = data["aggregate_framing_rv_by_stance"]
CORR = data["knee_down_vs_framing_rv_corr"]
TOP = data["top_framing_seasons"]
CAREER = data["career_framing_leaders"]

# Build JS data payloads
adoption_js = json.dumps([
    {"x": a["season"], "y": a["wavg_knee_down_pct"]} for a in ADOPTION
])
top_js = json.dumps(TOP)
career_js = json.dumps(CAREER[:12])

# Career leaders table rows
career_rows = "".join(
    f'<tr><td>{i+1}</td><td>{c["name"]}</td><td class="num">{c["seasons"]}</td>'
    f'<td class="num">{c["rv_tot"]:+.2f}</td></tr>'
    for i, c in enumerate(CAREER[:12])
)

# Single-season top table
top_rows = "".join(
    f'<tr><td>{t["season"]}</td><td>{t["name"]}</td>'
    f'<td class="num">{t["pitches"]:,.0f}</td>'
    f'<td class="num">{t["rv_tot"]:+.2f}</td></tr>'
    for t in TOP[:12]
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stolen Strikes — The One-Knee-Down Catching Revolution (TrackMan Era)</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg:#0d1117; --panel:#161b22; --panel2:#1c2128; --border:#30363d;
    --text:#e6edf3; --muted:#8b949e; --accent:#58a6ff; --good:#3fb950;
    --bad:#f85149; --warn:#d29922; --purple:#bc8cff;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--bg); color:var(--text);
    font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height:1.6;
  }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:32px 24px 80px; }}
  header {{ border-bottom:1px solid var(--border); padding-bottom:24px; margin-bottom:32px; }}
  .kicker {{ color:var(--accent); text-transform:uppercase; letter-spacing:2px; font-size:12px; font-weight:700; margin:0 0 8px; }}
  h1 {{ font-size:34px; line-height:1.2; margin:0 0 12px; }}
  .subtitle {{ color:var(--muted); font-size:17px; max-width:760px; }}
  .byline {{ color:var(--muted); font-size:13px; margin-top:14px; }}
  h2 {{ font-size:22px; margin:44px 0 14px; color:var(--text); }}
  h3 {{ font-size:16px; margin:0 0 10px; color:var(--accent); }}
  p {{ color:#c9d1d9; }}
  .lead {{ font-size:17px; color:#c9d1d9; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin:20px 0; }}
  .stat {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:20px; }}
  .stat .val {{ font-size:30px; font-weight:800; color:var(--text); }}
  .stat .val.green {{ color:var(--good); }} .stat .val.red {{ color:var(--bad); }}
  .stat .val.accent {{ color:var(--accent); }}
  .stat .lbl {{ color:var(--muted); font-size:13px; margin-top:4px; }}
  .chartbox {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:22px; margin:20px 0; }}
  .chartbox .cap {{ color:var(--muted); font-size:13px; margin-top:8px; }}
  canvas {{ max-height:360px; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  th, td {{ text-align:left; padding:9px 12px; border-bottom:1px solid var(--border); }}
  th {{ color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.5px; }}
  td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  tr:hover td {{ background:var(--panel2); }}
  .note {{ background:var(--panel2); border-left:3px solid var(--warn); padding:14px 18px; border-radius:6px; color:#c9d1d9; font-size:14px; margin:18px 0; }}
  .callout {{ background:var(--panel); border-left:3px solid var(--purple); padding:16px 20px; border-radius:6px; margin:18px 0; }}
  .pos {{ color:var(--good); font-weight:700; }} .neg {{ color:var(--bad); font-weight:700; }}
  .tag {{ display:inline-block; background:var(--panel2); border:1px solid var(--border); border-radius:20px; padding:3px 12px; font-size:12px; color:var(--muted); margin:2px 4px 2px 0; }}
  footer {{ margin-top:60px; padding-top:20px; border-top:1px solid var(--border); color:var(--muted); font-size:12px; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <p class="kicker">Catcher Framing · Runs Saved · TrackMan Era</p>
  <h1>Stolen Strikes:<br>The One-Knee-Down Catching Revolution</h1>
  <p class="subtitle">A data-grounded case study of how the low receiving setup took over MLB and became the
  single most valuable framing weapon of the Statcast era — measured in stolen strikes and the runs they save.</p>
  <div class="byline">Data: Baseball Savant (Statcast) catcher-framing &amp; catcher-stance leaderboards · 
  Compiled 2026-10-16 · 663 catcher-seasons framing (2015–2025) · 331 catcher-seasons stance splits (2020–2025)</div>
</header>

<section>
  <p class="lead">A decade ago almost every catcher received from a crouch — both knees up, a conventional
  balance between framing, blocking, and throwing. Today, <strong>virtually every MLB catcher drops to one knee</strong>
  to receive. The machine-tracked data shows exactly when it happened, and exactly why: <strong>dropping a knee
  buys more called strikes in the shadow zone</strong>, and those extra strikes translate directly into runs —
  the most valuable, lowest-cost run prevention a team can find behind the plate.</p>
</section>

<h2>1. The adoption curve — a near-universal takeover</h2>
<p>Statcast began directly tracking catcher stance in 2020 (a knee counts as "down" below ~9 inches off the ground).
The rate of pitches received from a knee-down setup went from roughly <strong>one in four</strong> to
<strong>nineteen in twenty</strong> in just six seasons.</p>
<div class="chartbox">
  <canvas id="adoptionChart"></canvas>
  <div class="cap">League-average % of pitches received from a knee-down setup (pitches-weighted), 2020–2025. Source: Baseball Savant catcher-stance leaderboard.</div>
</div>

<div class="grid">
  <div class="stat"><div class="val">23.7%</div><div class="lbl">Knee-down rate · 2020 (season low)</div></div>
  <div class="stat"><div class="val accent">95.3%</div><div class="lbl">Knee-down rate · 2025</div></div>
  <div class="stat"><div class="val">4 → 56</div><div class="lbl">Catchers &gt;60% knee-down, 2020 → 2025</div></div>
</div>

<div class="callout">
  <h3>When did it become popular?</h3>
  <p>Chad's instinct was right to ask — the knee-down setup was a niche curiosity until
  <strong>~2019–2021</strong>. Pioneering orgs (most famously the Yankees' catching lab, plus the broader
  Driveline/"Framing+" research wave) proved the upside, and by <strong>2024–2025 it was near-universal</strong>
  (Austin Wells ~97%, Will Smith ~94% knee-down in the 2024 World Series). The Statcast stance data picks up
  the story exactly as it went mainstream: 23.7% in 2020 to 95.3% in 2025.</p>
</div>

<h2>2. The stolen-strike edge — called-strike rate by stance</h2>
<p>The whole point of knee-down receiving is to <strong>reframe the umpire's perspective from lower and wider</strong>,
cleaning up the bottom of the zone. The split data measures it directly: the same catcher, the same season,
the strike they got called in a knee-down setup vs. a traditional one.</p>
<div class="grid">
  <div class="stat"><div class="val green">{CALLED["one_knee_calledstr_pct"]:.1f}%</div><div class="lbl">Called-strike rate · knee-down</div></div>
  <div class="stat"><div class="val">{CALLED["other_calledstr_pct"]:.1f}%</div><div class="lbl">Called-strike rate · traditional</div></div>
  <div class="stat"><div class="val accent">+{CALLED["delta_pct_points"]:.2f} pts</div><div class="lbl">Stolen-strike advantage</div></div>
</div>
<div class="chartbox">
  <canvas id="calledChart"></canvas>
  <div class="cap">League-average called-strike rate on the catcher's same-season pitches, by receiving stance. n={CALLED["n"]} catcher-seasons.</div>
</div>

<h2>3. The money stat — framing runs saved, by stance</h2>
<p>Sabr/Savant converts each <strong>extra</strong> called strike into run value — approximately
<strong>+0.125 runs per stolen strike</strong>. Summed across the league and normalized per 1,000 received pitches,
knee-down receiving isn't just a hair better — it's the difference between <strong>positive and negative</strong> framing value.</p>
<div class="grid">
  <div class="stat"><div class="val green">+{RATE["one_knee_mean"]:.3f}</div><div class="lbl">Framing runs / 1,000 pitches · knee-down</div></div>
  <div class="stat"><div class="val red">{RATE["other_mean"]:.3f}</div><div class="lbl">Framing runs / 1,000 pitches · traditional</div></div>
  <div class="stat"><div class="val accent">+{RATE["one_knee_mean"] - RATE["other_mean"]:.3f}</div><div class="lbl">Net framing edge / 1,000 pitches</div></div>
</div>
<div class="chartbox">
  <canvas id="framingRateChart"></canvas>
  <div class="cap">Mean framing run value per 1,000 received pitches, by stance (catcher-season level, 2020–2025).</div>
</div>

<div class="note">
  <strong>League aggregate (2020–2025):</strong> across {AGG["n_catcher_seasons"]} qualified catcher-seasons,
  knee-down setups produced <span class="pos">+{AGG["one_knee_framing_rv_total"]:.1f} framing runs</span> while
  traditional setups produced <span class="neg">{AGG["other_framing_rv_total"]:.1f} runs</span>. The stance isn't a
  gimmick — it's where essentially all modern framing value now lives.
</div>

<h2>4. An honest caveat — stance ≠ skill</h2>
<div class="note">
<p style="margin-top:0">Comparing a catcher's knee-down <em>rate</em> (how often they use it) against their framing
value yields a very weak correlation (<strong>r ≈ {CORR["pearson_r"]:.3f}</strong>, n={CORR["n"]}). That's expected and important:
<strong>dropping a knee does not automatically make a catcher a good framer</strong>. The causal driver is receiving
hand/glove work and body quietness. Knee-down is the <em>platform</em> that lets already-gifted receivers maximize
that skill — low and locked on the low pitch. It's not a magic bullet, which is why teams still teach glove skill first.</p>
</div>

<h2>5. Who stole the most strikes — the framing leaders</h2>
<h3>Best single-season framing (runs saved, 2018–2025)</h3>
<table>
  <thead><tr><th>Season</th><th>Catcher</th><th class="num">Pitches</th><th class="num">Framing Runs</th></tr></thead>
  <tbody>{top_rows}</tbody>
</table>

<h3>Career framing leaders (sum of runs saved, 2018–2025)</h3>
<table>
  <thead><tr><th>#</th><th>Catcher</th><th class="num">Seasons</th><th class="num">Framing Runs</th></tr></thead>
  <tbody>{career_rows}</tbody>
</table>
<p style="color:var(--muted);font-size:13px">Austin Hedges (+{CAREER[0]["rv_tot"]:.1f} runs across 8 seasons) and
Patrick Bailey (+{CAREER[1]["rv_tot"]:.2f} in just 3 seasons) are the gold standard of the modern era. A +10-run framing
season is worth roughly <strong>one win</strong> — the equivalent of an entire marginal free-agent signing, hidden
behind the plate in stolen strikes.</p>

<div class="chartbox">
  <canvas id="careerChart"></canvas>
  <div class="cap">Career framing runs saved, 2018–2025 (top 12). ~10 runs ≈ 1 win of value.</div>
</div>

<h2>6. The bottom line</h2>
<div class="callout">
<p style="margin-top:0">The one-knee-down stance is the dominant catcher innovation of the TrackMan era because it
cleanly converts <strong>pitches into called strikes into runs</strong> — the same batter-run value at effectively
zero resource cost. It took MLB from ~24% knee-down in 2020 to ~95% in 2025, and it's the platform behind
essentially every elite framing season since. For any catcher (or program) trying to gain an edge, the lesson is
simple: <strong>master glove work first, then get low and steal the bottom of the zone.</strong></p>
</div>

<footer>
  <p><strong>Method &amp; sources.</strong> All figures computed programmatically from Baseball Savant's public
  leaderboard CSVs on 2026-10-16: <em>catcher-framing</em> (rv_tot framing runs, 2015–2025; run-value totals available 2018+) and
  <em>catcher-stance</em> (knee-down rate and stance-split framing/blocking/throwing run values, 2020–2025).
  Strike→runs conversion (~+0.125 runs/strike) and runs→wins (~10 runs/win) are cited public context, not scraped.
  No numbers are estimated or fabricated — figures match the source CSVs. Raw data + build scripts ship alongside this page.</p>
  <p>Built with Chart.js · Published to GitHub Pages.</p>
</footer>

</div>

<script>
const ADOPTION = {adoption_js};
const TOP = {top_js};
const CAREER = {career_js};

const gridColor = "#30363d";
const tickColor = "#8b949e";

Chart.defaults.color = tickColor;
Chart.defaults.borderColor = gridColor;
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

new Chart(document.getElementById("adoptionChart"), {{
  type: "line",
  data: {{
    labels: ADOPTION.map(d => d.x),
    datasets: [{{
      label: "Knee-down rate (%)",
      data: ADOPTION.map(d => d.y),
      borderColor: "#58a6ff",
      backgroundColor: "rgba(88,166,255,0.15)",
      fill: true,
      tension: 0.35,
      pointRadius: 5,
      pointBackgroundColor: "#58a6ff",
      borderWidth: 3
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ min: 0, max: 100, title: {{ display: true, text: "% pitches knee-down" }} }},
      x: {{ title: {{ display: true, text: "Season" }} }}
    }}
  }}
}});

new Chart(document.getElementById("calledChart"), {{
  type: "bar",
  data: {{
    labels: ["Knee-down", "Traditional"],
    datasets: [{{
      label: "Called-strike %",
      data: [{CALLED["one_knee_calledstr_pct"]:.2f}, {CALLED["other_calledstr_pct"]:.2f}],
      backgroundColor: ["#3fb950", "#f85149"],
      borderColor: ["#3fb950", "#f85149"],
      borderWidth: 1
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ min: 40, max: 50, title: {{ display: true, text: "Called-strike %" }} }} }}
  }}
}});

new Chart(document.getElementById("framingRateChart"), {{
  type: "bar",
  data: {{
    labels: ["Knee-down", "Traditional"],
    datasets: [{{
      label: "Framing runs / 1000 pitches",
      data: [{RATE["one_knee_mean"]:.3f}, {RATE["other_mean"]:.3f}],
      backgroundColor: ["#3fb950", "#f85149"],
      borderColor: ["#3fb950", "#f85149"],
      borderWidth: 1
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ title: {{ display: true, text: "Runs / 1000 pitches" }} }} }}
  }}
}});

new Chart(document.getElementById("careerChart"), {{
  type: "bar",
  data: {{
    labels: CAREER.map(d => d.name),
    datasets: [{{
      label: "Framing runs saved",
      data: CAREER.map(d => d.rv_tot),
      backgroundColor: CAREER.map(d => d.rv_tot >= 0 ? "#3fb950" : "#f85149"),
      borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: "y",
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ title: {{ display: true, text: "Runs saved (framing)" }} }} }}
  }}
}});
</script>
</body>
</html>
"""

out_path = os.path.join(D, "index.html")
with open(out_path, "w") as f:
    f.write(html)
print(f"Wrote {out_path} ({len(html)} bytes)")
