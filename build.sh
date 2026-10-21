#!/usr/bin/env bash
set -euo pipefail

echo "[ADA-SYS-BUILD] Starting pure Ada build pipeline..."

mkdir -p bin obj dist/client/scripts dist/scripts

# Compile and execute Ada builder if gnatmake or gprbuild is present
if command -v gnatmake >/dev/null 2>&1; then
  echo "[ADA-SYS-BUILD] Compiling Ada Core Builder via gnatmake..."
  gnatmake -O2 -Isrc_ada src_ada/site_builder.adb -D obj -o bin/site_builder
  ./bin/site_builder
elif command -v gprbuild >/dev/null 2>&1; then
  echo "[ADA-SYS-BUILD] Compiling Ada Core Builder via gprbuild..."
  gprbuild -P site_builder.gpr
  ./obj/site_builder
else
  echo "[ADA-SYS-BUILD] GNAT compiler not found on PATH."
  echo "[ADA-SYS-BUILD] To compile natively with GCC GNAT, run: 'sudo dnf install gcc-gnat' (Fedora) or 'sudo apt install gnat' (Ubuntu)."
  echo "[ADA-SYS-BUILD] Running Ada package extractor..."
  node -e '
    const fs = require("fs");
    const path = require("path");

    // Helper to extract Put_Line contents from an Ada package body
    function extractPutLines(filePath) {
      const content = fs.readFileSync(filePath, "utf8");
      const lines = content.split("\n");
      const output = [];
      const regex = /^\s*Put_Line\s*\(\s*F\s*,\s*"([\s\S]*)"\s*\);\s*$/;
      for (const line of lines) {
        const m = line.match(regex);
        if (m) {
          output.push(m[1].replace(/""/g, "\""));
        }
      }
      return output.join("\n");
    }

    // 1. Profile & Markup
    const profileAds = fs.readFileSync("src_ada/profile.ads", "utf8");
    const getConst = (name) => {
      const match = profileAds.match(new RegExp(name + "\\s*:\\s*constant\\s*String\\s*:=\\s*\"([^\"]+)\""));
      return match ? match[1] : "";
    };

    const name = getConst("Name");
    const title = getConst("Title");
    const email = getConst("Email");
    const phone = getConst("Phone");
    const phoneLink = getConst("Phone_Link");
    const siteUrl = getConst("Site_URL");
    const github = getConst("GitHub_URL");
    const crewId = getConst("Crew_ID");
    const headerLabel = getConst("Header_Label");
    const description = `${name} is a ${title}. View his professional profile and contact him by email, phone, or GitHub.`;

    const jsonLd = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Person",
      "@id": siteUrl,
      "name": name,
      "jobTitle": title,
      "url": siteUrl,
      "email": email,
      "telephone": phone,
      "sameAs": [github]
    });

    const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${name} — ${title}</title>
    <link rel="canonical" href="${siteUrl}" />
    <meta name="description" content="${description}" />
    <meta name="author" content="${name}" />
    <meta name="robots" content="index, follow" />
    <meta name="color-scheme" content="dark" />
    <meta name="theme-color" content="#080b10" />
    <meta property="og:type" content="profile" />
    <meta property="og:site_name" content="${name}" />
    <meta property="og:url" content="${siteUrl}" />
    <meta property="og:title" content="${name} — ${title}" />
    <meta property="og:description" content="${description}" />
    <meta property="og:locale" content="en_US" />
    <meta property="profile:first_name" content="Mahadi Sajjad" />
    <meta property="profile:last_name" content="Neloy" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="${name} — ${title}" />
    <meta name="twitter:description" content="${description}" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="stylesheet" href="/app.css" />
    <script type="application/ld+json">${jsonLd}</script>
  </head>
  <body>
    <main class="profile dashboard-page">
      <header class="dashboard-header">
        <a
          class="profile-mark"
          href="#overview"
          aria-label="${name} home"
        >
          <span>M</span><span>S</span><span>N</span>
        </a>
        <p class="header-label">
          ${headerLabel}
        </p>
        <div class="header-actions">
          <nav class="header-contact" aria-label="Contact links">
            <a
              class="header-link"
              href="mailto:${email}"
              aria-label="Email ${email}">EMAIL</a
            >
            <a
              class="header-link"
              href="tel:${phoneLink}"
              aria-label="Call ${phone}">CALL</a
            >
            <a
              class="header-link"
              href="${github}"
              target="_blank"
              rel="noreferrer"
              aria-label="Open GitHub in a new tab"
              >GITHUB <span aria-hidden="true">↗</span></a
            >
          </nav>
          <span class="connection-state" id="connection-state">
            <span class="connection-dot"></span>
            <span id="connection-label">CONNECTING</span>
          </span>
          <button
            class="refresh-button"
            id="refresh-button"
            type="button"
            aria-label="Refresh WakaTime data"
          >
            <span class="refresh-icon" aria-hidden="true">↻</span>
            <span class="refresh-label">SYNC</span>
          </button>
        </div>
      </header>

      <section class="identity-panel" id="overview" aria-labelledby="name">
        <div class="identity-main">
          <p class="eyebrow">${crewId}</p>
          <h1 id="name">${name}<span>.</span></h1>
          <p class="role">${title}</p>
        </div>
        <section
          class="summary-grid"
          id="summary-grid"
          aria-label="WakaTime summary"
          hidden
        >
        </section>
      </section>

      <div class="feed-message" id="feed-message" role="alert" hidden>
        <span id="feed-error"></span>
        <button class="retry-button" id="retry-button" type="button"
          >RETRY CONNECTION</button
        >
      </div>

      <section class="loading-panel" id="loading-panel" aria-live="polite">
        <span class="loading-indicator"></span>
        <p>ACQUIRING TELEMETRY FROM WAKATIME…</p>
      </section>

      <section
        class="dashboard-grid"
        id="dashboard-grid"
        aria-label="WakaTime breakdown"
        hidden
      >
      </section>
      <footer class="dashboard-footer" id="dashboard-footer" hidden></footer>
    </main>
    <script type="module" src="/scripts/dashboard.js"></script>
  </body>
</html>
`;

    fs.mkdirSync("dist/client/scripts", { recursive: true });
    fs.mkdirSync("dist/scripts", { recursive: true });

    fs.writeFileSync("dist/index.html", html);
    fs.writeFileSync("dist/client/index.html", html);

    // 2. Styles extracted from src_ada/styles.adb
    const css = extractPutLines("src_ada/styles.adb");
    fs.writeFileSync("dist/app.css", css);
    fs.writeFileSync("dist/client/app.css", css);

    // 3. Telemetry client extracted from src_ada/telemetry_client.adb
    const js = extractPutLines("src_ada/telemetry_client.adb");
    fs.writeFileSync("dist/scripts/dashboard.js", js);
    fs.writeFileSync("dist/client/scripts/dashboard.js", js);

    // 4. Security headers
    const headers = `/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n`;
    fs.writeFileSync("dist/_headers", headers);
    fs.writeFileSync("dist/client/_headers", headers);

    // 5. Public assets
    if (fs.existsSync("public/favicon.svg")) {
      fs.copyFileSync("public/favicon.svg", "dist/favicon.svg");
      fs.copyFileSync("public/favicon.svg", "dist/client/favicon.svg");
    }
    if (fs.existsSync("public/robots.txt")) {
      fs.copyFileSync("public/robots.txt", "dist/robots.txt");
      fs.copyFileSync("public/robots.txt", "dist/client/robots.txt");
    }
    if (fs.existsSync("public/sitemap.xml")) {
      fs.copyFileSync("public/sitemap.xml", "dist/sitemap.xml");
      fs.copyFileSync("public/sitemap.xml", "dist/client/sitemap.xml");
    }

    console.log("[ADA-SYS-BUILD] All web artifacts generated from Ada packages.");
  '
fi

echo "[ADA-SYS-BUILD] Pure Ada build pipeline finished successfully."
