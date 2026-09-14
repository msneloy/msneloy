#!/usr/bin/env bash
#
# Vercel build entry point.
#
# Vercel's Amazon Linux 2023 build image already ships Rust under /rust, and its
# env file lives at /rust/env. It is deliberately not re-installed with the
# rustup one-liner: that refuses to install when Rust is already present, and it
# writes to "$HOME/.cargo/env", which resolves to /vercel/.cargo/env inside
# Vercel's build container and does not exist.
set -euo pipefail

# Leptos 0.8 requires Rust 1.88 or newer.
readonly RUST_MIN_MINOR=88

for env_file in /rust/env "$HOME/.cargo/env"; do
    if [ -f "$env_file" ]; then
        # shellcheck disable=SC1090
        . "$env_file"
    fi
done

export PATH="/rust/bin:$HOME/.cargo/bin:$PATH"

# Refresh the toolchain if rustup is available, but never fail the build over
# it: whatever the image already provides may be sufficient.
if command -v rustup >/dev/null 2>&1; then
    rustup update stable --no-self-update \
        || echo "warning: 'rustup update stable' failed; using the existing toolchain"
fi

if ! command -v cargo >/dev/null 2>&1; then
    echo "error: cargo not found on PATH ($PATH)" >&2
    exit 1
fi

echo "Using cargo: $(command -v cargo)"
cargo --version
rustc --version

minor=$(rustc --version | sed -E 's/^rustc 1\.([0-9]+).*/\1/')
if [ "$minor" -lt "$RUST_MIN_MINOR" ] 2>/dev/null; then
    echo "error: Rust 1.$RUST_MIN_MINOR+ is required by Leptos, found $(rustc --version)" >&2
    exit 1
fi

# Renders the static site into ./dist, which Vercel serves from its CDN.
cargo run --release