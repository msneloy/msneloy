# Portfolio

One responsive profile page for **Mahadi Sajjad Neloy**, built entirely with
Rust and [Leptos](https://leptos.dev). Rust renders the HTML and embeds the
stylesheet at build time. The deployed site is static: it has no JavaScript,
WASM, external assets, or server runtime.

## Build

Requires the stable Rust toolchain specified in `rust-toolchain.toml`.

```sh
bash build.sh
```

The build writes `dist/index.html`. `cargo run --release --locked` can also be
used directly.

## Deploy to Cloudflare Workers or Vercel

Both providers use the same Rust build command and static `dist` output:

| Setting | Cloudflare Workers | Vercel |
| --- | --- | --- |
| Framework preset | `None` / `Other` | `Other` |
| Build command | `bash build.sh` | Configured by `vercel.json` |
| Deploy command | `npx wrangler deploy` | Configured by `vercel.json` |

For **Cloudflare Workers**, connect this repository in **Workers & Pages →
Create application → Workers → Import a repository** and set the build command
to `bash build.sh`. Keep the deploy command as `npx wrangler deploy`. Cloudflare
does not include Rust in its build image, so the build script installs stable
when Cargo is unavailable. The root `wrangler.toml` configures Wrangler to
publish `dist` as static assets, which matches the Git build's default Worker
deploy command.

For **Vercel**, import the repository and leave the framework preset as
**Other**. The root `vercel.json` configures the shared build command, `dist`
output directory, and standard security and cache headers.

The repository's `rust-toolchain.toml` selects stable; Leptos requires Rust
1.88 or newer. Cloudflare serves the generated HTML directly from its static
asset network; there is no custom Worker handler or client-side runtime.
Vercel's `vercel.json` applies the security headers for that deployment.

## Structure

```
├── build.sh          # Shared Rust build command
├── vercel.json       # Vercel build, output, and headers
├── wrangler.toml     # Cloudflare Worker static assets configuration
├── Cargo.toml
├── rust-toolchain.toml
└── src/
    ├── main.rs       # Static output generation
    ├── components.rs # Single-page Leptos view and document shell
    ├── data.rs       # Name, title, and contact information
    └── styles.rs     # Rust-authored inline design system
```
