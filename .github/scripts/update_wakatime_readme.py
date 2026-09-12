#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import re
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
README_PATH = ROOT / "README.md"
CHART_DIR = ROOT / ".github" / "wakatime"
CHART_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://wakatime.com/share/@Sierra117/"
ENDPOINTS = {
    "summary": "ca964aaa-fcd3-4f9b-ad9b-855b90cb5ae4.json",
    "languages": "bb9729ad-9cb3-4d6c-b912-359e136ed48a.json",
    "editors": "7cab5d5a-187a-4687-9e05-db05c975bf68.json",
    "os": "8bb890bb-0128-4bb0-adaa-def4d63aa689.json",
    "categories": "bdfc68ea-2e02-4fef-8870-5f648645152a.json",
}
IGNORED_ITEM_NAMES = {"Other", "Unknown"}
ALIASED_ITEM_NAMES = {
    "Browser": "Brave",
    "Unknown Editor": "Ghost Mode",
    "Other": "Unmapped Runtime",
    "Unknown": "Unmapped Runtime",
    "Unknown Language": "Unmapped Runtime",
}
LANGUAGE_COLORS = {
    "python": "#3572A5",
    "javascript": "#f1e05a",
    "typescript": "#3178C6",
    "html": "#e34c26",
    "css": "#563d7c",
    "java": "#b07219",
    "c": "#555555",
    "c++": "#f34b7d",
    "go": "#00ADD8",
    "markdown": "#083fa1",
    "xml": "#0060ac",
    "json": "#f0db4f",
    "yaml": "#cb171e",
    "bash": "#89e051",
    "shell": "#89e051",
    "ruby": "#701516",
    "rust": "#dea584",
    "swift": "#ffac45",
    "php": "#4F5D95",
    "kotlin": "#7F52FF",
    "dart": "#00B4AB",
    "csharp": "#178600",
    "sql": "#e38c00",
    "dockerfile": "#2496ED",
    "makefile": "#427819",
    "tex": "#5d87bf",
    "jsx": "#61dafb",
    "tsx": "#3178C6",
    "vue": "#41B883",
}
EDITOR_COLORS = {
    "vscode": "#007ACC",
    "visual studio code": "#007ACC",
    "firefox": "#FF7139",
    "chrome": "#F7C948",
    "android studio": "#3DDC84",
    "intellij idea": "#7F5AF0",
    "idea": "#7F5AF0",
    "pycharm": "#21D789",
    "clion": "#14C9A5",
    "atom": "#49B77E",
    "sublime text": "#FF9800",
    "vim": "#019733",
    "neovim": "#57A143",
    "emacs": "#7F5AF0",
    "terminal": "#1F2937",
    "android": "#3DDC84",
    "windows terminal": "#00AEEF",
}


def get_brand_color(name: str, fallback: str, palette: dict[str, str]) -> str:
    key = name.strip().lower()
    for candidate in (key, key.replace("-", " ")):
        if candidate in palette:
            return palette[candidate]
    for candidate, value in palette.items():
        if candidate in key or key in candidate:
            return value
    return fallback


def format_duration(total_seconds: float) -> str:
    total_seconds = max(0, int(total_seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:04d}H {minutes:02d}M"


NICE_MULTIPLIERS = (1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5)


def log_axis_ceiling(max_value: float, fill_ratio: float = 0.92) -> float:
    """Smallest 'nice' value for the axis top keeping the tallest bar within ``fill_ratio``.

    Because the scale is logarithmic, a ceiling equal to the data max would make
    the top bar touch the top gridline. This picks the smallest nice value whose
    log position puts the tallest bar at or below ``fill_ratio`` of the plot,
    leaving headroom and delaying overshoot as the data grows.
    """
    if max_value <= 0:
        return 1.0
    log_max = math.log10(1 + max_value)
    base = 0.1
    while True:
        for mult in NICE_MULTIPLIERS:
            ceiling = base * mult
            if ceiling < max_value:
                continue
            fill = log_max / math.log10(1 + ceiling) if ceiling > 0 else 0
            if fill <= fill_ratio:
                return ceiling
        base *= 10


def log_scale_ticks(max_value: float, min_ratio_gap: float = 0.0) -> list[float]:
    """Return 'nice' tick values (1/2/5 progression) spanning a log scale.

    ``min_ratio_gap`` drops ticks that would land too close together once mapped
    onto the log axis, keeping the axis labels readable. The axis ceiling
    (``max_value``) is always included so the top of the scale is labelled.
    """
    if max_value <= 0:
        return []
    log_max = math.log10(1 + max_value)
    ticks: list[float] = []
    base = 0.1
    while base <= max_value * 1.0001:
        for mult in (1, 2, 5):
            value = base * mult
            if 0 < value <= max_value * 1.0001:
                ticks.append(value)
        base *= 10

    if not ticks or ticks[-1] < max_value * 0.9999:
        ticks.append(max_value)

    filtered: list[float] = []
    for value in ticks:
        ratio = math.log10(1 + value) / log_max if log_max else 0
        if not filtered:
            filtered.append(value)
            continue
        prev_ratio = math.log10(1 + filtered[-1]) / log_max if log_max else 0
        if ratio - prev_ratio >= min_ratio_gap:
            filtered.append(value)
    return filtered


def clean_chart_items(items: list[dict[str, Any]], excluded_names: set[str] | None = None) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    excluded = excluded_names or set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if name in excluded or not name:
            continue
        if name in ALIASED_ITEM_NAMES:
            name = ALIASED_ITEM_NAMES[name]
        if name in IGNORED_ITEM_NAMES:
            continue
        if name.lower() == "unknown os":
            name = "Android"
        total_seconds = float(item.get("total_seconds", 0) or 0)
        if total_seconds <= 0:
            continue
        cleaned.append({**item, "name": name, "total_seconds": total_seconds})
    return sorted(cleaned, key=lambda item: str(item.get("name", "")).lower())


def fetch_json(url: str) -> dict[str, Any] | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        text = response.read().decode("utf-8", "replace")

    cleaned = text
    if cleaned.startswith("[") or cleaned.startswith("{"):
        cleaned = re.sub(r"^[^{\[]*", "", cleaned)
        cleaned = re.sub(r"[^}\]]*$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from {url}: {exc}") from exc

    if isinstance(data, dict) and data.get("error"):
        return None
    return data


def format_metric(total: Any, average: Any, best_day: dict[str, Any], range_data: dict[str, Any]) -> tuple[str, str, str, str, str]:
    total_text = total.get("human_readable_total_including_other_language", "—") if isinstance(total, dict) else str(total)
    avg_text = average.get("human_readable_daily_average_including_other_language", "—") if isinstance(average, dict) else str(average)
    best_date = best_day.get("date", "—") if isinstance(best_day, dict) else "—"
    best_text = best_day.get("text", "—") if isinstance(best_day, dict) else "—"
    start_date = range_data.get("start", "—").split("T")[0] if isinstance(range_data, dict) else "—"
    days_count = range_data.get("days_including_holidays", "—") if isinstance(range_data, dict) else "—"
    return total_text, avg_text, f"{best_date} — {best_text}", start_date, str(days_count)


def save_svg(name: str, content: str) -> str:
    target = CHART_DIR / f"{name}.svg"
    target.write_text(content, encoding="utf-8")
    return f"./.github/wakatime/{name}.svg"


def create_pie_slice(cx: float, cy: float, outer_r: float, inner_r: float, start_angle: float, end_angle: float, color: str) -> str:
    start_rad = start_angle * 3.141592653589793 / 180.0
    end_rad = end_angle * 3.141592653589793 / 180.0

    x1_outer = cx + outer_r * math.cos(start_rad)
    y1_outer = cy + outer_r * math.sin(start_rad)
    x2_outer = cx + outer_r * math.cos(end_rad)
    y2_outer = cy + outer_r * math.sin(end_rad)

    x1_inner = cx + inner_r * math.cos(end_rad)
    y1_inner = cy + inner_r * math.sin(end_rad)
    x2_inner = cx + inner_r * math.cos(start_rad)
    y2_inner = cy + inner_r * math.sin(start_rad)

    large_arc = 1 if end_angle - start_angle > 180 else 0
    return (
        f'<path d="M {x1_outer} {y1_outer} '
        f'A {outer_r} {outer_r} 0 {large_arc} 1 {x2_outer} {y2_outer} '
        f'L {x1_inner} {y1_inner} '
        f'A {inner_r} {inner_r} 0 {large_arc} 0 {x2_inner} {y2_inner} Z" '
        f'fill="{color}" opacity="0.95" />'
    )


def make_pie_chart(title: str, items: list[dict[str, Any]], width: int = 760, height: int = 260) -> str:
    filtered = items[:8]
    total = sum(float(item.get("total_seconds", 0) or 0) for item in filtered)
    colors = ["#38bdf8", "#a78bfa", "#f59e0b", "#34d399", "#f472b6", "#f87171", "#60a5fa", "#c084fc"]
    cx, cy, r, inner_r = 160, 125, 86, 42
    start = 0.0
    slices = []
    legend = []

    for idx, item in enumerate(filtered):
        value = float(item.get("total_seconds", 0) or 0)
        ratio = value / total if total else 0
        end = start + ratio * 360
        slices.append(create_pie_slice(cx, cy, r, inner_r, start, end, colors[idx % len(colors)]))

        row = idx
        item_x = 300
        time_x = 530
        y = 40 + row * 20
        legend.append(
            f'<g font-family="sans-serif">'
            f'<rect x="{item_x}" y="{y}" width="12" height="12" rx="3" fill="{colors[idx % len(colors)]}" />'
            f'<text x="{item_x + 18}" y="{y + 10}" fill="#e5e7eb" font-size="11">{item.get("name", "Unknown")}</text>'
            f'<text x="{time_x}" y="{y + 10}" fill="#cbd5e1" font-size="11">{format_duration(value)}</text>'
            f'</g>'
        )
        start = end

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect width="100%" height="100%" fill="transparent"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1f2937" stroke-width="28"/>
      {''.join(slices)}
      <circle cx="{cx}" cy="{cy}" r="42" fill="transparent"/>
      {''.join(legend)}
    </svg>'''
    return svg


def make_bar_chart(title: str, items: list[dict[str, Any]], width: int = 760, height: int = 260, color: str = "#8ecae6", palette: dict[str, str] | None = None, excluded_names: set[str] | None = None) -> str:
    data = clean_chart_items(items, excluded_names=excluded_names)
    if not data:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#0b1220" rx="12"/><text x="24" y="26" fill="#e5e7eb" font-size="16" font-family="sans-serif" font-weight="700">{title}</text></svg>'''

    max_hours = max(float(item.get("total_seconds", 0) or 0) / 3600.0 for item in data)
    axis_hours = log_axis_ceiling(max_hours)
    log_axis_hours = math.log10(1 + axis_hours)
    name_x = 12
    time_x = 155
    bar_left = 285
    bar_right = 700
    plot_top = 24
    row_gap = 18
    row_height = 12

    bars = []
    labels = []
    for idx, item in enumerate(data):
        value_seconds = float(item.get("total_seconds", 0) or 0)
        value_hours = value_seconds / 3600.0
        ratio = math.log10(1 + value_hours) / log_axis_hours if log_axis_hours else 0
        bar_width = max(10, ratio * (bar_right - bar_left))
        y = plot_top + idx * row_gap
        item_color = get_brand_color(str(item.get("name", "")), color, palette or {}) if palette else color
        bars.append(f'<rect x="{bar_left}" y="{y}" width="{bar_width}" height="{row_height}" fill="{item_color}" rx="4" />')
        labels.append(f'<text x="{name_x}" y="{y + 10}" fill="#e2e8f0" font-size="10" font-family="sans-serif">{item.get("name", "")[:18]}</text>')
        labels.append(f'<text x="{time_x}" y="{y + 10}" fill="#cbd5e1" font-size="10" font-family="sans-serif">{format_duration(value_seconds)}</text>')

    height = max(height, plot_top + len(data) * row_gap + 30)

    gridlines = []
    axis_labels = []
    plot_bottom = plot_top + len(data) * row_gap
    for tick in log_scale_ticks(axis_hours, min_ratio_gap=0.08):
        ratio = math.log10(1 + tick) / log_axis_hours if log_axis_hours else 0
        x = bar_left + ratio * (bar_right - bar_left)
        gridlines.append(f'<line x1="{x}" y1="{plot_top - 6}" x2="{x}" y2="{plot_bottom}" stroke="#1f2937" stroke-width="1" />')
        axis_labels.append(f'<text x="{x}" y="{plot_bottom + 14}" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="middle">{tick:g}h</text>')
        axis_labels.append(f'<text x="{x}" y="{plot_top - 12}" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="middle">{tick:g}h</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect width="100%" height="100%" fill="transparent"/>
      {''.join(gridlines)}
      <line x1="{bar_left}" y1="{plot_top - 6}" x2="{bar_right}" y2="{plot_top - 6}" stroke="#334155" stroke-width="1"/>
      <line x1="{bar_left}" y1="{plot_bottom}" x2="{bar_right}" y2="{plot_bottom}" stroke="#334155" stroke-width="1"/>
      {''.join(bars)}
      {''.join(labels)}
      {''.join(axis_labels)}
    </svg>'''
    return svg


def make_vertical_bar_legend_chart(title: str, items: list[dict[str, Any]], width: int = 760, height: int = 260, palette: dict[str, str] | None = None, excluded_names: set[str] | None = None) -> str:
    data = clean_chart_items(items, excluded_names=excluded_names)
    if not data:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="transparent"/><text x="24" y="26" fill="#e5e7eb" font-size="16" font-family="sans-serif" font-weight="700">{title}</text></svg>'''

    max_hours = max(float(item.get("total_seconds", 0) or 0) / 3600.0 for item in data)
    axis_hours = log_axis_ceiling(max_hours)
    log_axis_hours = math.log10(1 + axis_hours)
    chart_left = 90
    chart_right = 660
    plot_bottom = 160
    bar_count = len(data)
    step = (chart_right - chart_left) / max(bar_count, 1)
    bar_width = max(10, min(24, step * 0.7))

    bars = []
    legend = []

    for idx, item in enumerate(data):
        value = float(item.get("total_seconds", 0) or 0) / 3600.0
        ratio = math.log10(1 + value) / log_axis_hours if log_axis_hours else 0
        x = chart_left + idx * step + (step - bar_width) / 2
        bar_height = 110 * ratio
        y = plot_bottom - bar_height
        item_color = get_brand_color(str(item.get("name", "")), "#8ecae6", palette or {}) if palette else "#8ecae6"
        bars.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{item_color}" rx="6" />')

    legend_cols = 2
    legend_rows = [data[i:i + legend_cols] for i in range(0, len(data), legend_cols)]
    for row_idx, row in enumerate(legend_rows):
        row_y = 185 + row_idx * 26
        for col_idx, item in enumerate(row):
            item_color = get_brand_color(str(item.get("name", "")), "#8ecae6", palette or {}) if palette else "#8ecae6"
            x = 120 + col_idx * 310
            label = item.get("name", "")[:15]
            legend.append(f'<rect x="{x}" y="{row_y}" width="12" height="12" rx="3" fill="{item_color}" />')
            legend.append(f'<text x="{x + 18}" y="{row_y + 10}" fill="#e5e7eb" font-size="10" font-family="sans-serif">{label}</text>')
            legend.append(f'<text x="{x + 200}" y="{row_y + 10}" fill="#cbd5e1" font-size="10" font-family="sans-serif" text-anchor="end">{format_duration(float(item.get("total_seconds", 0) or 0))}</text>')

    svg_height = max(height, 220 + len(legend_rows) * 28)

    gridlines = []
    axis_labels = []
    for tick in log_scale_ticks(axis_hours, min_ratio_gap=0.12):
        ratio = math.log10(1 + tick) / log_axis_hours if log_axis_hours else 0
        y = plot_bottom - 110 * ratio
        gridlines.append(f'<line x1="{chart_left}" y1="{y}" x2="{chart_right}" y2="{y}" stroke="#1f2937" stroke-width="1" />')
        axis_labels.append(f'<text x="{chart_left - 6}" y="{y + 3}" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="end">{tick:g}h</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{svg_height}" viewBox="0 0 {width} {svg_height}">
      <rect width="100%" height="100%" fill="transparent"/>
      {''.join(gridlines)}
      <line x1="{chart_left}" y1="{plot_bottom}" x2="{chart_right}" y2="{plot_bottom}" stroke="#334155" stroke-width="1"/>
      {''.join(bars)}
      {''.join(legend)}
      {''.join(axis_labels)}
    </svg>'''
    return svg


def make_os_bar_chart(title: str, items: list[dict[str, Any]], width: int = 760, height: int = 220) -> str:
    data = clean_chart_items(items)
    if not data:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#0b1220" rx="12"/><text x="24" y="26" fill="#f8fafc" font-size="16" font-family="sans-serif" font-weight="700">{title}</text></svg>'''

    total = sum(float(item.get("total_seconds", 0) or 0) for item in data)
    colors = ["#8ecae6", "#b8d432", "#c9a227", "#f4b942", "#9ad1d4", "#d9d9d9"]
    start_x = 120
    start_y = 80
    bar_width = 520
    bar_height = 28
    segments = []
    current_x = start_x

    for idx, item in enumerate(data):
        ratio = (float(item.get("total_seconds", 0) or 0) / total) if total else 0
        segment_width = ratio * bar_width
        segments.append(f'<rect x="{current_x}" y="{start_y}" width="{segment_width}" height="{bar_height}" fill="{colors[idx % len(colors)]}" rx="6" />')
        current_x += segment_width

    legend = []
    for idx, item in enumerate(data):
        total_seconds = float(item.get("total_seconds", 0) or 0)
        label = f"{item.get('name', '')[:12]} · {format_duration(total_seconds)}"
        legend.append(f'<rect x="{120 + (idx % 3) * 170}" y="{130 + (idx // 3) * 22}" width="12" height="12" rx="3" fill="{colors[idx % len(colors)]}" />')
        legend.append(f'<text x="{136 + (idx % 3) * 170}" y="{140 + (idx // 3) * 22}" fill="#e2e8f0" font-size="10" font-family="sans-serif">{label}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect width="100%" height="100%" fill="transparent"/>
      <rect x="{start_x}" y="{start_y}" width="{bar_width}" height="{bar_height}" fill="#1e293b" rx="6" />
      {''.join(segments)}
      {''.join(legend)}
    </svg>'''
    return svg


def make_horizontal_bar_chart(title: str, items: list[dict[str, Any]], width: int = 760, height: int = 240) -> str:
    filtered = items[:8]
    max_value = max((float(item.get("total_seconds", 0) or 0) for item in filtered), default=1)
    rows = []
    for idx, item in enumerate(filtered):
        value = float(item.get("total_seconds", 0) or 0)
        ratio = value / max_value if max_value else 0
        row_y = 40 + idx * 22
        bar_w = 350 * ratio
        rows.append(
            f'<g font-family="sans-serif">'
            f'<text x="20" y="{row_y + 12}" fill="#e5e7eb" font-size="11">{item.get("name", "Unknown")}</text>'
            f'<rect x="160" y="{row_y}" width="350" height="12" rx="6" fill="#1f2937" />'
            f'<rect x="160" y="{row_y}" width="{bar_w}" height="12" rx="6" fill="#34d399" />'
            f'<text x="525" y="{row_y + 12}" fill="#cbd5e1" font-size="11">{item.get("text", "")}</text>'
            f'</g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect width="100%" height="100%" fill="#111827" rx="12"/>
      <text x="24" y="26" fill="#f8fafc" font-size="16" font-family="sans-serif" font-weight="700">{title}</text>
      {''.join(rows)}
    </svg>'''
    return svg


def build_summary_svg(summary: dict[str, Any]) -> str:
    gt = summary.get("grand_total", {})
    av = gt.get("human_readable_daily_average_including_other_language", "—")
    total = gt.get("human_readable_total_including_other_language", "—")
    best = summary.get("best_day", {})
    range_data = summary.get("range", {})
    best_date = best.get("date", "—")
    best_text = best.get("text", "—")
    since = range_data.get("start", "—").split("T")[0]
    days = range_data.get("days_including_holidays", "—")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="200" viewBox="0 0 760 200">
  <rect width="100%" height="100%" fill="transparent"/>
  <g font-family="sans-serif" fill="#e5e7eb">
    <rect x="20" y="20" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="40" y="45" font-size="12" font-weight="600" fill="#cbd5e1">Total</text>
    <text x="40" y="72" font-size="22" font-weight="700">{total}</text>

    <rect x="390" y="20" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="410" y="45" font-size="12" font-weight="600" fill="#cbd5e1">Daily Average</text>
    <text x="410" y="72" font-size="22" font-weight="700">{av}</text>

    <rect x="20" y="110" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="40" y="135" font-size="12" font-weight="600" fill="#cbd5e1">Best Day</text>
    <text x="40" y="157" font-size="16" font-weight="700">{best_date} — {best_text}</text>

    <rect x="390" y="110" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="410" y="135" font-size="12" font-weight="600" fill="#cbd5e1">Since</text>
    <text x="410" y="157" font-size="18" font-weight="700">{since}</text>
    <text x="410" y="172" font-size="11" fill="#cbd5e1">Days: {days}</text>
  </g>
</svg>'''
    return svg


def build_markdown_block(summary: dict[str, Any], language_data: list[dict[str, Any]], editor_data: list[dict[str, Any]], os_data: list[dict[str, Any]], category_data: list[dict[str, Any]]) -> str:
    total_text, avg_text, best_line, since_date, days_count = format_metric(
        summary.get("grand_total", {}),
        summary.get("grand_total", {}),
        summary.get("best_day", {}),
        summary.get("range", {}),
    )

    summary_svg = save_svg("summary", build_summary_svg(summary))
    language_svg = save_svg("languages", make_bar_chart("Languages", language_data, color="#8ecae6", palette=LANGUAGE_COLORS))
    editor_svg = save_svg("editors", make_vertical_bar_legend_chart("Editors", editor_data, palette=EDITOR_COLORS))
    os_svg = save_svg("operating-systems", make_os_bar_chart("Operating Systems", os_data))
    category_svg = save_svg("categories", make_pie_chart("Categories", category_data, width=760, height=220))

    block = f'''<!-- WAKATIME:START -->

### Summary

![Summary]({summary_svg})

### Operating Systems

![Operating Systems]({os_svg})

### Languages

![Languages]({language_svg})

### Editors

![Editors]({editor_svg})

### Categories

![Categories]({category_svg})

<!-- WAKATIME:END -->'''
    return block


def main() -> None:
    summary_payload = fetch_json(BASE_URL + ENDPOINTS["summary"])
    if summary_payload is None:
        raise RuntimeError("Summary endpoint failed")

    language_payload = fetch_json(BASE_URL + ENDPOINTS["languages"])
    editor_payload = fetch_json(BASE_URL + ENDPOINTS["editors"])
    os_payload = fetch_json(BASE_URL + ENDPOINTS["os"])
    category_payload = fetch_json(BASE_URL + ENDPOINTS["categories"])

    summary_data = summary_payload.get("data", {}) if isinstance(summary_payload, dict) else {}
    language_data = language_payload.get("data", []) if isinstance(language_payload, dict) else []
    editor_data = editor_payload.get("data", []) if isinstance(editor_payload, dict) else []
    os_data = os_payload.get("data", []) if isinstance(os_payload, dict) else []
    category_data = category_payload.get("data", []) if isinstance(category_payload, dict) else []

    block = build_markdown_block(summary_data, language_data, editor_data, os_data, category_data)

    current = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    start_marker = "<!-- WAKATIME:START -->"
    end_marker = "<!-- WAKATIME:END -->"

    if start_marker in current and end_marker in current:
        before, _ = current.split(start_marker, 1)
        _, after = current.split(end_marker, 1)
        updated = before + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"

    README_PATH.write_text(updated, encoding="utf-8")
    print("WakaTime data refreshed and README updated.")


if __name__ == "__main__":
    main()
