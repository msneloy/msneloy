#!/usr/bin/env bash
set -euo pipefail

for env_file in "$HOME/.cargo/env" /rust/env; do
    if [ -f "$env_file" ]; then
        # shellcheck disable=SC1090
        . "$env_file"
    fi
done

if ! command -v cargo >/dev/null 2>&1; then
    if ! command -v curl >/dev/null 2>&1; then
        echo "error: curl is required to install Rust in the Cloudflare Pages build environment" >&2
        exit 1
    fi
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --profile minimal --default-toolchain stable
    . "$HOME/.cargo/env"
fi

if command -v rustup >/dev/null 2>&1 \
    && ! rustup toolchain list | grep -q '^stable-'; then
    echo "Installing the stable Rust toolchain required by rust-toolchain.toml."
    rustup toolchain install stable --profile minimal
fi

cargo run --release --locked
