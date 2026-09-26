"""Render the last 31 days of GitHub contributions as an SVG line chart.

Run by .github/workflows/stats.yml. Needs GITHUB_TOKEN and GITHUB_USER in the
environment; writes profile/activity.svg.
Use `--sample` to render made-up data locally without calling the API.
"""

import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

DAYS = 31
OUT = "profile/activity.svg"

# Theme (matches the stats cards in README.md)
SURFACE = "#0d1117"
ACCENT = "#00d9ff"
GRID = "#21262d"
INK = "#c9d1d9"
MUTED = "#8b949e"
FONT = "-apple-system, 'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif"

W, H = 1200, 420
LEFT, RIGHT, TOP, BOTTOM = 70, 40, 115, 60

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def fetch(user, token):
    today = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - dt.timedelta(days=DAYS - 1)
    body = json.dumps({
        "query": QUERY,
        "variables": {"login": user, "from": start.isoformat(), "to": dt.datetime.now(dt.timezone.utc).isoformat()},
    }).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return sorted(days)[-DAYS:]


def sample():
    end = dt.date.today()
    return [(end - dt.timedelta(days=DAYS - 1 - i), random.choice([0, 0, 1, 2, 3, 5, 8])) for i in range(DAYS)]


def nice_ticks(peak):
    """Clean y-axis ticks: 0 up to a round top, about four steps."""
    step = 1
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        step = s
        if peak / s <= 4:
            break
    top = max(step * math.ceil(peak / step), 4 * step if peak == 0 else step)
    return list(range(0, top + 1, step))


def render(user, days):
    counts = [c for _, c in days]
    ticks = nice_ticks(max(counts))
    y_top = ticks[-1]
    pw, ph = W - LEFT - RIGHT, H - TOP - BOTTOM

    def x(i):
        return LEFT + pw * i / (len(days) - 1)

    def y(v):
        return TOP + ph * (1 - v / y_top)

    pts = [(x(i), y(c)) for i, c in enumerate(counts)]
    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    area = f"{LEFT:.1f},{TOP + ph:.1f} {line} {pts[-1][0]:.1f},{TOP + ph:.1f}"
    total = sum(counts)
    first, last = days[0][0], days[-1][0]
    span = f"{first:%b} {first.day} – {last:%b} {last.day}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d">',
        f'<title id="t">{escape(user)} contribution graph</title>',
        f'<desc id="d">{total} contributions from {span}. Daily counts: '
        + ", ".join(f"{d:%b} {d.day}: {c}" for d, c in days) + "</desc>",
        "<defs><linearGradient id=\"fill\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">"
        f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="6" fill="{SURFACE}"/>',
        f'<g font-family="{FONT}">',
        f'<text x="{LEFT - 30}" y="50" font-size="24" font-weight="600" fill="{ACCENT}">'
        f"{escape(user)}'s Contribution Graph</text>",
        f'<text x="{LEFT - 30}" y="80" font-size="15" fill="{MUTED}">'
        f"{total} contributions · {span}</text>",
    ]

    for t in ticks:
        ty = y(t)
        out.append(f'<line x1="{LEFT}" x2="{W - RIGHT}" y1="{ty:.1f}" y2="{ty:.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{LEFT - 14}" y="{ty + 4:.1f}" font-size="13" fill="{MUTED}" text-anchor="end">{t}</text>')

    for i in range(0, len(days), 6):
        d = days[i][0]
        out.append(
            f'<text x="{x(i):.1f}" y="{H - BOTTOM + 28}" font-size="13" fill="{MUTED}" text-anchor="middle">'
            f"{d:%b} {d.day}</text>"
        )

    out.append(f'<polygon points="{area}" fill="url(#fill)"/>')
    out.append(
        f'<polyline points="{line}" fill="none" stroke="{ACCENT}" stroke-width="2" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Selective markers: the busiest day (with its value) and today.
    peak_i = max(range(len(counts)), key=lambda i: (counts[i], i))
    for i in sorted({peak_i, len(days) - 1}):
        px, py = pts[i]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{ACCENT}" stroke="{SURFACE}" stroke-width="2"/>')
    if counts[peak_i] > 0:
        px, py = pts[peak_i]
        anchor = "end" if peak_i == len(days) - 1 else "middle"
        out.append(
            f'<text x="{px:.1f}" y="{py - 14:.1f}" font-size="14" font-weight="600" fill="{INK}" '
            f'text-anchor="{anchor}">{counts[peak_i]}</text>'
        )

    out.append("</g></svg>")
    return "\n".join(out)


def main():
    user = os.environ.get("GITHUB_USER", "octocat")
    days = sample() if "--sample" in sys.argv else fetch(user, os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(user, days))
    print(f"Wrote {OUT}: {sum(c for _, c in days)} contributions over {len(days)} days")


if __name__ == "__main__":
    main()
