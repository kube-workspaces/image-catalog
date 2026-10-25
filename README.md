# Kube Workspaces Image Catalog

A catalog of [`Image`](https://github.com/kube-workspaces/controller) custom
resources for [kube-workspaces](https://github.com/kube-workspaces) — the
container images available to launch as workspaces, with their default port,
proxy behaviour, credentials, and other workspace-creation defaults.

This repo is the **source of truth** for these manifests. Downstream repos
(notably [`deploy`](https://github.com/kube-workspaces/deploy)) vendor a
pinned release rather than reading from `main` directly.

The [private Windows 11 image recipe](windows11/README.md) includes proof-only
bootstrap/evidence tooling and containerDisk packaging. It does not bundle
Windows binaries or enable a Windows Image CR in the released catalog.
Start with the [official-ISO-to-cluster build guide](windows11/BUILD-GUIDE.md)
for installation, native provisioning, private publishing and clone validation.

The [FreeBSD 15.1 recipe](freebsd/README.md) packages the official cloud-init
disk for KubeVirt, with a persistent root disk and SSH/serial-console access.

## Overview

Each YAML file under [`images/`](images/) is a single, complete `Image` CR:

```yaml
apiVersion: kubeworkspaces.io/v1alpha1
kind: Image
metadata:
  name: code-server
spec:
  image: codercom/code-server:latest
  displayName: "Code Server (VS Code)"
  defaultPort: 8080
  ...
```

The filename always matches `metadata.name` (e.g. `images/code-server.yaml`).
`Image` is cluster-scoped, so no file sets `metadata.namespace`.

The [Kasm collection](images/kasm/README.md) contains 45 core images in
`images/kasm/core/` and 109 desktop/application images in `images/kasm/desktop/`,
including all 86 workspaces in Kasm's public registry. Its README documents
metadata sources, versions, standalone defaults, and inventory coverage.
Validation and distribution builds include nested image folders recursively.

## Available Images

<!-- Generated from all YAML manifests recursively under images/. -->

| Name | Display Name | Category | Port | Example |
|------|---------------|----------|------|---------|
| `adminer` | Adminer (Database Manager) | Tool | 8080 | - |
| `alpine` | Alpine Linux | Tool | 80 | - |
| `alpine-vm` | Alpine VM | VM | 22 | ✓ |
| `arch-linux-gnome-vm` | Arch Linux GNOME Desktop VM | Desktop | 22 | - |
| `chromium` | Chromium Browser | Browser | 3000 | - |
| `code-server` | Code Server (VS Code) | IDE | 8080 | ✓ |
| `cyberchef` | CyberChef | Tool | 8000 | - |
| `debian-desktop` | Debian Desktop | Desktop | 6901 | ✓ |
| `debian-vm` | Debian VM | VM | 22 | ✓ |
| `debian-xfce` | Debian Desktop XFCE | Desktop | 8080 | ✓ |
| `doom` | Doom | Game | 6901 | - |
| `drawio` | draw.io (Diagrams) | Productivity | 8080 | - |
| `excalidraw` | Excalidraw (Whiteboard) | Productivity | 80 | - |
| `filebrowser` | File Browser | Tool | 80 | - |
| `firefox` | Firefox Browser | Browser | 3000 | - |
| `freebsd-vm` | FreeBSD 15.1 VM | VM | 22 | - |
| `game-2048` | 2048 | Game | 80 | - |
| `grafana` | Grafana | Tool | 3000 | - |
| `jlesage-chromium` | Chromium (Lightweight) | Browser | 5800 | - |
| `jlesage-firefox` | Firefox (Lightweight) | Browser | 5800 | - |
| `jupyter-datascience` | Jupyter Data Science | IDE | 8888 | - |
| `kasm` | Kasm Workspaces | Desktop | 3000 | ✓ |
| `kasm-desktop-deluxe` | Ubuntu Desktop Deluxe | Desktop | 6901 | - |
| `kasmweb-almalinux-8-desktop` | AlmaLinux 8 | Desktop | 6901 | - |
| `kasmweb-almalinux-9-desktop` | AlmaLinux 9 | Desktop | 6901 | - |
| `kasmweb-alpine-317-desktop` | Alpine 3.17 | Desktop | 6901 | - |
| `kasmweb-alpine-318-desktop` | Alpine 3.18 | Desktop | 6901 | - |
| `kasmweb-alpine-319-desktop` | Alpine 3.19 | Desktop | 6901 | - |
| `kasmweb-alpine-320-desktop` | Alpine 3.20 | Desktop | 6901 | - |
| `kasmweb-alpine-321-desktop` | Alpine 3.21 | Desktop | 6901 | - |
| `kasmweb-alpine-322-desktop` | Alpine 3.22 | Desktop | 6901 | - |
| `kasmweb-alpine-323-desktop` | Alpine 3.23 | Desktop | 6901 | - |
| `kasmweb-atom` | Atom | IDE | 6901 | - |
| `kasmweb-audacity` | Audacity | Tool | 6901 | - |
| `kasmweb-blender` | Blender | Tool | 6901 | - |
| `kasmweb-brave` | Brave | Browser | 6901 | - |
| `kasmweb-centos-7-desktop` | CentOS 7 | Desktop | 6901 | - |
| `kasmweb-chrome` | Chrome | Browser | 6901 | ✓ |
| `kasmweb-chromium` | Chromium | Browser | 6901 | - |
| `kasmweb-core-almalinux-8` | Core AlmaLinux 8 | Desktop | 6901 | - |
| `kasmweb-core-almalinux-9` | Core AlmaLinux 9 | Desktop | 6901 | - |
| `kasmweb-core-alpine-317` | Core Alpine 3.17 | Desktop | 6901 | - |
| `kasmweb-core-alpine-318` | Core Alpine 3.18 | Desktop | 6901 | - |
| `kasmweb-core-alpine-319` | Core Alpine 3.19 | Desktop | 6901 | - |
| `kasmweb-core-alpine-320` | Core Alpine 3.20 | Desktop | 6901 | - |
| `kasmweb-core-alpine-321` | Core Alpine 3.21 | Desktop | 6901 | - |
| `kasmweb-core-alpine-322` | Core Alpine 3.22 | Desktop | 6901 | - |
| `kasmweb-core-alpine-323` | Core Alpine 3.23 | Desktop | 6901 | - |
| `kasmweb-core-centos-7` | Core CentOS 7 | Desktop | 6901 | - |
| `kasmweb-core-cuda-bionic` | Core CUDA Development Toolkit Bionic | Desktop | 6901 | - |
| `kasmweb-core-cuda-focal` | CUDA Development Toolkit | Desktop | 6901 | - |
| `kasmweb-core-cuda-jammy` | CUDA Development Toolkit (Ubuntu Jammy) | Desktop | 6901 | - |
| `kasmweb-core-debian-bookworm` | Core Debian Bookworm | Desktop | 6901 | - |
| `kasmweb-core-debian-bullseye` | Core Debian Bullseye | Desktop | 6901 | - |
| `kasmweb-core-debian-trixie` | Core Debian Trixie | Desktop | 6901 | - |
| `kasmweb-core-fedora-37` | Core Fedora 37 | Desktop | 6901 | - |
| `kasmweb-core-fedora-38` | Core Fedora 38 | Desktop | 6901 | - |
| `kasmweb-core-fedora-39` | Core Fedora 39 | Desktop | 6901 | - |
| `kasmweb-core-fedora-40` | Core Fedora 40 | Desktop | 6901 | - |
| `kasmweb-core-fedora-41` | Core Fedora 41 | Desktop | 6901 | - |
| `kasmweb-core-fedora-42` | Core Fedora 42 | Desktop | 6901 | - |
| `kasmweb-core-fedora-43` | Core Fedora 43 | Desktop | 6901 | - |
| `kasmweb-core-kali-rolling` | Core Kali Linux Rolling | Desktop | 6901 | - |
| `kasmweb-core-kasmos` | Core KasmOS | Desktop | 6901 | - |
| `kasmweb-core-nvidia-focal` | Core NVIDIA Focal | Desktop | 6901 | - |
| `kasmweb-core-opensuse-15` | Core OpenSUSE Leap 15 | Desktop | 6901 | - |
| `kasmweb-core-opensuse-16` | Core OpenSUSE Leap 16 | Desktop | 6901 | - |
| `kasmweb-core-oracle-7` | Core Oracle Linux 7 | Desktop | 6901 | - |
| `kasmweb-core-oracle-8` | Core Oracle Linux 8 | Desktop | 6901 | - |
| `kasmweb-core-oracle-9` | Core Oracle Linux 9 | Desktop | 6901 | - |
| `kasmweb-core-parrotos-5` | Core Parrot OS 5 | Desktop | 6901 | - |
| `kasmweb-core-parrotos-6` | Core Parrot OS 6 | Desktop | 6901 | - |
| `kasmweb-core-parrotos-7` | Core Parrot OS 7 | Desktop | 6901 | - |
| `kasmweb-core-remnux-bionic` | Core REMnux Bionic | Desktop | 6901 | - |
| `kasmweb-core-remnux-focal` | Core REMnux Focal | Desktop | 6901 | - |
| `kasmweb-core-rhel-9` | Core RHEL 9 | Desktop | 6901 | - |
| `kasmweb-core-rockylinux-8` | Core Rocky Linux 8 | Desktop | 6901 | - |
| `kasmweb-core-rockylinux-9` | Core Rocky Linux 9 | Desktop | 6901 | - |
| `kasmweb-core-ubuntu-bionic` | Core Ubuntu Bionic | Desktop | 6901 | - |
| `kasmweb-core-ubuntu-focal` | Core Ubuntu Focal | Desktop | 6901 | - |
| `kasmweb-core-ubuntu-jammy` | Core Ubuntu Jammy | Desktop | 6901 | - |
| `kasmweb-core-ubuntu-noble` | Core Ubuntu Noble | Desktop | 6901 | - |
| `kasmweb-core-ubuntu-resolute` | Core Ubuntu Resolute | Desktop | 6901 | - |
| `kasmweb-core-ubuntu-resolute-wkde` | Core Ubuntu Resolute Wkde | Desktop | 6901 | - |
| `kasmweb-cursor` | Cursor | IDE | 6901 | - |
| `kasmweb-cyberbro` | Cyberbro | Tool | 6901 | - |
| `kasmweb-debian-bookworm-desktop` | Debian Bookworm | Desktop | 6901 | - |
| `kasmweb-debian-bullseye-desktop` | Debian Bullseye | Desktop | 6901 | - |
| `kasmweb-debian-trixie-desktop` | Debian Trixie | Desktop | 6901 | - |
| `kasmweb-deluge` | Deluge | Productivity | 6901 | - |
| `kasmweb-desktop` | Ubuntu Desktop | Desktop | 6901 | ✓ |
| `kasmweb-discord` | Discord | Tool | 6901 | - |
| `kasmweb-edge` | Edge | Browser | 6901 | - |
| `kasmweb-fedora-37-desktop` | Fedora 37 | Desktop | 6901 | - |
| `kasmweb-fedora-38-desktop` | Fedora 38 | Desktop | 6901 | - |
| `kasmweb-fedora-39-desktop` | Fedora 39 | Desktop | 6901 | - |
| `kasmweb-fedora-40-desktop` | Fedora 40 | Desktop | 6901 | - |
| `kasmweb-fedora-41-desktop` | Fedora 41 | Desktop | 6901 | - |
| `kasmweb-fedora-42-desktop` | Fedora 42 | Desktop | 6901 | - |
| `kasmweb-fedora-43-desktop` | Fedora 43 | Desktop | 6901 | - |
| `kasmweb-filezilla` | FileZilla | Productivity | 6901 | - |
| `kasmweb-firefox` | Firefox | Browser | 6901 | - |
| `kasmweb-forensic-osint` | Forensic OSINT | Productivity | 6901 | - |
| `kasmweb-gimp` | Gimp | Tool | 6901 | - |
| `kasmweb-hunchly` | Hunchly | Productivity | 6901 | - |
| `kasmweb-inkscape` | Inkscape | Tool | 6901 | - |
| `kasmweb-insomnia` | Insomnia | Tool | 6901 | - |
| `kasmweb-java-dev` | Java Development | IDE | 6901 | - |
| `kasmweb-kali-rolling-desktop` | Kali Linux | Desktop | 6901 | - |
| `kasmweb-kasmos-desktop` | KasmOS | Desktop | 6901 | - |
| `kasmweb-libre-office` | Libre Office | Productivity | 6901 | - |
| `kasmweb-maltego` | Maltego | Productivity | 6901 | - |
| `kasmweb-minetest` | Minetest | Game | 6901 | - |
| `kasmweb-nessus` | Nessus | Tool | 6901 | - |
| `kasmweb-obsidian` | Obsidian | Productivity | 6901 | - |
| `kasmweb-only-office` | Only Office | Productivity | 6901 | - |
| `kasmweb-opensuse-15-desktop` | OpenSUSE Leap 15 | Desktop | 6901 | - |
| `kasmweb-opensuse-16-desktop` | OpenSUSE Leap 16 | Desktop | 6901 | - |
| `kasmweb-oracle-7-desktop` | Oracle Linux 7 | Desktop | 6901 | - |
| `kasmweb-oracle-8-desktop` | Oracle Linux 8 | Desktop | 6901 | - |
| `kasmweb-oracle-9-desktop` | Oracle Linux 9 | Desktop | 6901 | - |
| `kasmweb-parrotos-5-desktop` | Parrot OS 5 | Desktop | 6901 | - |
| `kasmweb-parrotos-6-desktop` | Parrot OS 6 | Desktop | 6901 | - |
| `kasmweb-parrotos-7-desktop` | Parrot OS 7 | Desktop | 6901 | - |
| `kasmweb-pinta` | Pinta | Tool | 6901 | - |
| `kasmweb-postman` | Postman | Tool | 6901 | - |
| `kasmweb-qbittorrent` | qBittorrent | Productivity | 6901 | - |
| `kasmweb-redroid` | Redroid | Productivity | 6901 | - |
| `kasmweb-remmina` | Remmina | Productivity | 6901 | - |
| `kasmweb-remnux-focal-desktop` | REMnux Focal | Desktop | 6901 | - |
| `kasmweb-remnux-noble-desktop` | REMnux | Desktop | 6901 | - |
| `kasmweb-retroarch` | RetroArch | Game | 6901 | - |
| `kasmweb-rhel-9-desktop` | RHEL 9 | Desktop | 6901 | - |
| `kasmweb-rockylinux-8-desktop` | Rocky Linux 8 | Desktop | 6901 | - |
| `kasmweb-rockylinux-9-desktop` | Rocky Linux 9 | Desktop | 6901 | - |
| `kasmweb-signal` | Signal | Tool | 6901 | - |
| `kasmweb-slack` | Slack | Productivity | 6901 | - |
| `kasmweb-spiderfoot` | Spiderfoot | Productivity | 6901 | - |
| `kasmweb-steam` | Steam | Game | 6901 | - |
| `kasmweb-sublime-text` | Sublime Text | IDE | 6901 | - |
| `kasmweb-super-tux-kart` | SuperTuxKart | Game | 6901 | - |
| `kasmweb-teams` | Teams | Tool | 6901 | - |
| `kasmweb-telegram` | Telegram | Tool | 6901 | - |
| `kasmweb-terminal` | Terminal | Tool | 6901 | - |
| `kasmweb-thunderbird` | Thunderbird | Productivity | 6901 | - |
| `kasmweb-tracelabs` | Trace Labs - Kali | Productivity | 6901 | - |
| `kasmweb-tracelabs-debian` | Trace Labs - Debian | Productivity | 6901 | - |
| `kasmweb-ubuntu-bionic-desktop` | Ubuntu Bionic | Desktop | 6901 | - |
| `kasmweb-ubuntu-bionic-dind` | Ubuntu Bionic Dind | Desktop | 6901 | - |
| `kasmweb-ubuntu-bionic-dind-rootless` | Ubuntu Bionic Dind Rootless | Desktop | 6901 | - |
| `kasmweb-ubuntu-focal-desktop` | Ubuntu Focal | Desktop | 6901 | - |
| `kasmweb-ubuntu-focal-desktop-vpn` | Ubuntu Focal VPN | Desktop | 6901 | - |
| `kasmweb-ubuntu-focal-dind` | Docker Ubuntu Focal | Desktop | 6901 | - |
| `kasmweb-ubuntu-focal-dind-rootless` | Docker Rootless Ubuntu Focal | Desktop | 6901 | - |
| `kasmweb-ubuntu-jammy-desktop` | Ubuntu Jammy | Desktop | 6901 | - |
| `kasmweb-ubuntu-jammy-desktop-ai-dev` | Ubuntu AI Dev | Desktop | 6901 | - |
| `kasmweb-ubuntu-jammy-desktop-vpn` | Ubuntu Jammy VPN | Desktop | 6901 | - |
| `kasmweb-ubuntu-jammy-dind` | Docker Ubuntu Jammy | Desktop | 6901 | - |
| `kasmweb-ubuntu-jammy-dind-rootless` | Docker Rootless Ubuntu Jammy | Desktop | 6901 | - |
| `kasmweb-ubuntu-jammy-nvidia` | Ubuntu Jammy NVIDIA | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-anythingllm` | AnythingLLM | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-desktop` | Ubuntu Noble | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-dind` | Docker Ubuntu Noble | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-dind-rootless` | Docker Rootless Ubuntu Noble | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-easydiffusion` | Easy Diffusion | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-ml-engineering` | ML Engineering | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-nvidia` | Ubuntu Noble NVIDIA | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-nvidia-pytorch` | Ubuntu Noble NVIDIA PyTorch | Desktop | 6901 | - |
| `kasmweb-ubuntu-noble-nvidia-tensorflow` | Ubuntu Noble NVIDIA TensorFlow | Desktop | 6901 | - |
| `kasmweb-unityhub` | Unity Hub | IDE | 6901 | - |
| `kasmweb-vivaldi` | Vivaldi | Browser | 6901 | - |
| `kasmweb-vlc` | VLC | Tool | 6901 | - |
| `kasmweb-vs-code` | Visual Studio Code | IDE | 6901 | - |
| `kasmweb-zoom` | Zoom | Tool | 6901 | - |
| `libreoffice` | LibreOffice | Productivity | 3000 | - |
| `ms-dos-622` | MS-DOS 6.22 | Desktop | 21 | ✓ |
| `ms-windows-11-vm` | Windows 11 VM (self-built) | VM | 3389 | - |
| `obsidian` | Obsidian | Productivity | 3000 | - |
| `openvscode-server` | OpenVSCode Server | IDE | 3000 | - |
| `pacman` | Pac-Man (HTML5) | Game | 80 | - |
| `rdesktop-ubuntu-xfce` | Ubuntu XFCE RDP Desktop | Desktop | 3000 | - |
| `rstudio` | RStudio Server | IDE | 8787 | - |
| `signal-desktop` | Signal Private Messenger | Productivity | 6080 | - |
| `snake` | Snake | Game | 80 | - |
| `stirling-pdf` | Stirling PDF | Tool | 8080 | - |
| `tetris` | Tetris | Game | 80 | - |
| `thelounge` | The Lounge (IRC) | Productivity | 9000 | - |
| `tor-browser` | Tor-Browser | Browser | 6901 | - |
| `trilium-notes` | Trilium Notes | Productivity | 8080 | - |
| `ttyd` | ttyd Web Terminal | Tool | 7681 | - |
| `vscodium` | VSCodium | IDE | 3000 | - |
| `webtop-alpine-kde` | Alpine KDE Desktop | Desktop | 3000 | - |
| `webtop-arch-kde` | Arch Linux KDE Desktop | Desktop | 3000 | - |
| `webtop-ubuntu-xfce` | Ubuntu XFCE Desktop | Desktop | 3000 | - |
| `wordle` | Wordle | Game | 80 | - |
| `zeppelin` | Apache Zeppelin | IDE | 8080 | - |

"Example" marks the curated subset installed by default by the
`kube-workspaces/deploy` Helm chart. See
[Curated examples](CONTRIBUTING.md#curated-examples).

## Schema

The full field reference lives in the controller repo's
[`image_types.go`](https://github.com/kube-workspaces/controller/blob/main/api/v1alpha1/image_types.go).
Commonly used fields:

| Field | Type | Notes |
|-------|------|-------|
| `image` | string | Container image reference (required) |
| `defaultPort` | int32 | Container port (required) |
| `displayName` | string | UI label |
| `description` | string | UI description |
| `category` | string | UI grouping, e.g. `IDE`, `Desktop`, `Game`, `Tool`, `Productivity`, `Browser` |
| `tags` | []string | Filtering/search labels |
| `defaultPath` | string | URL path appended when connecting |
| `defaultArgs` | []string | Extra container args at creation time |
| `defaultEnv` | []{name,value} | Env vars; supports `{{namespace}}`/`{{name}}` placeholders |
| `defaultCredentials` | {username,password} | Default login shown in the UI |
| `defaultUser` / `defaultHomedir` / `defaultShell` | string | Shell/exec session defaults |
| `defaultPassword` | string | Default password for `defaultUser` (only set when there is a known default) |
| `defaultCloudInit` | bool | Image has cloud-init baked in; lets user-data be seeded at first boot |
| `defaultUserData` | string | cloud-init user-data (e.g. `#cloud-config`) applied to VM guests |
| `workspaceTypes` | []string | Workspace types this image supports: `container`, `vm`, `scratch` (empty = container only) |
| `persistentRootDisk` / `persistentRootDiskSize` | bool / string | VM root as a CDI DataVolume-backed PVC (e.g. `20Gi`) instead of an ephemeral containerDisk |
| `memoryLimit` / `memoryRequest` | string | VM guest RAM and virt-launcher pod memory overrides (e.g. `4Gi` / `5Gi`) |
| `videoDevice` | string | VM video device type: `virtio` (virtio-gpu, recommended), `vga`, `bochs`, `cirrus`, `ramfb` |
| `defaultUID` | int64 | Sets pod `securityContext.runAsUser`/`fsGroup` |
| `defaultInitContainers` | []Container | Injected at creation (e.g. volume chown) |
| `additionalPorts` | []{name,port,protocol} | Extra exposed ports (e.g. audio) |
| `defaultSharedMemory` | bool | Mounts `/dev/shm` as memory-backed |
| `defaultImagePullPolicy` | string | Container pull policy (`Always`, `IfNotPresent`, `Never`); empty = Kubernetes default (`Always` for `:latest`, `IfNotPresent` for pinned tags). Set `Always` for images published under a rolling tag so restarted workspaces pick up new builds. A workspace can override it |
| `privileged` | bool | Runs the container privileged |
| `proxyConfig` | object | Reverse-proxy behaviour hints — see below |

VM images can opt into platform-managed live SSH keys with metadata annotation
`kubeworkspaces.io/ssh-key-propagation: qemuGuestAgent` and `spec.defaultUser`.
The guest must install and run `qemu-guest-agent` with SSH-key command support.
The controller then attaches a stable Secret using KubeVirt access credentials;
key additions and deletions replace the account's entire `authorized_keys`
(manual entries are not preserved). Existing VMs require one restart to attach
the credential source. `debian-vm` and `debian-xfce` opt in and provision the
agent; cloud-init capability alone does not enable managed keys.

The XFCE defaults configure MAC-independent netplan/networkd DHCP and static
public DNS (`1.1.1.1`, `9.9.9.9`) before package installation and on each boot.
Customize the resolvers in `defaultUserData` when cluster-internal DNS is needed
or public DNS egress is restricted. Updated defaults apply to fresh provisions;
they do not automatically retrofit an existing persistent guest.

The XFCE image uses **xfce4-screensaver** for password-protected screen locking.
Selkies captures and injects input into `DISPLAY=:0`; Debian's alternative
`light-locker` switches to a separate LightDM greeter on another X display/VT.
That leaves Selkies capturing a black, inactive user display while the QEMU/VNC
console correctly shows the greeter. Client wake keys cannot repair that
display mismatch. Keep the locker within the captured session rather than
disabling authentication or automatically switching away from a locked greeter.
The virtual monitor's DPMS power-saving is disabled; the screensaver can still
blank and lock the session without turning off the captured output.

For an existing persistent XFCE guest provisioned with `light-locker`, install
the replacement and remove the old locker inside the guest:

```bash
sudo apt-get install xfce4-screensaver
sudo apt-get purge light-locker
```

Then log out and back in through the VM console so the new locker autostarts.
This ends the graphical session; save work first. Verify that clicking inside
the connected remote display reveals the password prompt on the same X
display, without a VT switch. A blank lock screen before clicking can be
normal. In the logged-in guest's terminal, also disable monitor power-saving:

```bash
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled --create -t bool -s false
xset dpms force on
xset -dpms
```

`proxyConfig` fields (all optional): `needsNoopSW`, `websocketPaths`,
`rewriteHostAbsolutePaths`, `customRequestHeaders`, `injectBaseTag`,
`scheme` (`http`/`https`), `tlsSkipVerify`, `preservePathPrefix`, `audioPort`,
`agentPort` (guest TCP port of the workspace-agent listener; when set on a VM
image the controller forwards it through masquerade and exposes it on the
workspace Service, and the proxy serves the `/agent/` bridge against it).

The CRD schema itself is vendored at
[`crds/kubeworkspaces.io_images.yaml`](crds/kubeworkspaces.io_images.yaml)
for offline validation — see [Updating the CRD schema](CONTRIBUTING.md#updating-the-crd-schema).

## Usage

### Apply directly to a cluster

```bash
kubectl apply --server-side -f https://github.com/kube-workspaces/image-catalog/releases/download/v0.1.0/images.yaml
```

### Consume from another repo

Each GitHub Release publishes two build artifacts:

- `images.yaml` — every image in the catalog
- `images-examples.yaml` — only the curated example subset

Pin a version and vendor the file(s) you need rather than fetching `main` at
install time — see `kube-workspaces/deploy`'s `make sync-images` target for
the pattern this repo expects downstream consumers to follow.

### Build locally

```bash
make validate   # structural + schema checks
make build      # writes dist/images.yaml and dist/images-examples.yaml
```

## Development

```bash
git clone https://github.com/kube-workspaces/image-catalog.git
cd image-catalog
make validate
```

Requires [`yq`](https://github.com/mikefarah/yq) and
[`jq`](https://jqlang.github.io/jq/). Optionally
[`kubeconform`](https://github.com/yannh/kubeconform) for schema validation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new image, mark it as
a curated example, update the vendored CRD schema, and cut a release.

## Related Repositories

| Repository | Description |
|-----------|-------------|
| [kube-workspaces/controller](https://github.com/kube-workspaces/controller) | Kubernetes controller — owns the `Image` CRD |
| [kube-workspaces/deploy](https://github.com/kube-workspaces/deploy) | Deployment manifests — primary consumer of this catalog |
| [kube-workspaces/api](https://github.com/kube-workspaces/api) | REST API — serves `Image` CRs to the frontend |
| [kube-workspaces/frontend](https://github.com/kube-workspaces/frontend) | UI — includes an `Image` CR editor |

## License

Apache License 2.0 — see [LICENSE](LICENSE).
