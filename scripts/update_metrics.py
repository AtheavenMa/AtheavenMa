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
        "background": "#f8fafb", "border": "#dae1e7", "primary": "#17242e",
        "secondary": "#50616e", "accent": "#235d81", "rule": "#dce4e9",
    },
    "dark": {
        "background": "#141b22", "border": "#303c47", "primary": "#eaf0f6",
        "secondary": "#a2b0bd", "accent": "#95c8e6", "rule": "#35414c",
    },
}


def make_svg(theme: str, merged_prs: int, stars: int) -> str:
    c = THEMES[theme]
    metrics = (
        (merged_prs, "PUBLIC MERGED PRS", "Pull requests merged"),
        (stars, "PROJECT REACH", "Stars across 7 selected repositories"),
        (len(REPOSITORIES), "RESEARCH CODE", "Featured repositories"),
    )
    lefts = (30, 350, 670)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="160" viewBox="0 0 960 160" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub open-source activity</title>',
        f'<desc id="desc">{merged_prs} publicly merged pull requests, {stars} stars across seven selected research repositories, and seven featured research repositories. Data from the GitHub public API.</desc>',
        f'<rect x="0.5" y="0.5" width="959" height="159" rx="12" fill="{c["background"]}" stroke="{c["border"]}"/>',
        f'<path d="M320 26 V134 M640 26 V134" fill="none" stroke="{c["rule"]}"/>',
    ]
    for x, (number, category, label) in zip(lefts, metrics):
        parts.extend((
            f'<text x="{x}" y="36" fill="{c["secondary"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="13" font-weight="650" letter-spacing="1.6">{category}</text>',
            f'<text x="{x}" y="101" fill="{c["accent"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="54" font-weight="700">{number:,}</text>',
            f'<text x="{x}" y="135" fill="{c["primary"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="16">{label}</text>',
        ))
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Use an offline 2026-10-22 snapshot")
    args = parser.parse_args()
    merged_prs, stars = (49, 62) if args.preview else read_public_metrics()
    (ROOT / "assets").mkdir(exist_ok=True)
    for theme in THEMES:
        (ROOT / "assets" / f"github-activity-{theme}.svg").write_text(
            make_svg(theme, merged_prs, stars), encoding="utf-8"
        )
    print(f"Public merged PRs: {merged_prs}; selected repo stars: {stars}")


if __name__ == "__main__":
    main()
