# Portfolio

Personal portfolio for **Mahadi Sajjad Neloy**, written entirely in Rust with
[Leptos](https://leptos.dev). No HTML, CSS, or JavaScript is authored by hand:
Leptos renders the markup, and the stylesheet and palette are Rust constants.

The crate lives at the repository root so that Vercel needs no Root Directory
setting and `include_str!` can reach the WakaTime assets in `.github/`.

## How it works

This is a **static site generator**, not a server:

1. `src/data.rs` holds the content, transcribed from `resume.tex`, plus the
   WakaTime SVGs from `.github/wakatime` (embedded with `include_str!`).
2. `src/components.rs` describes the page as Leptos components.
3. `src/styles.rs` is the design system. `PALETTE` is emitted as CSS custom
   properties, and `STYLESHEET` holds the rules that reference them — so the
   Rust palette and the CSS can never drift apart.
4. `src/main.rs` renders `App` once with `RenderHtml::to_html()` and writes
   `dist/index.html` and `dist/404.html`.

Because rendering happens at build time, the deployed site is plain HTML plus
one inline `<style>` block. There is no WASM bundle, no hydration, and no
runtime — so it loads fast and works with JavaScript disabled.

### Why static rather than SSR

Vercel's Rust Functions runtime is currently **permission-gated** ("🔒
Permissions Required: The Rust runtime", public beta on Fluid compute) and
Leptos' own deployment guide only documents Docker/Containerfile for SSR. A
pre-rendered static site needs neither, so it deploys on any Vercel plan.

## Local development

Requires a stable Rust toolchain ([rustup.rs](https://rustup.rs)).

```bash
cargo run --release        # writes dist/
```

Then open `dist/index.html`, or serve it locally:

```bash
python3 -m http.server --directory dist
```

> Build in `--release`. The release profile (`opt-level = "z"`, `lto = true`,
> `panic = "abort"`, `strip = true`) is what keeps the generator binary small.

## Deployment

`vercel.json` at the repository root performs three steps:

| Setting           | Value                          | Purpose                                          |
| ----------------- | ------------------------------ | ------------------------------------------------ |
| `installCommand`  | a no-op `echo`                 | There are no Node dependencies to install.       |
| `buildCommand`    | `bash build.sh`                | Puts Rust on PATH, then renders into `dist/`.    |
| `outputDirectory` | `dist`                         | The static artifact Vercel serves from its CDN.  |

`build.sh` exists because Vercel's Amazon Linux 2023 build image **already ships
Rust under `/rust`**:

- The rustup one-liner is not used. It refuses to install when Rust is already
  present ("cannot install while Rust is installed"), and it writes to
  `$HOME/.cargo/env`, which resolves to `/vercel/.cargo/env` in the build
  container and does not exist — so sourcing it fails the build.
- The script sources `/rust/env`, falls back to `$HOME/.cargo/env`, and exports
  `/rust/bin` on `PATH`. It refreshes the toolchain when rustup is available and
  asserts the Rust version meets Leptos' MSRV of 1.88.

### Deploying

1. Push this repository to GitHub.
2. In Vercel, **Add New → Project** and import the repository.
3. Leave **Root Directory** at the repository root.
4. Leave the Framework Preset as **Other**; `vercel.json` supplies the rest.
5. Deploy.

The first build installs the Rust toolchain and compiles Leptos, so expect it to
take several minutes. Later builds reuse cargo's cache.

> **Note:** Vercel's Root Directory setting restricts a build to that
> subdirectory, and files outside it are not readable. This is why the crate
> sits at the root rather than in a `portfolio/` folder — otherwise the
> `include_str!` calls for the WakaTime SVGs would fail to compile.

## Refreshing the WakaTime charts

The charts under `.github/wakatime` are embedded at compile time. To update
them:

```bash
python3 .github/scripts/update_wakatime_readme.py
cargo run --release
```

## Layout

```
.
├── build.sh          # Vercel entry point: configure Rust, then render
├── Cargo.toml        # leptos with only the `ssr` feature enabled
├── vercel.json       # build + output configuration
├── rust-toolchain.toml
└── src/
    ├── main.rs       # entry point: render, write dist/
    ├── components.rs # Leptos components and document shell
    ├── data.rs       # content from resume.tex and the WakaTime SVGs
    └── styles.rs     # palette + stylesheet, both as Rust
```
