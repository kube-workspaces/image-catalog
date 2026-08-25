#!/usr/bin/env bash
# Build distributable artifacts from images/*.yaml:
#
#   dist/images.yaml          - every Image CR in the catalog, concatenated
#   dist/images-examples.yaml - only the Image CRs annotated as curated
#                               examples (catalog.kubeworkspaces.io/example: "true")
#
# Usage: scripts/build.sh

SCRIPT_NAME="build"
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

require_tools yq

cd "$REPO_ROOT"

mkdir -p dist

full_out="dist/images.yaml"
examples_out="dist/images-examples.yaml"

: > "$full_out"
: > "$examples_out"

full_count=0
examples_count=0

for f in $(find images -maxdepth 1 -name '*.yaml' | sort); do
  content=$(cat "$f")

  if [ -s "$full_out" ]; then printf -- '---\n' >> "$full_out"; fi
  printf '%s\n' "$content" >> "$full_out"
  full_count=$((full_count + 1))

  example=$(yq -N '.metadata.annotations."catalog.kubeworkspaces.io/example"' "$f" 2>/dev/null)
  if [ "$example" = "true" ]; then
    if [ -s "$examples_out" ]; then printf -- '---\n' >> "$examples_out"; fi
    printf '%s\n' "$content" >> "$examples_out"
    examples_count=$((examples_count + 1))
  fi
done

info "wrote $full_count image(s) to $full_out"
info "wrote $examples_count example image(s) to $examples_out"
