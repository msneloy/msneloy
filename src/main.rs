//! Static site generator for the portfolio.
//!
//! Leptos renders `App` to an HTML string on the server, which is written to
//! `dist/index.html`. That directory is the deployment artifact consumed by
//! Vercel's CDN: no JavaScript, no WASM, and no server runtime are involved at
//! request time.

mod components;
mod data;
mod styles;

use std::fs;
use std::path::Path;

use leptos::prelude::*;
use leptos::tachys::view::RenderHtml;

fn main() {
    let html = components::document();

    let out_dir = Path::new("dist");
    fs::create_dir_all(out_dir).expect("failed to create dist/");
    fs::write(out_dir.join("index.html"), &html).expect("failed to write index.html");

    // Vercel serves `404.html` for unmatched routes on static deployments.
    fs::write(out_dir.join("404.html"), components::not_found_document())
        .expect("failed to write 404.html");

    println!("Rendered {} bytes to dist/index.html", html.len());
}

/// Renders any Leptos view to an HTML string using server-side rendering.
///
/// `RenderHtml::to_html` is the synchronous SSR entry point; an [`Owner`] is
/// established so that any reactive state created while rendering is scoped to
/// this call rather than leaking into the global arena.
pub fn render<F, V>(f: F) -> String
where
    F: FnOnce() -> V,
    V: IntoView + RenderHtml + Send + 'static,
{
    let owner = Owner::new();
    owner.with(move || f().to_html())
}
