//! The complete visual system, authored as Rust string constants.

pub const THEME_COLOR: &str = "#10120f";

/// Stylesheet rules are embedded in the generated document, so the deployment
/// needs no separate asset pipeline or client-side runtime.
pub fn stylesheet() -> &'static str {
    STYLESHEET
}

const STYLESHEET: &str = r#"
:root {
  color-scheme: dark;
  --ink: #f1f2e9;
  --muted: #92978b;
  --dim: #5e655a;
  --acid: #d8ff62;
  --line: rgba(221, 231, 207, 0.14);
  --bg: #10120f;
}

*, *::before, *::after { box-sizing: border-box; }

html {
  min-width: 320px;
  min-height: 100%;
  overflow-x: clip;
  background: var(--bg);
  -webkit-text-size-adjust: 100%;
}

body {
  min-height: 100vh;
  margin: 0;
  overflow-x: hidden;
  color: var(--ink);
  background:
    radial-gradient(ellipse at 79% 48%, rgba(93, 112, 47, 0.16), transparent 35rem),
    radial-gradient(ellipse at 12% 100%, rgba(47, 62, 39, 0.12), transparent 40rem),
    var(--bg);
  font-family: Inter, "Helvetica Neue", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}

body::before {
  position: fixed;
  z-index: 0;
  inset: 0;
  background-image:
    linear-gradient(rgba(235, 245, 220, 0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(235, 245, 220, 0.022) 1px, transparent 1px);
  background-size: 64px 64px;
  content: "";
  pointer-events: none;
  mask-image: linear-gradient(to bottom, black, transparent 88%);
}

.profile {
  position: relative;
  z-index: 1;
  display: flex;
  min-height: 100svh;
  align-items: center;
  isolation: isolate;
  max-width: 1600px;
  margin: 0 auto;
  padding: clamp(48px, 9vh, 112px) clamp(28px, 9vw, 144px);
}

.profile-mark {
  position: absolute;
  top: clamp(28px, 5vh, 52px);
  left: clamp(28px, 9vw, 144px);
  display: flex;
  gap: 5px;
  color: var(--dim);
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
}

.profile-mark span:first-child { color: var(--acid); }

.intro {
  position: relative;
  z-index: 2;
  width: min(100%, 760px);
  padding: clamp(24px, 5vw, 72px) 0;
}

h1 {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin: 0;
  color: var(--ink);
  font-size: clamp(4.25rem, 9vw, 8.4rem);
  font-weight: 560;
  letter-spacing: -0.092em;
  line-height: 0.91;
}

h1 > span { display: block; }

.name-last { margin-top: 0.08em; }
.name-period { color: var(--acid); }

.role {
  margin: clamp(24px, 4vh, 38px) 0 0;
  color: #c1c8b7;
  font-size: clamp(1.1rem, 2vw, 1.4rem);
  font-weight: 400;
  letter-spacing: -0.025em;
}

.contact {
  display: grid;
  width: min(100%, 560px);
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: clamp(42px, 7vh, 72px);
  border-top: 1px solid var(--line);
}

.contact-link {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 10px;
  padding: 18px 22px 16px 0;
  color: inherit;
  text-decoration: none;
}

.contact-link + .contact-link { padding-left: 20px; }

.contact-link + .contact-link::before {
  position: absolute;
  top: 18px;
  bottom: 16px;
  left: 0;
  width: 1px;
  background: var(--line);
  content: "";
}

.contact-label {
  color: var(--dim);
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.contact-value {
  overflow-wrap: anywhere;
  color: #dce0d4;
  font-size: 12px;
  line-height: 1.5;
  transition: color 160ms ease;
}

.contact-arrow {
  position: absolute;
  top: 16px;
  right: 12px;
  color: var(--dim);
  font-size: 13px;
  transition: color 160ms ease, transform 160ms ease;
}

.contact-link:hover .contact-value,
.contact-link:focus-visible .contact-value { color: var(--acid); }

.contact-link:hover .contact-arrow,
.contact-link:focus-visible .contact-arrow {
  color: var(--acid);
  transform: translate(2px, -2px);
}

.contact-link:focus-visible {
  outline: 1px solid var(--acid);
  outline-offset: 5px;
}

.orbit {
  position: absolute;
  z-index: 1;
  top: 50%;
  right: clamp(-8rem, 0vw, 2rem);
  width: clamp(340px, 43vw, 660px);
  aspect-ratio: 1;
  transform: translateY(-50%);
  pointer-events: none;
}

.orbit-ring, .orbit-core, .orbit-line, .orbit-node {
  position: absolute;
  display: block;
}

.orbit-ring {
  top: 50%;
  left: 50%;
  border: 1px solid rgba(216, 255, 98, 0.13);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.orbit-ring-one {
  width: 70%;
  height: 70%;
  animation: revolve 34s linear infinite;
}

.orbit-ring-two {
  width: 100%;
  height: 100%;
  border-color: rgba(216, 255, 98, 0.08);
  animation: revolve 48s linear infinite reverse;
}

.orbit-ring-one::before,
.orbit-ring-two::before,
.orbit-ring-two::after {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--acid);
  box-shadow: 0 0 18px rgba(216, 255, 98, 0.75);
  content: "";
}

.orbit-ring-one::before { top: 16%; right: 17%; }
.orbit-ring-two::before { top: 28%; left: 5%; width: 3px; height: 3px; }
.orbit-ring-two::after { right: 14%; bottom: 14%; width: 3px; height: 3px; }

.orbit-core {
  top: 50%;
  left: 50%;
  width: 28%;
  height: 28%;
  border: 1px solid rgba(216, 255, 98, 0.28);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(216, 255, 98, 0.16), rgba(216, 255, 98, 0.015) 68%);
  box-shadow: 0 0 90px rgba(216, 255, 98, 0.09), inset 0 0 40px rgba(216, 255, 98, 0.06);
  transform: translate(-50%, -50%);
}

.orbit-line {
  top: 50%;
  left: 5%;
  width: 90%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(216, 255, 98, 0.28), transparent);
  transform: rotate(-38deg);
}

.orbit-node {
  width: 8px;
  height: 8px;
  border: 1px solid var(--acid);
  border-radius: 50%;
  background: var(--bg);
  box-shadow: 0 0 17px rgba(216, 255, 98, 0.65);
}

.orbit-node-one { top: 18%; left: 30%; }
.orbit-node-two { top: 69%; left: 78%; width: 5px; height: 5px; }
.orbit-node-three { top: 83%; left: 22%; width: 4px; height: 4px; }

@keyframes revolve {
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@media (min-width: 1100px) {
  .intro { transform: translateY(-1vh); }
}

@media (max-width: 760px) {
  .profile {
    min-height: 100svh;
    padding: 108px 32px 64px;
  }

  .profile-mark { left: 32px; }

  .intro { width: 100%; }

  h1 { font-size: clamp(4.2rem, 14vw, 6.7rem); }

  .orbit {
    top: 42%;
    right: -38%;
    width: min(90vw, 560px);
    opacity: 0.58;
  }
}

@media (max-width: 480px) {
  .profile { padding-right: 24px; padding-left: 24px; }
  .profile-mark { left: 24px; }
  h1 { font-size: clamp(3.75rem, 15vw, 4.5rem); }
  .contact { grid-template-columns: 1fr; margin-top: 38px; }
  .contact-link,
  .contact-link + .contact-link { padding: 14px 22px 14px 0; }
  .contact-link + .contact-link { border-top: 1px solid var(--line); }
  .contact-link + .contact-link::before { display: none; }
  .contact-arrow { top: 14px; right: 4px; }
  .orbit { top: 34%; right: -66%; opacity: 0.38; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
"#;
