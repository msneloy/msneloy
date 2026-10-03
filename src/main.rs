//! Static site generator for the portfolio.
//!
//! Leptos renders the one-page profile to static HTML for edge deployment.
//! No JavaScript, WASM, or server runtime is needed after the build.

mod components;
mod data;
mod styles;

use std::fs;
use std::path::Path;

use leptos::prelude::*;
use leptos::tachys::view::RenderHtml;

fn main() {
    let out_dir = Path::new("dist");
    fs::create_dir_all(out_dir).expect("failed to create dist/");

    let html = components::document();
    fs::write(out_dir.join("index.html"), &html).expect("failed to write index.html");
    fs::write(out_dir.join("_headers"), CLOUDFLARE_HEADERS)
        .expect("failed to write Cloudflare Pages headers");

    // Remove the old custom not-found page if this output directory predates
    // the single-page build.
    match fs::remove_file(out_dir.join("404.html")) {
        Ok(()) => {}
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => panic!("failed to remove legacy dist/404.html: {error}"),
    }

    println!("Rendered {} bytes to dist/index.html", html.len());
}

const CLOUDFLARE_HEADERS: &str = r#"/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/index.html
  Cache-Control: public, max-age=0, must-revalidate
"#;

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
