#!/usr/bin/env bash
# Shared helpers for the image-catalog scripts.
#
# Source this, do not execute it:
#   source "$(dirname "$0")/lib/common.sh"

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export REPO_ROOT

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
  C_BLUE=$'\033[34m'; C_BOLD=$'\033[1m'; C_OFF=$'\033[0m'
else
  C_RED=''; C_GREEN=''; C_YELLOW=''; C_BLUE=''; C_BOLD=''; C_OFF=''
fi

CHECKS_PASSED=0
CHECKS_FAILED=0
FAILED_NAMES=()

group() {
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    echo "::group::$*"
  else
    printf '\n%s==> %s%s\n' "$C_BOLD$C_BLUE" "$*" "$C_OFF"
  fi
}

endgroup() {
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    echo "::endgroup::"
  fi
}

info()  { printf '%s--%s %s\n' "$C_BLUE" "$C_OFF" "$*"; }
warn()  { printf '%s!!%s %s\n' "$C_YELLOW" "$C_OFF" "$*" >&2; }

pass() {
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  printf '%sPASS%s %s\n' "$C_GREEN" "$C_OFF" "$*"
}

fail() {
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
  FAILED_NAMES+=("$*")
  printf '%sFAIL%s %s\n' "$C_RED" "$C_OFF" "$*"
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    echo "::error::$*"
  fi
}

die() {
  printf '%sfatal:%s %s\n' "$C_RED$C_BOLD" "$C_OFF" "$*" >&2
  exit 1
}

finish() {
  local total=$((CHECKS_PASSED + CHECKS_FAILED))
  printf '\n%s%s%s: %d/%d checks passed' \
    "$C_BOLD" "${SCRIPT_NAME:-results}" "$C_OFF" "$CHECKS_PASSED" "$total"
  if [ "$CHECKS_FAILED" -gt 0 ]; then
    printf ', %s%d failed%s\n' "$C_RED" "$CHECKS_FAILED" "$C_OFF"
    printf '\nFailed checks:\n'
    local n
    for n in "${FAILED_NAMES[@]}"; do
      printf '  %s-%s %s\n' "$C_RED" "$C_OFF" "$n"
    done
    return 1
  fi
  printf '\n'
  return 0
}

require_tools() {
  local missing=() t
  for t in "$@"; do
    command -v "$t" >/dev/null 2>&1 || missing+=("$t")
  done
  if [ ${#missing[@]} -gt 0 ]; then
    die "required tool(s) not on PATH: ${missing[*]}"
  fi
}

LOCAL_BIN="${REPO_ROOT}/.bin"
export PATH="${LOCAL_BIN}:${PATH}"
ensure_local_bin() { mkdir -p "$LOCAL_BIN"; }
