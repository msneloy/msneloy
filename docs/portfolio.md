# Portfolio

Personal profile and live WakaTime telemetry dashboard for **Mahadi Sajjad Neloy**. The whole site is one EJS file, served as static assets from Cloudflare Workers, with Vercel as a mirror.

## Architecture

Every source file is an EJS template. The build renders each one to the file a browser needs: `src/X.ejs` becomes `dist/X`. There are no `.html`, `.css` or `.js` files in the repository.

- **`src/index.html.ejs`:** The entire website. In order: the site data load and favicon definition, the `<head>` (SEO, Open Graph, JSON-LD), the stylesheet inline in `<style>`, the page body (top bar, identity panel, loading/error states, dashboard grid, footer), and the telemetry client inline in `<script type="module">`. The client fetches the WakaTime share feeds, merges languages with frameworks, applies the one-hour listing cutoff, renders the summary cards and the panels (languages, editors, operating systems, categories) with brand icons and log-scale bars, and drives the SYNC / RETRY controls. The favicon (Tux on the dark tile) is inlined as a data URI, so the page makes no requests of its own beyond the WakaTime feeds and the analytics beacon.
- **`src/profile.ejs`:** Site data as JSON: name, title, contact details, URLs, WakaTime feed IDs and the Cloudflare Web Analytics token. Templates load it with `JSON.parse(include("profile"))`, so there is one place to change any of it.
- **`src/robots.txt.ejs`, `src/sitemap.xml.ejs`:** Crawler rules and sitemap, with URLs from the profile.
- **`src/_headers.ejs`:** The edge security headers Cloudflare applies to every response, including HSTS and a Content-Security-Policy. The CSP allows the page's inline script by SHA-256; the template renders `index.html.ejs` itself and hashes the exact script text that ships, so the policy can never drift from the code. (This is why `_headers` renders last and why the build needs Node 22.3+.)
- **Social preview card:** `.github/scripts/render_social_card.py` draws a 1200×630 PNG from the live WakaTime summary and top languages, in the weekly workflow, and commits it to `.github/wakatime/social-card.png`. The build copies it to `dist/social-card.png`, which `og:image` and `twitter:image` point at. It reads name, title and crew ID from `src/profile.ejs`.

The build is the `ejs` CLI, driven from `package.json`. Each render gets `</dev/null`: the CLI otherwise reads JSON data from stdin whenever stdin is not a terminal, which would hang a CI build. Note that `include()` only appends `.ejs` to a path with no extension, so a template that includes `index.html.ejs` must name it in full.

## Local Development & Build

### Requirements

- **Node.js** 22.x+

### Commands

```sh
npm ci            # install ejs and wrangler
npm run build     # render src/ into dist/
npm start         # preview dist/ with wrangler dev (http://localhost:8787)
npm run deploy    # build and deploy to Cloudflare Workers
```

## Deployment

| Provider | Build command | Output | Config |
| :--- | :--- | :--- | :--- |
| **Cloudflare Workers** (canonical) | `npm run build` | `./dist` via Workers Static Assets | `wrangler.toml` |
| **Vercel** (mirror) | `npm run build` | `dist` | `vercel.json` |

Security headers come from `dist/_headers` on Cloudflare and from `vercel.json` on Vercel.

## Repository Structure

```text
├── package.json             # build (ejs CLI), preview and deploy scripts
├── wrangler.toml            # Cloudflare Workers static assets
├── vercel.json              # Vercel mirror
├── docs/
│   └── portfolio.md         # This document
├── src/
│   ├── index.html.ejs       # The site: head, inline CSS, body, inline JS
│   ├── profile.ejs          # Site data (JSON)
│   ├── robots.txt.ejs       # Crawler rules
│   ├── sitemap.xml.ejs      # Sitemap
│   └── _headers.ejs         # Edge security headers
└── .github/
    ├── scripts/update_wakatime_readme.py   # README chart generator
    ├── scripts/render_social_card.py       # og:image card generator
    ├── wakatime/social-card.png            # Generated weekly; copied to dist/
    └── workflows/wakatime.yml              # Weekly README + card refresh (Fridays)
```

## Adding a D1 Worker later

Workers block `new Function()`, so EJS cannot render at request time. Any future Worker is authored as `src/worker.js.ejs`, rendered to `dist/worker.js` by the same build, and pointed to from `wrangler.toml` with `main = "dist/worker.js"` and a `[[d1_databases]]` binding. Templates it needs at runtime are precompiled at build time with `ejs.compile(..., { client: true })`.
