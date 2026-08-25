#!/usr/bin/env bash
# Extract the OpenAPI v3 schema from crds/kubeworkspaces.io_images.yaml into a
# standalone JSON Schema file, so kubeconform can validate Image manifests
# instead of skipping them.
#
# Usage: scripts/crd-to-schema.sh <output-dir>
# Emits: <output-dir>/image.json

set -euo pipefail

OUT_DIR="${1:?usage: crd-to-schema.sh <output-dir>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRD_FILE="$REPO_ROOT/crds/kubeworkspaces.io_images.yaml"

command -v yq >/dev/null 2>&1 || { echo "yq is required" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }

mkdir -p "$OUT_DIR"

# Take the schema from the first served version, then wrap it so that
# apiVersion/kind/metadata are permitted alongside spec/status — otherwise
# strict validation rejects every real manifest.
yq -N -o=json '.spec.versions[0].schema.openAPIV3Schema' "$CRD_FILE" \
  | jq '
      . as $s
      | {
          "$schema": "http://json-schema.org/draft-07/schema#",
          type: "object",
          properties: (
            ($s.properties // {})
            + {
                apiVersion: { type: "string" },
                kind: { type: "string" },
                metadata: { type: "object" }
              }
          ),
          required: ($s.required // [])
        }
    ' > "${OUT_DIR}/image.json"

echo "wrote image.json to ${OUT_DIR}"
