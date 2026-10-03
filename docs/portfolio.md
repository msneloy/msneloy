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

The build writes `dist/index.html` and Cloudflare Pages' `_headers` file.
`cargo run --release --locked` can also be used directly.

## Deploy to Cloudflare Pages or Vercel

Both providers use the same Rust build command and static `dist` output:

| Setting | Cloudflare Pages | Vercel |
| --- | --- | --- |
| Framework preset | `None` / `Other` | `Other` |
| Build command | `bash build.sh` | Configured by `vercel.json` |
| Build output directory | `dist` | Configured by `vercel.json` |

For **Cloudflare Pages**, connect this repository under **Workers & Pages →
Create application → Pages → Import an existing Git repository** and set the
build command and output directory shown above. Cloudflare's build image does
not include Rust, so `build.sh` installs the stable toolchain with rustup when
Cargo is not already available.

If using a custom build pipeline with a separate deploy command, configure
these as two distinct commands:

| Pipeline setting | Command |
| --- | --- |
| Build command | `bash build.sh` |
| Deploy command | `npx wrangler pages deploy dist --project-name=msneloy` |

Do not use `npx wrangler deploy`: that command deploys a Worker, not a Pages
site, and does not build or upload this static output. For Pages Git
integration, set the build command and output directory in the Pages project
settings and let Pages publish the build output itself; do not configure a
separate Worker deploy command.

For **Vercel**, import the repository and leave the framework preset as
**Other**. The root `vercel.json` configures the shared build command, `dist`
output directory, and standard security and cache headers.

The repository's `rust-toolchain.toml` selects stable; Leptos requires Rust
1.88 or newer. The root `wrangler.toml` records the Cloudflare Pages output
directory for Wrangler-compatible workflows. Cloudflare's generated
`_headers` file and Vercel's `vercel.json` apply equivalent security headers
without adding a runtime or assets.

## Structure

```
├── build.sh          # Shared Rust build command
├── vercel.json       # Vercel build, output, and headers
├── wrangler.toml     # Cloudflare Pages build output and command
├── Cargo.toml
├── rust-toolchain.toml
└── src/
    ├── main.rs       # Static output generation and Cloudflare headers
    ├── components.rs # Single-page Leptos view and document shell
    ├── data.rs       # Name, title, and contact information
    └── styles.rs     # Rust-authored inline design system
```
