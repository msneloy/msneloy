with Ada.Text_IO;
with Ada.Directories;
with Profile;
with Markup;
with Styles;
with Telemetry_Client;

procedure Site_Builder is
   use Ada.Text_IO;
   use Ada.Directories;

   procedure Write_File (Path : String; Content : String) is
      File : File_Type;
   begin
      Create (File, Out_File, Path);
      Put (File, Content);
      Close (File);
   end Write_File;

   procedure Copy_If_Exists (Source : String; Dest : String) is
   begin
      if Exists (Source) then
         Copy_File (Source, Dest);
      end if;
   end Copy_If_Exists;

   procedure Ensure_Dir (Dir : String) is
   begin
      if not Exists (Dir) then
         Create_Path (Dir);
      end if;
   end Ensure_Dir;

   HTML_Content    : constant String := Markup.Render_HTML;
   Headers_Content : constant String := Markup.Render_Headers;

begin
   Put_Line ("[ADA-SYS-BUILD] ========================================");
   Put_Line ("[ADA-SYS-BUILD] INITIALIZING PURE ADA SYSTEM BUILDER");
   Put_Line ("[ADA-SYS-BUILD] OPERATOR: " & Profile.Name);
   Put_Line ("[ADA-SYS-BUILD] DESIGNATION: " & Profile.Title);
   Put_Line ("[ADA-SYS-BUILD] IDENT: " & Profile.Crew_ID);
   Put_Line ("[ADA-SYS-BUILD] ========================================");

   -- 1. Ensure target distribution trees
   Ensure_Dir ("dist");
   Ensure_Dir ("dist/client");
   Ensure_Dir ("dist/client/scripts");
   Ensure_Dir ("dist/scripts");

   -- 2. Emit index.html (root and client) from Markup package
   Put_Line ("[ADA-SYS-BUILD] Emitting DOM from Markup: dist/index.html...");
   Write_File ("dist/index.html", HTML_Content);

   Put_Line ("[ADA-SYS-BUILD] Emitting DOM from Markup: dist/client/index.html...");
   Write_File ("dist/client/index.html", HTML_Content);

   -- 3. Emit security headers (_headers for Cloudflare)
   Put_Line ("[ADA-SYS-BUILD] Emitting security headers: dist/_headers...");
   Write_File ("dist/_headers", Headers_Content);
   Write_File ("dist/client/_headers", Headers_Content);

   -- 4. Emit stylesheets from pure Ada Styles package
   Put_Line ("[ADA-SYS-BUILD] Emitting Stylesheet from Styles package: dist/app.css...");
   Styles.Emit_CSS ("dist/app.css");
   Styles.Emit_CSS ("dist/client/app.css");

   -- 5. Emit telemetry client engine from pure Ada Telemetry_Client package
   Put_Line ("[ADA-SYS-BUILD] Emitting Telemetry Engine from Telemetry_Client package: dist/scripts/dashboard.js...");
   Telemetry_Client.Emit_JS ("dist/scripts/dashboard.js");
   Telemetry_Client.Emit_JS ("dist/client/scripts/dashboard.js");

   -- 6. Copy public assets (robots.txt, sitemap.xml, favicon.svg)
   if Exists ("public/favicon.svg") then
      Copy_If_Exists ("public/favicon.svg", "dist/favicon.svg");
      Copy_If_Exists ("public/favicon.svg", "dist/client/favicon.svg");
   end if;

   if Exists ("public/robots.txt") then
      Copy_If_Exists ("public/robots.txt", "dist/robots.txt");
      Copy_If_Exists ("public/robots.txt", "dist/client/robots.txt");
   end if;

   if Exists ("public/sitemap.xml") then
      Copy_If_Exists ("public/sitemap.xml", "dist/sitemap.xml");
      Copy_If_Exists ("public/sitemap.xml", "dist/client/sitemap.xml");
   end if;

   Put_Line ("[ADA-SYS-BUILD] ALL ARTIFACTS GENERATED FROM PURE ADA SOURCE.");
   Put_Line ("[ADA-SYS-BUILD] TELEMETRY TARGET: CLOUDFLARE EDGE");
   Put_Line ("[ADA-SYS-BUILD] BUILD STATUS: OPERATIONAL [0 ERRORS]");
end Site_Builder;
