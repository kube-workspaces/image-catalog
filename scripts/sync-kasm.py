#!/usr/bin/env python3
"""Refresh Kasm CRs from public metadata (requires PyYAML, crane and upstream clones).

Usage: python scripts/sync-kasm.py /path/to/workspaces-core-images /path/to/workspaces-images
Existing resource names, image references, example annotations and runtime
settings are preserved. New images use the newest published stable tag, a
versioned rolling tag, or develop when upstream has no versioned release yet.
"""

import concurrent.futures
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "https://registry.kasmweb.com/1.1/"
HUB = "https://hub.docker.com/v2/repositories/kasmweb/"
# Infrastructure, plugins, build utilities and headless CLI images are not
# browser-accessible workspace images from the two upstream image libraries.
NON_WORKSPACES = set("""
agent agent-api agent-operator api appserver browser-cdp claude-code codex-cli
egress-cni egress-daemon forward-proxy gemini-cli kasm-apps kasm-guac kasm-helm
kasm-logging-plugin kasm-network-plugin kasm-overlayfs kasm_workspace_builder_util
manager nginx nginx-sidecar postgres proxy rdp-gateway rdp-https-gateway
redirector seccomp-installer share squid squid-proxy video-device-plugin
webfilter-sidecar workspaces
""".split())
NAMES = {
    "desktop": "Ubuntu Desktop", "desktop-deluxe": "Ubuntu Desktop Deluxe",
    "java-dev": "Java Development", "atom": "Atom", "teams": "Teams",
    "openoffice": "OpenOffice", "angelfish": "Angelfish", "anydesk": "AnyDesk",
    "bitwarden": "Bitwarden", "cursor": "Cursor", "google-earth": "Google Earth",
    "realvnc-vncviewer": "RealVNC VNC Viewer", "vmware-horizon": "VMware Horizon",
    "zsnes": "ZSNES", "kasmos": "KasmOS", "cuda": "CUDA Development Toolkit",
    "nvidia": "NVIDIA", "remnux": "REMnux", "ubuntu": "Ubuntu",
    "debian": "Debian", "alpine": "Alpine", "fedora": "Fedora",
    "oracle": "Oracle Linux", "opensuse": "OpenSUSE Leap", "centos": "CentOS",
    "almalinux": "AlmaLinux", "rockylinux": "Rocky Linux", "rhel": "RHEL",
    "parrotos": "Parrot OS", "kali": "Kali Linux",
    "ubuntu-jammy-desktop-ai-dev": "Ubuntu AI Dev",
    "ubuntu-noble-anythingllm": "AnythingLLM", "ubuntu-noble-easydiffusion": "Easy Diffusion",
    "ubuntu-noble-ml-engineering": "ML Engineering", "ubuntu-noble-n8n": "n8n",
    "ubuntu-noble-nvidia": "Ubuntu Noble NVIDIA",
    "ubuntu-jammy-nvidia": "Ubuntu Jammy NVIDIA",
    "ubuntu-noble-nvidia-pytorch": "Ubuntu Noble NVIDIA PyTorch",
    "ubuntu-noble-nvidia-tensorflow": "Ubuntu Noble NVIDIA TensorFlow",
}
ICONS = {
    "desktop": REGISTRY + "icons/ubuntu.png",
    "desktop-deluxe": REGISTRY + "icons/ubuntu.png",
    "java-dev": "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/java.svg",
    "teams": "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/microsoft-teams.svg",
    "centos-7-desktop": "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/centos.svg",
    "core-centos-7": "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/centos.svg",
}


def fetch(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return json.load(response)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def friendly(repo):
    if repo in NAMES:
        return NAMES[repo]
    parts = repo.removeprefix("core-").removesuffix("-desktop").split("-")
    title = NAMES.get(parts[0], parts[0].title())
    rest = parts[1:]
    if parts[0] == "alpine" and rest:
        rest[0] = rest[0][0] + "." + rest[0][1:]
    title = " ".join([title] + [x.title() for x in rest])
    return "Core " + title if repo.startswith("core-") else title


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    clones = {"core": Path(sys.argv[1]), "desktop": Path(sys.argv[2])}
    configs = {
        group: yaml.safe_load((clone / "ci-scripts/template-vars.yaml").read_text())
        for group, clone in clones.items()
    }
    source_files = {}
    for config in configs["desktop"].values():
        if isinstance(config, list):
            for entry in config:
                if isinstance(entry, dict) and "name" in entry and "dockerfile" in entry:
                    source_files[entry["name"]] = entry["dockerfile"]
    for config in configs["core"].values():
        if isinstance(config, list):
            for entry in config:
                if isinstance(entry, dict) and "name1" in entry:
                    name = "core-" + entry["name1"]
                    if entry["name2"] != entry["name1"]:
                        name += "-" + str(entry["name2"])
                    source_files[name] = entry["dockerfile"]

    registry = fetch(REGISTRY + "list.json")
    workspaces = {
        w["compatibility"][-1]["image"].split(":")[0].split("/")[-1]: w
        for w in registry["workspaces"]
    }
    # The Hub caps pages at 100. Opposite alphabetical order covers the current
    # namespace without depending on its intermittently inaccessible page=2 URL.
    repositories = {}
    for ordering in ("name", "-name"):
        page = fetch(HUB + "?page_size=100&ordering=" + ordering)
        repositories.update((r["name"], r) for r in page["results"])
    if len(repositories) != page["count"]:
        raise RuntimeError("Docker Hub inventory is incomplete; update pagination")
    selected = sorted(set(repositories) - NON_WORKSPACES)
    missing = set(workspaces) - set(selected)
    if missing:
        raise RuntimeError(f"Registry workspaces missing from Docker Hub inventory: {missing}")

    existing = {}
    for path in (ROOT / "images").rglob("*.yaml"):
        document = yaml.safe_load(path.read_text())
        ref = document["spec"]["image"]
        if ref.startswith("kasmweb/"):
            repo = ref.split(":")[0].split("/")[-1]
            if repo in existing:
                raise RuntimeError(f"Multiple existing CRs for {repo}")
            existing[repo] = (path, document)

    def published_tags(repo):
        data = fetch(HUB + repo + "/tags/?page_size=100")
        tags = [t["name"] for t in data["results"]]
        if not tags:
            return repo, None
        stable = [t for t in tags if re.fullmatch(r"\d+\.\d+\.\d+", t)]
        if stable:
            return repo, max(stable, key=lambda t: tuple(map(int, t.split("."))))
        rolling = [t for t in tags if re.fullmatch(r"\d+\.\d+\.\d+-rolling-daily", t)]
        if rolling:
            return repo, max(rolling, key=lambda t: tuple(map(int, t.split("-")[0].split("."))))
        for fallback in ("develop", "develop-rolling", "latest"):
            if fallback in tags:
                return repo, fallback
        raise RuntimeError(f"No stable or development tag found for {repo}: {tags}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        tags = dict(pool.map(published_tags, selected))
    unpublished = [repo for repo in selected if tags[repo] is None]
    selected = [repo for repo in selected if tags[repo] is not None]
    if unpublished:
        print("Skipped repositories with no published tags: " + ", ".join(unpublished))

    def image_config(repo):
        ref = existing[repo][1]["spec"]["image"] if repo in existing else "kasmweb/" + repo + ":" + tags[repo]
        result = subprocess.run(["crane", "config", ref], check=True, capture_output=True, text=True)
        config = json.loads(result.stdout)["config"]
        if "6901/tcp" not in config.get("ExposedPorts", {}):
            raise RuntimeError(f"{ref} does not expose the expected KasmVNC endpoint")
        return repo, dict(e.split("=", 1) for e in config.get("Env", []))

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        image_env = dict(pool.map(image_config, selected))

    # Reuse Kasm's official OS icons for core and historical distro variants.
    family_icons = {}
    for repo, w in workspaces.items():
        family_icons.setdefault(repo.split("-")[0], w["image_src"])
    family_icons.update(cuda="nvidia.png", nvidia="nvidia.png", ubuntu="ubuntu.png", remnux="remnux.png")
    records = []
    for repo in selected:
        group = "core" if repo.startswith("core-") else "desktop"
        w = workspaces.get(repo, {})
        old_path, document = existing.get(repo, (None, {
            "apiVersion": "kubeworkspaces.io/v1alpha1", "kind": "Image",
            "metadata": {"name": "kasmweb-" + repo}, "spec": {},
        }))
        spec = document["spec"]
        config_env = image_env[repo]
        spec.setdefault("image", "kasmweb/" + repo + ":" + tags[repo])
        spec.setdefault("defaultCredentials", {"username": "kasm_user", "password": "password"})
        spec.setdefault("defaultEnv", [{"name": "VNC_PW", "value": "password"}])
        run = w.get("run_config", {})
        env = {e["name"] for e in spec["defaultEnv"]}
        if group == "core" and config_env.get("START_XFCE4") == "0" and "START_XFCE4" not in env:
            spec["defaultEnv"].append({"name": "START_XFCE4", "value": "1"})
        for key, value in run.get("environment", {}).items():
            if key not in env:
                spec["defaultEnv"].append({"name": key, "value": str(value)})
        spec.setdefault("defaultPath", "/")
        spec["defaultPort"] = int(config_env.get("NO_VNC_PORT", "6901"))
        spec.setdefault("defaultSharedMemory", True)
        spec.setdefault("defaultUser", "root" if run.get("user") == "root" else "kasm_user")
        # The HTTP login is kasm_user; the Linux user's home has a hyphen.
        spec["defaultHomedir"] = "/root" if spec["defaultUser"] == "root" else config_env.get("HOME", "/home/kasm-user")
        spec["defaultShell"] = config_env.get("SHELL", "/bin/bash")
        if run.get("privileged") or "-dind" in repo or repo == "redroid":
            spec["privileged"] = True
        spec.setdefault("proxyConfig", {})
        for key, value in {
            "needsNoopSW": True, "rewriteHostAbsolutePaths": True,
            "scheme": "https", "tlsSkipVerify": True, "websocketPaths": ["/websockify"],
        }.items():
            spec["proxyConfig"].setdefault(key, value)
        if "rolling" in spec["image"] or spec["image"].endswith((":develop", ":latest")):
            spec["defaultImagePullPolicy"] = "Always"
        spec["displayName"] = w.get("friendly_name", friendly(repo))
        description = w.get("description") or repositories[repo].get("description", "").strip()
        if not description:
            desc_path = clones[group] / "docs" / repo / "description.txt"
            if desc_path.exists():
                description = desc_path.read_text().strip()
        spec["description"] = " ".join((description or f"{spec['displayName']} workspace streamed via KasmVNC.").split())
        categories = w.get("categories", [])
        if group == "core" or "-desktop" in repo or repo in ("desktop", "desktop-deluxe") or "-dind" in repo or repo.startswith("ubuntu-"):
            category = "Desktop"
        elif repo in ("chrome", "chromium", "firefox", "brave", "edge", "vivaldi", "tor-browser", "angelfish"):
            category = "Browser"
        elif repo in ("doom", "steam", "minetest", "retroarch", "super-tux-kart", "zsnes"):
            category = "Game"
        elif repo in ("vs-code", "atom", "sublime-text", "java-dev", "cursor", "unityhub"):
            category = "IDE"
        else:
            category = "Productivity" if "Productivity" in categories else "Tool"
        spec["category"] = category
        spec["tags"] = sorted(set(spec.get("tags", []) + ["kasm", "kasmvnc", "linux", group] + [c.lower() for c in categories]))
        spec["homepageURL"] = "https://kasm.com/images"
        spec["imageHomepageURL"] = "https://hub.docker.com/r/kasmweb/" + repo
        family = repo.removeprefix("core-").split("-")[0]
        icon = w.get("image_src", family_icons.get(family))
        spec["icon"] = ICONS.get(repo) or (REGISTRY + "icons/" + icon if icon else "https://kasm.com/assets/images/logo.svg")
        source_repo = "workspaces-core-images" if group == "core" else "workspaces-images"
        spec["sourceURL"] = "https://github.com/kasmtech/" + source_repo
        if repo in source_files:
            spec["sourceURL"] += "/blob/develop/" + source_files[repo]
        destination = ROOT / "images/kasm" / group / (document["metadata"]["name"] + ".yaml")
        if old_path and old_path != destination:
            raise RuntimeError(f"Move {old_path} to {destination} before syncing")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=88))
        records.append((repo, document))

    for group, clone in clones.items():
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=clone, text=True).strip()
        print(f"{group} source revision: {revision}")
    print(f"Generated {len(records)} Kasm CRs ({sum(r.startswith('core-') for r, _ in records)} core).")
    print("Excluded non-workspace repositories: " + ", ".join(sorted(set(repositories) & NON_WORKSPACES)))
    update_readme()


def update_readme():
    readme = ROOT / "README.md"
    text = readme.read_text()
    start = text.index("| Name | Display Name | Category | Port | Example |")
    end = text.index('\n\n"Example"', start)
    documents = [yaml.safe_load(p.read_text()) for p in (ROOT / "images").rglob("*.yaml")]
    rows = ["| Name | Display Name | Category | Port | Example |",
            "|------|---------------|----------|------|---------|"]
    for doc in sorted(documents, key=lambda d: d["metadata"]["name"]):
        meta, spec = doc["metadata"], doc["spec"]
        example = "✓" if str(meta.get("annotations", {}).get("catalog.kubeworkspaces.io/example")).lower() == "true" else "-"
        rows.append(f"| `{meta['name']}` | {spec.get('displayName', meta['name'])} | {spec.get('category', '')} | {spec['defaultPort']} | {example} |")
    readme.write_text(text[:start] + "\n".join(rows) + text[end:])


if __name__ == "__main__":
    main()
