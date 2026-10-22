#!/usr/bin/env python3
"""Generate self-hosted GitHub activity graphics for AtheavenMa's profile.

Uses GitHub's public REST API and the standard library only.
--preview uses the verified 2026-10-22 snapshot without making network calls.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

USER = "AtheavenMa"
REPOSITORIES = (
    "OpenSAE/SAEBase",
    "OpenSAE/SAE-Behavioral-Compositionality",
    "OpenSAE/Redistribution-Sensitivity-Score",
    "OpenSAE/SAE-Input-Localization",
    "AtheavenMa/Spectral-Spatial-Interpretation",
    "AtheavenMa/SymSelect",
    "AtheavenMa/The-Limits-of-Reward-Guidance-under-Finite-Adaptation",
)
ROOT = Path(__file__).resolve().parents[1]


def api(path: str) -> dict:
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AtheavenMa-profile-stats",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request("https://api.github.com" + path, headers=headers)
    with urlopen(req, timeout=25) as response:
        return json.load(response)


def read_public_metrics() -> tuple[int, int]:
    query = quote(f"author:{USER} is:pr is:merged is:public")
    merged_prs = int(api(f"/search/issues?q={query}&per_page=1")["total_count"])
    stars = sum(int(api(f"/repos/{repo}")["stargazers_count"]) for repo in REPOSITORIES)
    return merged_prs, stars


THEMES = {
    "light": {
        "canvas": "#ffffff",
        "card_fill": "#f8fbff",
        "card_fill_2": "#f7fafc",
        "card_fill_3": "#f9fafb",
        "border": "#d9e3ee",
        "shadow": "#eef3f8",
        "primary": "#182431",
        "secondary": "#5a6b7b",
        "accent": "#1f6feb",
        "accent_2": "#0ea5a4",
        "accent_3": "#7c4dff",
    },
    "dark": {
        "canvas": "#0d1117",
        "card_fill": "#141b24",
        "card_fill_2": "#141a22",
        "card_fill_3": "#151923",
        "border": "#2f3845",
        "shadow": "#10161d",
        "primary": "#eef4fb",
        "secondary": "#a1b0be",
        "accent": "#77b3ff",
        "accent_2": "#56d4d2",
        "accent_3": "#b392ff",
    },
}

FONT = '-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif'


def _card(x: int, title: str, value: int, fill: str, accent: str, border: str, primary: str, secondary: str) -> str:
    y = 18
    w = 286
    h = 168
    return "\n".join(
        [
            f'<g transform="translate({x}, {y})">',
            f'  <rect x="6" y="8" width="{w}" height="{h}" rx="20" fill="{border}" opacity="0.18"/>',
            f'  <rect width="{w}" height="{h}" rx="20" fill="{fill}" stroke="{border}"/>',
            f'  <rect x="0" y="0" width="{w}" height="8" rx="20" fill="{accent}"/>',
            f'  <text x="28" y="82" fill="{accent}" font-family="{FONT}" font-size="60" font-weight="760">{value:,}</text>',
            f'  <text x="28" y="122" fill="{primary}" font-family="{FONT}" font-size="24" font-weight="680">{title}</text>',
            '</g>',
        ]
    )


def make_svg(theme: str, merged_prs: int, stars: int) -> str:
    c = THEMES[theme]
    metrics = (
        ("Merged PRs", merged_prs, c["card_fill"], c["accent"]),
        ("Project Stars", stars, c["card_fill_2"], c["accent_2"]),
        ("Research Repos", len(REPOSITORIES), c["card_fill_3"], c["accent_3"]),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="204" viewBox="0 0 960 204" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub activity highlights</title>',
        f'<desc id="desc">{merged_prs} publicly merged pull requests, {stars} stars across selected research repositories, and {len(REPOSITORIES)} featured research repositories.</desc>',
        f'<rect width="960" height="204" rx="24" fill="{c["canvas"]}"/>',
    ]
    xs = (18, 337, 656)
    for x, (title, value, fill, accent) in zip(xs, metrics):
        parts.append(_card(x, title, value, fill, accent, c["border"], c["primary"], c["secondary"]))
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Use an offline 2026-10-22 snapshot")
    args = parser.parse_args()
    merged_prs, stars = (51, 62) if args.preview else read_public_metrics()
    (ROOT / "assets").mkdir(exist_ok=True)
    for theme in THEMES:
        (ROOT / "assets" / f"github-activity-{theme}.svg").write_text(
            make_svg(theme, merged_prs, stars), encoding="utf-8"
        )
    print(f"Public merged PRs: {merged_prs}; selected repo stars: {stars}")


if __name__ == "__main__":
    main()
