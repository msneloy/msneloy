//! Visual design system, expressed as Rust string constants.
//!
//! No `.css` file, build step, or external stylesheet is used. The single
//! stylesheet below is emitted into the generated document by Rust, which keeps
//! the entire front end inside this Rust crate while still allowing the
//! responsive layout, hover states, and theming a portfolio needs. The palette
//! is taken directly from `resume.tex`.

pub const PALETTE: Palette = Palette {
    background: "#141311",
    surface: "#1e1d1a",
    surface_alt: "#26241f",
    border: "#332f28",
    text: "#d4d4d4",
    text_muted: "#8f8a80",
    accent: "#c9a96e",
    accent_soft: "rgba(201, 169, 110, 0.12)",
};

pub struct Palette {
    pub background: &'static str,
    pub surface: &'static str,
    pub surface_alt: &'static str,
    pub border: &'static str,
    pub text: &'static str,
    pub text_muted: &'static str,
    pub accent: &'static str,
    pub accent_soft: &'static str,
}

/// Background colour, mirrored into the document's `theme-color` meta tag.
pub const THEME_COLOR: &str = PALETTE.background;

/// Emits [`PALETTE`] as CSS custom properties so the stylesheet and the Rust
/// palette can never drift apart.
fn palette_vars() -> String {
    format!(
        ":root {{\n\
  --bg: {background};\n\
  --surface: {surface};\n\
  --surface-alt: {surface_alt};\n\
  --border: {border};\n\
  --text: {text};\n\
  --text-muted: {text_muted};\n\
  --accent: {accent};\n\
  --accent-soft: {accent_soft};\n\
}}\n",
        background = PALETTE.background,
        surface = PALETTE.surface,
        surface_alt = PALETTE.surface_alt,
        border = PALETTE.border,
        text = PALETTE.text,
        text_muted = PALETTE.text_muted,
        accent = PALETTE.accent,
        accent_soft = PALETTE.accent_soft,
    )
}

/// The complete stylesheet: palette variables followed by the authored rules.
pub fn stylesheet() -> String {
    format!("{}{}", palette_vars(), STYLESHEET)
}

/// Stylesheet rules, emitted into `<head>`. Authored as Rust, not as a `.css`
/// file. Colours reference the custom properties defined in [`palette_vars`].
const STYLESHEET: &str = r#"
*, *::before, *::after { box-sizing: border-box; }

html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 16px;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.page {
  max-width: 880px;
  margin: 0 auto;
  padding: 0 24px 96px;
}

.masthead {
  padding: 72px 0 40px;
  border-bottom: 1px solid var(--border);
}

.eyebrow {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 14px;
}

h1 {
  font-size: clamp(2rem, 6vw, 3rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 0 0 10px;
  color: #f4f1ea;
  font-weight: 700;
}

.role {
  font-size: 1.05rem;
  color: var(--text-muted);
  margin: 0 0 26px;
}

.contact {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 22px;
  font-size: 0.92rem;
}

.contact a, .contact span { color: var(--text); }
.contact a:hover { color: var(--accent); }

section { margin-top: 64px; }

h2 {
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 28px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
}

h3 { font-size: 1.08rem; margin: 0 0 3px; color: #f4f1ea; font-weight: 650; }
h4 { font-size: 0.88rem; margin: 26px 0 10px; color: #f4f1ea; font-weight: 600; }

.lede { font-size: 1.02rem; color: #b9b4aa; margin: 0; }

.thesis {
  border-left: 2px solid var(--accent);
  background: var(--accent-soft);
  padding: 18px 22px;
  margin: 34px 0 0;
  border-radius: 0 8px 8px 0;
}
.thesis p { margin: 0; font-size: 0.95rem; color: #cfc9be; }

.timeline { display: flex; flex-direction: column; gap: 38px; }

.entry { position: relative; padding-left: 22px; }
.entry::before {
  content: "";
  position: absolute;
  left: 0; top: 9px;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--accent);
}
.entry::after {
  content: "";
  position: absolute;
  left: 3px; top: 22px; bottom: -20px;
  width: 1px;
  background: var(--border);
}
.entry:last-child::after { display: none; }

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 14px;
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 12px;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
}

.meta .org { color: var(--accent); }

ul.ticks { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 9px; }
ul.ticks li { position: relative; padding-left: 20px; font-size: 0.94rem; color: #c4bfb4; }
ul.ticks li::before {
  content: "\2192";
  position: absolute;
  left: 0; top: 0;
  color: var(--accent);
  font-size: 0.85rem;
}

.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 16px; }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
}

.card .label {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  display: block;
  margin-bottom: 10px;
}

.card p { margin: 0; font-size: 0.94rem; color: var(--text); }

.tags { display: flex; flex-wrap: wrap; gap: 7px; }
.tag {
  font-size: 0.78rem;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--surface-alt);
  border: 1px solid var(--border);
  color: #c4bfb4;
  white-space: nowrap;
}
.tag.accent { background: var(--accent-soft); border-color: rgba(201, 169, 110, 0.35); color: var(--accent); }

.cert { display: flex; flex-direction: column; gap: 14px; }
.cert .row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 6px 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}
.cert .row:last-child { border-bottom: none; padding-bottom: 0; }
.cert .who { font-size: 0.94rem; color: var(--text); }
.cert .id {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
  font-size: 0.76rem;
  color: var(--text-muted);
}

.chart {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
  overflow-x: auto;
}
.chart svg { max-width: 100%; height: auto; display: block; }
.chart h4 { margin: 0 0 14px; }

/* Charts are authored at 760px, so they stack full-width rather than
   shrinking into the multi-column grid used for the skill cards. */
.charts { display: flex; flex-direction: column; gap: 18px; margin-top: 22px; }

footer {
  margin-top: 80px;
  padding-top: 28px;
  border-top: 1px solid var(--border);
  font-size: 0.86rem;
  color: var(--text-muted);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
}

@media (max-width: 560px) {
  .masthead { padding-top: 48px; }
  section { margin-top: 48px; }
  .entry { padding-left: 18px; }
}
"#;
