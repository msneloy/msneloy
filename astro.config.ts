import cloudflare from "@astrojs/cloudflare";
import netlify from "@astrojs/netlify";
import node from "@astrojs/node";
import vercel from "@astrojs/vercel";
import { defineConfig } from "astro/config";

function getAdapter(target: string) {
  switch (target) {
    case "cloudflare":
      return cloudflare({
        imageService: "passthrough",
        imagesBindingName: false,
      });
    case "netlify":
      return netlify();
    case "render":
      return node({ mode: "standalone" });
    case "vercel":
      return vercel();
    default:
      throw new Error(`Unsupported DEPLOY_TARGET "${target}".`);
  }
}

export default defineConfig({
  output: "server",
  session: false,
  image: {
    service: { entrypoint: "astro/assets/services/noop" },
  },
  adapter: getAdapter(process.env.DEPLOY_TARGET ?? "render"),
});
