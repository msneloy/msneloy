with Profile;

package body Markup is

   NL : constant Character := Character'Val (10);

   function Render_HTML return String is
   begin
      return
        "<!doctype html>" & NL &
        "<html lang=""en"">" & NL &
        "  <head>" & NL &
        "    <meta charset=""utf-8"" />" & NL &
        "    <meta name=""viewport"" content=""width=device-width, initial-scale=1"" />" & NL &
        "    <title>" & Profile.Name & " — " & Profile.Title & "</title>" & NL &
        "    <link rel=""canonical"" href=""" & Profile.Site_URL & """ />" & NL &
        "    <meta name=""description"" content=""" & Profile.Description & """ />" & NL &
        "    <meta name=""author"" content=""" & Profile.Name & """ />" & NL &
        "    <meta name=""robots"" content=""index, follow"" />" & NL &
        "    <meta name=""color-scheme"" content=""dark"" />" & NL &
        "    <meta name=""theme-color"" content=""#080b10"" />" & NL &
        "    <meta property=""og:type"" content=""profile"" />" & NL &
        "    <meta property=""og:site_name"" content=""" & Profile.Name & """ />" & NL &
        "    <meta property=""og:url"" content=""" & Profile.Site_URL & """ />" & NL &
        "    <meta property=""og:title"" content=""" & Profile.Name & " — " & Profile.Title & """ />" & NL &
        "    <meta property=""og:description"" content=""" & Profile.Description & """ />" & NL &
        "    <meta property=""og:locale"" content=""en_US"" />" & NL &
        "    <meta property=""profile:first_name"" content=""" & Profile.First_Name & """ />" & NL &
        "    <meta property=""profile:last_name"" content=""" & Profile.Last_Name & """ />" & NL &
        "    <meta name=""twitter:card"" content=""summary"" />" & NL &
        "    <meta name=""twitter:title"" content=""" & Profile.Name & " — " & Profile.Title & """ />" & NL &
        "    <meta name=""twitter:description"" content=""" & Profile.Description & """ />" & NL &
        "    <link rel=""icon"" type=""image/svg+xml"" href=""/favicon.svg"" />" & NL &
        "    <link rel=""stylesheet"" href=""/app.css"" />" & NL &
        "    <script type=""application/ld+json"">" &
        "{""@context"":""https://schema.org"",""@type"":""Person"",""@id"":""" & Profile.Site_URL & """," &
        """name"":""" & Profile.Name & """,""jobTitle"":""" & Profile.Title & """," &
        """url"":""" & Profile.Site_URL & """,""email"":""" & Profile.Email & """," &
        """telephone"":""" & Profile.Phone & """,""sameAs"":[""" & Profile.GitHub_URL & """]}" &
        "</script>" & NL &
        "  </head>" & NL &
        "  <body>" & NL &
        "    <main class=""profile dashboard-page"">" & NL &
        "      <header class=""dashboard-header"">" & NL &
        "        <a" & NL &
        "          class=""profile-mark""" & NL &
        "          href=""#overview""" & NL &
        "          aria-label=""" & Profile.Name & " home""" & NL &
        "        >" & NL &
        "          <span>M</span><span>S</span><span>N</span>" & NL &
        "        </a>" & NL &
        "        <p class=""header-label"">" & NL &
        "          " & Profile.Header_Label & NL &
        "        </p>" & NL &
        "        <div class=""header-actions"">" & NL &
        "          <nav class=""header-contact"" aria-label=""Contact links"">" & NL &
        "            <a" & NL &
        "              class=""header-link""" & NL &
        "              href=""mailto:" & Profile.Email & """" & NL &
        "              aria-label=""Email " & Profile.Email & """>EMAIL</a" & NL &
        "            >" & NL &
        "            <a" & NL &
        "              class=""header-link""" & NL &
        "              href=""tel:" & Profile.Phone_Link & """" & NL &
        "              aria-label=""Call " & Profile.Phone & """>CALL</a" & NL &
        "            >" & NL &
        "            <a" & NL &
        "              class=""header-link""" & NL &
        "              href=""" & Profile.GitHub_URL & """" & NL &
        "              target=""_blank""" & NL &
        "              rel=""noreferrer""" & NL &
        "              aria-label=""Open GitHub in a new tab""" & NL &
        "              >GITHUB <span aria-hidden=""true"">↗</span></a" & NL &
        "            >" & NL &
        "          </nav>" & NL &
        "          <span class=""connection-state"" id=""connection-state"">" & NL &
        "            <span class=""connection-dot""></span>" & NL &
        "            <span id=""connection-label"">CONNECTING</span>" & NL &
        "          </span>" & NL &
        "          <button" & NL &
        "            class=""refresh-button""" & NL &
        "            id=""refresh-button""" & NL &
        "            type=""button""" & NL &
        "            aria-label=""Refresh WakaTime data""" & NL &
        "          >" & NL &
        "            <span class=""refresh-icon"" aria-hidden=""true"">↻</span>" & NL &
        "            <span class=""refresh-label"">SYNC</span>" & NL &
        "          </button>" & NL &
        "        </div>" & NL &
        "      </header>" & NL &
        "" & NL &
        "      <section class=""identity-panel"" id=""overview"" aria-labelledby=""name"">" & NL &
        "        <div class=""identity-main"">" & NL &
        "          <p class=""eyebrow"">" & Profile.Crew_ID & "</p>" & NL &
        "          <h1 id=""name"">" & Profile.Name & "<span>.</span></h1>" & NL &
        "          <p class=""role"">" & Profile.Title & "</p>" & NL &
        "        </div>" & NL &
        "        <section" & NL &
        "          class=""summary-grid""" & NL &
        "          id=""summary-grid""" & NL &
        "          aria-label=""WakaTime summary""" & NL &
        "          hidden" & NL &
        "        >" & NL &
        "        </section>" & NL &
        "      </section>" & NL &
        "" & NL &
        "      <div class=""feed-message"" id=""feed-message"" role=""alert"" hidden>" & NL &
        "        <span id=""feed-error""></span>" & NL &
        "        <button class=""retry-button"" id=""retry-button"" type=""button""" & NL &
        "          >RETRY CONNECTION</button" & NL &
        "        >" & NL &
        "      </div>" & NL &
        "" & NL &
        "      <section class=""loading-panel"" id=""loading-panel"" aria-live=""polite"">" & NL &
        "        <span class=""loading-indicator""></span>" & NL &
        "        <p>ACQUIRING TELEMETRY FROM WAKATIME…</p>" & NL &
        "      </section>" & NL &
        "" & NL &
        "      <section" & NL &
        "        class=""dashboard-grid""" & NL &
        "        id=""dashboard-grid""" & NL &
        "        aria-label=""WakaTime breakdown""" & NL &
        "        hidden" & NL &
        "      >" & NL &
        "      </section>" & NL &
        "      <footer class=""dashboard-footer"" id=""dashboard-footer"" hidden></footer>" & NL &
        "    </main>" & NL &
        "    <script type=""module"" src=""/scripts/dashboard.js""></script>" & NL &
        "  </body>" & NL &
        "</html>" & NL;
   end Render_HTML;

   function Render_Headers return String is
   begin
      return
        "/*" & NL &
        "  X-Content-Type-Options: nosniff" & NL &
        "  Referrer-Policy: strict-origin-when-cross-origin" & NL &
        "  X-Frame-Options: DENY" & NL &
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()" & NL;
   end Render_Headers;

end Markup;
