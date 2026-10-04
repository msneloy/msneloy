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
    "vs code": "#007ACC",
    "firefox": "#FF7139",
    "chrome": "#4285F4",
    "android studio": "#3DDC84",
    "antigravity": "#8ecae6",
    "atom": "#66595C",
    "bash": "#4EAA25",
    "brave": "#FB542B",
    "eclipse": "#2C2255",
    "google calendar": "#4285F4",
    "histre": "#8ecae6",
    "intellij idea": "#7F5AF0",
    "idea": "#7F5AF0",
    "pycharm": "#21D789",
    "clion": "#14C9A5",
    "sublime text": "#FF9800",
    "webstorm": "#07C3F2",
    "zed": "#084CCF",
    "zoom": "#0B5CFF",
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


EDITOR_ICON_PATHS = {
    "android studio": "M18.4395 5.5586c-.675 1.1664-1.352 2.3318-2.0274 3.498-.0366-.0155-.0742-.0286-.1113-.043-1.8249-.6957-3.484-.8-4.42-.787-1.8551.0185-3.3544.4643-4.2597.8203-.084-.1494-1.7526-3.021-2.0215-3.4864a1.1451 1.1451 0 0 0-.1406-.1914c-.3312-.364-.9054-.4859-1.379-.203-.475.282-.7136.9361-.3886 1.5019 1.9466 3.3696-.0966-.2158 1.9473 3.3593.0172.031-.4946.2642-1.3926 1.0177C2.8987 12.176.452 14.772 0 18.9902h24c-.119-1.1108-.3686-2.099-.7461-3.0683-.7438-1.9118-1.8435-3.2928-2.7402-4.1836a12.1048 12.1048 0 0 0-2.1309-1.6875c.6594-1.122 1.312-2.2559 1.9649-3.3848.2077-.3615.1886-.7956-.0079-1.1191a1.1001 1.1001 0 0 0-.8515-.5332c-.5225-.0536-.9392.3128-1.0488.5449zm-.0391 8.461c.3944.5926.324 1.3306-.1563 1.6503-.4799.3197-1.188.0985-1.582-.4941-.3944-.5927-.324-1.3307.1563-1.6504.4727-.315-1.1812-.1086-1.582.4941zM7.207 13.5273c.4803.3197.5507 1.0577.1563 1.6504-.394.5926-1.1038.8138-1.584.4941-.48-.3197-.5503-1.0577-.1563-1.6504.4008-.6021 1.1087-.8106 1.584-.4941z",
    "chrome": "M12 0C8.21 0 4.831 1.757 2.632 4.501l3.953 6.848A5.454 5.454 0 0 1 12 6.545h10.691A12 12 0 0 0 12 0zM1.931 5.47A11.943 11.943 0 0 0 0 12c0 6.012 4.42 10.991 10.189 11.864l3.953-6.847a5.45 5.45 0 0 1-6.865-2.29zm13.342 2.166a5.446 5.446 0 0 1 1.45 7.09l.002.001h-.002l-5.344 9.257c.206.01.413.016.621.016 6.627 0 12-5.373 12-12 0-1.54-.29-3.011-.818-4.364zM12 16.364a4.364 4.364 0 1 1 0-8.728 4.364 4.364 0 0 1 0 8.728Z",
    "eclipse": "M11.109.024a15.58 15.58 0 0 0-.737.023C6.728.361 3.469 2.517 1.579 5.86A12.53 12.53 0 0 0 .021 11.11c-.04.517-.02 1.745.035 2.208.306 2.682 1.353 5.06 3.07 6.965 1.962 2.173 4.586 3.467 7.437 3.663.42.032 1.043.04 1.02.012a2.404 2.404 0 0 0-.338-.074c-1.674-.33-3.388-1.13-4.777-2.232a12.344 12.344 0 0 1-2.45-2.636A12.387 12.387 0 0 1 1.884 12.5a12.413 12.413 0 0 1 .56-4.274c.785-2.522 2.37-4.726 4.475-6.228A11.073 11.073 0 0 1 11.156.122l.443-.098zm1.474.51C10.646.65 8.807 1.299 7.301 2.4 5.426 3.77 3.995 5.644 3.22 7.746c-.145.397-.282.82-.282.879 0 .012 3.828.024 10.31.024 8.463 0 10.315-.008 10.315-.036 0-.047-.153-.525-.283-.878-.153-.42-.576-1.31-.82-1.722-.4-.683-.91-1.373-1.474-1.992-1.65-1.82-3.593-2.934-5.82-3.334-.785-.141-1.8-.2-2.585-.153zM23.83 9.97c-.02 0-4.792 0-10.609.004l-10.573.008-.011.059c-.036.16-.134 1.081-.134 1.242 0 .028 1.785.032 10.746.032H24v-.075c0-.102-.07-.791-.106-1.054-.02-.16-.04-.216-.063-.216zm-10.573 2.635c-9.37-.004-10.73 0-10.742.035-.02.04.024.557.075.973.02.157.035.298.035.314 0 .027 2.137.035 10.624.035h10.624l.024-.188c.043-.326.102-.97.094-1.067l-.008-.094zm.003 2.718c-8.882 0-10.321.004-10.321.035 0 .02.054.208.12.42a11.122 11.122 0 0 0 2.072 3.741c.282.342.945 1.036 1.228 1.287 1.568 1.4 3.247 2.216 5.18 2.53.605.094.886.113 1.75.11.91 0 1.297-.032 2.023-.177 2.11-.416 3.914-1.451 5.53-3.17 1.267-1.348 2.106-2.76 2.628-4.41l.117-.366z",
    "firefox": "M20.452 3.445a11.002 11.002 0 0 0-2.482-1.908C16.944.997 15.098.093 12.477.032c-.734-.017-1.457.03-2.174.144-.72.114-1.398.292-2.118.56-1.017.377-1.996.975-2.574 1.554.583-.349 1.476-.733 2.55-.992a10.083 10.083 0 0 1 3.729-.167c2.341.34 4.178 1.381 5.48 2.625a8.066 8.066 0 0 1 1.298 1.587c1.468 2.382 1.33 5.376.184 7.142-.85 1.312-2.67 2.544-4.37 2.53-.583-.023-1.438-.152-2.25-.566-2.629-1.343-3.021-4.688-1.118-6.306-.632-.136-1.82.13-2.646 1.363-.742 1.107-.7 2.816-.242 4.028a6.473 6.473 0 0 1-.59-1.895 7.695 7.695 0 0 1 .416-3.845A8.212 8.212 0 0 1 9.45 5.399c.896-1.069 1.908-1.72 2.75-2.005-.54-.471-1.411-.738-2.421-.767C8.31 2.583 6.327 3.061 4.7 4.41a8.148 8.148 0 0 0-1.976 2.414c-.455.836-.691 1.659-.697 1.678.122-1.445.704-2.994 1.248-4.055-.79.413-1.827 1.668-2.41 3.042C.095 9.37-.2 11.608.14 13.989c.966 5.668 5.9 9.982 11.843 9.982C18.62 23.971 24 18.591 24 11.956a11.93 11.93 0 0 0-3.548-8.511z",
    "jetbrains": "M2.345 23.997A2.347 2.347 0 0 1 0 21.652V10.988C0 9.665.535 8.37 1.473 7.433l5.965-5.961A5.01 5.01 0 0 1 10.989 0h10.666A2.347 2.347 0 0 1 24 2.345v10.664a5.056 5.056 0 0 1-1.473 3.554l-5.965 5.965A5.017 5.017 0 0 1 13.007 24v-.003H2.345Zm8.969-6.854H5.486v1.371h5.828v-1.371ZM3.963 6.514h13.523v13.519l4.257-4.257a3.936 3.936 0 0 0 1.146-2.767V2.345c0-.678-.552-1.234-1.234-1.234H10.989a3.897 3.897 0 0 0-2.767 1.145L3.963 6.514Zm-.192.192L2.256 8.22a3.944 3.944 0 0 0-1.145 2.768v10.664c0 .678.552 1.234 1.234 1.234h10.666a3.9 3.9 0 0 0 2.767-1.146l1.512-1.511H3.771V6.706Z",
    "sublime text": "M20.953.004a.397.397 0 0 0-.18.017L3.225 5.585c-.175.055-.323.214-.402.398a.42.42 0 0 0-.06.22v5.726a.42.42 0 0 0 .06.22c.079.183.227.341.402.397l7.454 2.364-7.454 2.363c-.255.08-.463.374-.463.655v5.688c0 .282.208.444.463.363l17.55-5.565c.237-.075.426-.336.452-.6.003-.022.013-.04.013-.065V12.06c0-.281-.208-.575-.463-.656L13.4 9.065l7.375-2.339c.255-.08.462-.375.462-.656V.384c0-.211-.117-.355-.283-.38z",
    "zed": "M2.25 1.5a.75.75 0 0 0-.75.75v16.5H0V2.25A2.25 2.25 0 0 1 2.25 0h20.095c1.002 0 1.504 1.212.795 1.92L10.764 14.298h3.486V12.75h1.5v1.922a1.125 1.125 0 0 1-1.125 1.125H9.264l-2.578 2.578h11.689V9h1.5v9.375a1.5 1.5 0 0 1-1.5 1.5H5.185L2.562 22.5H21.75a.75.75 0 0 0 .75-.75V5.25H24v16.5A2.25 2.25 0 0 1 21.75 24H1.655C.653 24 .151 22.788.86 22.08L13.19 9.75H9.75v1.5h-1.5V9.375A1.125 1.125 0 0 1 9.375 8.25h5.314l2.625-2.625H5.625V15h-1.5V5.625a1.5 1.5 0 0 1 1.5-1.5h13.19L21.438 1.5z",
    "zoom": "M5.033 14.649H.743a.74.74 0 0 1-.686-.458.74.74 0 0 1 .16-.808L3.19 10.41H1.06A1.06 1.06 0 0 1 0 9.35h3.957c.301 0 .57.18.686.458a.74.74 0 0 1-.161.808L1.51 13.59h2.464c.585 0 1.06.475 1.06 1.06zM24 11.338c0-1.14-.927-2.066-2.066-2.066-.61 0-1.158.265-1.537.686a2.061 2.061 0 0 0-1.536-.686c-1.14 0-2.066.926-2.066 2.066v3.311a1.06 1.06 0 0 0 1.06-1.06v-2.251a1.004 1.004 0 0 1 2.013 0v2.251c0 .586.474 1.06 1.06 1.06v-3.311a1.004 1.004 0 0 1 2.012 0v2.251c0 .586.475 1.06 1.06 1.06zM16.265 12a2.728 2.728 0 1 1-5.457 0 2.728 2.728 0 0 1 5.457 0zm-1.06 0a1.669 1.669 0 1 0-3.338 0 1.669 1.669 0 0 0 3.338 0zm-4.82 0a2.728 2.728 0 1 1-5.458 0 2.728 2.728 0 0 1 5.457 0zm-1.06 0a1.669 1.669 0 1 0-3.338 0 1.669 1.669 0 0 0 3.338 0z",
}

EDITOR_ICON_PATHS.update({
    "android studio": "M18.4395 5.5586c-.675 1.1664-1.352 2.3318-2.0274 3.498-.0366-.0155-.0742-.0286-.1113-.043-1.8249-.6957-3.484-.8-4.42-.787-1.8551.0185-3.3544.4643-4.2597.8203-.084-.1494-1.7526-3.021-2.0215-3.4864a1.1451 1.1451 0 0 0-.1406-.1914c-.3312-.364-.9054-.4859-1.379-.203-.475.282-.7136.9361-.3886 1.5019 1.9466 3.3696-.0966-.2158 1.9473 3.3593.0172.031-.4946.2642-1.3926 1.0177C2.8987 12.176.452 14.772 0 18.9902h24c-.119-1.1108-.3686-2.099-.7461-3.0683-.7438-1.9118-1.8435-3.2928-2.7402-4.1836a12.1048 12.1048 0 0 0-2.1309-1.6875c.6594-1.122 1.312-2.2559 1.9649-3.3848.2077-.3615.1886-.7956-.0079-1.1191a1.1001 1.1001 0 0 0-.8515-.5332c-.5225-.0536-.9392.3128-1.0488.5449zm-.0391 8.461c.3944.5926.324 1.3306-.1563 1.6503-.4799.3197-1.188.0985-1.582-.4941-.3944-.5927-.324-1.3307.1563-1.6504.4727-.315 1.1812-.1086 1.582.4941zM7.207 13.5273c.4803.3197.5503 1.0577.1563 1.6504-.394.5926-1.1038.8138-1.584.4941-.48-.3197-.5503-1.0577-.1563-1.6504.4008-.6021 1.1087-.8106 1.584-.4941z",
    "brave": "M15.68 0l2.096 2.38s1.84-.512 2.709.358c.868.87 1.584 1.638 1.584 1.638l-.562 1.381.715 2.047s-2.104 7.98-2.35 8.955c-.486 1.919-.818 2.66-2.198 3.633-1.38.972-3.884 2.66-4.293 2.916-.409.256-.92.692-1.38.692-.46 0-.97-.436-1.38-.692a185.796 185.796 0 0 1-4.293-2.916c-1.38-.973-1.712-1.714-2.197-3.633-.247-.975-2.351-8.955-2.351-8.955l.715-2.047-.562-1.381s.716-.768 1.585-1.638c.868-.87 2.708-.358 2.708-.358L8.321 0h7.36zm-3.679 14.936c-.14 0-1.038.317-1.758.69-.72.373-1.242.637-1.409.742-.167.104-.065.301.087.409.152.107 2.194 1.69 2.393 1.866.198.175.489.464.687.464.198 0 .49-.29.688-.464.198-.175 2.24-1.759 2.392-1.866.152-.108.254-.305.087-.41-.167-.104-.689-.368-1.41-.741-.72-.373-1.617-.69-1.757-.69zm0-11.278s-.409.001-1.022.206-1.278.46-1.584.46c-.307 0-2.581-.434-2.581-.434S4.119 7.152 4.119 7.849c0 .697.339.881.68 1.243l2.02 2.149c.192.203.59.511.356 1.066-.235.555-.58 1.26-.196 1.977.384.716 1.042 1.194 1.464 1.115.421-.08 1.412-.598 1.776-.834.364-.237 1.518-1.19 1.518-1.554 0-.365-1.193-1.02-1.413-1.168-.22-.15-1.226-.725-1.247-.95-.02-.227-.012-.293.284-.851.297-.559.831-1.304.742-1.8-.089-.495-.95-.753-1.565-.986-.615-.232-1.799-.671-1.947-.74-.148-.068-.11-.133.339-.175.448-.043 1.719-.212 2.292-.052.573.16 1.552.403 1.632.532.079.13.149.134.067.579-.081.445-.5 2.581-.541 2.96-.04.38-.12.63.288.724.409.094 1.097.256 1.333.256s.924-.162 1.333-.256c.408-.093.329-.344.288-.723-.04-.38-.46-2.516-.541-2.961-.082-.445-.012-.45.067-.579.08-.129 1.059-.372 1.632-.532.573-.16 1.845.009 2.292.052.449.042.487.107.339.175-.148.069-1.332.508-1.947.74-.615.233-1.476.49-1.565.986-.09.496.445 1.241.742 1.8.297.558.304.624.284.85-.02.226-1.026.802-1.247.95-.22.15-1.413.804-1.413 1.169 0 .364 1.154 1.317 1.518 1.554.364.236 1.355.755 1.776.834.422.079 1.08-.4 1.464-1.115.384-.716.039-1.422-.195-1.977-.235-.555.163-.863.355-1.066l2.02-2.149c.341-.362.68-.546.68-1.243 0-.697-2.695-3.96-2.695-3.96s-2.274.436-2.58.436c-.307 0-.972-.256-1.585-.461-.613-.205-1.022-.206-1.022-.206z",
    "google calendar": "M18.316 5.684H24v12.632h-5.684V5.684zM5.684 24h12.632v-5.684H5.684V24zM18.316 5.684V0H1.895A1.894 1.894 0 0 0 0 1.895v16.421h5.684V5.684h12.632zm-7.207 6.25v-.065c.272-.144.5-.349.687-.617s.279-.595.279-.982c0-.379-.099-.72-.3-1.025a2.05 2.05 0 0 0-.832-.714 2.703 2.703 0 0 0-1.197-.257c-.6 0-1.094.156-1.481.467-.386.311-.65.671-.793 1.078l1.085.452c.086-.249.224-.461.413-.633.189-.172.445-.257.767-.257.33 0 .602.088.816.264a.86.86 0 0 1 .322.703c0 .33-.12.589-.36.778-.24.19-.535.284-.886.284h-.567v1.085h.633c.407 0 .748.109 1.02.327.272.218.407.499.407.843 0 .336-.129.614-.387.832s-.565.327-.924.327c-.351 0-.651-.103-.897-.311-.248-.208-.422-.502-.521-.881l-1.096.452c.178.616.505 1.082.977 1.401.472.319.984.478 1.538.477a2.84 2.84 0 0 0 1.293-.291c.382-.193.684-.458.902-.794.218-.336.327-.72.327-1.149 0-.429-.115-.797-.344-1.105a2.067 2.067 0 0 0-.881-.689zm2.093-1.931l.602.913L15 10.045v5.744h1.187V8.446h-.827l-2.158 1.557zM22.105 0h-3.289v5.184H24V1.895A1.894 1.894 0 0 0 22.105 0zm-3.289 23.5l4.684-4.684h-4.684V23.5zM0 22.105C0 23.152.848 24 1.895 24h3.289v-5.184H0v3.289z",
})

EDITOR_ICON_ALIASES = {
    "android studio": "android studio",
    "brave": "brave",
    "chrome": "chrome",
    "clion": "jetbrains",
    "eclipse": "eclipse",
    "firefox": "firefox",
    "google calendar": "google calendar",
    "intellij": "jetbrains",
    "pycharm": "jetbrains",
    "sublime text": "sublime text",
    "webstorm": "jetbrains",
    "zed": "zed",
    "zoom": "zoom",
}


def make_editor_icon(name: str, x: float, y: float, color: str) -> str:
    normalized_name = name.strip().lower()
    path_key = next(
        (path for alias, path in EDITOR_ICON_ALIASES.items() if alias in normalized_name),
        None,
    )
    if path_key is None:
        return f'<rect x="{x}" y="{y}" width="20" height="20" rx="4" fill="{color}"/>'

    icon_color = {
        "android studio": "#3DDC84",
        "brave": "#FB542B",
        "chrome": "#4285F4",
        "eclipse": "#2C2255",
        "firefox": "#FF7139",
        "google calendar": "#4285F4",
        "jetbrains": color,
        "sublime text": "#FF9800",
        "zed": "#084CCF",
        "zoom": "#0B5CFF",
    }[path_key]
    return f'<svg x="{x}" y="{y}" width="20" height="20" viewBox="0 0 24 24"><path d="{EDITOR_ICON_PATHS[path_key]}" fill="{icon_color}"/></svg>'


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
    if filtered[-1] < max_value * 0.9999:
        filtered.append(max_value)
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
        y = 30 + row * 28
        legend.append(
            f'<g font-family="sans-serif">'
            f'<rect x="{item_x}" y="{y}" width="16" height="16" rx="3" fill="{colors[idx % len(colors)]}" />'
            f'<text x="{item_x + 24}" y="{y + 15}" fill="#e5e7eb" font-size="20">{item.get("name", "Unknown")}</text>'
            f'<text x="{time_x}" y="{y + 15}" fill="#cbd5e1" font-size="20">{format_duration(value)}</text>'
            f'</g>'
        )
        start = end

    height = max(height, 46 + len(filtered) * 28)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect width="100%" height="100%" fill="transparent"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1f2937" stroke-width="28"/>
      {''.join(slices)}
      <circle cx="{cx}" cy="{cy}" r="42" fill="transparent"/>
      {''.join(legend)}
    </svg>'''
    return svg


def make_bar_chart(title: str, items: list[dict[str, Any]], width: int = 900, height: int = 260, color: str = "#8ecae6", palette: dict[str, str] | None = None, excluded_names: set[str] | None = None) -> str:
    data = [
        item
        for item in clean_chart_items(items, excluded_names=excluded_names)
        if int(item["total_seconds"]) >= 60
    ]
    if not data:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#0b1220" rx="12"/><text x="24" y="26" fill="#e5e7eb" font-size="16" font-family="sans-serif" font-weight="700">{title}</text></svg>'''

    max_hours = max(float(item.get("total_seconds", 0) or 0) / 3600.0 for item in data)
    axis_hours = log_axis_ceiling(max_hours)
    log_axis_hours = math.log10(1 + axis_hours)
    name_x = 12
    time_x = 205
    bar_left = 310
    bar_right = width - 50
    plot_top = 36
    row_gap = 30
    row_height = 18

    bars = []
    labels = []
    for idx, item in enumerate(data):
        value_seconds = float(item.get("total_seconds", 0) or 0)
        value_hours = value_seconds / 3600.0
        ratio = math.log10(1 + value_hours) / log_axis_hours if log_axis_hours else 0
        bar_width = max(10, ratio * (bar_right - bar_left))
        y = plot_top + idx * row_gap
        item_color = get_brand_color(str(item.get("name", "")), color, palette or {}) if palette else color
        bars.append(f'<rect x="{bar_left}" y="{y + 4}" width="{bar_width}" height="{row_height}" fill="{item_color}" rx="4" />')
        labels.append(f'<text x="{name_x}" y="{y + 19}" fill="#e2e8f0" font-size="20" font-family="sans-serif">{item.get("name", "")}</text>')
        labels.append(f'<text x="{time_x}" y="{y + 19}" fill="#cbd5e1" font-size="20" font-family="sans-serif">{format_duration(value_seconds)}</text>')

    gridlines = []
    axis_labels = []
    plot_bottom = plot_top + len(data) * row_gap
    ticks = log_scale_ticks(axis_hours, min_ratio_gap=0.2)
    for index, tick in enumerate(ticks):
        ratio = math.log10(1 + tick) / log_axis_hours if log_axis_hours else 0
        x = bar_left + ratio * (bar_right - bar_left)
        gridlines.append(f'<line x1="{x}" y1="{plot_top - 6}" x2="{x}" y2="{plot_bottom}" stroke="#1f2937" stroke-width="1" />')
        anchor = "end" if index == len(ticks) - 1 else "middle"
        axis_labels.append(f'<text x="{x}" y="{plot_top - 16}" fill="#94a3b8" font-size="16" font-family="sans-serif" text-anchor="{anchor}">{tick:g}h</text>')
        axis_labels.append(f'<text x="{x}" y="{plot_bottom + 30}" fill="#94a3b8" font-size="16" font-family="sans-serif" text-anchor="{anchor}">{tick:g}h</text>')

    height = max(height, plot_bottom + 50)

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


def make_vertical_bar_legend_chart(title: str, items: list[dict[str, Any]], width: int = 900, height: int = 300, palette: dict[str, str] | None = None, excluded_names: set[str] | None = None) -> str:
    data = [
        item
        for item in clean_chart_items(items, excluded_names=excluded_names)
        if int(item["total_seconds"]) >= 60
    ]
    if not data:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="transparent"/><text x="24" y="26" fill="#e5e7eb" font-size="16" font-family="sans-serif" font-weight="700">{title}</text></svg>'''

    max_hours = max(float(item.get("total_seconds", 0) or 0) / 3600.0 for item in data)
    axis_hours = log_axis_ceiling(max_hours)
    log_axis_hours = math.log10(1 + axis_hours)
    chart_left = 90
    chart_right = width - 30
    plot_bottom = 210
    bar_count = len(data)
    step = (chart_right - chart_left) / max(bar_count, 1)
    bar_width = max(10, min(24, step * 0.7))

    bars = []
    legend = []

    for idx, item in enumerate(data):
        value = float(item.get("total_seconds", 0) or 0) / 3600.0
        ratio = math.log10(1 + value) / log_axis_hours if log_axis_hours else 0
        x = chart_left + idx * step + (step - bar_width) / 2
        bar_height = 160 * ratio
        y = plot_bottom - bar_height
        item_color = get_brand_color(str(item.get("name", "")), "#8ecae6", palette or {}) if palette else "#8ecae6"
        bars.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{item_color}" rx="6" />')

    legend_cols = 2
    legend_rows = [data[i:i + legend_cols] for i in range(0, len(data), legend_cols)]
    for row_idx, row in enumerate(legend_rows):
        row_y = 235 + row_idx * 34
        for col_idx, item in enumerate(row):
            item_color = get_brand_color(str(item.get("name", "")), "#8ecae6", palette or {}) if palette else "#8ecae6"
            x = 70 + col_idx * 400
            label = item.get("name", "")[:15]
            legend.append(make_editor_icon(str(item.get("name", "")), x, row_y - 2, item_color))
            legend.append(f'<text x="{x + 30}" y="{row_y + 15}" fill="#e5e7eb" font-size="20" font-family="sans-serif">{label}</text>')
            legend.append(f'<text x="{x + 390}" y="{row_y + 15}" fill="#cbd5e1" font-size="20" font-family="sans-serif" text-anchor="end">{format_duration(float(item.get("total_seconds", 0) or 0))}</text>')

    svg_height = max(height, 280 + len(legend_rows) * 34)

    gridlines = []
    axis_labels = []
    for tick in log_scale_ticks(axis_hours, min_ratio_gap=0.12):
        ratio = math.log10(1 + tick) / log_axis_hours if log_axis_hours else 0
        y = plot_bottom - 160 * ratio
        gridlines.append(f'<line x1="{chart_left}" y1="{y}" x2="{chart_right}" y2="{y}" stroke="#1f2937" stroke-width="1" />')
        axis_labels.append(f'<text x="{chart_left - 6}" y="{y + 5}" fill="#94a3b8" font-size="14" font-family="sans-serif" text-anchor="end">{tick:g}h</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{svg_height}" viewBox="0 0 {width} {svg_height}">
      <rect width="100%" height="100%" fill="transparent"/>
      {''.join(gridlines)}
      <line x1="{chart_left}" y1="{plot_bottom}" x2="{chart_right}" y2="{plot_bottom}" stroke="#334155" stroke-width="1"/>
      {''.join(bars)}
      {''.join(legend)}
      {''.join(axis_labels)}
    </svg>'''
    return svg


def make_os_icon(name: str, x: float, y: float) -> str:
    normalized_name = name.lower()
    if "android" in normalized_name:
        artwork = '<path d="M18.4395 5.5586c-.675 1.1664-1.352 2.3318-2.0274 3.498-.0366-.0155-.0742-.0286-.1113-.043-1.8249-.6957-3.484-.8-4.42-.787-1.8551.0185-3.3544.4643-4.2597.8203-.084-.1494-1.7526-3.021-2.0215-3.4864a1.1451 1.1451 0 0 0-.1406-.1914c-.3312-.364-.9054-.4859-1.379-.203-.475.282-.7136.9361-.3886 1.5019 1.9466 3.3696-.0966-.2158 1.9473 3.3593.0172.031-.4946.2642-1.3926 1.0177C2.8987 12.176.452 14.772 0 18.9902h24c-.119-1.1108-.3686-2.099-.7461-3.0683-.7438-1.9118-1.8435-3.2928-2.7402-4.1836a12.1048 12.1048 0 0 0-2.1309-1.6875c.6594-1.122 1.312-2.2559 1.9649-3.3848.2077-.3615.1886-.7956-.0079-1.1191a1.1001 1.1001 0 0 0-.8515-.5332c-.5225-.0536-.9392.3128-1.0488.5449zm-.0391 8.461c.3944.5926.324 1.3306-.1563 1.6503-.4799.3197-1.188.0985-1.582-.4941-.394-.5927-.324-1.3307.1563-1.6504.4727-.315 1.1812-.1086 1.582.4941zM7.207 13.5273c.4803.3197.5503 1.0577.1563 1.6504-.394.5926-1.1038.8138-1.584.4941-.48-.3197-.5503-1.0577-.1563-1.6504.4008-.6021 1.1087-.8106 1.584-.4941z" fill="#3DDC84"/>'
    elif "linux" in normalized_name:
        artwork = '<path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 0 0-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 0 0-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139zm.529 3.405h.013c.213 0 .396.062.584.198.19.135.33.332.438.533.105.259.158.459.166.724 0-.02.006-.04.006-.06v.105a.086.086 0 0 1-.004-.021l-.004-.024a1.807 1.807 0 0 1-.15.706.953.953 0 0 1-.213.335.71.71 0 0 0-.088-.042c-.104-.045-.198-.064-.284-.133a1.312 1.312 0 0 0-.22-.066c.05-.06.146-.133.183-.198.053-.128.082-.264.088-.402v-.02a1.21 1.21 0 0 0-.061-.4c-.045-.134-.101-.2-.183-.333-.084-.066-.167-.132-.267-.132h-.016c-.093 0-.176.03-.262.132a.8.8 0 0 0-.205.334 1.18 1.18 0 0 0-.09.4v.019c.002.089.008.179.02.267-.193-.067-.438-.135-.607-.202a1.635 1.635 0 0 1-.018-.2v-.02a1.772 1.772 0 0 1 .15-.768c.082-.22.232-.406.43-.533a.985.985 0 0 1 .594-.2zm-2.962.059h.036c.142 0 .27.048.399.135.146.129.264.288.344.465.09.199.14.4.153.667v.004c.007.134.006.2-.002.266v.08c-.03.007-.056.018-.083.024-.152.055-.274.135-.393.2.012-.09.013-.18.003-.267v-.015c-.012-.133-.04-.2-.082-.333a.613.613 0 0 0-.166-.267.248.248 0 0 0-.183-.064h-.021c-.071.006-.13.04-.186.132a.552.552 0 0 0-.12.27.944.944 0 0 0-.023.33v.015c.012.135.037.2.08.334.046.134.098.2.166.268.01.009.02.018.034.024-.07.057-.117.07-.176.136a.304.304 0 0 1-.131.068 2.62 2.62 0 0 1-.275-.402 1.772 1.772 0 0 1-.155-.667 1.759 1.759 0 0 1 .08-.668 1.43 1.43 0 0 1 .283-.535c.128-.133.26-.2.418-.2zm1.37 1.706c.332 0 .733.065 1.216.399.293.2.523.269 1.052.468h.003c.255.136.405.266.478.399v-.131a.571.571 0 0 1 .016.47c-.123.31-.516.643-1.063.842v.002c-.268.135-.501.333-.775.465-.276.135-.588.292-1.012.267a1.139 1.139 0 0 1-.448-.067 3.566 3.566 0 0 1-.322-.198c-.195-.135-.363-.332-.612-.465v-.005h-.005c-.4-.246-.616-.512-.686-.71-.07-.268-.005-.47.193-.6.224-.135.38-.271.483-.336.104-.074.143-.102.176-.131h.002v-.003c.169-.202.436-.47.839-.601.139-.036.294-.065.466-.065zm2.8 2.142c.358 1.417 1.196 3.475 1.735 4.473.286.534.855 1.659 1.102 3.024.156-.005.33.018.513.064.646-1.671-.546-3.467-1.089-3.966-.22-.2-.232-.335-.123-.335.59.534 1.365 1.572 1.646 2.757.13.535.16 1.104.021 1.67.067.028.135.06.205.067 1.032.534 1.413.938 1.23 1.537v-.043c-.06-.003-.12 0-.18 0h-.016c.151-.467-.182-.825-1.065-1.224-.915-.4-1.646-.336-1.77.465-.008.043-.013.066-.018.135-.068.023-.139.053-.209.064-.43.268-.662.669-.793 1.187-.13.533-.17 1.156-.205 1.869v.003c-.02.334-.17.838-.319 1.35-1.5 1.072-3.58 1.538-5.348.334a2.645 2.645 0 0 0-.402-.533 1.45 1.45 0 0 0-.275-.333c.182 0 .338-.03.465-.067a.615.615 0 0 0 .314-.334c.108-.267 0-.697-.345-1.163-.345-.467-.931-.995-1.788-1.521-.63-.4-.986-.87-1.15-1.396-.165-.534-.143-1.085-.015-1.645.245-1.07.873-2.11 1.274-2.763.107-.065.037.135-.408.974-.396.751-1.14 2.497-.122 3.854a8.123 8.123 0 0 1 .647-2.876c.564-1.278 1.743-3.504 1.836-5.268.048.036.217.135.289.202.218.133.38.333.59.465.21.201.477.335.876.335.039.003.075.006.11.006.412 0 .73-.134.997-.268.29-.134.52-.334.74-.4h.005c.467-.135.835-.402 1.044-.7zm2.185 8.958c.037.6.343 1.245.882 1.377.588.134 1.434-.333 1.791-.765l.211-.01c.315-.007.577.01.847.268l.003.003c.208.199.305.53.391.876.085.4.154.78.409 1.066.486.527.645.906.636 1.14l.003-.007v.018l-.003-.012c-.015.262-.185.396-.498.595-.63.401-1.746.712-2.457 1.57-.618.737-1.37 1.14-2.036 1.191-.664.053-1.237-.2-1.574-.898l-.005-.003c-.21-.4-.12-1.025.056-1.69.176-.668.428-1.344.463-1.897.037-.714.076-1.335.195-1.814.12-.465.308-.797.641-.984l.045-.022zm-10.814.049h.01c.053 0 .105.005.157.014.376.055.706.333 1.023.752l.91 1.664.003.003c.243.533.754 1.064 1.189 1.637.434.598.77 1.131.729 1.57v.006c-.057.744-.48 1.148-1.125 1.294-.645.135-1.52.002-2.395-.464-.968-.536-2.118-.469-2.857-.602-.369-.066-.61-.2-.723-.4-.11-.2-.113-.602.123-1.23v-.004l.002-.003c.117-.334.03-.752-.027-1.118-.055-.401-.083-.71.043-.94.16-.334.396-.4.69-.533.294-.135.64-.202.915-.47h.002v-.002c.256-.268.445-.601.668-.838.19-.201.38-.336.663-.336zm7.159-9.074c-.435.201-.945.535-1.488.535-.542 0-.97-.267-1.28-.466-.154-.134-.28-.268-.373-.335-.164-.134-.144-.333-.074-.333.109.016.129.134.199.2.096.066.215.2.36.333.292.2.68.467 1.167.467.485 0 1.053-.267 1.398-.466.195-.135.445-.334.648-.467.156-.136.149-.267.279-.267.128.016.034.134-.147.332a8.097 8.097 0 0 1-.69.468zm-1.082-1.583V5.64c-.006-.02.013-.042.029-.05.074-.043.18-.027.26.004.063 0 .16.067.15.135-.006.049-.085.066-.135.066-.055 0-.092-.043-.141-.068-.052-.018-.146-.008-.163-.065zm-.551 0c-.02.058-.113.049-.166.066-.047.025-.086.068-.14.068-.05 0-.13-.02-.136-.068-.01-.066.088-.133.15-.133.08-.031.184-.047.259-.005.019.009.036.03.03.05v.02h.003z" fill="#FCC624"/>'
    elif "mac" in normalized_name or "apple" in normalized_name:
        artwork = '<path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701" fill="#e5e7eb"/>'
    elif "windows" in normalized_name:
        artwork = '<path d="M0 12.402l35.687-4.86.016 34.423-35.67.203zm35.67 33.529l.028 34.453L.028 75.48.026 45.7zm4.326-39.025L87.314 0v41.527l-47.318.376zm47.329 39.349l-.011 41.34-47.318-6.678-.066-34.739z" fill="#00adef"/>'
    else:
        artwork = (
            '<circle cx="10" cy="10" r="8" fill="#8ecae6"/>'
            '<path d="M10 5v10m-5-5h10" stroke="#0b1220" stroke-width="1.5" stroke-linecap="round"/>'
        )
    scale = 'scale(0.2273)' if "windows" in normalized_name else 'scale(0.8333)'
    return f'<g transform="translate({x} {y}) {scale}">{artwork}</g>'


def make_os_bar_chart(title: str, items: list[dict[str, Any]], width: int = 900, height: int = 220) -> str:
    data = clean_chart_items(items)
    if not data:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#0b1220" rx="12"/><text x="24" y="26" fill="#f8fafc" font-size="16" font-family="sans-serif" font-weight="700">{title}</text></svg>'''

    total = sum(float(item.get("total_seconds", 0) or 0) for item in data)

    def os_color(name: str) -> str:
        normalized_name = name.lower()
        if "android" in normalized_name:
            return "#3DDC84"
        if "linux" in normalized_name:
            return "#FCC624"
        if "mac" in normalized_name or "apple" in normalized_name:
            return "#e5e7eb"
        if "windows" in normalized_name:
            return "#00adef"
        return "#8ecae6"

    start_x = 25
    start_y = 80
    bar_width = width - 50
    bar_height = 28
    segments = []
    current_x = start_x

    for idx, item in enumerate(data):
        ratio = (float(item.get("total_seconds", 0) or 0) / total) if total else 0
        segment_width = ratio * bar_width
        segments.append(f'<rect x="{current_x}" y="{start_y}" width="{segment_width}" height="{bar_height}" fill="{os_color(str(item.get("name", "")))}" rx="6" />')
        current_x += segment_width

    legend = []
    for idx, item in enumerate(data):
        total_seconds = float(item.get("total_seconds", 0) or 0)
        column = idx % 2
        row = idx // 2
        x = 25 + column * 430
        y = 130 + row * 34
        legend.append(make_os_icon(str(item.get("name", "")), x, y - 2))
        legend.append(f'<text x="{x + 30}" y="{y + 18}" fill="#e2e8f0" font-size="20" font-family="sans-serif">{item.get("name", "")}</text>')
        time_x = x + 405
        legend.append(f'<text x="{time_x}" y="{y + 18}" fill="#cbd5e1" font-size="20" font-family="sans-serif" text-anchor="end">{format_duration(total_seconds)}</text>')

    height = max(height, 130 + math.ceil(len(data) / 2) * 34 + 16)

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
        row_y = 40 + idx * 30
        bar_w = 350 * ratio
        rows.append(
            f'<g font-family="sans-serif">'
            f'<text x="20" y="{row_y + 18}" fill="#e5e7eb" font-size="16">{item.get("name", "Unknown")}</text>'
            f'<rect x="160" y="{row_y}" width="350" height="12" rx="6" fill="#1f2937" />'
            f'<rect x="160" y="{row_y}" width="{bar_w}" height="12" rx="6" fill="#34d399" />'
            f'<text x="525" y="{row_y + 18}" fill="#cbd5e1" font-size="16">{item.get("text", "")}</text>'
            f'</g>'
        )

    height = max(height, 40 + len(filtered) * 30 + 12)

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
    <text x="40" y="45" font-size="16" font-weight="600" fill="#cbd5e1">Total</text>
    <text x="40" y="72" font-size="20" font-weight="700">{total}</text>

    <rect x="390" y="20" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="410" y="45" font-size="16" font-weight="600" fill="#cbd5e1">Daily Average</text>
    <text x="410" y="72" font-size="20" font-weight="700">{av}</text>

    <rect x="20" y="110" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="40" y="135" font-size="16" font-weight="600" fill="#cbd5e1">Best Day</text>
    <text x="40" y="161" font-size="20" font-weight="700">{best_date} — {best_text}</text>

    <rect x="390" y="110" width="330" height="70" rx="10" fill="#1f2937"/>
    <text x="410" y="135" font-size="16" font-weight="600" fill="#cbd5e1">Since</text>
    <text x="410" y="161" font-size="20" font-weight="700">{since} ({days} days)</text>
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
