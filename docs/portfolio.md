# Portfolio

One responsive profile page for **Mahadi Sajjad Neloy**, built with
[Astro](https://astro.build) and on-demand server rendering on all four hosts.

## Develop

Requires Node.js 22.17 or newer and npm.

```sh
npm ci
npm run dev
```

Run Astro and TypeScript checks with:

```sh
npm run check
```

## Build and deploy

Use the provider-specific build command:

| Setting | Cloudflare Workers | Vercel | Netlify | Render |
| --- | --- | --- | --- | --- |
| Framework preset | Astro | Astro | Astro | Node |
| Install command | `npm ci` | `npm ci` | `npm ci` | `npm ci` |
| Build command | `npm run build:cloudflare` | `npm run build:vercel` | `npm run build:netlify` | `npm run build:render` |
| Runtime command | `npx wrangler deploy` | Managed by Vercel | Managed by Netlify | `npm start` |
| Adapter | `@astrojs/cloudflare` | `@astrojs/vercel` | `@astrojs/netlify` | `@astrojs/node` |

For **Cloudflare Workers**, use `npm run build:cloudflare` as the build command
and `npx wrangler deploy` as the deploy command. `wrangler.toml` defines the
Astro Worker entrypoint, compatibility settings, and static asset directory.

For **Vercel**, use the Astro framework preset. `vercel.json` selects the
Vercel build and configures security and cache headers.

For **Netlify**, `netlify.toml` selects the Netlify build, `dist/client`
publish directory, Node.js version, and security/cache headers.

For **Render**, use a Blueprint from `render.yaml`. It builds an Astro
standalone Node server and starts it with `npm start`. For a manual Web
Service, use `npm ci && npm run build:render` as the build command and
`npm start` as the start command.

All four deployments use on-demand server rendering through their native Astro
adapter. `npm run build` is an alias for the Render Node build. Cloudflare
Workers runs on the Workers runtime; future server code there must use
supported Web APIs and Cloudflare bindings rather than assume Node.js APIs.
The WakaTime dashboard data continues to load in the browser.

The page metadata and Person structured data are rendered per request on each
host. The canonical URL and sitemap currently target
`https://neloy.vercel.app/`; update `siteUrl` in `src/lib/profile.ts`,
`public/sitemap.xml`, and `public/robots.txt` together if the primary domain
changes. After deployment, verify `https://neloy.vercel.app/` as a URL-prefix
property in Google Search Console, inspect the homepage, request indexing, and
submit `https://neloy.vercel.app/sitemap.xml`. Search Console verification and
indexing requests must be completed by the site owner, and indexing is not
instant or guaranteed.

## Structure

```text
├── astro.config.ts
├── package.json
├── package-lock.json
├── tsconfig.json
├── vercel.json
├── netlify.toml
├── render.yaml
├── wrangler.toml
└── src/
    ├── app.css
    ├── layouts/
    │   └── BaseLayout.astro
    ├── lib/
    │   └── profile.ts
    ├── middleware.ts
    ├── pages/
    │   └── index.astro
    └── scripts/
        └── dashboard.ts
```
