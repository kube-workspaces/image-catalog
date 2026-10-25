# Kasm workspace images

This collection covers **154 published browser-accessible Kasm workspace
images**, including historical distribution versions:

- [`core/`](core/): **45** base images from
  [workspaces-core-images](https://github.com/kasmtech/workspaces-core-images).
- [`desktop/`](desktop/): **109** desktops and applications from
  [workspaces-images](https://github.com/kasmtech/workspaces-images).
  Kasm's “Desktop Images” repository includes single-application images too.

## Metadata sources

Inventory and metadata were retrieved on **2026-10-25** from:

- [Kasm's image library](https://kasm.com/images).
- [Kasm's public registry JSON](https://registry.kasmweb.com/1.1/list.json):
  all **86** listed workspaces are represented. Display names, descriptions,
  icons, categories and applicable runtime environment settings come directly
  from this feed. Registry icons are hosted under
  `https://registry.kasmweb.com/1.1/icons/`.
- [Docker Hub's public repositories API](https://hub.docker.com/v2/repositories/kasmweb/):
  all **198** repositories were enumerated, with published tags checked for
  workspace candidates. Core and historical images absent from the public
  workspace registry use upstream repository names formatted as readable labels,
  Docker Hub descriptions, and the corresponding OS icon or Kasm's own logo.
- Upstream Dockerfiles, `ci-scripts/template-vars.yaml`, and image documentation:
  core revision `4598af0a73938d3ed42e810b92251f6ad4b4abca`;
  desktop revision `a6d0e65bc5ad131b48951d0928e641aa8f5ea30d`.
- Published OCI image configurations, retrieved with `crane config`, for the
  selected references: web port, home directory, shell, and core desktop startup
  defaults. Image layers do not need to be downloaded.

Each CR includes a display name, description, category, tags, icon, project URL,
Docker Hub URL, source URL, image reference, connection defaults, and HTTPS
proxy settings. Kubernetes resource names are RFC 1123-compatible and normally
prefixed `kasmweb-`; existing resource names are retained.

## Versions and standalone defaults

New entries select the newest stable semantic-version tag returned by Docker
Hub, falling back to a versioned rolling tag (currently Cursor) before using a
development tag. Existing entries retain their selected image references. Historical images
therefore intentionally use older releases rather than nonexistent new tags.
The following repositories currently offer development tags without a stable
version: `core-nvidia-focal`, `core-ubuntu-resolute`,
`core-ubuntu-resolute-wkde`, `tracelabs-debian`,
`ubuntu-bionic-dind`, and `ubuntu-bionic-dind-rootless`.
Development and rolling references use `defaultImagePullPolicy: Always`.

Standalone connections use HTTPS on port **6901**, with Kasm's self-signed
backend certificate and WebSocket proxying. The browser login is **kasm_user /
password**, configured with `VNC_PW=password`. The Linux home is
`/home/kasm-user`. Shared memory is enabled. Historical core images that ship
with `START_XFCE4=0` explicitly set `START_XFCE4=1` for a usable standalone
desktop; KDE images retain their own startup configuration.

Kasm's upstream [standalone deployment documentation](https://github.com/kasmtech/workspaces-images#manual-deployment)
explains that audio, file transfer and microphone integration depend on Kasm
orchestration; these CRs configure the standalone KasmVNC endpoint.
Docker-in-Docker, Steam and Redroid entries retain upstream privileged-mode
requirements. GPU images require appropriate GPU scheduling/runtime support;
VPN images need provider configuration; Redroid needs the host Android kernel
prerequisites documented upstream. Docker-specific settings such as hostnames,
DNS, sysctls, security options, device mappings and Kasm launch/exec hooks cannot
all be represented by an Image CR; consult the registry entry's `notes`,
`run_config`, `exec_config` and `launch_config` when using specialized variants.
The catalog manifests and image metadata have been validated; this is not a
runtime smoke test of all 154 applications.

## Inventory boundaries

Ten workspace-named Docker Hub repositories currently have **no published
tags**, so there is no pullable image to reference:

`angelfish`, `anydesk`, `bitwarden`, `google-earth`, `openoffice`,
`remnux-bionic-desktop`, `ubuntu-noble-n8n`, `ubuntu-resolute-desktop`,
`ubuntu-resolute-dind`, `ubuntu-resolute-dind-rootless`.

The remaining **34** repositories are Kasm platform services, networking/storage
plugins, build utilities, or headless CLI images. They are not browser-accessible
core/desktop workspaces. The explicit list is maintained in
[`scripts/sync-kasm.py`](../../scripts/sync-kasm.py).

## Refreshing

Install Python's `PyYAML` package and [crane](https://github.com/google/go-containerregistry/tree/main/cmd/crane),
then clone the two upstream repositories and run from this catalog's root:

```bash
python scripts/sync-kasm.py /path/to/workspaces-core-images /path/to/workspaces-images
make validate
make build
```

The refresh preserves existing resource names, references, curated-example
annotations and runtime overrides, refreshes upstream metadata, creates new
entries, and regenerates the root README table. It does not delete historical
entries. Review inventory counts and these source-revision notes after a refresh.

Install the complete Kasm collection directly with:

```bash
kubectl apply --recursive -f images/kasm/
```
