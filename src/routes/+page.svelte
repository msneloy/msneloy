<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { description, profile } from '../lib/profile';

  const shareBase = 'https://wakatime.com/share/@Sierra117/';
  const feeds = {
    summary: 'ca964aaa-fcd3-4f9b-ad9b-855b90cb5ae4',
    languages: 'bb9729ad-9cb3-4d6c-b912-359e136ed48a',
    editors: '7cab5d5a-187a-4687-9e05-db05c975bf68',
    systems: '8bb890bb-0128-4bb0-adaa-def4d63aa689',
    categories: 'bdfc68ea-2e02-4fef-8870-5f648645152a'
  } as const;

  const ignoredNames = new Set(['other', 'unknown']);
  const nameAliases: Record<string, string> = {
    Browser: 'Brave',
    'Unknown Editor': 'Ghost Mode',
    Other: 'Unmapped Runtime',
    Unknown: 'Unmapped Runtime',
    'Unknown Language': 'Unmapped Runtime',
    'Unknown OS': 'Android'
  };
  const categoryColors = ['#f04455', '#42b9c8', '#f0b64a', '#9584ef', '#71c98d', '#ed7f55', '#58a4e0', '#e879b0'];
  const editorColors = ['#f04455', '#42b9c8', '#f0b64a', '#9584ef', '#71c98d', '#ed7f55', '#58a4e0', '#e879b0', '#b4d94e', '#aab8c5'];
  const axisMultipliers = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5];
  const axisTickMultipliers = [1, 2, 5];
  const operatingSystemColors = ['#f04455', '#e9a343', '#43b9c8', '#7187e8', '#70bd83'];

  interface WakaItem {
    name: string;
    percent: number;
    totalSeconds: number;
    text: string;
  }

  function formatAxisTick(hours: number): string {
    return `${new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3, useGrouping: false }).format(hours)}h`;
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

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    '@id': profile.siteUrl,
    name: profile.name,
    jobTitle: profile.title,
    url: profile.siteUrl,
    email: profile.email,
    telephone: profile.phone,
    sameAs: [profile.github]
  };
  const structuredDataJson = JSON.stringify(structuredData).replace(/</g, '\\u003c');

  let dashboard = $state<DashboardData | null>(null);
  let loading = $state(true);
  let refreshing = $state(false);
  let error = $state('');
  let lastUpdated = $state<Date | null>(null);
  let refreshTimer: ReturnType<typeof setInterval>;

  function record(value: unknown, label: string): Record<string, unknown> {
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
      throw new Error(`WakaTime returned an invalid ${label} response.`);
    }
    return value as Record<string, unknown>;
  }

  function requiredText(source: Record<string, unknown>, key: string, label: string): string {
    const value = source[key];
    if (typeof value !== 'string' || !value.trim()) {
      throw new Error(`WakaTime response is missing ${label}.`);
    }
    return value;
  }

  function parseItems(
    value: unknown,
    label: string,
    limit = Infinity,
    keepShortEntries = false
  ): WakaItem[] {
    if (!Array.isArray(value)) {
      throw new Error(`WakaTime returned invalid ${label} data.`);
    }

    const items = value
      .map((entry): WakaItem | null => {
        if (typeof entry !== 'object' || entry === null || Array.isArray(entry)) return null;
        const item = entry as Record<string, unknown>;
        const sourceName = typeof item.name === 'string' ? item.name.trim() : '';
        const name = nameAliases[sourceName] ?? sourceName;
        const totalSeconds = Number(item.total_seconds);
        const percent = Number(item.percent);
        if (
          !name ||
          (label === 'languages' && name === 'Unmapped Runtime') ||
          !Number.isFinite(totalSeconds) ||
          totalSeconds <= 0 ||
          (!keepShortEntries && totalSeconds < 60) ||
          !Number.isFinite(percent) ||
          percent < 0
        ) return null;
        if (ignoredNames.has(name.toLowerCase())) return null;
        return {
          name,
          percent: Math.min(percent, 100),
          totalSeconds,
          text: typeof item.text === 'string' ? item.text : formatDuration(totalSeconds)
        };
      })
      .filter((item): item is WakaItem => item !== null);

    const ordered = label === 'categories'
      ? items
      : items.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }));
    return limit === Infinity ? ordered : ordered.slice(0, limit);
  }

  function formatDuration(seconds: number): string {
    const wholeSeconds = Math.max(0, Math.floor(seconds));
    const hours = Math.floor(wholeSeconds / 3600);
    const minutes = Math.floor((wholeSeconds % 3600) / 60);
    return `${hours.toString().padStart(4, '0')}H ${minutes.toString().padStart(2, '0')}M`;
  }

  async function fetchFeed(id: string): Promise<unknown> {
    const response = await fetch(`${shareBase}${id}.json`, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`WakaTime request failed (${response.status}).`);
    }
    return response.json();
  }

  async function refreshDashboard(): Promise<void> {
    if (refreshing) return;
    refreshing = true;
    error = '';
    try {
      const [summaryResponse, languagesResponse, editorsResponse, systemsResponse, categoriesResponse] =
        await Promise.all(Object.values(feeds).map(fetchFeed));
      const summaryPayload = record(summaryResponse, 'summary');
      const summary = record(summaryPayload.data, 'summary data');
      const grandTotal = record(summary.grand_total, 'summary totals');
      const range = record(summary.range, 'summary date range');
      const bestDay = record(summary.best_day, 'best-day');

      const languagePayload = record(languagesResponse, 'language');
      const editorPayload = record(editorsResponse, 'editor');
      const systemPayload = record(systemsResponse, 'operating-system');
      const categoryPayload = record(categoriesResponse, 'category');
      const rangeStart = requiredText(range, 'start', 'the tracking start date');
      const rangeEnd = requiredText(range, 'end', 'the latest tracking date');
      const days = Number(range.days_including_holidays);
      if (!Number.isFinite(days)) throw new Error('WakaTime returned an invalid tracked-day count.');

      dashboard = {
        summary: {
          total: requiredText(grandTotal, 'human_readable_total_including_other_language', 'the total tracked time'),
          dailyAverage: requiredText(
            grandTotal,
            'human_readable_daily_average_including_other_language',
            'the daily average'
          ),
          bestDay: {
            date: requiredText(bestDay, 'date', 'the best-day date'),
            text: requiredText(bestDay, 'text', 'the best-day duration')
          },
          start: rangeStart.slice(0, 10),
          end: rangeEnd.slice(0, 10),
          days
        },
        languages: parseItems(languagePayload.data, 'languages'),
        editors: parseItems(editorPayload.data, 'editors'),
        systems: parseItems(systemPayload.data, 'operating systems', Infinity, true),
        categories: parseItems(categoryPayload.data, 'categories', 8, true)
      };
      lastUpdated = new Date();
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Unable to load WakaTime data.';
    } finally {
      loading = false;
      refreshing = false;
    }
  }

  function logAxisCeiling(items: WakaItem[], fillRatio = 0.92): number {
    const maxHours = Math.max(...items.map((item) => item.totalSeconds / 3600), 0);
    if (maxHours <= 0) return 1;
    const logMax = Math.log10(1 + maxHours);
    let base = 0.1;
    while (true) {
      for (const multiplier of axisMultipliers) {
        const ceiling = base * multiplier;
        if (ceiling < maxHours) continue;
        const fill = logMax / Math.log10(1 + ceiling);
        if (fill <= fillRatio) return ceiling;
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
    if (!values.length || values[values.length - 1] < ceiling * 0.9999) values.push(ceiling);

    const filtered: number[] = [];
    for (const value of values) {
      const position = Math.log10(1 + value) / logCeiling;
      const previousPosition = filtered.length
        ? Math.log10(1 + filtered[filtered.length - 1]) / logCeiling
        : 0;
      if (!filtered.length || position - previousPosition >= minRatioGap) filtered.push(value);
    }
    if (filtered[filtered.length - 1] < ceiling * 0.9999) filtered.push(ceiling);
    return filtered.map((value) => ({
      value,
      position: (Math.log10(1 + value) / logCeiling) * 100
    }));
  }

  function logBarWidth(item: WakaItem, items: WakaItem[]): number {
    const hours = item.totalSeconds / 3600;
    const axis = logAxisCeiling(items);
    return Math.max(2, (Math.log10(1 + hours) / Math.log10(1 + axis)) * 100);
  }

  function linearAxis(items: WakaItem[]): { ceiling: number } {
    const maxHours = Math.max(...items.map((item) => item.totalSeconds / 3600), 0);
    if (maxHours <= 0) return { ceiling: 1 };

    const roughStep = maxHours / 4;
    const magnitude = 10 ** Math.floor(Math.log10(roughStep));
    const normalizedStep = roughStep / magnitude;
    const step = (normalizedStep <= 1 ? 1 : normalizedStep <= 2 ? 2 : normalizedStep <= 5 ? 5 : 10) * magnitude;
    const ceiling = Math.ceil(maxHours / step) * step;
    return { ceiling };
  }

  function linearBarWidth(item: WakaItem, maxHours: number): number {
    return Math.max(1, ((item.totalSeconds / 3600) / maxHours) * 100);
  }

  function verticalBarHeight(item: WakaItem, items: WakaItem[]): number {
    return logBarWidth(item, items);
  }

  function osShare(item: WakaItem, items: WakaItem[]): number {
    const total = items.reduce((sum, entry) => sum + entry.totalSeconds, 0);
    return total ? (item.totalSeconds / total) * 100 : 0;
  }

  function osColor(index: number): string {
    return operatingSystemColors[index % operatingSystemColors.length];
  }

  function editorColor(index: number): string {
    return editorColors[index % editorColors.length];
  }

  function categoryGradient(items: WakaItem[]): string {
    let cursor = 0;
    const stops = items.map((item, index) => {
      const start = cursor;
      cursor += item.percent;
      return `${categoryColors[index % categoryColors.length]} ${start}% ${cursor}%`;
    });
    if (cursor < 100) stops.push(`#293746 ${cursor}% 100%`);
    return `conic-gradient(${stops.join(', ')})`;
  }

  const languageAxis = $derived(dashboard ? linearAxis(dashboard.languages) : { ceiling: 1 });
  const editorAxis = $derived(dashboard ? logScaleTicks(dashboard.editors, 0.12) : []);

  onMount(() => {
    void refreshDashboard();
    refreshTimer = setInterval(() => void refreshDashboard(), 15 * 60 * 1000);
  });

  onDestroy(() => clearInterval(refreshTimer));
</script>

<svelte:head>
  <title>{profile.name} — {profile.title}</title>
  <link rel="canonical" href={profile.siteUrl} />
  <meta name="description" content={description} />
  <meta name="author" content={profile.name} />
  <meta name="robots" content="index, follow" />
  <meta name="color-scheme" content="dark" />
  <meta name="theme-color" content="#080b10" />
  <meta property="og:type" content="profile" />
  <meta property="og:site_name" content={profile.name} />
  <meta property="og:url" content={profile.siteUrl} />
  <meta property="og:title" content={`${profile.name} — ${profile.title}`} />
  <meta property="og:description" content={description} />
  <meta property="og:locale" content="en_US" />
  <meta property="profile:first_name" content={profile.firstName} />
  <meta property="profile:last_name" content={profile.lastName} />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content={`${profile.name} — ${profile.title}`} />
  <meta name="twitter:description" content={description} />
  {@html `<script type="application/ld+json">${structuredDataJson}</script>`}
</svelte:head>

<main class="profile dashboard-page">
  <header class="dashboard-header">
    <a class="profile-mark" href="#overview" aria-label="Mahadi Sajjad Neloy home">
      <span>M</span><span>S</span><span>N</span>
    </a>
    <p class="header-label">PERSONNEL FILE <span>/</span> SYSTEMS ENGINEERING</p>
    <div class="header-actions">
      <nav class="header-contact" aria-label="Contact links">
        <a class="header-link" href={`mailto:${profile.email}`} aria-label={`Email ${profile.email}`}>EMAIL</a>
        <a class="header-link" href={`tel:${profile.phoneLink}`} aria-label={`Call ${profile.phone}`}>CALL</a>
        <a class="header-link" href={profile.github} target="_blank" rel="noreferrer" aria-label="Open GitHub in a new tab">GITHUB <span aria-hidden="true">↗</span></a>
      </nav>
      <span class:online={dashboard !== null && !error} class="connection-state">
        <span class="connection-dot"></span>
        {#if loading}CONNECTING{:else if error && dashboard}STALE FEED{:else if error}OFFLINE{:else}LIVE FEED{/if}
      </span>
      <button class="refresh-button" onclick={refreshDashboard} disabled={refreshing} aria-label="Refresh WakaTime data">
        <span class:spinning={refreshing} aria-hidden="true">↻</span>
        <span>{refreshing ? 'SYNCING' : 'SYNC'}</span>
      </button>
    </div>
  </header>

  <section class="identity-panel" id="overview" aria-labelledby="name">
    <div class="identity-main">
      <p class="eyebrow">CREW ID / MS-NL-01</p>
      <h1 id="name">{profile.name}<span>.</span></h1>
      <p class="role">{profile.title}</p>
    </div>
    {#if dashboard}
      <section class="summary-grid" aria-label="WakaTime summary">
        <article class="instrument-card">
          <p class="card-label">TOTAL LOGGED</p>
          <strong>{dashboard.summary.total}</strong>
          <span class="card-index">CAREER HOURS</span>
        </article>
        <article class="instrument-card">
          <p class="card-label">DAILY AVERAGE</p>
          <strong>{dashboard.summary.dailyAverage}</strong>
          <span class="card-index">ALL TRACKED DAYS</span>
        </article>
        <article class="instrument-card">
          <p class="card-label">PEAK OUTPUT</p>
          <strong>{dashboard.summary.bestDay.text}</strong>
          <span class="card-index">{dashboard.summary.bestDay.date}</span>
        </article>
        <article class="instrument-card">
          <p class="card-label">TRACKING WINDOW</p>
          <strong>{dashboard.summary.days.toLocaleString()} <small>DAYS</small></strong>
          <span class="card-index">{dashboard.summary.start} — {dashboard.summary.end}</span>
        </article>
      </section>
    {/if}
  </section>

  {#if error}
    <div class="feed-message" role="alert">
      <span>{error}</span>
      <button class="retry-button" onclick={refreshDashboard}>RETRY CONNECTION</button>
    </div>
  {/if}

  {#if loading && !dashboard}
    <section class="loading-panel" aria-live="polite">
      <span class="loading-indicator"></span>
      <p>ACQUIRING TELEMETRY FROM WAKATIME…</p>
    </section>
  {:else if dashboard}
    <section class="dashboard-grid" aria-label="WakaTime breakdown">
      <article class="dashboard-panel language-panel">
        <header class="panel-heading">
          <div><p class="panel-kicker">02 / DISTRIBUTION</p><h2>Languages</h2></div>
          <span class="panel-meta">{dashboard.languages.length} TRACKED</span>
        </header>
        {#if dashboard.languages.length}
          <ol class="data-list">
            {#each dashboard.languages as item (item.name)}
              <li class="data-row">
                <div class="row-heading"><span>{item.name}</span><span class="row-value">{formatDuration(item.totalSeconds)}<b>{item.percent.toFixed(2)}%</b></span></div>
                <div class="bar-track linear-track" role="meter" aria-label={`${item.name}: ${formatDuration(item.totalSeconds)}`} aria-valuemin="0" aria-valuemax={languageAxis.ceiling} aria-valuenow={item.totalSeconds / 3600}>
                  <span class="bar-fill" style={`--bar-width: ${linearBarWidth(item, languageAxis.ceiling)}%`}></span>
                </div>
              </li>
            {/each}
          </ol>
        {:else}
          <p class="empty-data">No language activity was reported for this range.</p>
        {/if}
      </article>

      <article class="dashboard-panel editor-panel">
        <header class="panel-heading">
          <div><p class="panel-kicker">03 / WORKSTATIONS</p><h2>Editors</h2></div>
          <span class="panel-meta">{dashboard.editors.length} TRACKED</span>
        </header>
        {#if dashboard.editors.length}
          <div class="vertical-chart">
            <div class="vertical-axis" aria-hidden="true">
              {#each editorAxis as tick (tick.value)}
                <span style={`--tick-position: ${tick.position}%`}>{formatAxisTick(tick.value)}</span>
              {/each}
            </div>
            <div class="vertical-plot" role="img" aria-label="Editor activity, vertical log-scale bars; alphabetical order">
              {#each editorAxis as tick (tick.value)}
                <i class="vertical-gridline" style={`--tick-position: ${tick.position}%`}></i>
              {/each}
              <div class="vertical-bars">
                {#each dashboard.editors as item, index (item.name)}
                  <div class="vertical-bar-column" title={`${item.name}: ${formatDuration(item.totalSeconds)}`}>
                    <span class="vertical-bar" style={`--bar-height: ${verticalBarHeight(item, dashboard.editors)}%; --editor-color: ${editorColor(index)}`}></span>
                  </div>
                {/each}
              </div>
            </div>
          </div>
          <ol class="editor-legend">
            {#each dashboard.editors as item, index (item.name)}
              <li>
                <span class="editor-swatch" style={`--editor-color: ${editorColor(index)}`} aria-hidden="true"></span>
                <span>{item.name}</span>
                <strong>{formatDuration(item.totalSeconds)}</strong>
              </li>
            {/each}
          </ol>
        {:else}
          <p class="empty-data">No editor activity above one minute in this range.</p>
        {/if}
      </article>

      <div class="dashboard-side-stack">
        <article class="dashboard-panel systems-panel">
          <header class="panel-heading">
            <div><p class="panel-kicker">04 / ENVIRONMENT</p><h2>Operating systems</h2></div>
            <span class="panel-meta">{dashboard.systems.length} TRACKED</span>
          </header>
          {#if dashboard.systems.length}
            <div class="os-chart" role="group" aria-label="Operating system distribution">
              <div class="os-stacked-bar" role="img" aria-label={dashboard.systems.map((item) => `${item.name} ${item.percent.toFixed(2)}%`).join(', ')}>
                {#each dashboard.systems as item, index (item.name)}
                  <span
                    class="os-segment"
                    style={`--segment-width: ${osShare(item, dashboard.systems)}%; --segment-color: ${osColor(index)}`}
                  ></span>
                {/each}
              </div>
              <ol class="os-legend">
                {#each dashboard.systems as item, index (item.name)}
                  <li>
                    <span class="os-swatch" style={`--segment-color: ${osColor(index)}`}></span>
                    <span class="os-name">{item.name}</span>
                    <span class="os-percent">{item.percent.toFixed(2)}%</span>
                    <strong>{formatDuration(item.totalSeconds)}</strong>
                  </li>
                {/each}
              </ol>
            </div>
          {:else}
            <p class="empty-data">No operating-system activity was reported for this range.</p>
          {/if}
        </article>

        <article class="dashboard-panel category-panel">
          <header class="panel-heading">
            <div><p class="panel-kicker">05 / MISSION PROFILE</p><h2>Categories</h2></div>
            <span class="panel-meta">TOP {dashboard.categories.length}</span>
          </header>
          {#if dashboard.categories.length}
            <div class="category-layout">
              <div class="category-ring" style={`--category-gradient: ${categoryGradient(dashboard.categories)}`} role="img" aria-label="Category distribution ring">
                <div><span>TIME</span><strong>LOG</strong></div>
              </div>
              <ol class="category-list">
                {#each dashboard.categories as item, index (item.name)}
                  <li>
                    <span class="category-swatch" style={`--swatch: ${categoryColors[index % categoryColors.length]}`}></span>
                    <span class="category-name">{item.name}</span>
                    <span class="category-values">
                      <span>{formatDuration(item.totalSeconds)}</span>
                      <b>{item.percent.toFixed(2)}%</b>
                    </span>
                  </li>
                {/each}
              </ol>
            </div>
          {:else}
            <p class="empty-data">No category activity was reported for this range.</p>
          {/if}
        </article>
      </div>
    </section>
    <footer class="dashboard-footer">
      <span>WAKATIME PUBLIC SHARE FEED <span class="footer-divider">/</span> REFRESHED ON LOAD &amp; EVERY 15 MIN <span class="footer-divider">/</span> UNMAPPED RUNTIME = WAKATIME “OTHER”</span>
      {#if lastUpdated}<time datetime={lastUpdated.toISOString()}>LAST SYNC {lastUpdated.toLocaleTimeString()}</time>{/if}
    </footer>
  {/if}
</main>
