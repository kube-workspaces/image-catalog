---
name: create-workspace-image
description: Use when adding, creating, or authoring a new kube-workspaces Image catalog entry in this repo (images/*.yaml), e.g. "add an image for X", "create a workspace image", "catalog entry". Covers Image CR authoring, container vs VM images, proxyConfig, validation (make validate), and README table updates.
---

# Creating a kube-workspaces Image

This repo is the [kube-workspaces](https://kubeworkspaces.io) image catalog:
the source of truth for ready-to-use workspace `Image` custom resources that
the `kube-workspaces/deploy` chart vendors and the frontend surfaces in the UI.

Each file in `images/` is one complete, cluster-scoped `Image` CR. The API
resolves an Image **by matching `spec.image` against the Workspace's container
image reference** — not by name — so `spec.image` must be unique across the
whole catalog (two Images sharing a ref are indistinguishable and silently
reconfigure existing workspaces).

## Workflow

1. Pick a unique RFC 1123 name (lowercase alphanumerics + hyphens, e.g.
   `stirling-pdf`, `debian-vm`).
2. Check the name AND the `spec.image` ref are not already used:
   `ls images/` and `yq '.spec.image' images/*.yaml | grep -F '<ref>'`.
3. Create `images/<name>.yaml` — filename **must** equal `metadata.name`.
4. Fill the spec (see field reference below). Required: `spec.image` and
   `spec.defaultPort`. No `metadata.namespace` — `Image` is cluster-scoped.
5. Update the "Available Images" table in `README.md` (add a row in
   alphabetical-ish position; Example column is `✓` only for curated
   examples).
6. Run `make validate` (requires `yq`; `jq` + `kubeconform` for full schema
   checks) and `make build`. Fix anything it flags.
7. Open a PR. CI runs the same validate + build, plus windows11 regression
   tests if you touched `windows11/`.

Do **not** add `metadata.annotations.catalog.kubeworkspaces.io/example:
"true"` unless deliberately expanding the curated default install set —
keep that set small and representative. Most contributions must not set it.

## Minimal template (container app)

```yaml
apiVersion: kubeworkspaces.io/v1alpha1
kind: Image
metadata:
  name: my-app
spec:
  defaultPath: /
  defaultPort: 8080
  description: One-line description shown in the UI.
  category: Tool
  displayName: My App
  homepageURL: https://example.com
  icon: https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/my-app.svg
  image: myorg/my-app:latest
  imageHomepageURL: https://hub.docker.com/r/myorg/my-app
  proxyConfig:
    needsNoopSW: true
    rewriteHostAbsolutePaths: true
  sourceURL: https://github.com/myorg/my-app
```

Copy field style and ordering from a similar existing file (e.g.
`images/stirling-pdf.yaml` for a simple tool, `images/code-server.yaml` for
an IDE, `images/debian-xfce.yaml` for a full VM).

## Field reference

Full schema: `crds/kubeworkspaces.io_images.yaml` (vendored from the
controller; `controller/api/v1alpha1/image_types.go` is the canonical Go
reference). Only `image` and `defaultPort` are required.

### Display / metadata

| Field | Notes |
|---|---|
| `displayName` | UI label (falls back to the CR name) |
| `description` | UI description; wrap long lines at ~80 cols like existing files |
| `category` | Free-form; catalog conventions: `IDE`, `Desktop`, `Browser`, `Tool`, `Game`, `Productivity`, `VM` |
| `tags` | Free-form search/filter labels (e.g. `vm`, `linux`, `pdf`, `editor`) |
| `homepageURL` / `imageHomepageURL` / `sourceURL` | Project site, container registry page, source repo |
| `icon` | Emoji string, inline `<svg ...>...</svg>`, or an `http(s)` URL. Convention: `https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/<name>.svg` |

### Container behavior

| Field | Notes |
|---|---|
| `image` | Container image ref — **must be unique across the catalog**. Prefer pinned tags for VMs; `:latest` is common for container apps |
| `defaultPort` | Required. The app's listen port. The controller maps the first port to Service port 80 |
| `additionalPorts` | Extra `{name, port, protocol}` entries exposed on the Service (e.g. SSH 22) |
| `defaultPath` | URL path appended when the user clicks Connect (client-side hint; e.g. `/vnc.html?resize=remote`, `/`, `?folder=/workspace`) |
| `defaultArgs` | Container args at workspace creation. Supports `{{namespace}}` / `{{name}}` placeholders (NOT `{{uid}}`) |
| `defaultEnv` | `{name, value}` env vars. Same placeholders. `{{port}}` in values is NOT substituted by the API — some apps (code-server) resolve it themselves |
| `defaultUser` / `defaultHomedir` / `defaultShell` | Exec-session and SSH defaults. `defaultShell` falls back to `/bin/bash` then `/bin/sh` |
| `defaultPassword` | Password for `defaultUser` when a well-known default exists |
| `defaultCredentials` | `{username, password}` shown as login badges in the UI |
| `defaultUID` | Sets pod `runAsUser` / `fsGroup` |
| `defaultInitContainers` | Full pod-Container schema; injected with `runAsUser: 0`; supports `{{namespace}}`/`{{name}}`/`{{uid}}`; inherits main container mounts unless `volumeMounts` are set |
| `defaultSharedMemory` | Mount memory-backed `/dev/shm` (rejected for `vm` workspaces) |
| `privileged` | Run the container privileged |

### proxyConfig

Read at runtime by the proxy (not baked into the pod):

| Field | Effect |
|---|---|
| `scheme` | `http` (default) or `https` backend dial |
| `tlsSkipVerify` | Skip TLS verification on the https backend |
| `preservePathPrefix` | Forward the full `/proxy/{ns}/{name}/...` path to the pod (filebrowser, webtop, JupyterLab style base-URL apps) |
| `needsNoopSW` | Frontend badge; the no-op ServiceWorker is currently always served, but keep setting it for documentation/UI value |
| `rewriteHostAbsolutePaths` | Frontend badge; path recovery is currently unconditional in the proxy |
| `websocketPaths` | Frontend badge; informational (all paths support WebSocket) |
| `customRequestHeaders` | Map of headers injected into proxied requests |
| `injectBaseTag` | Inject `<base href=...>` into HTML responses |
| `audioPort` | Route `/audio/...` to this Service port — **requires a matching `additionalPorts` entry** |
| `agentPort` | Guest TCP port of workspace-agent; enables `/agent/` bridge (canonical: `44787`) |
| `port` | Target a non-80 workspace Service port for non-audio traffic |

Most simple HTTP apps: set `needsNoopSW: true` and
`rewriteHostAbsolutePaths: true` (matches the catalog convention).

### VM-only fields

Set `workspaceTypes: [vm]` for VM images (empty list = container only).

| Field | Notes |
|---|---|
| `image` | A KubeVirt containerDisk (e.g. `quay.io/kubevirt/alpine-container-disk-demo:...`, `quay.io/containerdisks/debian:13`). Custom-built containerdisks must be **digest-pinned** (`repo@sha256:...`, not `:tag@sha256:`) |
| `defaultPort` | First container port → Service port 80 via masquerade; often the in-guest web app port (e.g. 8080 for Selkies) — a bare SSH port 22 Service is not an HTTP endpoint |
| `additionalPorts` | e.g. `ssh` on 22 |
| `defaultCloudInit` | `true` — guest runs cloud-init (required for user-data seeding) |
| `defaultUserData` | Explicit `#cloud-config` user-data (wins over generated). ContainerDisk roots re-run cloud-init every boot; DataVolume roots are PER_INSTANCE |
| `defaultUser` / `defaultPassword` | Seeded via cloud-init `chpasswd` when `defaultUserData` is empty |
| `persistentRootDisk` / `persistentRootDiskSize` | CDI DataVolume root PVC (default `10Gi`) so the guest survives restarts |
| `memoryLimit` / `memoryRequest` | Guest RAM vs virt-launcher pod allocation (request ≥ limit; keep equal for Guaranteed QoS) |
| `videoDevice` | `virtio` (recommended for desktops), `vga`, `bochs`, `cirrus`, `ramfb` |
| `soundDevice` | `ac97` or `ich9` (`ich9` preferred; enables QEMU VNC audio) |
| `remoteDesktop` | `{protocol: selkies\|agent, port, path}` — Tier-1 transport ad for the desktop client |
| annotation `kubeworkspaces.io/ssh-key-propagation: qemuGuestAgent` | Opt into platform-managed guest SSH keys (guest must run `qemu-guest-agent`; platform owns that user's entire `authorized_keys`) |

## Gotchas

- **`spec.image` uniqueness is enforced by `scripts/validate.sh`.** If you
  need a second image flavor of the same base (e.g. a "desktop" variant),
  the base ref cannot be reused — build/publish a distinct ref.
- Fields marked "creation-time" (`defaultArgs`, `defaultEnv`, `defaultUID`,
  `defaultInitContainers`, `additionalPorts`, `defaultSharedMemory`,
  `privileged`, and the snapshotted `preservePathPrefix`) are baked into the
  Workspace pod at creation and are **not** retroactively applied to existing
  workspaces when the Image CR is edited.
- Placeholders: `{{namespace}}`/`{{name}}` work in `defaultArgs`/`defaultEnv`;
  `{{uid}}` additionally works in `defaultInitContainers`.
- Do not hand-edit `crds/kubeworkspaces.io_images.yaml` — re-sync via
  `make sync-crd CONTROLLER_REPO=/path/to/controller`.
- Recipe dirs (`freebsd/`, `ms-dos-622/`, `windows11/`) are only needed when
  you must build a custom containerDisk; plain catalog entries need no
  Dockerfile.
- The README "Available Images" table is manually maintained — update it in
  the same PR.

## Verification

```bash
make validate   # structural + (optional) kubeconform schema checks
make build      # writes dist/images.yaml and dist/images-examples.yaml
```

Install missing tools if needed: `yq` (mikefarah), `jq`, `kubeconform`.
Repo-local binaries can go in `.bin/` (already on PATH via
`scripts/lib/common.sh`, gitignored).

## Reference links

- Platform docs: <https://kubeworkspaces.io/docs/> (overview, VM, proxy)
- Field reference: `README.md` (Schema section) + controller's
  `api/v1alpha1/image_types.go`
- Authoring guide: `CONTRIBUTING.md`
- Exemplars: `images/stirling-pdf.yaml` (simple tool),
  `images/code-server.yaml` (IDE + env/initContainers),
  `images/kasmweb-chrome.yaml` (privileged + rich proxyConfig),
  `images/debian-xfce.yaml` (full VM with cloud-init)
