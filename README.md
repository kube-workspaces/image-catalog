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

The [LinuxServer collection](images/linuxserver/README.md) contains 297 Image CRs
in `images/linuxserver/`, covering 292 runnable repositories and five existing
pinned/desktop variants. Its inventory includes all 203 maintained images,
deprecated images and legacy/infrastructure repositories retained on Docker Hub.
The collection README documents metadata sources, native-protocol/CLI entries,
and per-image setup requirements. These images support container and scratch
workspaces; none are bootable VM disks.

Validation and distribution builds include nested image folders recursively.
`ImageRepository` syncing scans only the direct files in each configured folder.
To sync the full catalog, list all four paths explicitly (trailing `/` optional):

```yaml
spec:
  paths:
    - images
    - images/kasm/core
    - images/kasm/desktop
    - images/linuxserver
```

## Available Images

<!-- Generated from all YAML manifests recursively under images/. -->

| Name | Display Name | Category | Port | Example |
|------|---------------|----------|------|---------|
| `adminer` | Adminer (Database Manager) | Tool | 8080 | - |
| `alpine` | Alpine Linux | Tool | 80 | - |
| `alpine-container-init` | Alpine Linux — container-init demo | Tool | 80 | - |
| `alpine-vm` | Alpine VM | VM | 22 | ✓ |
| `arch-linux-gnome-vm` | Arch Linux GNOME Desktop VM | Desktop | 22 | - |
| `chromium` | Chromium (LinuxServer) | Browser | 3000 | - |
| `code-server` | Code Server (VS Code) | IDE | 8080 | ✓ |
| `craft-apps` | Craft Apps (ArtCraft) (LinuxServer) | Tool | 3000 | - |
| `cyberchef` | CyberChef | Tool | 8000 | - |
| `debian-desktop` | Debian Desktop | Desktop | 6901 | ✓ |
| `debian-vm` | Debian VM | VM | 22 | ✓ |
| `debian-xfce` | Debian Desktop XFCE | Desktop | 8080 | ✓ |
| `doom` | Doom | Game | 6901 | - |
| `drawio` | draw.io (Diagrams) | Productivity | 8080 | - |
| `excalidraw` | Excalidraw (Whiteboard) | Productivity | 80 | - |
| `filebrowser` | File Browser | Tool | 80 | - |
| `firefox` | Firefox (LinuxServer) | Browser | 3000 | - |
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
| `libreoffice` | LibreOffice (LinuxServer) | Tool | 3000 | - |
| `linuxserver-adguardhome-sync` | AdGuard Home Sync (LinuxServer) | Tool | 8080 | - |
| `linuxserver-airsonic` | Airsonic (LinuxServer) | Tool | 4040 | - |
| `linuxserver-airsonic-advanced` | Airsonic Advanced (LinuxServer) | Tool | 4040 | - |
| `linuxserver-altus` | Altus (LinuxServer) | Tool | 3000 | - |
| `linuxserver-apache` | Apache (LinuxServer) | Tool | 80 | - |
| `linuxserver-apprise-api` | Apprise API (LinuxServer) | Tool | 8000 | - |
| `linuxserver-ardour` | Ardour (LinuxServer) | Tool | 3000 | - |
| `linuxserver-audacity` | Audacity (LinuxServer) | Tool | 3000 | - |
| `linuxserver-audiosilo` | AudioSilo (LinuxServer) | Tool | 8080 | - |
| `linuxserver-azahar` | Azahar (LinuxServer) | Game | 3000 | - |
| `linuxserver-babybuddy` | Baby Buddy (LinuxServer) | Tool | 8000 | - |
| `linuxserver-bambustudio` | Bambu Studio (LinuxServer) | Tool | 3000 | - |
| `linuxserver-bazarr` | Bazarr (LinuxServer) | Tool | 6767 | - |
| `linuxserver-beets` | Beets (LinuxServer) | Tool | 8337 | - |
| `linuxserver-bitcoin-knots` | Bitcoin Knots (LinuxServer) | Tool | 3000 | - |
| `linuxserver-blade-of-agony` | Blade of Agony (LinuxServer) | Game | 3000 | - |
| `linuxserver-blender` | Blender (LinuxServer) | Tool | 3000 | - |
| `linuxserver-boinc` | BOINC (LinuxServer) | Tool | 8080 | - |
| `linuxserver-booksonic` | Booksonic (LinuxServer) | Tool | 4040 | - |
| `linuxserver-booksonic-air` | Booksonic Air (LinuxServer) | Tool | 4040 | - |
| `linuxserver-bookstack` | BookStack (LinuxServer) | Tool | 80 | - |
| `linuxserver-brave` | Brave (LinuxServer) | Browser | 3000 | - |
| `linuxserver-budge` | Budge (LinuxServer) | Tool | 80 | - |
| `linuxserver-build-agent` | Build Agent (LinuxServer) | Tool | 2222 | - |
| `linuxserver-calibre` | Calibre (LinuxServer) | Tool | 8080 | - |
| `linuxserver-calibre-web` | Calibre-Web (LinuxServer) | Tool | 8083 | - |
| `linuxserver-calligra` | Calligra (LinuxServer) | Tool | 3000 | - |
| `linuxserver-cardigann` | Cardigann (LinuxServer) | Tool | 5060 | - |
| `linuxserver-changedetection-io` | changedetection.io (LinuxServer) | Tool | 5000 | - |
| `linuxserver-chevereto` | Chevereto (LinuxServer) | Tool | 443 | - |
| `linuxserver-chrome` | Google Chrome (LinuxServer) | Browser | 3000 | - |
| `linuxserver-ci` | LinuxServer CI (LinuxServer) | Tool | 80 | - |
| `linuxserver-ci-debug` | LinuxServer CI Debug (LinuxServer) | Tool | 80 | - |
| `linuxserver-citron` | Citron (LinuxServer) | Game | 3000 | - |
| `linuxserver-clarkson` | Clarkson (LinuxServer) | Tool | 3000 | - |
| `linuxserver-cloud9` | Cloud9 (LinuxServer) | IDE | 8000 | - |
| `linuxserver-code-server` | code-server (LinuxServer) | IDE | 8443 | - |
| `linuxserver-codiad` | Codiad (LinuxServer) | IDE | 80 | - |
| `linuxserver-codimd` | CodiMD (LinuxServer) | Tool | 3000 | - |
| `linuxserver-cops` | COPS (LinuxServer) | Tool | 80 | - |
| `linuxserver-couchpotato` | CouchPotato (LinuxServer) | Tool | 5050 | - |
| `linuxserver-cura` | Cura (LinuxServer) | Tool | 3000 | - |
| `linuxserver-d2-builder` | D2 Builder (LinuxServer) | Tool | 80 | - |
| `linuxserver-daapd` | DAAPd (LinuxServer) | Tool | 3689 | - |
| `linuxserver-darktable` | darktable (LinuxServer) | Tool | 3000 | - |
| `linuxserver-davos` | Davos (LinuxServer) | Tool | 8080 | - |
| `linuxserver-ddclient` | DDClient (LinuxServer) | Tool | 80 | - |
| `linuxserver-deluge` | Deluge (LinuxServer) | Tool | 8112 | - |
| `linuxserver-digikam` | digiKam (LinuxServer) | Tool | 3000 | - |
| `linuxserver-dillinger` | Dillinger (LinuxServer) | Tool | 8080 | - |
| `linuxserver-diskover` | Diskover (LinuxServer) | Tool | 80 | - |
| `linuxserver-doc-builder` | Doc Builder (LinuxServer) | Tool | 80 | - |
| `linuxserver-docker-compose` | Docker Compose (LinuxServer) | Tool | 80 | - |
| `linuxserver-dogwalk` | Dogwalk (LinuxServer) | Game | 3000 | - |
| `linuxserver-dokuwiki` | DokuWiki (LinuxServer) | Tool | 80 | - |
| `linuxserver-dolphin` | Dolphin (LinuxServer) | Game | 3000 | - |
| `linuxserver-domoticz` | Domoticz (LinuxServer) | Tool | 8080 | - |
| `linuxserver-doplarr` | Doplarr (LinuxServer) | Tool | 80 | - |
| `linuxserver-doplarr-rs` | Doplarr RS (LinuxServer) | Tool | 80 | - |
| `linuxserver-dosbox-staging` | DOSBox Staging (LinuxServer) | Game | 3000 | - |
| `linuxserver-doublecommander` | Double Commander (LinuxServer) | Tool | 3000 | - |
| `linuxserver-duckdns` | DuckDNS (LinuxServer) | Tool | 80 | - |
| `linuxserver-duckstation` | DuckStation (LinuxServer) | Game | 3000 | - |
| `linuxserver-duplicati` | Duplicati (LinuxServer) | Tool | 8200 | - |
| `linuxserver-eden` | Eden (LinuxServer) | Game | 3000 | - |
| `linuxserver-emby` | Emby (LinuxServer) | Tool | 8096 | - |
| `linuxserver-embystat` | EmbyStat (LinuxServer) | Tool | 6555 | - |
| `linuxserver-emulatorjs` | EmulatorJS (LinuxServer) | Game | 3000 | - |
| `linuxserver-endlessh` | Endlessh (LinuxServer) | Tool | 2222 | - |
| `linuxserver-fail2ban` | Fail2Ban (LinuxServer) | Tool | 80 | - |
| `linuxserver-faster-whisper` | Faster Whisper (LinuxServer) | Tool | 10300 | - |
| `linuxserver-feed2toot` | Feed2Toot (LinuxServer) | Tool | 80 | - |
| `linuxserver-ferdium` | Ferdium (LinuxServer) | Tool | 3000 | - |
| `linuxserver-ffmpeg` | FFmpeg (LinuxServer) | Tool | 80 | - |
| `linuxserver-filezilla` | FileZilla (LinuxServer) | Tool | 3000 | - |
| `linuxserver-fleet` | Fleet (LinuxServer) | Tool | 8080 | - |
| `linuxserver-flexget` | FlexGet (LinuxServer) | Tool | 5050 | - |
| `linuxserver-flood` | Flood (LinuxServer) | Tool | 3000 | - |
| `linuxserver-flycast` | Flycast (LinuxServer) | Game | 3000 | - |
| `linuxserver-foldingathome` | Folding@home (LinuxServer) | Tool | 7396 | - |
| `linuxserver-freecad` | FreeCAD (LinuxServer) | Tool | 3000 | - |
| `linuxserver-freetube` | FreeTube (LinuxServer) | Tool | 3000 | - |
| `linuxserver-freshrss` | FreshRSS (LinuxServer) | Tool | 80 | - |
| `linuxserver-gazee` | Gazee (LinuxServer) | Tool | 4242 | - |
| `linuxserver-gimp` | GIMP (LinuxServer) | Tool | 3000 | - |
| `linuxserver-github-desktop` | GitHub Desktop (LinuxServer) | Tool | 3000 | - |
| `linuxserver-gitqlient` | GitQlient (LinuxServer) | Tool | 3000 | - |
| `linuxserver-grav` | Grav (LinuxServer) | Tool | 80 | - |
| `linuxserver-grocy` | grocy (LinuxServer) | Tool | 80 | - |
| `linuxserver-guacd` | Guacd (LinuxServer) | Tool | 4822 | - |
| `linuxserver-gzdoom` | GZDoom (LinuxServer) | Game | 3000 | - |
| `linuxserver-habridge` | HA Bridge (LinuxServer) | Tool | 8080 | - |
| `linuxserver-handbrake` | HandBrake (LinuxServer) | Tool | 3000 | - |
| `linuxserver-headphones` | Headphones (LinuxServer) | Tool | 8181 | - |
| `linuxserver-healthchecks` | Healthchecks (LinuxServer) | Tool | 8000 | - |
| `linuxserver-hedgedoc` | HedgeDoc (LinuxServer) | Tool | 3000 | - |
| `linuxserver-heimdall` | Heimdall (LinuxServer) | Tool | 80 | - |
| `linuxserver-helium` | Helium (LinuxServer) | Browser | 3000 | - |
| `linuxserver-hishtory-server` | hiSHtory Server (LinuxServer) | Tool | 8080 | - |
| `linuxserver-homeassistant` | Home Assistant (LinuxServer) | Tool | 8123 | - |
| `linuxserver-htpcmanager` | HTPC Manager (LinuxServer) | Tool | 8085 | - |
| `linuxserver-hydra` | Hydra (LinuxServer) | Tool | 5075 | - |
| `linuxserver-hydra2` | Hydra2 (LinuxServer) | Tool | 5076 | - |
| `linuxserver-inkscape` | Inkscape (LinuxServer) | Tool | 3000 | - |
| `linuxserver-intellij-idea` | IntelliJ IDEA (LinuxServer) | IDE | 3000 | - |
| `linuxserver-ipfs` | IPFS (LinuxServer) | Tool | 80 | - |
| `linuxserver-jackett` | Jackett (LinuxServer) | Tool | 9117 | - |
| `linuxserver-jellyfin` | Jellyfin (LinuxServer) | Tool | 8096 | - |
| `linuxserver-jenkins-builder` | Jenkins Builder (LinuxServer) | Tool | 80 | - |
| `linuxserver-joplin` | Joplin (LinuxServer) | Tool | 3000 | - |
| `linuxserver-kali-linux` | Kali Linux (LinuxServer) | Desktop | 3000 | - |
| `linuxserver-kanzi` | Kanzi (LinuxServer) | Tool | 8000 | - |
| `linuxserver-kasm` | Kasm Workspaces (LinuxServer) | Desktop | 3000 | - |
| `linuxserver-kavita` | Kavita (LinuxServer) | Tool | 5000 | - |
| `linuxserver-kdenlive` | Kdenlive (LinuxServer) | Tool | 3000 | - |
| `linuxserver-keepassxc` | KeePassXC (LinuxServer) | Tool | 3000 | - |
| `linuxserver-kicad` | KiCad (LinuxServer) | Tool | 3000 | - |
| `linuxserver-kimai` | Kimai (LinuxServer) | Tool | 80 | - |
| `linuxserver-kodi-headless` | Kodi Headless (LinuxServer) | Tool | 8080 | - |
| `linuxserver-kometa` | Kometa (LinuxServer) | Tool | 80 | - |
| `linuxserver-krita` | Krita (LinuxServer) | Tool | 3000 | - |
| `linuxserver-lazylibrarian` | Lazylibrarian (LinuxServer) | Tool | 5299 | - |
| `linuxserver-ldap-auth` | LDAP Auth (LinuxServer) | Tool | 9000 | - |
| `linuxserver-letsencrypt` | Letsencrypt (LinuxServer) | Tool | 443 | - |
| `linuxserver-libresonic` | Libresonic (LinuxServer) | Tool | 4040 | - |
| `linuxserver-librespeed` | LibreSpeed (LinuxServer) | Tool | 80 | - |
| `linuxserver-librewolf` | LibreWolf (LinuxServer) | Browser | 3000 | - |
| `linuxserver-lidarr` | Lidarr (LinuxServer) | Tool | 8686 | - |
| `linuxserver-limnoria` | Limnoria (LinuxServer) | Tool | 8080 | - |
| `linuxserver-lm-studio` | LM Studio (LinuxServer) | Tool | 3000 | - |
| `linuxserver-lollypop` | Lollypop (LinuxServer) | Tool | 3000 | - |
| `linuxserver-lsio-api` | LinuxServer API (LinuxServer) | Tool | 8000 | - |
| `linuxserver-luanti` | Luanti (LinuxServer) | Game | 30000 | - |
| `linuxserver-lychee` | Lychee (LinuxServer) | Tool | 80 | - |
| `linuxserver-mame` | MAME (LinuxServer) | Game | 3000 | - |
| `linuxserver-manyfold` | Manyfold (LinuxServer) | Tool | 3214 | - |
| `linuxserver-mariadb` | MariaDB (LinuxServer) | Tool | 3306 | - |
| `linuxserver-mastodon` | Mastodon (LinuxServer) | Tool | 443 | - |
| `linuxserver-mcmyadmin2` | McMyAdmin 2 (LinuxServer) | Tool | 8080 | - |
| `linuxserver-mediaelch` | MediaElch (LinuxServer) | Tool | 3000 | - |
| `linuxserver-medusa` | Medusa (LinuxServer) | Tool | 8081 | - |
| `linuxserver-melonds` | melonDS (LinuxServer) | Game | 3000 | - |
| `linuxserver-minetest` | Minetest (LinuxServer) | Game | 30000 | - |
| `linuxserver-minisatip` | minisatip (LinuxServer) | Tool | 8875 | - |
| `linuxserver-modmanager` | Modmanager (LinuxServer) | Tool | 80 | - |
| `linuxserver-modrinth` | Modrinth (LinuxServer) | Game | 3000 | - |
| `linuxserver-monica` | Monica (LinuxServer) | Tool | 80 | - |
| `linuxserver-msedge` | Microsoft Edge (LinuxServer) | Browser | 3000 | - |
| `linuxserver-mstream` | mStream (LinuxServer) | Tool | 3000 | - |
| `linuxserver-mullvad-browser` | Mullvad Browser (LinuxServer) | Browser | 3000 | - |
| `linuxserver-musicbrainz` | Musicbrainz (LinuxServer) | Tool | 5000 | - |
| `linuxserver-muximux` | Muximux (LinuxServer) | Tool | 80 | - |
| `linuxserver-mylar` | Mylar (LinuxServer) | Tool | 8090 | - |
| `linuxserver-mylar3` | Mylar 3 (LinuxServer) | Tool | 8090 | - |
| `linuxserver-mysql` | MySQL (LinuxServer) | Tool | 3306 | - |
| `linuxserver-mysql-workbench` | MySQL Workbench (LinuxServer) | Tool | 3000 | - |
| `linuxserver-nano` | Nano (LinuxServer) | Tool | 8075 | - |
| `linuxserver-nano-wallet` | Nano Wallet (LinuxServer) | Tool | 80 | - |
| `linuxserver-netbootxyz` | netboot.xyz (LinuxServer) | Tool | 3000 | - |
| `linuxserver-netbox` | NetBox (LinuxServer) | Tool | 8000 | - |
| `linuxserver-nextcloud` | Nextcloud (LinuxServer) | Tool | 443 | - |
| `linuxserver-nginx` | NGINX (LinuxServer) | Tool | 80 | - |
| `linuxserver-ngircd` | ngIRCd (LinuxServer) | Tool | 6667 | - |
| `linuxserver-nntp2nntp` | NNTP2NNTP (LinuxServer) | Tool | 1563 | - |
| `linuxserver-nomacs` | nomacs (LinuxServer) | Tool | 3000 | - |
| `linuxserver-nzbget` | NZBGet (LinuxServer) | Tool | 6789 | - |
| `linuxserver-nzbhydra2` | NZBHydra 2 (LinuxServer) | Tool | 5076 | - |
| `linuxserver-ombi` | Ombi (LinuxServer) | Tool | 3579 | - |
| `linuxserver-onlyoffice` | ONLYOFFICE (LinuxServer) | Tool | 3000 | - |
| `linuxserver-openshot` | OpenShot (LinuxServer) | Tool | 3000 | - |
| `linuxserver-openssh-server` | OpenSSH Server (LinuxServer) | Tool | 2222 | - |
| `linuxserver-openvscode-server` | OpenVSCode Server (LinuxServer) | IDE | 3000 | - |
| `linuxserver-opera` | Opera (LinuxServer) | Browser | 3000 | - |
| `linuxserver-orcaslicer` | OrcaSlicer (LinuxServer) | Tool | 3000 | - |
| `linuxserver-organizr` | Organizr (LinuxServer) | Tool | 80 | - |
| `linuxserver-oscam` | OSCam (LinuxServer) | Tool | 8888 | - |
| `linuxserver-overseerr` | Overseerr (LinuxServer) | Tool | 5055 | - |
| `linuxserver-pairdrop` | PairDrop (LinuxServer) | Tool | 3000 | - |
| `linuxserver-paperless-ng` | Paperless Ng (LinuxServer) | Tool | 8000 | - |
| `linuxserver-paperless-ngx` | Paperless Ngx (LinuxServer) | Tool | 8000 | - |
| `linuxserver-papermerge` | Papermerge (LinuxServer) | Tool | 8000 | - |
| `linuxserver-pcsx2` | PCSX2 (LinuxServer) | Game | 3000 | - |
| `linuxserver-pelorus` | Pelorus (LinuxServer) | Tool | 3001 | - |
| `linuxserver-photoshow` | Photoshow (LinuxServer) | Tool | 80 | - |
| `linuxserver-phpmyadmin` | phpMyAdmin (LinuxServer) | Tool | 80 | - |
| `linuxserver-pidgin` | Pidgin (LinuxServer) | Tool | 3000 | - |
| `linuxserver-piper` | Piper (LinuxServer) | Tool | 10200 | - |
| `linuxserver-piwigo` | Piwigo (LinuxServer) | Tool | 80 | - |
| `linuxserver-pixapop` | Pixapop (LinuxServer) | Tool | 80 | - |
| `linuxserver-planka` | Planka (LinuxServer) | Tool | 1337 | - |
| `linuxserver-plex` | Plex (LinuxServer) | Tool | 32400 | - |
| `linuxserver-plex-meta-manager` | Plex Meta Manager (LinuxServer) | Tool | 80 | - |
| `linuxserver-plexpy` | Plexpy (LinuxServer) | Tool | 8181 | - |
| `linuxserver-ppsspp` | PPSSPP (LinuxServer) | Game | 3000 | - |
| `linuxserver-projectsend` | ProjectSend (LinuxServer) | Tool | 80 | - |
| `linuxserver-prowlarr` | Prowlarr (LinuxServer) | Tool | 9696 | - |
| `linuxserver-pwndrop` | pwndrop (LinuxServer) | Tool | 8080 | - |
| `linuxserver-pycharm` | PyCharm (LinuxServer) | IDE | 3000 | - |
| `linuxserver-pydio` | Pydio (LinuxServer) | Tool | 443 | - |
| `linuxserver-pydio-cells` | Pydio Cells (LinuxServer) | Tool | 8080 | - |
| `linuxserver-pyload` | pyLoad (LinuxServer) | Tool | 8000 | - |
| `linuxserver-pyload-ng` | pyLoad NG (LinuxServer) | Tool | 8000 | - |
| `linuxserver-pylon` | Pylon (LinuxServer) | Tool | 3131 | - |
| `linuxserver-python` | Python (LinuxServer) | Tool | 80 | - |
| `linuxserver-qbittorrent` | qBittorrent (LinuxServer) | Tool | 8080 | - |
| `linuxserver-qdirstat` | QDirStat (LinuxServer) | Tool | 3000 | - |
| `linuxserver-qemu-static` | QEMU Static (LinuxServer) | Tool | 80 | - |
| `linuxserver-quassel-core` | Quassel Core (LinuxServer) | Tool | 4242 | - |
| `linuxserver-quassel-web` | Quassel Web (LinuxServer) | Tool | 64443 | - |
| `linuxserver-radarr` | Radarr (LinuxServer) | Tool | 7878 | - |
| `linuxserver-raneto` | Raneto (LinuxServer) | Tool | 3000 | - |
| `linuxserver-rawtherapee` | RawTherapee (LinuxServer) | Tool | 3000 | - |
| `linuxserver-rdesktop` | RDesktop (LinuxServer) | Desktop | 3389 | - |
| `linuxserver-readarr` | Readarr (LinuxServer) | Tool | 8787 | - |
| `linuxserver-readme-sync` | Readme Sync (LinuxServer) | Tool | 80 | - |
| `linuxserver-remmina` | Remmina (LinuxServer) | Tool | 3000 | - |
| `linuxserver-requestrr` | Requestrr (LinuxServer) | Tool | 4545 | - |
| `linuxserver-resilio-sync` | Resilio Sync (LinuxServer) | Tool | 8888 | - |
| `linuxserver-retroarch` | RetroArch (LinuxServer) | Game | 3000 | - |
| `linuxserver-rpcs3` | RPCS3 (LinuxServer) | Game | 3000 | - |
| `linuxserver-rsnapshot` | rsnapshot (LinuxServer) | Tool | 80 | - |
| `linuxserver-rustdesk` | RustDesk (LinuxServer) | Tool | 3000 | - |
| `linuxserver-rutorrent` | ruTorrent (LinuxServer) | Tool | 80 | - |
| `linuxserver-sabnzbd` | SABnzbd (LinuxServer) | Tool | 8080 | - |
| `linuxserver-scrutiny` | Scrutiny (LinuxServer) | Tool | 8080 | - |
| `linuxserver-scummvm` | ScummVM (LinuxServer) | Game | 3000 | - |
| `linuxserver-sealskin` | Sealskin (LinuxServer) | Tool | 8443 | - |
| `linuxserver-series-troxide` | Series Troxide (LinuxServer) | Tool | 3000 | - |
| `linuxserver-shadps4` | shadPS4 (LinuxServer) | Game | 3000 | - |
| `linuxserver-shotcut` | Shotcut (LinuxServer) | Tool | 3000 | - |
| `linuxserver-sickbeard` | Sickbeard (LinuxServer) | Tool | 8081 | - |
| `linuxserver-sickchill` | SickChill (LinuxServer) | Tool | 8081 | - |
| `linuxserver-sickgear` | SickGear (LinuxServer) | Tool | 8081 | - |
| `linuxserver-sickrage` | Sickrage (LinuxServer) | Tool | 8081 | - |
| `linuxserver-signal` | Signal (LinuxServer) | Tool | 3000 | - |
| `linuxserver-smokeping` | Smokeping (LinuxServer) | Tool | 80 | - |
| `linuxserver-snapdrop` | Snapdrop (LinuxServer) | Tool | 80 | - |
| `linuxserver-snipe-it` | Snipe-IT (LinuxServer) | Tool | 80 | - |
| `linuxserver-socket-proxy` | Socket Proxy (LinuxServer) | Tool | 2375 | - |
| `linuxserver-sonarr` | Sonarr (LinuxServer) | Tool | 8989 | - |
| `linuxserver-speedtest-tracker` | Speedtest Tracker (LinuxServer) | Tool | 80 | - |
| `linuxserver-spotube` | Spotube (LinuxServer) | Tool | 3000 | - |
| `linuxserver-sqlitebrowser` | DB Browser for SQLite (LinuxServer) | Tool | 3000 | - |
| `linuxserver-steam` | Steam (LinuxServer) | Game | 3000 | - |
| `linuxserver-steamos` | SteamOS (LinuxServer) | Game | 3000 | - |
| `linuxserver-swag` | SWAG (LinuxServer) | Tool | 443 | - |
| `linuxserver-synclounge` | SyncLounge (LinuxServer) | Tool | 8088 | - |
| `linuxserver-syncthing` | Syncthing (LinuxServer) | Tool | 8384 | - |
| `linuxserver-syslog-ng` | syslog-ng (LinuxServer) | Tool | 5514 | - |
| `linuxserver-taisun` | Taisun (LinuxServer) | Tool | 3000 | - |
| `linuxserver-tautulli` | Tautulli (LinuxServer) | Tool | 8181 | - |
| `linuxserver-telegram` | Telegram (LinuxServer) | Tool | 3000 | - |
| `linuxserver-tester` | Tester (LinuxServer) | Tool | 3000 | - |
| `linuxserver-thunderbird` | Thunderbird (LinuxServer) | Tool | 3000 | - |
| `linuxserver-transmission` | Transmission (LinuxServer) | Tool | 9091 | - |
| `linuxserver-tvheadend` | Tvheadend (LinuxServer) | Tool | 9981 | - |
| `linuxserver-ubooquity` | Ubooquity (LinuxServer) | Tool | 2202 | - |
| `linuxserver-ungoogled-chromium` | Ungoogled Chromium (LinuxServer) | Browser | 3000 | - |
| `linuxserver-unifi` | UniFi (LinuxServer) | Tool | 8443 | - |
| `linuxserver-unifi-controller` | UniFi Controller (LinuxServer) | Tool | 8443 | - |
| `linuxserver-unifi-network-application` | UniFi Network Application (LinuxServer) | Tool | 8443 | - |
| `linuxserver-unrar` | UnRAR (LinuxServer) | Tool | 80 | - |
| `linuxserver-vivaldi` | Vivaldi (LinuxServer) | Browser | 3000 | - |
| `linuxserver-vlc` | VLC (LinuxServer) | Tool | 3000 | - |
| `linuxserver-vscode` | Visual Studio Code (LinuxServer) | IDE | 3000 | - |
| `linuxserver-vscodium-web` | VSCodium Web (LinuxServer) | IDE | 8000 | - |
| `linuxserver-webcord` | WebCord (LinuxServer) | Tool | 3000 | - |
| `linuxserver-webgrabplus` | WebGrab+Plus (LinuxServer) | Tool | 80 | - |
| `linuxserver-webstation` | Webstation (LinuxServer) | Tool | 3000 | - |
| `linuxserver-webtop` | Webtop (LinuxServer) | Desktop | 3000 | - |
| `linuxserver-weixin` | Weixin (LinuxServer) | Tool | 3000 | - |
| `linuxserver-wikijs` | Wiki.js (LinuxServer) | Tool | 3000 | - |
| `linuxserver-winegui` | WineGUI (LinuxServer) | Tool | 3000 | - |
| `linuxserver-wireguard` | WireGuard (LinuxServer) | Tool | 51820 | - |
| `linuxserver-wireshark` | Wireshark (LinuxServer) | Tool | 3000 | - |
| `linuxserver-wps-office` | WPS Office (LinuxServer) | Tool | 3000 | - |
| `linuxserver-xbackbone` | XBackBone (LinuxServer) | Tool | 80 | - |
| `linuxserver-xemu` | xemu (LinuxServer) | Game | 3000 | - |
| `linuxserver-xvfb` | Xvfb (LinuxServer) | Tool | 80 | - |
| `linuxserver-yaak` | Yaak (LinuxServer) | Tool | 3000 | - |
| `linuxserver-your-spotify` | Your Spotify (LinuxServer) | Tool | 80 | - |
| `linuxserver-yq` | yq (LinuxServer) | Tool | 80 | - |
| `linuxserver-zen` | Zen (LinuxServer) | Browser | 3000 | - |
| `linuxserver-znc` | ZNC (LinuxServer) | Tool | 6501 | - |
| `linuxserver-zotero` | Zotero (LinuxServer) | Tool | 3000 | - |
| `ms-dos-622` | MS-DOS 6.22 | Desktop | 21 | ✓ |
| `ms-windows-11-vm` | Windows 11 VM (self-built) | VM | 3389 | - |
| `obsidian` | Obsidian (LinuxServer) | Tool | 3000 | - |
| `openvscode-server` | OpenVSCode Server | IDE | 3000 | - |
| `pacman` | Pac-Man (HTML5) | Game | 80 | - |
| `rdesktop-ubuntu-xfce` | Ubuntu XFCE RDP Desktop | Desktop | 3389 | - |
| `rstudio` | RStudio Server | IDE | 8787 | - |
| `signal-desktop` | Signal Private Messenger | Productivity | 6080 | - |
| `snake` | Snake | Game | 80 | - |
| `stirling-pdf` | Stirling PDF | Tool | 8080 | - |
| `tetris` | Tetris | Game | 80 | - |
| `thelounge` | The Lounge (LinuxServer) | Tool | 9000 | - |
| `tor-browser` | Tor-Browser | Browser | 6901 | - |
| `trilium-notes` | Trilium Notes | Productivity | 8080 | - |
| `ttyd` | ttyd Web Terminal | Tool | 7681 | - |
| `vscodium` | VSCodium (LinuxServer) | IDE | 3000 | - |
| `webtop-alpine-kde` | Alpine KDE Desktop | Desktop | 3000 | - |
| `webtop-arch-kde` | Arch Linux KDE Desktop | Desktop | 3000 | - |
| `webtop-ubuntu-xfce` | Ubuntu XFCE Desktop | Desktop | 3000 | - |
| `wordle` | Wordle | Game | 80 | - |
| `zeppelin` | Apache Zeppelin | IDE | 8080 | - |

"Example" marks the curated subset installed by default by the
`kube-workspaces/deploy` Helm chart. See
[Curated examples](CONTRIBUTING.md#curated-examples).

Craft Apps supports both `container` (StatefulSet) and `scratch` (Deployment)
workspace types in one Image CR. Its application container is not a bootable
KubeVirt containerDisk, so it does not support `vm`. The proxy connects to HTTP
port 3000 with a workspace-specific `SUBFOLDER`; browser access must use HTTPS
for Selkies' media APIs. User files and settings live in `/config`; mount
persistent storage there when they need to survive pod replacement.

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
| `defaultCommand` | []string | Explicit container entrypoint; required for injected initialization unless supplied by the workspace |
| `defaultContainerInit` | {mode} | Opt-in `injected` or `baked-in` initialization for container/scratch; omitted or `disabled` preserves startup |
| `defaultEnv` | []{name,value} | Env vars; supports `{{namespace}}`/`{{name}}` placeholders |
| `defaultCredentials` | {username,password} | Default login shown in the UI |
| `defaultUser` / `defaultHomedir` / `defaultShell` | string | Shell/exec session defaults |
| `defaultPassword` | string | Default password for `defaultUser` (only set when there is a known default) |
| `defaultCloudInit` | bool | Image has cloud-init baked in; lets user-data be seeded at first boot |
| `defaultUserData` | string | Cloud-config for VM guests or explicitly enabled container initialization; container defaults are snapshotted at creation |
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

### Injected Alpine initialization example

`images/alpine-container-init.yaml` uses stock `alpine:3.22` and supports both
container and scratch workspaces. It installs curl, writes
`/etc/container-init-demo.txt`, records curl's version in
`/run/container-init-demo-curl.txt` and creates
`/run/container-init-demo-ready` before execing `sleep infinity`. Use terminal
access to inspect those files; port 80 is a schema placeholder, not an HTTP app.

Requires the matching controller/API/CRDs and an operator-configured immutable
container-init installer image (`controller.containerInitImage` in Helm or
`KW_CONTAINER_INIT_IMAGE` for the controller). The installer copies a static
binary into a shared volume; initialization runs in the main container.
`defaultUserData` alone does not enable it, and `defaultCloudInit` is not used.
See [container initialization](https://github.com/kube-workspaces/deploy/blob/main/docs/container-init.md)
for setup, direct Workspace examples, lifecycle and Secret-reference behavior.

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
