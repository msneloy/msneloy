const shareBase = "https://wakatime.com/share/@Sierra117/";
const feeds: {
  summary: string;
  languages: string;
  editors: string;
  systems: string;
  categories: string;
  frameworks?: string;
} = {
  summary: "ca964aaa-fcd3-4f9b-ad9b-855b90cb5ae4",
  languages: "bb9729ad-9cb3-4d6c-b912-359e136ed48a",
  frameworks: "",
  editors: "7cab5d5a-187a-4687-9e05-db05c975bf68",
  systems: "8bb890bb-0128-4bb0-adaa-def4d63aa689",
  categories: "bdfc68ea-2e02-4fef-8870-5f648645152a",
};

const ignoredNames = new Set(["other", "unknown"]);
const nameAliases: Record<string, string> = {
  Browser: "Brave",
  "Unknown Editor": "Ghost Mode",
  Other: "Unmapped Runtime",
  Unknown: "Unmapped Runtime",
  "Unknown Language": "Unmapped Runtime",
  "Unknown OS": "Android",
};
const categoryColors = [
  "#f04455",
  "#42b9c8",
  "#f0b64a",
  "#9584ef",
  "#71c98d",
  "#ed7f55",
  "#58a4e0",
  "#e879b0",
];
const editorColors = [
  "#f04455",
  "#42b9c8",
  "#f0b64a",
  "#9584ef",
  "#71c98d",
  "#ed7f55",
  "#58a4e0",
  "#e879b0",
  "#b4d94e",
  "#aab8c5",
];
const axisMultipliers = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5];
const axisTickMultipliers = [1, 2, 5];
const operatingSystemColors = [
  "#f04455",
  "#e9a343",
  "#43b9c8",
  "#7187e8",
  "#70bd83",
];

interface WakaItem {
  name: string;
  percent: number;
  totalSeconds: number;
  text: string;
  color?: string;
}

interface WakaSummary {
  total: string;
  dailyAverage: string;
  bestDay: {
    date: string;
    text: string;
  };
  start: string;
  end: string;
  days: number;
}

interface DashboardData {
  summary: WakaSummary;
  languages: WakaItem[];
  editors: WakaItem[];
  systems: WakaItem[];
  categories: WakaItem[];
}

interface AxisTick {
  value: number;
  position: number;
}

function escapeHtml(value: unknown): string {
  return String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character]!,
  );
}

function formatAxisTick(hours: number): string {
  return `${new Intl.NumberFormat("en-US", { maximumSignificantDigits: 3, useGrouping: false }).format(hours)}h`;
}

function record(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`WakaTime returned an invalid ${label} response.`);
  }
  return value as Record<string, unknown>;
}

function requiredText(
  source: Record<string, unknown>,
  key: string,
  label: string,
): string {
  const value = source[key];
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`WakaTime response is missing ${label}.`);
  }
  return value;
}

function formatDuration(seconds: number): string {
  const wholeSeconds = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(wholeSeconds / 3600);
  const minutes = Math.floor((wholeSeconds % 3600) / 60);
  const secs = wholeSeconds % 60;
  return `${hours.toString().padStart(2, "0")}:${minutes
    .toString()
    .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

function formatSummaryDuration(seconds: number): string {
  const wholeSeconds = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(wholeSeconds / 3600);
  const minutes = Math.floor((wholeSeconds % 3600) / 60);
  return `${hours.toLocaleString()}H ${minutes.toString().padStart(2, "0")}M`;
}

function parseItems(
  value: unknown,
  label: string,
  limit = Infinity,
): WakaItem[] {
  if (!Array.isArray(value)) {
    throw new Error(`WakaTime returned invalid ${label} data.`);
  }

  const items = value
    .map((entry): WakaItem | null => {
      if (typeof entry !== "object" || entry === null || Array.isArray(entry))
        return null;
      const item = entry as Record<string, unknown>;
      const sourceName = typeof item.name === "string" ? item.name.trim() : "";
      const name = nameAliases[sourceName] ?? sourceName;
      const totalSeconds = Number(item.total_seconds);
      const percent = Number(item.percent);
      const color =
        typeof item.color === "string" && item.color.trim()
          ? item.color.trim()
          : undefined;

      // Filter out invalid entries, unmapped runtime for languages, and anything with 0 min (< 60s)
      if (
        !name ||
        (label === "languages" && name === "Unmapped Runtime") ||
        !Number.isFinite(totalSeconds) ||
        totalSeconds < 60 ||
        Math.floor(totalSeconds / 60) <= 0 ||
        !Number.isFinite(percent) ||
        percent < 0
      )
        return null;
      if (ignoredNames.has(name.toLowerCase())) return null;
      return {
        name,
        percent: Math.min(percent, 100),
        totalSeconds,
        text: formatDuration(totalSeconds),
        color,
      };
    })
    .filter((item): item is WakaItem => item !== null);

  // Sort alphabetically by name (case-insensitive)
  const ordered = items.sort((a, b) =>
    a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
  );
  return limit === Infinity ? ordered : ordered.slice(0, limit);
}

async function fetchFeed(id: string): Promise<unknown> {
  const response = await fetch(`${shareBase}${id}.json`, { cache: "no-store" });
  if (!response.ok)
    throw new Error(`WakaTime request failed (${response.status}).`);
  return response.json();
}

async function loadDashboard(): Promise<DashboardData> {
  const [
    summaryResponse,
    languagesResponse,
    editorsResponse,
    systemsResponse,
    categoriesResponse,
    frameworksResponse,
  ] = await Promise.all([
    fetchFeed(feeds.summary),
    fetchFeed(feeds.languages),
    fetchFeed(feeds.editors),
    fetchFeed(feeds.systems),
    fetchFeed(feeds.categories),
    feeds.frameworks
      ? fetchFeed(feeds.frameworks).catch(() => null)
      : Promise.resolve(null),
  ]);
  const summaryPayload = record(summaryResponse, "summary");
  const summary = record(summaryPayload.data, "summary data");
  const grandTotal = record(summary.grand_total, "summary totals");
  const range = record(summary.range, "summary date range");
  const bestDay = record(summary.best_day, "best-day");
  const totalSeconds = Number(
    grandTotal.total_seconds_including_other_language ??
      grandTotal.total_seconds ??
      0,
  );
  const dailyAverageSeconds = Number(
    grandTotal.daily_average_including_other_language ??
      grandTotal.daily_average ??
      0,
  );
  const bestDaySeconds = Number(bestDay.total_seconds ?? 0);

  const languagePayload = record(languagesResponse, "language");
  const editorPayload = record(editorsResponse, "editor");
  const systemPayload = record(systemsResponse, "operating-system");
  const categoryPayload = record(categoriesResponse, "category");
  const rangeStart = requiredText(range, "start", "the tracking start date");
  const rangeEnd = requiredText(range, "end", "the latest tracking date");
  const days = Number(range.days_including_holidays);
  if (!Number.isFinite(days))
    throw new Error("WakaTime returned an invalid tracked-day count.");

  const languagesList = parseItems(languagePayload.data, "languages");
  const frameworksList =
    frameworksResponse && typeof frameworksResponse === "object"
      ? parseItems(record(frameworksResponse, "frameworks").data, "frameworks")
      : [];

  const combinedLanguageMap = new Map<string, WakaItem>();
  for (const item of [...languagesList, ...frameworksList]) {
    const existing = combinedLanguageMap.get(item.name);
    if (existing) {
      existing.totalSeconds += item.totalSeconds;
      existing.percent = Math.min(100, existing.percent + item.percent);
      existing.text = formatDuration(existing.totalSeconds);
      if (!existing.color && item.color) existing.color = item.color;
    } else {
      combinedLanguageMap.set(item.name, { ...item });
    }
  }

  const combinedLanguages = Array.from(combinedLanguageMap.values()).sort(
    (a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
  );

  return {
    summary: {
      total: Number.isFinite(totalSeconds)
        ? formatSummaryDuration(totalSeconds)
        : requiredText(
            grandTotal,
            "human_readable_total_including_other_language",
            "the total tracked time",
          ),
      dailyAverage: Number.isFinite(dailyAverageSeconds)
        ? formatSummaryDuration(dailyAverageSeconds)
        : requiredText(
            grandTotal,
            "human_readable_daily_average",
            "the daily average",
          ),
      bestDay: {
        date: requiredText(bestDay, "date", "the best-day date"),
        text: Number.isFinite(bestDaySeconds)
          ? formatSummaryDuration(bestDaySeconds)
          : requiredText(bestDay, "text", "the best-day duration"),
      },
      start: rangeStart.slice(0, 10),
      end: rangeEnd.slice(0, 10),
      days,
    },
    languages: combinedLanguages,
    editors: parseItems(editorPayload.data, "editors"),
    systems: parseItems(systemPayload.data, "operating systems"),
    categories: parseItems(categoryPayload.data, "categories", 8),
  };
}

function logAxisCeiling(items: WakaItem[], fillRatio = 0.92): number {
  const maxHours = Math.max(
    ...items.map((item) => item.totalSeconds / 3600),
    0,
  );
  if (maxHours <= 0) return 1;
  const logMax = Math.log10(1 + maxHours);
  let base = 0.1;
  while (true) {
    for (const multiplier of axisMultipliers) {
      const ceiling = base * multiplier;
      if (ceiling < maxHours) continue;
      if (logMax / Math.log10(1 + ceiling) <= fillRatio) return ceiling;
    }
    base *= 10;
  }
}

function logScaleTicks(items: WakaItem[], minRatioGap: number): AxisTick[] {
  const ceiling = logAxisCeiling(items);
  const logCeiling = Math.log10(1 + ceiling);
  const values: number[] = [];
  for (let base = 0.1; base <= ceiling * 1.0001; base *= 10) {
    for (const multiplier of axisTickMultipliers) {
      const value = base * multiplier;
      if (value <= ceiling * 1.0001) values.push(value);
    }
  }
  if (!values.length || values[values.length - 1] < ceiling * 0.9999)
    values.push(ceiling);

  const filtered: number[] = [];
  for (const value of values) {
    const position = Math.log10(1 + value) / logCeiling;
    const previousPosition = filtered.length
      ? Math.log10(1 + filtered[filtered.length - 1]) / logCeiling
      : 0;
    if (!filtered.length || position - previousPosition >= minRatioGap)
      filtered.push(value);
  }
  if (filtered[filtered.length - 1] < ceiling * 0.9999) filtered.push(ceiling);
  return filtered.map((value) => ({
    value,
    position: (Math.log10(1 + value) / logCeiling) * 100,
  }));
}

function logBarWidth(item: WakaItem, items: WakaItem[]): number {
  const hours = item.totalSeconds / 3600;
  const axis = logAxisCeiling(items);
  return Math.max(2, (Math.log10(1 + hours) / Math.log10(1 + axis)) * 100);
}

function linearAxis(items: WakaItem[]): number {
  const maxHours = Math.max(
    ...items.map((item) => item.totalSeconds / 3600),
    0,
  );
  if (maxHours <= 0) return 1;
  const roughStep = maxHours / 4;
  const magnitude = 10 ** Math.floor(Math.log10(roughStep));
  const normalizedStep = roughStep / magnitude;
  const step =
    (normalizedStep <= 1
      ? 1
      : normalizedStep <= 2
        ? 2
        : normalizedStep <= 5
          ? 5
          : 10) * magnitude;
  return Math.ceil(maxHours / step) * step;
}

function categoryGradient(items: WakaItem[]): string {
  let cursor = 0;
  const stops = items.map((item, index) => {
    const start = cursor;
    cursor += item.percent;
    return `${categoryColors[index % categoryColors.length]} ${start}% ${cursor}%`;
  });
  if (cursor < 100) stops.push(`#293746 ${cursor}% 100%`);
  return `conic-gradient(${stops.join(", ")})`;
}

function summaryMarkup(summary: WakaSummary): string {
  return `
    <article class="instrument-card">
      <p class="card-label">TOTAL LOGGED</p>
      <strong>${escapeHtml(summary.total)}</strong>
      <span class="card-index">CAREER HOURS</span>
    </article>
    <article class="instrument-card">
      <p class="card-label">DAILY AVERAGE</p>
      <strong>${escapeHtml(summary.dailyAverage)}</strong>
      <span class="card-index">ALL TRACKED DAYS</span>
    </article>
    <article class="instrument-card">
      <p class="card-label">PEAK OUTPUT</p>
      <strong>${escapeHtml(summary.bestDay.text)}</strong>
      <span class="card-index">${escapeHtml(summary.bestDay.date)}</span>
    </article>
    <article class="instrument-card">
      <p class="card-label">TRACKING WINDOW</p>
      <strong>${summary.days.toLocaleString()} <small>DAYS</small></strong>
      <span class="card-index">${escapeHtml(summary.start)} — ${escapeHtml(summary.end)}</span>
    </article>`;
}

function languageMarkup(items: WakaItem[]): string {
  const ceiling = linearAxis(items);
  const rows = items
    .map(
      (item) => `
    <li class="data-row">
      <div class="row-heading"><span>${escapeHtml(item.name)}</span><span class="row-value">${formatDuration(item.totalSeconds)}<b>${item.percent.toFixed(2)}%</b></span></div>
      <div class="bar-track linear-track" role="meter" aria-label="${escapeHtml(`${item.name}: ${formatDuration(item.totalSeconds)}`)}" aria-valuemin="0" aria-valuemax="${ceiling}" aria-valuenow="${item.totalSeconds / 3600}">
        <span class="bar-fill" style="--bar-width: ${Math.max(1, (item.totalSeconds / 3600 / ceiling) * 100)}%"></span>
      </div>
    </li>`,
    )
    .join("");
  return `
    <article class="dashboard-panel language-panel">
      <header class="panel-heading">
        <div><p class="panel-kicker">02 / DISTRIBUTION</p><h2>Languages &amp; Frameworks</h2></div>
        <span class="panel-meta">${items.length} TRACKED</span>
      </header>
      ${items.length ? `<ol class="data-list">${rows}</ol>` : '<p class="empty-data">No language or framework activity was reported for this range.</p>'}
    </article>`;
}

function editorMarkup(items: WakaItem[]): string {
  const ticks = logScaleTicks(items, 0.12);
  const axis = ticks
    .map(
      (tick) =>
        `<span style="--tick-position: ${tick.position}%">${formatAxisTick(tick.value)}</span>`,
    )
    .join("");
  const gridlines = ticks
    .map(
      (tick) =>
        `<i class="vertical-gridline" style="--tick-position: ${tick.position}%"></i>`,
    )
    .join("");
  const bars = items
    .map(
      (item, index) => {
        const color = item.color || editorColors[index % editorColors.length];
        return `
    <div class="vertical-bar-column" title="${escapeHtml(`${item.name}: ${formatDuration(item.totalSeconds)}`)}">
      <span class="vertical-bar" style="--bar-height: ${logBarWidth(item, items)}%; --editor-color: ${color}"></span>
    </div>`;
      },
    )
    .join("");
  const legend = items
    .map(
      (item, index) => {
        const color = item.color || editorColors[index % editorColors.length];
        return `
    <li>
      <span class="editor-swatch" style="--editor-color: ${color}" aria-hidden="true"></span>
      <span>${escapeHtml(item.name)}</span>
      <strong>${formatDuration(item.totalSeconds)}</strong>
    </li>`;
      },
    )
    .join("");
  return `
    <article class="dashboard-panel editor-panel">
      <header class="panel-heading">
        <div><p class="panel-kicker">03 / WORKSTATIONS</p><h2>Editors</h2></div>
        <span class="panel-meta">${items.length} TRACKED</span>
      </header>
      ${
        items.length
          ? `
        <div class="vertical-chart">
          <div class="vertical-axis" aria-hidden="true">${axis}</div>
          <div class="vertical-plot" role="img" aria-label="Editor activity, vertical log-scale bars; alphabetical order">
            ${gridlines}<div class="vertical-bars">${bars}</div>
          </div>
        </div>
        <ol class="editor-legend">${legend}</ol>`
          : '<p class="empty-data">No editor activity was reported for this range.</p>'
      }
    </article>`;
}

function systemsMarkup(items: WakaItem[]): string {
  const segments = items
    .map(
      (item, index) => `
    <span class="os-segment" style="--segment-width: ${osShare(item, items)}%; --segment-color: ${operatingSystemColors[index % operatingSystemColors.length]}"></span>`,
    )
    .join("");
  const legend = items
    .map(
      (item, index) => `
    <li>
      <span class="os-swatch" style="--segment-color: ${operatingSystemColors[index % operatingSystemColors.length]}"></span>
      <span class="os-name">${escapeHtml(item.name)}</span>
      <span class="os-percent">${item.percent.toFixed(2)}%</span>
      <strong>${formatDuration(item.totalSeconds)}</strong>
    </li>`,
    )
    .join("");
  const chartLabel = items
    .map((item) => `${item.name} ${item.percent.toFixed(2)}%`)
    .map(escapeHtml)
    .join(", ");
  return `
    <article class="dashboard-panel systems-panel">
      <header class="panel-heading">
        <div><p class="panel-kicker">04 / ENVIRONMENT</p><h2>Operating systems</h2></div>
        <span class="panel-meta">${items.length} TRACKED</span>
      </header>
      ${
        items.length
          ? `
        <div class="os-chart" role="group" aria-label="Operating system distribution">
          <div class="os-stacked-bar" role="img" aria-label="${chartLabel}">${segments}</div>
          <ol class="os-legend">${legend}</ol>
        </div>`
          : '<p class="empty-data">No operating-system activity was reported for this range.</p>'
      }
    </article>`;
}

function osShare(item: WakaItem, items: WakaItem[]): number {
  const total = items.reduce((sum, entry) => sum + entry.totalSeconds, 0);
  return total ? (item.totalSeconds / total) * 100 : 0;
}

function categoriesMarkup(items: WakaItem[]): string {
  const legend = items
    .map(
      (item, index) => `
    <li>
      <span class="category-swatch" style="--swatch: ${categoryColors[index % categoryColors.length]}"></span>
      <span class="category-name">${escapeHtml(item.name)}</span>
      <span class="category-values">
        <span>${formatDuration(item.totalSeconds)}</span>
        <b>${item.percent.toFixed(2)}%</b>
      </span>
    </li>`,
    )
    .join("");
  return `
    <article class="dashboard-panel category-panel">
      <header class="panel-heading">
        <div><p class="panel-kicker">05 / MISSION PROFILE</p><h2>Categories</h2></div>
        <span class="panel-meta">TOP ${items.length}</span>
      </header>
      ${
        items.length
          ? `
        <div class="category-layout">
          <div class="category-ring" style="--category-gradient: ${categoryGradient(items)}" role="img" aria-label="Category distribution ring">
            <div><span>TIME</span><strong>LOG</strong></div>
          </div>
          <ol class="category-list">${legend}</ol>
        </div>`
          : '<p class="empty-data">No category activity was reported for this range.</p>'
      }
    </article>`;
}

function dashboardMarkup(data: DashboardData): string {
  return `
    ${languageMarkup(data.languages)}
    ${editorMarkup(data.editors)}
    <div class="dashboard-side-stack">
      ${systemsMarkup(data.systems)}
      ${categoriesMarkup(data.categories)}
    </div>`;
}

const getElement = <T extends HTMLElement>(selector: string): T => {
  const element = document.querySelector<T>(selector);
  if (!element)
    throw new Error(`Dashboard element "${selector}" was not found.`);
  return element;
};

const connectionState = getElement(".connection-state");
const connectionLabel = getElement<HTMLElement>("#connection-label");
const refreshButton = getElement<HTMLButtonElement>("#refresh-button");
const refreshLabel = getElement<HTMLElement>(".refresh-label");
const refreshIcon = getElement<HTMLElement>(".refresh-icon");
const summaryGrid = getElement<HTMLElement>("#summary-grid");
const feedMessage = getElement<HTMLElement>("#feed-message");
const feedError = getElement<HTMLElement>("#feed-error");
const retryButton = getElement<HTMLButtonElement>("#retry-button");
const loadingPanel = getElement<HTMLElement>("#loading-panel");
const dashboardGrid = getElement<HTMLElement>("#dashboard-grid");
const dashboardFooter = getElement<HTMLElement>("#dashboard-footer");
let refreshing = false;
let loadedDashboard = false;

async function refreshDashboard(): Promise<void> {
  if (refreshing) return;
  refreshing = true;
  refreshButton.disabled = true;
  refreshIcon.classList.add("spinning");
  refreshLabel.textContent = "SYNCING";
  feedMessage.hidden = true;
  connectionState.classList.remove("online");
  if (loadedDashboard) connectionLabel.textContent = "SYNCING";

  try {
    const data = await loadDashboard();
    summaryGrid.innerHTML = summaryMarkup(data.summary);
    summaryGrid.hidden = false;
    dashboardGrid.innerHTML = dashboardMarkup(data);
    dashboardGrid.hidden = false;
    dashboardFooter.innerHTML = `
      <span>WAKATIME PUBLIC SHARE FEED <span class="footer-divider">/</span> REFRESHED ON LOAD &amp; EVERY 15 MIN <span class="footer-divider">/</span> UNMAPPED RUNTIME = WAKATIME “OTHER”</span>
      <time datetime="${new Date().toISOString()}">LAST SYNC ${escapeHtml(new Date().toLocaleTimeString())}</time>`;
    dashboardFooter.hidden = false;
    loadingPanel.hidden = true;
    connectionState.classList.add("online");
    connectionLabel.textContent = "LIVE FEED";
    loadedDashboard = true;
  } catch (cause) {
    const message =
      cause instanceof Error ? cause.message : "Unable to load WakaTime data.";
    feedError.textContent = message;
    feedMessage.hidden = false;
    connectionState.classList.remove("online");
    connectionLabel.textContent = loadedDashboard ? "STALE FEED" : "OFFLINE";
    if (!loadedDashboard) loadingPanel.hidden = true;
  } finally {
    refreshing = false;
    refreshButton.disabled = false;
    refreshIcon.classList.remove("spinning");
    refreshLabel.textContent = "SYNC";
  }
}

refreshButton.addEventListener("click", () => void refreshDashboard());
retryButton.addEventListener("click", () => void refreshDashboard());
void refreshDashboard();
window.setInterval(() => void refreshDashboard(), 15 * 60 * 1000);
