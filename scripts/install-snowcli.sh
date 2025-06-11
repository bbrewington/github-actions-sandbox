#!/usr/bin/bash
set -euo pipefail

# Use uv tool install - leverages astral-sh/setup-uv action for uv availability
UV_TOOL_DIR="snow_uv_tools"

# These commands ensure that each time `snow` command is executed the system will use 
# the executable in the uv tool installation and not in any other installation folder.
export UV_TOOL_BIN_DIR=${UV_TOOL_BIN_DIR:-"${HOME}/.local/bin"}/$UV_TOOL_DIR
mkdir -p "${UV_TOOL_BIN_DIR}"

# Validate that both CUSTOM_GITHUB_REF and CLI_VERSION are not set together
if [ -n "${CUSTOM_GITHUB_REF:-}" ] && [ -n "${CLI_VERSION:-}" ] ; then
    echo "Error: Both CUSTOM_GITHUB_REF and CLI_VERSION are set. Please provide only one (either a GitHub ref or a CLI version)." >&2
    exit 1
fi

# Install using uv tool install (uv provided by astral-sh/setup-uv action)
if [ -n "${CUSTOM_GITHUB_REF:-}" ]; then
    uv tool install \
        --force \
        --install-dir "$UV_TOOL_BIN_DIR" \
        "git+https://github.com/snowflakedb/snowflake-cli.git@${CUSTOM_GITHUB_REF}"
elif [ -n "${CLI_VERSION:-}" ] && [ "${CLI_VERSION}" != "latest" ]; then
    uv tool install \
        --force \
        --install-dir "$UV_TOOL_BIN_DIR" \
        "snowflake-cli==$CLI_VERSION"
else
    uv tool install \
        --force \
        --install-dir "$UV_TOOL_BIN_DIR" \
        snowflake-cli
fi

echo "$UV_TOOL_BIN_DIR" >> "$GITHUB_PATH"
