#!/usr/bin/bash
set -euo pipefail

# uv tool install doesn't need custom directories - it manages tools automatically
# The tools are installed to UV_TOOL_DIR (defaults to ~/.local/share/uv/tools)
# and executables are linked to ~/.local/bin automatically

# Validate that both CUSTOM_GITHUB_REF and CLI_VERSION are not set together
if [ -n "${CUSTOM_GITHUB_REF:-}" ] && [ -n "${CLI_VERSION:-}" ] ; then
    echo "Error: Both CUSTOM_GITHUB_REF and CLI_VERSION are set. Please provide only one (either a GitHub ref or a CLI version)." >&2
    exit 1
fi

# Install using uv tool install (uv provided by astral-sh/setup-uv action)
# Note: --force not needed in fresh GitHub Actions environment
if [ -n "${CUSTOM_GITHUB_REF:-}" ]; then
    uv tool install \
        "git+https://github.com/snowflakedb/snowflake-cli.git@${CUSTOM_GITHUB_REF}"
elif [ -n "${CLI_VERSION:-}" ] && [ -n "${CLI_VERSION}" ] && [ "${CLI_VERSION}" != "latest" ]; then
    uv tool install \
        "snowflake-cli==$CLI_VERSION"
else
    uv tool install \
        snowflake-cli
fi

# uv automatically adds ~/.local/bin to PATH during tool installation
# but we need to ensure it's available for subsequent steps in GitHub Actions
echo "$HOME/.local/bin" >> "$GITHUB_PATH"
