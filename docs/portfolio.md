# Portfolio

High-reliability personal profile and live WakaTime telemetry system for **Mahadi Sajjad Neloy**, built with **Ada** and deployed with edge-first static assets across Cloudflare, Vercel, Netlify, and Render.

## Architecture

The codebase is built with pure **Ada** (`src_ada/`), emitting optimized HTML, CSS, client scripts, and edge security headers:

- **`Profile` (`src_ada/profile.ads`):** Strongly typed Ada package storing credentials, Crew ID, metadata, and contact endpoints.
- **`Markup` (`src_ada/markup.ads`, `src_ada/markup.adb`):** Emits the semantic HTML document and Cloudflare/Netlify `_headers` security directives.
- **`Styles` (`src_ada/styles.ads`, `src_ada/styles.adb`):** Pure Ada styling package defining theme variables, responsive grid systems, and animations.
- **`Telemetry_Client` (`src_ada/telemetry_client.ads`, `src_ada/telemetry_client.adb`):** Browser-side telemetry engine managing live WakaTime feeds, alphabetical sorting, 0-min item filtering, and `hh:mm:ss` formatting.
- **`Site_Builder` (`src_ada/site_builder.adb`):** Main build binary compiled via GNAT (`site_builder.gpr`).

## Local Development & Build

### Requirements
- **Node.js** 22.x+ (for local preview/CI runner)
- **GNAT** (optional for native Ada compilation, install via `sudo dnf install gcc-gnat` on Fedora or `sudo apt install gnat` on Ubuntu)

### Commands

```sh
# Run build pipeline
npm run build
# or: ./build.sh

# Preview production build locally
npm run preview
# or: npm start
```

## Multi-Cloud Deployment

All providers deploy from the same unified pipeline, serving static edge assets from `dist/client/`:

| Provider | Build Command | Output / Directory | Config File |
| :--- | :--- | :--- | :--- |
| **Cloudflare Workers / Pages** | `npm run build:cloudflare` | `./dist/client` | `wrangler.toml` |
| **Vercel** | `npm run build:vercel` | `dist/client` | `vercel.json` |
| **Netlify** | `npm run build:netlify` | `dist/client` | `netlify.toml` |
| **Render** | `npm run build:render` | `dist/client` (via `node server.mjs`) | `render.yaml` |

## Repository Structure

```text
├── build.sh                 # Unified build script
├── site_builder.gpr         # GNAT project file for Ada
├── server.mjs               # Minimal zero-dependency production server
├── wrangler.toml            # Cloudflare edge assets configuration
├── vercel.json              # Vercel deployment configuration
├── netlify.toml             # Netlify deployment configuration
├── render.yaml              # Render deployment configuration
├── docs/
│   └── portfolio.md         # Technical architecture documentation
├── public/
│   ├── favicon.svg          # Official Ada language favicon
│   ├── robots.txt           # Search engine crawling rules
│   └── sitemap.xml          # Sitemap specification
└── src_ada/
    ├── profile.ads          # Identity & profile spec
    ├── markup.ads           # Markup generation spec
    ├── markup.adb           # Markup generation body
    ├── styles.ads           # Stylesheet spec
    ├── styles.adb           # Stylesheet body
    ├── telemetry_client.ads # Client telemetry spec
    ├── telemetry_client.adb # Client telemetry body
    └── site_builder.adb     # Main Ada build routine
```
