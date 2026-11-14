#!/usr/bin/env bash
# Stable build entry point for the hosting providers.
#
# Cloudflare and Vercel both run `bash build.sh`, and that command never
# changes when the site's technology does: whatever the current stack needs
# to produce dist/ goes in here. The host installs dependencies before this
# runs (npm clean-install, detected from package.json).
set -euo pipefail
cd "$(dirname "$0")"

npm run build
