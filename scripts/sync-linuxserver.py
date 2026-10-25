#!/usr/bin/env python3
"""Refresh the LinuxServer collection from upstream (requires PyYAML).

Usage: python scripts/sync-linuxserver.py --cache-dir /tmp/linuxserver-metadata
The cache stores the API inventory, Docker Hub inventory, upstream readme-vars
and icon checks. Remove individual cache files to refresh them. Existing resource
names, image references, example annotations and application-specific defaults
are retained. Review upstream requirements and the generated diff before use.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import html
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parents[1]
API = "https://api.linuxserver.io/api/v1/images?include_deprecated=true"
HUB = "https://hub.docker.com/v2/repositories/linuxserver/?page_size=100"
LOGO = "https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/linuxserver-ls-logo.png"
# Mods are filesystem overlays consumed by docker-mods, not bootable root filesystems.
EXCLUDED = {"mods": "Docker Mods overlays, not runnable container root filesystems"}
NAMES = {
    "adguardhome-sync": "AdGuard Home Sync", "airsonic-advanced": "Airsonic Advanced",
    "apprise-api": "Apprise API", "audiosilo": "AudioSilo", "babybuddy": "Baby Buddy",
    "bambustudio": "Bambu Studio", "bitcoin-knots": "Bitcoin Knots",
    "blade-of-agony": "Blade of Agony", "boinc": "BOINC", "bookstack": "BookStack",
    "calibre-web": "Calibre-Web", "calligra": "Calligra", "changedetection.io": "changedetection.io",
    "chrome": "Google Chrome", "chromium": "Chromium", "ci": "LinuxServer CI",
    "ci-debug": "LinuxServer CI Debug", "cloud9": "Cloud9", "code-server": "code-server",
    "codimd": "CodiMD", "cops": "COPS", "couchpotato": "CouchPotato",
    "craft-apps": "Craft Apps (ArtCraft)", "daapd": "DAAPd", "darktable": "darktable",
    "ddclient": "DDClient", "digikam": "digiKam", "diskover": "Diskover",
    "docker-compose": "Docker Compose", "dokuwiki": "DokuWiki",
    "doplarr_rs": "Doplarr RS", "dosbox-staging": "DOSBox Staging",
    "doublecommander": "Double Commander", "duckdns": "DuckDNS", "duckstation": "DuckStation",
    "emulatorjs": "EmulatorJS", "embystat": "EmbyStat", "ffmpeg": "FFmpeg",
    "filezilla": "FileZilla", "flexget": "FlexGet", "foldingathome": "Folding@home",
    "freecad": "FreeCAD", "freetube": "FreeTube", "freshrss": "FreshRSS", "gimp": "GIMP",
    "github-desktop": "GitHub Desktop", "gitqlient": "GitQlient", "grocy": "grocy",
    "gzdoom": "GZDoom", "habridge": "HA Bridge", "handbrake": "HandBrake",
    "healthchecks": "Healthchecks", "hedgedoc": "HedgeDoc", "hishtory-server": "hiSHtory Server",
    "homeassistant": "Home Assistant", "htpcmanager": "HTPC Manager",
    "intellij-idea": "IntelliJ IDEA", "ipfs": "IPFS", "joplin": "Joplin",
    "kali-linux": "Kali Linux", "kasm": "Kasm Workspaces", "kdenlive": "Kdenlive",
    "keepassxc": "KeePassXC", "kicad": "KiCad", "ldap-auth": "LDAP Auth",
    "libreoffice": "LibreOffice", "librespeed": "LibreSpeed", "librewolf": "LibreWolf",
    "lm-studio": "LM Studio", "lsio-api": "LinuxServer API", "mame": "MAME",
    "mariadb": "MariaDB", "mcmyadmin2": "McMyAdmin 2", "mediaelch": "MediaElch",
    "melonds": "melonDS", "minisatip": "minisatip", "msedge": "Microsoft Edge",
    "mstream": "mStream", "mullvad-browser": "Mullvad Browser", "mylar3": "Mylar 3",
    "mysql": "MySQL", "mysql-workbench": "MySQL Workbench", "nano-wallet": "Nano Wallet",
    "netbootxyz": "netboot.xyz", "netbox": "NetBox", "ngircd": "ngIRCd", "nginx": "NGINX",
    "nntp2nntp": "NNTP2NNTP", "nomacs": "nomacs", "nzbget": "NZBGet",
    "nzbhydra2": "NZBHydra 2", "onlyoffice": "ONLYOFFICE", "openshot": "OpenShot",
    "openssh-server": "OpenSSH Server", "openvscode-server": "OpenVSCode Server",
    "orcaslicer": "OrcaSlicer", "oscam": "OSCam", "pairdrop": "PairDrop", "pcsx2": "PCSX2",
    "phpmyadmin": "phpMyAdmin", "piper": "Piper", "plex": "Plex", "ppsspp": "PPSSPP",
    "projectsend": "ProjectSend", "pwndrop": "pwndrop", "pycharm": "PyCharm",
    "pydio-cells": "Pydio Cells", "pyload": "pyLoad", "pyload-ng": "pyLoad NG",
    "qbittorrent": "qBittorrent", "qdirstat": "QDirStat", "qemu-static": "QEMU Static",
    "rawtherapee": "RawTherapee", "rdesktop": "RDesktop", "resilio-sync": "Resilio Sync",
    "retroarch": "RetroArch", "rpcs3": "RPCS3", "rsnapshot": "rsnapshot", "rustdesk": "RustDesk",
    "rutorrent": "ruTorrent", "sabnzbd": "SABnzbd", "scummvm": "ScummVM",
    "series-troxide": "Series Troxide", "shadps4": "shadPS4", "sickchill": "SickChill",
    "sickgear": "SickGear", "snipe-it": "Snipe-IT", "speedtest-tracker": "Speedtest Tracker",
    "sqlitebrowser": "DB Browser for SQLite", "steamos": "SteamOS", "swag": "SWAG",
    "synclounge": "SyncLounge", "syslog-ng": "syslog-ng", "thelounge": "The Lounge",
    "tvheadend": "Tvheadend", "ungoogled-chromium": "Ungoogled Chromium",
    "unifi": "UniFi", "unifi-controller": "UniFi Controller",
    "unifi-network-application": "UniFi Network Application", "unrar": "UnRAR",
    "vlc": "VLC", "vscode": "Visual Studio Code", "vscodium": "VSCodium",
    "vscodium-web": "VSCodium Web", "webcord": "WebCord", "webgrabplus": "WebGrab+Plus",
    "webstation": "Webstation", "webtop": "Webtop", "weixin": "Weixin",
    "wikijs": "Wiki.js", "winegui": "WineGUI", "wireguard": "WireGuard",
    "wireshark": "Wireshark", "wps-office": "WPS Office", "xbackbone": "XBackBone",
    "xemu": "xemu", "xvfb": "Xvfb", "yq": "yq", "your_spotify": "Your Spotify", "znc": "ZNC",
}
PORTS = {"readarr": 8787, "letsencrypt": 443, "musicbrainz": 5000,
         "socket-proxy": 2375, "lsio-api": 8000, "unifi": 8443,
         "ldap-auth": 9000, "quassel-web": 64443, "mastodon": 443,
         "chevereto": 443}
TAGS = {"python": "alpine324", "xvfb": "ubunturesolute"}
SCHEMES = {"code-server": "http", "audiosilo": "https", "kanzi": "https",
           "pydio-cells": "https", "kasm": "https"}
PATHS = {"audiosilo": "/web", "plex": "/web", "pelorus": "/pelorus/",
         "ubooquity": "/ubooquity/", "lazylibrarian": "/home",
         "pwndrop": "/pwndrop", "smokeping": "/smokeping/smokeping.cgi",
         "transmission": "/transmission/web/"}
# Only upstream-documented built-in logins, never example configurable secrets.
CREDENTIALS = {
    "airsonic": ("admin", "admin"), "airsonic-advanced": ("admin", "admin"),
    "babybuddy": ("admin", "admin"), "booksonic": ("admin", "admin"),
    "booksonic-air": ("admin", "admin"), "bookstack": ("admin@admin.com", "password"),
    "calibre-web": ("admin", "admin123"), "daapd": ("admin", "changeme"),
    "deluge": ("admin", "deluge"), "diskover": ("diskover", "darkdata"),
    "gazee": ("admin", "gazee"), "grocy": ("admin", "admin"),
    "libresonic": ("admin", "admin"), "nzbget": ("nzbget", "tegbzn6789"),
    "kodi-headless": ("kodi", "kodi"), "rdesktop": ("abc", "abc"),
    "paperless-ng": ("admin", "admin"), "paperless-ngx": ("admin", "admin"),
    "papermerge": ("admin", "admin"), "pyload": ("admin", "password"),
    "pyload-ng": ("pyload", "pyload"), "raneto": ("admin", "password"),
    "speedtest-tracker": ("admin@example.com", "password"), "znc": ("admin", "admin"),
}
ICONS = {
    "cardigann": "cardigann", "codiad": "codiad", "codimd": "hedgedoc",
    "couchpotato": "couchpotato", "foldingathome": "foldingathome",
    "ipfs": "ipfs", "nano": "nano", "nano-wallet": "nano",
    "projectsend": "projectsend", "sickgear": "sickgear", "thelounge": "thelounge",
    "webgrabplus": "webgrabplus", "wikijs": "wiki-js", "xbackbone": "xbackbone",
}
NON_HTTP = set("""build-agent guacd mariadb mysql openssh-server ngircd quassel-core
    rdesktop faster-whisper piper wireguard syslog-ng luanti minetest endlessh nntp2nntp""".split())
CLI = set("""ci ci-debug d2-builder doc-builder docker-compose ddclient doplarr doplarr_rs
    duckdns fail2ban feed2toot ffmpeg jenkins-builder kometa plex-meta-manager python
    qemu-static readme-sync rsnapshot unrar webgrabplus xvfb yq modmanager""".split())
BROWSERS = set("chrome chromium firefox brave librewolf msedge mullvad-browser opera ungoogled-chromium vivaldi zen helium".split())
IDES = set("code-server cloud9 codiad intellij-idea openvscode-server pycharm vscode vscodium vscodium-web".split())
GAMES = set("azahar blade-of-agony citron dogwalk dolphin dosbox-staging duckstation eden emulatorjs flycast gzdoom luanti mame melonds minetest modrinth pcsx2 ppsspp retroarch rpcs3 scummvm shadps4 steam steamos xemu".split())
DESKTOPS = {"webtop", "rdesktop", "kali-linux", "kasm"}
FALLBACK_DESCRIPTIONS = {
    "apache": "Apache HTTP Server with PHP support.",
    "ci-debug": "LinuxServer continuous-integration debugging utility.",
    "flood": "Flood web interface for rTorrent.",
    "kodi-headless": "Headless Kodi media library server with a web interface.",
    "mcmyadmin2": "McMyAdmin 2 web management interface for a Minecraft server.",
    "mysql": "MySQL relational database server.",
    "readarr": "Readarr ebook and audiobook collection manager.",
    "sickbeard": "Sick Beard television library and download manager.",
    "unifi": "Legacy UniFi network controller and web administration interface.",
    "ci": "LinuxServer image testing, SBOM generation and CI reporting tool.",
    "d2-builder": "LinuxServer CI tool for generating D2 diagrams from image definitions.",
    "build-agent": "SSH-accessible LinuxServer build agent with Docker-in-Docker.",
    "doc-builder": "LinuxServer CI documentation build utility.",
}


def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code in (403, 404) or attempt == 2:
                raise
        except OSError:
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def clean(text, name):
    text = re.sub(r"{{\s*project_name(?:\|\w+)?\s*}}", NAMES.get(name, name), text)
    text = re.sub(r"{{\s*project_url\s*}}", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(html.unescape(text).replace("**", "").replace("`", "").split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args()
    cache = args.cache_dir
    cache.mkdir(parents=True, exist_ok=True)

    def cached(filename, url):
        path = cache / filename
        if not path.exists():
            path.write_bytes(fetch(url))
        return path.read_text()

    inventory = json.loads(cached("inventory.json", API))
    api = {r["name"]: r for r in inventory["data"]["repositories"]["linuxserver"]}
    hub_path = cache / "hub.json"
    if not hub_path.exists():
        hub, url = {}, HUB
        while url:
            page = json.loads(fetch(url))
            hub.update((r["name"], r) for r in page["results"])
            url = page["next"]
        if len(hub) != page["count"]:
            raise RuntimeError("Incomplete Docker Hub inventory")
        hub_path.write_text(json.dumps(hub))
    hub = json.loads(hub_path.read_text())
    selected = sorted((set(api) | set(hub)) - set(EXCLUDED))

    def metadata(name):
        path = cache / (name + ".yml")
        if not path.exists():
            for branch in ("master", "main"):
                try:
                    path.write_bytes(fetch(f"https://raw.githubusercontent.com/linuxserver/docker-{name}/{branch}/readme-vars.yml"))
                    break
                except urllib.error.HTTPError as error:
                    if error.code != 404:
                        raise
        values = yaml.safe_load(path.read_text()) if path.exists() else {}
        return name, values

    with ThreadPoolExecutor(max_workers=8) as pool:
        values = dict(pool.map(metadata, selected))

    # Check actual upstream assets rather than guessing application icon filenames.
    icon_path = cache / "icons.json"
    icons = json.loads(icon_path.read_text()) if icon_path.exists() else {}

    def icon_check(url):
        if url in icons:
            return url, icons[url]
        try:
            raw = fetch(url)
            valid = bool(raw) and (raw.startswith((b"\x89PNG", b"\xff\xd8", b"GIF", b"RIFF")) or b"<svg" in raw[:1000])
        except (OSError, urllib.error.HTTPError):
            valid = False
        return url, valid

    replacements = {n: f"https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/{icon}.svg" for n, icon in ICONS.items()}
    logos = {r.get("project_logo") or values[n].get("project_logo") or LOGO
             for n, r in ((n, api.get(n, {})) for n in selected)} | {LOGO}
    logos.update(replacements.values())
    with ThreadPoolExecutor(max_workers=12) as pool:
        icons.update(pool.map(icon_check, sorted(logos)))
    icon_path.write_text(json.dumps(icons, indent=2) + "\n")
    if not icons[LOGO]:
        raise RuntimeError("LinuxServer fallback logo is unavailable")

    existing = {}
    for path in (ROOT / "images").rglob("*.yaml"):
        doc = yaml.safe_load(path.read_text())
        ref = doc["spec"]["image"]
        if ref.startswith(("linuxserver/", "lscr.io/linuxserver/")):
            existing[ref] = (path, doc)
    folder = ROOT / "images/linuxserver"
    folder.mkdir(exist_ok=True)
    rows = []
    for name in selected:
        r, v = api.get(name, {}), values[name]
        status = "deprecated" if r.get("deprecated") else "maintained" if name in api else "Hub-only"
        title = NAMES.get(name, name.replace("-", " ").replace("_", " ").title())
        description = clean(r.get("description") or v.get("project_blurb") or FALLBACK_DESCRIPTIONS.get(name, title + " container from LinuxServer.io."), name)
        if len(description) > 400:
            description = description[:397].rsplit(" ", 1)[0] + "..."
        ports = []
        for p in (v.get("param_ports") or []) + (v.get("opt_param_ports") or []):
            raw, _, protocol = str(p["internal_port"]).partition("/")
            # Kubernetes needs individual ports, not Docker's port-range syntax.
            first, _, last = raw.partition("-")
            for number in range(int(first), int(last or first) + 1):
                item = (number, (protocol or "tcp").upper(), p["port_desc"])
                if item[:2] not in [x[:2] for x in ports]:
                    ports.append(item)
        if not ports:
            dockerfile = cache / (name + ".Dockerfile")
            if not dockerfile.exists():
                try:
                    dockerfile.write_bytes(fetch(f"https://raw.githubusercontent.com/linuxserver/docker-{name}/master/Dockerfile"))
                except urllib.error.HTTPError as error:
                    if error.code != 404:
                        raise
            if dockerfile.exists():
                for line in re.findall(r"(?m)^EXPOSE\s+(.+)", dockerfile.read_text()):
                    for port in re.findall(r"\b(\d+)(?:/(tcp|udp))?\b", line):
                        ports.append((int(port[0]), (port[1] or "tcp").upper(), "Dockerfile EXPOSE"))
        default = PORTS.get(name, ports[0][0] if ports else 80)
        if name == "plex":
            default = 32400
        desktop = bool(v.get("selkies_blurb") or v.get("kasmvnc_blurb"))
        no_http = name in NON_HTTP or name in CLI
        if not ports and name not in PORTS:
            no_http = True
        if name == "pelorus":
            desktop = True
        category = "Browser" if name in BROWSERS else "IDE" if name in IDES else "Game" if name in GAMES else "Desktop" if name in DESKTOPS else "Tool"
        tags = ["linuxserver", "linux"] + [s.strip().lower().replace(" ", "-") for s in (r.get("category") or v.get("project_categories") or "").split(",") if s.strip()]
        if status != "maintained":
            tags.append(status.lower())
            description = ("Deprecated by LinuxServer.io. " if status == "deprecated" else "Legacy or infrastructure image available on Docker Hub. ") + description
        if no_http:
            tags.append("cli" if name in CLI else "non-http")
            description += " No browser endpoint; use the terminal or native client."
        logo = r.get("project_logo") or v.get("project_logo") or LOGO
        if not icons.get(logo) and icons.get(replacements.get(name)):
            logo = replacements[name]
        spec = {
            "defaultPath": PATHS.get(name, "/"),
            "defaultPort": default, "description": description, "category": category,
            "tags": list(dict.fromkeys(tags)), "displayName": title + " (LinuxServer)",
            "homepageURL": r.get("project_url") or v.get("project_url") or f"https://hub.docker.com/r/linuxserver/{name}",
            "icon": logo if icons.get(logo) else LOGO,
            "image": f"linuxserver/{name}:" + ("latest" if not r.get("tags") or any(t["tag"] == "latest" for t in r["tags"]) else r["tags"][0]["tag"]),
            "imageHomepageURL": f"https://hub.docker.com/r/linuxserver/{name}",
            "workspaceTypes": ["container", "scratch"],
        }
        if name in TAGS:
            spec["image"] = f"linuxserver/{name}:{TAGS[name]}"
        if r.get("github_url") or v or (cache / (name + ".Dockerfile")).exists():
            spec["sourceURL"] = r.get("github_url") or f"https://github.com/linuxserver/docker-{name}"
        extras = [{"name": f"{protocol.lower()}-{port}", "port": port, "protocol": protocol}
                  for port, protocol, _ in ports if (port, protocol) != (default, "TCP")]
        if extras:
            spec["additionalPorts"] = extras
        if not no_http:
            spec["proxyConfig"] = {"needsNoopSW": True, "rewriteHostAbsolutePaths": True}
            primary = next((p for p in ports if p[0] == default), None)
            scheme = SCHEMES.get(name, "https" if default in (443, 8443, 64443) or (primary and "https" in primary[2].lower() and default != 3000) else "http")
            if scheme == "https":
                spec["proxyConfig"].update(scheme="https", tlsSkipVerify=True)
        if name in CREDENTIALS:
            username, password = CREDENTIALS[name]
            spec["defaultCredentials"] = {"username": username, "password": password}
        if desktop:
            spec["defaultSharedMemory"] = True
            spec["defaultEnv"] = [{"name": "SUBFOLDER", "value": "/proxy/{{namespace}}/{{name}}/"}]
            spec["proxyConfig"]["preservePathPrefix"] = True
            spec["defaultUser"] = "abc"
            spec["defaultHomedir"] = "/config"
        if name == "rdesktop":
            spec.update(defaultUser="abc", defaultHomedir="/config", defaultPassword="abc", defaultSharedMemory=True)
        if v.get("privileged") or name in ("qemu-static", "build-agent"):
            spec["privileged"] = True
        # Keep existing catalog identities and deliberate runtime configuration.
        ref = spec["image"]
        resource = "linuxserver-" + re.sub(r"[^a-z0-9-]", "-", name)
        if ref in existing:
            path, doc = existing[ref]
            old = doc["spec"]
            for key in ("defaultArgs", "defaultEnv", "defaultUser", "defaultHomedir", "defaultShell", "defaultPassword", "defaultCredentials", "defaultUID", "defaultInitContainers", "privileged"):
                if key in old:
                    spec[key] = old[key]
            if not doc["metadata"]["name"].startswith("linuxserver-") and "proxyConfig" in old:
                spec["proxyConfig"] = old["proxyConfig"]
            doc["spec"] = spec
        else:
            path = folder / (resource + ".yaml")
            doc = {"apiVersion": "kubeworkspaces.io/v1alpha1", "kind": "Image", "metadata": {"name": resource}, "spec": spec}
        path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=88))
        required = [e["env_var"] for e in v.get("param_env_vars") or [] if e["env_var"] not in ("TZ", "PUID", "PGID")]
        devices = [d["device_path"] for d in v.get("param_devices") or []]
        notes = []
        if required:
            notes.append("Configure env: " + ", ".join(required))
        if devices:
            notes.append("Devices: " + ", ".join(devices))
        if v.get("param_usage_include_net") is True:
            notes.append("Upstream uses " + str(v.get("param_net", "host")) + " networking")
        if v.get("cap_add_param"):
            notes.append("Additional capabilities; see upstream setup")
        if spec.get("privileged"):
            notes.append("Privileged container")
        if name in ("socket-proxy", "ci", "ci-debug", "jenkins-builder", "docker-compose", "modmanager", "readme-sync"):
            notes.append("Docker socket/daemon or upstream CI integration")
        if name == "build-agent":
            notes.append("Configure PUBLIC_KEY for SSH access")
        if name == "qemu-static":
            notes.append("Host binfmt_misc registration, not a guest VM")
        if name in CLI:
            notes.append("CLI/background utility; configure arguments or config files")
        if default == 80 and not ports and name not in PORTS:
            notes.append("Port 80 is a schema placeholder; no listening port")
        rows.append((name, doc["metadata"]["name"], status, str(default), "native/terminal" if no_http else "HTTPS" if spec.get("proxyConfig", {}).get("scheme") == "https" else "HTTP", "; ".join(notes) or "See upstream application setup"))

    readme = """# LinuxServer.io image collection

One Image CR per LinuxServer repository, plus the catalog's pre-existing pinned
and desktop variants. Resource names and image references of existing entries
are retained when moving them into this folder.

## Sources and coverage

Inventory checked on {date}: **{active} maintained**, **{deprecated} deprecated**
entries from the [LinuxServer API]({api}), combined with **{hub} Docker Hub
repositories**. All {total} distinct repositories are accounted for below,
except `mods`: Docker Mods are overlays, not runnable container root filesystems.
Hub-only entries include older images and internal build tools; that label does
not assert that an image is maintained. `deprecated` is taken from the API.

Descriptions, project URLs, categories and logos come from LinuxServer's API
and each image's `readme-vars.yml`. Ports are **internal container ports**,
including documented optional TCP/UDP ports. Custom-readme images use their
Dockerfile EXPOSE declarations or explicitly reviewed application ports.
Icons are checked for an image response; unavailable assets use LinuxServer's
logo or a verified Dashboard Icons replacement. Project source links and registry
links are recorded separately in each CR. Registry manifest checks confirmed every
reference is published; `python:alpine324` and `xvfb:ubunturesolute` are used because
those repositories do not publish a `latest` tag.

## Workspace types and connection behavior

These OCI containers are offered for `container` and `scratch` workspaces.
They are not KubeVirt containerDisks; **none support `vm`**. In particular,
`qemu-static` registers CPU emulation and is not a bootable virtual machine.
Scratch selects the image root filesystem; it does not automatically reproduce
the upstream Docker entrypoint, service initialization, or host integration.

Web apps use the documented HTTP/HTTPS port; HTTPS backends with self-signed
certificates use `tlsSkipVerify`. Selkies/KasmVNC desktops use shared memory and
the workspace proxy subfolder. Native protocols (SSH, RDP, databases, IRC,
Wyoming, WireGuard, syslog and UDP game servers) require a native client or
terminal rather than browser Connect. CLI-only images have no web endpoint;
where no port exists, required `defaultPort: 80` is explicitly a placeholder.
UDP services are listed in additionalPorts with protocol UDP, since the primary
workspace port is TCP. Docker Mods itself is excluded because it has no runnable
workspace root filesystem.

## Application setup

These CRs provide image metadata and connection defaults, not a Docker Compose
deployment. Follow each project's **Application Setup** and **Parameters** in
its linked upstream README before launching. Persistent `/config`, media/data
mounts, database/Redis/MongoDB dependencies, secrets, domains, device mappings,
capabilities and host networking must be configured on the Workspace/deployment
as applicable. The Image schema cannot express all those settings. Environment
variable names below identify upstream required-parameter examples; their sample
passwords, tokens and hostnames are deliberately not installed as defaults.
LinuxServer's s6 init normally starts as root and drops application privileges;
do not set runAsUser to PUID. Configure PUID/PGID only when appropriate to mounts.

For synchronization, add `images/linuxserver` to your ImageRepository `spec.paths`;
repository synchronization does not recurse into subfolders. The build and
validation scripts do recurse. Existing curated example annotations are retained.

Refresh with `python scripts/sync-linuxserver.py --cache-dir /tmp/linuxserver-metadata`
(requires PyYAML and network access). The cache allows interrupted upstream fetches
to resume. Remove cached inventory/metadata/icon results when refreshing sources.
Review runtime-specific settings after generation, then run `make validate` and
`make build`.

## Repository inventory

| Repository | Resource name | Upstream status | Port | Connection | Setup notes |
|---|---|---|---|---|---|
""".format(date=inventory["last_updated"].split()[0], active=sum(not r["deprecated"] for r in api.values()), deprecated=sum(r["deprecated"] for r in api.values()), api=API, hub=len(hub), total=len(set(api) | set(hub)))
    readme += "\n".join("| " + " | ".join(x.replace("|", "\\|") for x in row) + " |" for row in rows) + "\n"
    readme += "\nExisting additional variants:\n\n"
    generated = {r[1] for r in rows}
    for path in sorted(folder.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        if doc["metadata"]["name"] not in generated:
            doc["spec"]["workspaceTypes"] = ["container", "scratch"]
            repo = doc["spec"]["image"].split("/")[-1].split(":")[0]
            logo = api.get(repo, {}).get("project_logo") or values.get(repo, {}).get("project_logo") or LOGO
            doc["spec"]["icon"] = logo if icons.get(logo) else LOGO
            doc["spec"]["tags"] = list(dict.fromkeys(["linuxserver"] + doc["spec"].get("tags", [])))
            if doc["spec"]["image"].startswith("linuxserver/rdesktop:"):
                # RDesktop publishes native XRDP; it does not bundle Guacamole.
                doc["spec"]["defaultPort"] = 3389
                doc["spec"]["description"] = "Ubuntu XFCE desktop with native RDP access on port 3389. Deprecated by LinuxServer.io; use an RDP client rather than browser Connect."
                doc["spec"]["tags"] = ["linuxserver", "linux", "desktop", "rdp", "deprecated", "non-http"]
                doc["spec"]["defaultCredentials"] = {"username": "abc", "password": "abc"}
                doc["spec"]["defaultPassword"] = "abc"
                doc["spec"].pop("proxyConfig", None)
                doc["spec"].pop("defaultEnv", None)
            path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=88))
            readme += f"- `{doc['metadata']['name']}`: `{doc['spec']['image']}`\n"
    (folder / "README.md").write_text(readme)

    # The root table covers nested collections, matching the Kasm importer.
    path = ROOT / "README.md"
    text = path.read_text()
    start = text.index("| Name | Display Name | Category | Port | Example |")
    end = text.index("\n\n", start)
    documents = [yaml.safe_load(p.read_text()) for p in (ROOT / "images").rglob("*.yaml")]
    table = "| Name | Display Name | Category | Port | Example |\n|------|---------------|----------|------|---------|\n"
    for d in sorted(documents, key=lambda d: d["metadata"]["name"]):
        m, s = d["metadata"], d["spec"]
        example = "✓" if str(m.get("annotations", {}).get("catalog.kubeworkspaces.io/example", "false")).lower() == "true" else "-"
        table += f"| `{m['name']}` | {s.get('displayName', m['name'])} | {s.get('category', '')} | {s['defaultPort']} | {example} |\n"
    path.write_text(text[:start] + table.rstrip() + text[end:])
    print(f"Wrote {len(rows)} repository entries; {len(list(folder.glob('*.yaml')))} total LinuxServer CRs")
    print("Unavailable upstream logos:", ", ".join(url for url in sorted(logos) if not icons.get(url)))


if __name__ == "__main__":
    main()
