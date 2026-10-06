# Portfolio

One responsive profile page for **Mahadi Sajjad Neloy**, built with
[SvelteKit](https://kit.svelte.dev) and exported as static files.

## Develop

Requires Node.js 22 or newer and npm.

```sh
npm ci
npm run dev
```

Run the Svelte and TypeScript checks with:

```sh
npm run check
```

## Build and deploy

```sh
npm run build
```

The static site is written to `dist/`.

| Setting | Cloudflare Workers | Vercel | Netlify | Render |
| --- | --- | --- | --- | --- |
| Framework preset | `None` / `Other` | `Other` | SvelteKit / Other | Static Site |
| Install command | `npm ci` | Configured by `vercel.json` | `npm install` | `npm ci` |
| Build command | `npm run build` | Configured by `vercel.json` | Configured by `netlify.toml` | Configured by `render.yaml` |
| Deploy command | `npx wrangler deploy` | Configured by `vercel.json` | Managed by Netlify | Managed by Render |
| Output directory | `dist` | Configured by `vercel.json` | Configured by `netlify.toml` | Configured by `render.yaml` |

For **Cloudflare Workers**, import the repository in Workers Builds and use
`npm ci` as the install command and `bash build.sh` (or `npm run build`) as the
build command. Keep the deploy command as `npx wrangler deploy`. The root
`build.sh` delegates to the npm build script, and `wrangler.toml` publishes the
SvelteKit static output from `dist/`.

For **Vercel**, import the repository and leave the framework preset as
**Other**. The root `vercel.json` configures installation, the static build
output, and security and cache headers.

For **Netlify**, import the repository and let `netlify.toml` configure the
build command, `dist` publish directory, Node.js version, and security/cache
headers.

For **Render**, create a Blueprint from the repository using `render.yaml`.
It defines a static site with `dist` as its publish directory and configures
the build, Node.js version, and security/cache headers.

SvelteKit uses the static adapter; the site does not require a server runtime.
The page metadata and Person structured data are rendered at build time.
The canonical URL and sitemap currently target `https://neloy.vercel.app/`;
update `siteUrl` in `src/lib/profile.ts`, `static/sitemap.xml`, and
`static/robots.txt` together if the primary domain changes. After deployment,
verify `https://neloy.vercel.app/` as a URL-prefix property in Google Search
Console, inspect the homepage, request indexing, and submit
`https://neloy.vercel.app/sitemap.xml`. Search Console verification and
indexing requests must be completed by the site owner, and indexing is not
instant or guaranteed.

The WakaTime dashboard fetches the same public share JSON feeds as the README
charts directly in the browser on page load, with manual refresh and a
15-minute refresh interval. No WakaTime secret or GitHub Actions-generated
site data is required.

## Structure

```
├── package.json
├── package-lock.json
├── svelte.config.js
├── vite.config.ts
├── tsconfig.json
├── vercel.json
├── wrangler.toml
└── src/
    ├── app.html
    ├── app.css
    ├── lib/
    │   └── profile.ts
    └── routes/
        ├── +layout.svelte
        ├── +layout.ts
        └── +page.svelte
```
