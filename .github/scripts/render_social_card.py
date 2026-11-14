#!/usr/bin/env python3
"""Render the site's social preview card (og:image) from live WakaTime data.

Runs in the weekly workflow after update_wakatime_readme.py and writes
.github/wakatime/social-card.png (1200x630). The site build copies that file
into dist/, and index.html.ejs points og:image / twitter:image at it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont

from update_wakatime_readme import (
    BASE_URL,
    CHART_DIR,
    ENDPOINTS,
    LANGUAGE_COLORS,
    ROOT,
    clean_chart_items,
    fetch_json,
    get_brand_color,
)

WIDTH, HEIGHT = 1200, 630
MARGIN = 60
OUTPUT = CHART_DIR / "social-card.png"
PROFILE_PATH = ROOT / "src" / "profile.ejs"

# Site palette (mirrors the :root variables in src/index.html.ejs).
BG = "#080b10"
GRID = "#0e141b"
PANEL = "#0d131a"
LINE = "#1b232c"
INK = "#eeeae1"
MUTED = "#a5a9a8"
DIM = "#68717a"
SIGNAL = "#a8132b"
SIGNAL_BRIGHT = "#f04455"

FONT_DIRS = [Path("/usr/share/fonts"), Path("/usr/local/share/fonts"), Path.home() / ".fonts"]
SANS_BOLD = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"]
SANS = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "NotoSans-Regular.ttf"]
MONO = ["DejaVuSansMono.ttf", "LiberationMono-Regular.ttf", "NotoSansMono-Regular.ttf"]


def load_profile() -> dict[str, Any]:
    # profile.ejs is JSON preceded by an EJS comment line; drop the EJS lines.
    lines = [line for line in PROFILE_PATH.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("<%")]
    return json.loads("\n".join(lines))


def find_font(names: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for directory in FONT_DIRS:
        if not directory.exists():
            continue
        for name in names:
            hits = sorted(directory.rglob(name))
            if hits:
                return ImageFont.truetype(str(hits[0]), size)
    print(f"[social-card] none of {names} found; using Pillow's default font")
    return ImageFont.load_default(size)


def top_languages(language_data: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    items = [item for item in clean_chart_items(language_data) if item["name"] != "Unmapped Runtime"]
    items.sort(key=lambda item: item["total_seconds"], reverse=True)
    top = items[:limit]
    total = sum(item["total_seconds"] for item in top) or 1
    for item in top:
        item["share"] = item["total_seconds"] / total
        fallback = str(item.get("color", "")).strip() or "#8ecae6"
        item["brand"] = get_brand_color(item["name"], fallback, LANGUAGE_COLORS)
    return top


def draw_card(profile: dict[str, Any], summary: dict[str, Any], languages: list[dict[str, Any]]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # Faint grid, like the page background.
    for x in range(0, WIDTH, 40):
        draw.line([(x, 0), (x, HEIGHT)], fill=GRID, width=1)
    for y in range(0, HEIGHT, 40):
        draw.line([(0, y), (WIDTH, y)], fill=GRID, width=1)

    eyebrow_font = find_font(MONO, 20)
    name_font = find_font(SANS_BOLD, 82)
    title_font = find_font(SANS, 34)
    label_font = find_font(MONO, 15)
    value_font = find_font(SANS_BOLD, 30)
    sub_font = find_font(MONO, 14)
    legend_font = find_font(SANS, 19)
    footer_font = find_font(MONO, 17)

    # Identity block.
    draw.rectangle([(MARGIN, 58), (MARGIN + 80, 61)], fill=SIGNAL_BRIGHT)
    draw.text((MARGIN, 80), profile["crewId"], font=eyebrow_font, fill=SIGNAL)
    name = profile["name"]
    draw.text((MARGIN, 112), name, font=name_font, fill=INK)
    draw.text((MARGIN + draw.textlength(name, font=name_font), 112), ".", font=name_font, fill=SIGNAL_BRIGHT)
    draw.text((MARGIN, 218), profile["title"], font=title_font, fill=MUTED)

    # Stat tiles.
    grand_total = summary.get("grand_total", {})
    best_day = summary.get("best_day", {})
    date_range = summary.get("range", {})
    days = date_range.get("days_including_holidays")
    tiles = [
        ("TOTAL LOGGED", grand_total.get("human_readable_total_including_other_language", "—"), "CAREER HOURS"),
        ("DAILY AVERAGE", grand_total.get("human_readable_daily_average_including_other_language", "—"), "ALL TRACKED DAYS"),
        ("PEAK OUTPUT", best_day.get("text", "—"), best_day.get("date", "—")),
        ("TRACKING WINDOW", f"{days:,} DAYS" if isinstance(days, int) else "—", f"SINCE {str(date_range.get('start', '—'))[:10]}"),
    ]
    gap = 16
    tile_width = (WIDTH - 2 * MARGIN - gap * (len(tiles) - 1)) // len(tiles)
    tile_top, tile_bottom = 300, 416
    for index, (label, value, sub) in enumerate(tiles):
        left = MARGIN + index * (tile_width + gap)
        draw.rectangle([(left, tile_top), (left + tile_width, tile_bottom)], fill=PANEL, outline=LINE)
        draw.text((left + 18, tile_top + 16), label, font=label_font, fill=SIGNAL)
        draw.text((left + 18, tile_top + 44), str(value), font=value_font, fill=INK)
        draw.text((left + 18, tile_top + 88), str(sub), font=sub_font, fill=DIM)

    # Top languages: stacked bar plus legend.
    draw.text((MARGIN, 448), "TOP LANGUAGES", font=label_font, fill=SIGNAL)
    bar_top, bar_height = 474, 12
    bar_width = WIDTH - 2 * MARGIN
    draw.rectangle([(MARGIN, bar_top), (MARGIN + bar_width, bar_top + bar_height)], fill=PANEL, outline=LINE)
    cursor = MARGIN
    for item in languages:
        segment = int(round(item["share"] * bar_width))
        draw.rectangle([(cursor, bar_top), (cursor + segment, bar_top + bar_height)], fill=item["brand"])
        cursor += segment
    legend_x = MARGIN
    for item in languages:
        draw.rectangle([(legend_x, 506), (legend_x + 10, 516)], fill=item["brand"])
        text = f"{item['name']}  {item['share'] * 100:.0f}%"
        draw.text((legend_x + 18, 500), text, font=legend_font, fill=INK)
        legend_x += 18 + int(draw.textlength(text, font=legend_font)) + 30

    # Footer.
    draw.line([(MARGIN, 560), (WIDTH - MARGIN, 560)], fill=LINE, width=1)
    draw.text((MARGIN, 576), "LIVE WAKATIME TELEMETRY", font=footer_font, fill=DIM)
    host = urlparse(profile["siteUrl"]).netloc
    draw.text((WIDTH - MARGIN - draw.textlength(host, font=footer_font), 576), host, font=footer_font, fill=MUTED)

    return image


def main() -> None:
    summary_payload = fetch_json(BASE_URL + ENDPOINTS["summary"])
    language_payload = fetch_json(BASE_URL + ENDPOINTS["languages"])
    if not isinstance(summary_payload, dict) or not isinstance(language_payload, dict):
        raise RuntimeError("WakaTime summary or languages endpoint failed")

    profile = load_profile()
    languages = top_languages(list(language_payload.get("data", [])))
    card = draw_card(profile, summary_payload.get("data", {}), languages)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    card.save(OUTPUT, format="PNG", optimize=True)
    print(f"Social card written to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
