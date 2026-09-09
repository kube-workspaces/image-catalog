# Contributing to image-catalog

Thank you for considering a contribution to the kube-workspaces image catalog.

## Adding a new image

1. Create `images/<name>.yaml` where `<name>` matches `metadata.name` exactly
   and is RFC 1123 compliant (lowercase alphanumerics and hyphens).
2. Write a complete `Image` custom resource — see an existing file such as
   `images/code-server.yaml` for the shape, and
   [README.md](README.md#schema) for the field reference.
3. Do not set `metadata.namespace` — `Image` is cluster-scoped.
4. Run `make validate` and fix anything it flags.
5. Open a PR. CI runs the same validation.

## Curated examples

A small number of images are annotated:

```yaml
metadata:
  annotations:
    catalog.kubeworkspaces.io/example: "true"
```

These are the images the `kube-workspaces/deploy` Helm chart installs by
default (`installExampleImages: true`). Keep this set small (currently 8) and
representative — it is what a first-time installer sees. Adding this
annotation to a new image is a deliberate choice, not the default; most
contributions should not set it.

## Updating the CRD schema

The `Image` CRD schema is owned by the
[controller](https://github.com/kube-workspaces/controller) repo and vendored
here for offline `kubeconform` validation:

1. In the controller repo: `make manifests`
2. From this repo: `make sync-crd CONTROLLER_REPO=/path/to/controller`
3. Run `make validate`
4. Commit `crds/kubeworkspaces.io_images.yaml`

`make check-crd` runs in CI to catch drift.

## Releasing

Releases are cut from the Actions tab (`Release` workflow) with a `vX.Y.Z`
version. This:

1. Validates the catalog
2. Builds `dist/images.yaml` and `dist/images-examples.yaml`
3. Tags the commit and creates a GitHub Release with both files attached

Downstream repositories (e.g. `deploy`) pin a specific release and vendor
these two files — see that repo's `make sync-images` target.

## Code Style

- One `Image` CR per file, filename matching `metadata.name`
- Shell scripts use `bash`, live in `scripts/`, and are `shellcheck`-clean
- Run `make validate` before committing

## License

By contributing, you agree that your contributions will be licensed under the
Apache License 2.0.
