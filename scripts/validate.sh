#!/usr/bin/env bash
# Static validation for the image catalog. No cluster required, runs in
# seconds.
#
# Checks:
#   - every images/*.yaml file parses as a single valid YAML document
#   - metadata.name matches the filename
#   - no duplicate names across files
#   - names are RFC 1123 compliant
#   - no metadata.namespace (Image is cluster-scoped)
#   - required spec fields are present (image, defaultPort)
#   - schema validation via kubeconform, when available
#
# Usage: scripts/validate.sh

SCRIPT_NAME="validate"
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

require_tools yq

cd "$REPO_ROOT"

group "per-file structure"

declare -A seen_names

for f in images/*.yaml; do
  base=$(basename "$f" .yaml)

  if out=$(yq -e 'true' "$f" 2>&1 >/dev/null); then
    pass "$f is valid YAML"
  else
    fail "$f is valid YAML"
    printf '%s\n' "$out" | sed 's/^/     /' >&2
    continue
  fi

  ndocs=$(yq -N 'document_index' "$f" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$ndocs" = "1" ]; then
    pass "$f contains exactly one document"
  else
    fail "$f contains exactly one document (found $ndocs)"
  fi

  kind=$(yq -N '.kind' "$f" 2>/dev/null)
  if [ "$kind" = "Image" ]; then
    pass "$f has kind: Image"
  else
    fail "$f has kind: Image (found '$kind')"
  fi

  name=$(yq -N '.metadata.name' "$f" 2>/dev/null)
  if [ "$name" = "$base" ]; then
    pass "$f: metadata.name matches filename"
  else
    fail "$f: metadata.name matches filename (found '$name')"
  fi

  if [[ "$name" =~ ^[a-z0-9]([-a-z0-9]*[a-z0-9])?$ ]]; then
    pass "$f: name is RFC 1123 compliant"
  else
    fail "$f: name is RFC 1123 compliant (found '$name')"
  fi

  if [ -n "${seen_names[$name]:-}" ]; then
    fail "$f: name '$name' is unique (also used by ${seen_names[$name]})"
  else
    seen_names[$name]="$f"
  fi

  ns=$(yq -N '.metadata.namespace' "$f" 2>/dev/null)
  if [ -z "$ns" ] || [ "$ns" = "null" ]; then
    pass "$f has no metadata.namespace (Image is cluster-scoped)"
  else
    fail "$f has no metadata.namespace (Image is cluster-scoped, found '$ns')"
  fi

  image=$(yq -N '.spec.image' "$f" 2>/dev/null)
  if [ -n "$image" ] && [ "$image" != "null" ]; then
    pass "$f has spec.image"
  else
    fail "$f has spec.image"
  fi

  port=$(yq -N '.spec.defaultPort' "$f" 2>/dev/null)
  if [ -n "$port" ] && [ "$port" != "null" ]; then
    pass "$f has spec.defaultPort"
  else
    fail "$f has spec.defaultPort"
  fi
done

endgroup

group "image reference uniqueness"

# Two Image CRs sharing a spec.image are indistinguishable to the controller:
# a Workspace records only the image reference, and imageByRef resolves the
# first matching Image. That silently reconfigures existing workspaces when a
# second image with the same reference appears (e.g. a 'desktop' variant of
# the same base). Keep spec.image unique across the catalog.
declare -A seen_images
for f in images/*.yaml; do
  ref=$(yq -N '.spec.image' "$f" 2>/dev/null)
  if [ -n "$ref" ] && [ "$ref" != "null" ]; then
    if [ -n "${seen_images[$ref]:-}" ]; then
      fail "spec.image '$ref' is unique (also used by ${seen_images[$ref]})"
    else
      seen_images[$ref]="$f"
    fi
  fi
done
if [ ${#seen_images[@]} -gt 0 ]; then
  pass "every spec.image reference is unique across the catalog"
fi

endgroup

group "schema validation"

if command -v kubeconform >/dev/null 2>&1; then
  SCHEMA_DIR=$(mktemp -d)
  trap 'rm -rf "$SCHEMA_DIR"' EXIT
  scripts/crd-to-schema.sh "$SCHEMA_DIR" >/dev/null

  for f in images/*.yaml; do
    if out=$(kubeconform -strict -summary=false \
        -schema-location default \
        -schema-location "${SCHEMA_DIR}/{{.ResourceKind}}.json" \
        "$f" 2>&1); then
      pass "kubeconform $f"
    else
      fail "kubeconform $f"
      printf '%s\n' "$out" | sed 's/^/     /' >&2
    fi
  done
else
  warn "kubeconform not found on PATH, skipping schema validation"
fi

endgroup

finish
