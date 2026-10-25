# LinuxServer.io image collection

One Image CR per LinuxServer repository, plus the catalog's pre-existing pinned
and desktop variants. Resource names and image references of existing entries
are retained when moving them into this folder.

## Sources and coverage

Inventory checked on 2026-10-25: **203 maintained**, **21 deprecated**
entries from the [LinuxServer API](https://api.linuxserver.io/api/v1/images?include_deprecated=true), combined with **293 Docker Hub
repositories**. All 293 distinct repositories are accounted for below,
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
| adguardhome-sync | linuxserver-adguardhome-sync | maintained | 8080 | HTTP | See upstream application setup |
| airsonic | linuxserver-airsonic | Hub-only | 4040 | HTTP | See upstream application setup |
| airsonic-advanced | linuxserver-airsonic-advanced | maintained | 4040 | HTTP | See upstream application setup |
| altus | linuxserver-altus | maintained | 3000 | HTTP | See upstream application setup |
| apache | linuxserver-apache | Hub-only | 80 | HTTP | See upstream application setup |
| apprise-api | linuxserver-apprise-api | maintained | 8000 | HTTP | See upstream application setup |
| ardour | linuxserver-ardour | maintained | 3000 | HTTP | See upstream application setup |
| audacity | linuxserver-audacity | maintained | 3000 | HTTP | See upstream application setup |
| audiosilo | linuxserver-audiosilo | maintained | 8080 | HTTPS | See upstream application setup |
| azahar | linuxserver-azahar | maintained | 3000 | HTTP | See upstream application setup |
| babybuddy | linuxserver-babybuddy | maintained | 8000 | HTTP | Configure env: CSRF_TRUSTED_ORIGINS |
| bambustudio | linuxserver-bambustudio | maintained | 3000 | HTTP | See upstream application setup |
| bazarr | linuxserver-bazarr | maintained | 6767 | HTTP | See upstream application setup |
| beets | linuxserver-beets | maintained | 8337 | HTTP | See upstream application setup |
| bitcoin-knots | linuxserver-bitcoin-knots | maintained | 3000 | HTTP | See upstream application setup |
| blade-of-agony | linuxserver-blade-of-agony | maintained | 3000 | HTTP | See upstream application setup |
| blender | linuxserver-blender | maintained | 3000 | HTTP | See upstream application setup |
| boinc | linuxserver-boinc | maintained | 8080 | HTTP | See upstream application setup |
| booksonic | linuxserver-booksonic | Hub-only | 4040 | HTTP | Configure env: CONTEXT_PATH |
| booksonic-air | linuxserver-booksonic-air | Hub-only | 4040 | HTTP | See upstream application setup |
| bookstack | linuxserver-bookstack | maintained | 80 | HTTP | Configure env: APP_URL, APP_KEY, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_DATABASE |
| brave | linuxserver-brave | maintained | 3000 | HTTP | See upstream application setup |
| budge | linuxserver-budge | deprecated | 80 | HTTP | See upstream application setup |
| build-agent | linuxserver-build-agent | Hub-only | 2222 | native/terminal | Privileged container; Configure PUBLIC_KEY for SSH access |
| calibre | linuxserver-calibre | maintained | 8080 | HTTP | See upstream application setup |
| calibre-web | linuxserver-calibre-web | maintained | 8083 | HTTP | See upstream application setup |
| calligra | linuxserver-calligra | maintained | 3000 | HTTP | See upstream application setup |
| cardigann | linuxserver-cardigann | Hub-only | 5060 | HTTP | Configure env: SOCKS_PROXY, HTTP_PROXY |
| changedetection.io | linuxserver-changedetection-io | maintained | 5000 | HTTP | See upstream application setup |
| chevereto | linuxserver-chevereto | Hub-only | 443 | HTTPS | See upstream application setup |
| chrome | linuxserver-chrome | maintained | 3000 | HTTP | See upstream application setup |
| chromium | chromium | maintained | 3000 | HTTP | See upstream application setup |
| ci | linuxserver-ci | Hub-only | 80 | native/terminal | Docker socket/daemon or upstream CI integration; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| ci-debug | linuxserver-ci-debug | Hub-only | 80 | native/terminal | Docker socket/daemon or upstream CI integration; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| citron | linuxserver-citron | deprecated | 3000 | HTTP | See upstream application setup |
| clarkson | linuxserver-clarkson | Hub-only | 3000 | HTTP | Configure env: MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, ENABLE_REGISTRATIONS |
| cloud9 | linuxserver-cloud9 | Hub-only | 8000 | HTTP | See upstream application setup |
| code-server | linuxserver-code-server | maintained | 8443 | HTTP | See upstream application setup |
| codiad | linuxserver-codiad | Hub-only | 80 | HTTP | See upstream application setup |
| codimd | linuxserver-codimd | Hub-only | 3000 | HTTP | Configure env: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME |
| cops | linuxserver-cops | maintained | 80 | HTTP | See upstream application setup |
| couchpotato | linuxserver-couchpotato | Hub-only | 5050 | HTTP | See upstream application setup |
| craft-apps | craft-apps | maintained | 3000 | HTTP | See upstream application setup |
| cura | linuxserver-cura | maintained | 3000 | HTTP | See upstream application setup |
| d2-builder | linuxserver-d2-builder | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| daapd | linuxserver-daapd | deprecated | 3689 | HTTP | Upstream uses host networking |
| darktable | linuxserver-darktable | maintained | 3000 | HTTP | See upstream application setup |
| davos | linuxserver-davos | maintained | 8080 | HTTP | See upstream application setup |
| ddclient | linuxserver-ddclient | maintained | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| deluge | linuxserver-deluge | maintained | 8112 | HTTP | See upstream application setup |
| digikam | linuxserver-digikam | maintained | 3000 | HTTP | See upstream application setup |
| dillinger | linuxserver-dillinger | Hub-only | 8080 | HTTP | See upstream application setup |
| diskover | linuxserver-diskover | maintained | 80 | HTTP | Configure env: ES_HOST, ES_PORT |
| doc-builder | linuxserver-doc-builder | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| docker-compose | linuxserver-docker-compose | Hub-only | 80 | native/terminal | Docker socket/daemon or upstream CI integration; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| dogwalk | linuxserver-dogwalk | maintained | 3000 | HTTP | See upstream application setup |
| dokuwiki | linuxserver-dokuwiki | maintained | 80 | HTTP | See upstream application setup |
| dolphin | linuxserver-dolphin | maintained | 3000 | HTTP | See upstream application setup |
| domoticz | linuxserver-domoticz | Hub-only | 8080 | HTTP | Devices: path to device |
| doplarr | linuxserver-doplarr | deprecated | 80 | native/terminal | Configure env: DISCORD__TOKEN, OVERSEERR__API, OVERSEERR__URL, RADARR__API, RADARR__URL, SONARR__API, SONARR__URL; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| doplarr_rs | linuxserver-doplarr-rs | maintained | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| dosbox-staging | linuxserver-dosbox-staging | maintained | 3000 | HTTP | See upstream application setup |
| doublecommander | linuxserver-doublecommander | maintained | 3000 | HTTP | See upstream application setup |
| duckdns | linuxserver-duckdns | maintained | 80 | native/terminal | Configure env: SUBDOMAINS, TOKEN; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| duckstation | linuxserver-duckstation | maintained | 3000 | HTTP | See upstream application setup |
| duplicati | linuxserver-duplicati | maintained | 8200 | HTTP | Configure env: SETTINGS_ENCRYPTION_KEY |
| eden | linuxserver-eden | maintained | 3000 | HTTP | See upstream application setup |
| emby | linuxserver-emby | maintained | 8096 | HTTP | See upstream application setup |
| embystat | linuxserver-embystat | Hub-only | 6555 | HTTP | See upstream application setup |
| emulatorjs | linuxserver-emulatorjs | deprecated | 3000 | HTTP | See upstream application setup |
| endlessh | linuxserver-endlessh | Hub-only | 2222 | native/terminal | See upstream application setup |
| fail2ban | linuxserver-fail2ban | maintained | 80 | native/terminal | Upstream uses host networking; Additional capabilities; see upstream setup; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| faster-whisper | linuxserver-faster-whisper | maintained | 10300 | native/terminal | See upstream application setup |
| feed2toot | linuxserver-feed2toot | deprecated | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| ferdium | linuxserver-ferdium | maintained | 3000 | HTTP | See upstream application setup |
| ffmpeg | linuxserver-ffmpeg | maintained | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| filezilla | linuxserver-filezilla | maintained | 3000 | HTTP | See upstream application setup |
| firefox | firefox | maintained | 3000 | HTTP | See upstream application setup |
| fleet | linuxserver-fleet | deprecated | 8080 | HTTP | Configure env: fleet_admin_authentication_type, fleet_database_url, fleet_database_username, fleet_database_password |
| flexget | linuxserver-flexget | maintained | 5050 | HTTP | Configure env: FG_LOG_LEVEL, FG_LOG_FILE, FG_CONFIG_FILE |
| flood | linuxserver-flood | Hub-only | 3000 | HTTP | See upstream application setup |
| flycast | linuxserver-flycast | maintained | 3000 | HTTP | See upstream application setup |
| foldingathome | linuxserver-foldingathome | maintained | 7396 | HTTPS | Configure env: ACCOUNT_TOKEN, MACHINE_NAME |
| freecad | linuxserver-freecad | maintained | 3000 | HTTP | See upstream application setup |
| freetube | linuxserver-freetube | deprecated | 3000 | HTTP | See upstream application setup |
| freshrss | linuxserver-freshrss | maintained | 80 | HTTP | See upstream application setup |
| gazee | linuxserver-gazee | Hub-only | 4242 | HTTP | See upstream application setup |
| gimp | linuxserver-gimp | maintained | 3000 | HTTP | See upstream application setup |
| github-desktop | linuxserver-github-desktop | maintained | 3000 | HTTP | Additional capabilities; see upstream setup |
| gitqlient | linuxserver-gitqlient | maintained | 3000 | HTTP | See upstream application setup |
| grav | linuxserver-grav | maintained | 80 | HTTP | See upstream application setup |
| grocy | linuxserver-grocy | maintained | 80 | HTTP | See upstream application setup |
| guacd | linuxserver-guacd | Hub-only | 4822 | native/terminal | See upstream application setup |
| gzdoom | linuxserver-gzdoom | maintained | 3000 | HTTP | See upstream application setup |
| habridge | linuxserver-habridge | maintained | 8080 | HTTP | Configure env: SEC_KEY |
| handbrake | linuxserver-handbrake | maintained | 3000 | HTTP | See upstream application setup |
| headphones | linuxserver-headphones | Hub-only | 8181 | HTTP | See upstream application setup |
| healthchecks | linuxserver-healthchecks | maintained | 8000 | HTTP | Configure env: SECRET_KEY, SITE_ROOT, SITE_NAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD |
| hedgedoc | linuxserver-hedgedoc | maintained | 3000 | HTTP | Configure env: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME, CMD_DOMAIN |
| heimdall | linuxserver-heimdall | maintained | 80 | HTTP | See upstream application setup |
| helium | linuxserver-helium | maintained | 3000 | HTTP | See upstream application setup |
| hishtory-server | linuxserver-hishtory-server | maintained | 8080 | HTTP | See upstream application setup |
| homeassistant | linuxserver-homeassistant | maintained | 8123 | HTTP | Upstream uses host networking |
| htpcmanager | linuxserver-htpcmanager | maintained | 8085 | HTTP | See upstream application setup |
| hydra | linuxserver-hydra | Hub-only | 5075 | HTTP | See upstream application setup |
| hydra2 | linuxserver-hydra2 | Hub-only | 5076 | HTTP | See upstream application setup |
| inkscape | linuxserver-inkscape | maintained | 3000 | HTTP | See upstream application setup |
| intellij-idea | linuxserver-intellij-idea | maintained | 3000 | HTTP | See upstream application setup |
| ipfs | linuxserver-ipfs | Hub-only | 80 | HTTP | See upstream application setup |
| jackett | linuxserver-jackett | maintained | 9117 | HTTP | See upstream application setup |
| jellyfin | linuxserver-jellyfin | maintained | 8096 | HTTP | See upstream application setup |
| jenkins-builder | linuxserver-jenkins-builder | Hub-only | 80 | native/terminal | Docker socket/daemon or upstream CI integration; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| joplin | linuxserver-joplin | maintained | 3000 | HTTP | See upstream application setup |
| kali-linux | linuxserver-kali-linux | maintained | 3000 | HTTP | See upstream application setup |
| kanzi | linuxserver-kanzi | Hub-only | 8000 | HTTPS | Configure env: INVOCATION_NAME, URL_ENDPOINT |
| kasm | linuxserver-kasm | maintained | 3000 | HTTPS | Configure env: KASM_PORT; Privileged container |
| kavita | linuxserver-kavita | maintained | 5000 | HTTP | See upstream application setup |
| kdenlive | linuxserver-kdenlive | maintained | 3000 | HTTP | See upstream application setup |
| keepassxc | linuxserver-keepassxc | maintained | 3000 | HTTP | See upstream application setup |
| kicad | linuxserver-kicad | maintained | 3000 | HTTP | See upstream application setup |
| kimai | linuxserver-kimai | maintained | 80 | HTTP | Configure env: APP_SECRET, DATABASE_URL, TRUSTED_HOSTS |
| kodi-headless | linuxserver-kodi-headless | Hub-only | 8080 | HTTP | See upstream application setup |
| kometa | linuxserver-kometa | maintained | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| krita | linuxserver-krita | maintained | 3000 | HTTP | See upstream application setup |
| lazylibrarian | linuxserver-lazylibrarian | maintained | 5299 | HTTP | See upstream application setup |
| ldap-auth | linuxserver-ldap-auth | maintained | 9000 | HTTP | See upstream application setup |
| letsencrypt | linuxserver-letsencrypt | Hub-only | 443 | HTTPS | See upstream application setup |
| libreoffice | libreoffice | maintained | 3000 | HTTP | See upstream application setup |
| libresonic | linuxserver-libresonic | Hub-only | 4040 | HTTP | See upstream application setup |
| librespeed | linuxserver-librespeed | maintained | 80 | HTTP | Configure env: PASSWORD |
| librewolf | linuxserver-librewolf | maintained | 3000 | HTTP | See upstream application setup |
| lidarr | linuxserver-lidarr | maintained | 8686 | HTTP | See upstream application setup |
| limnoria | linuxserver-limnoria | maintained | 8080 | HTTP | See upstream application setup |
| lm-studio | linuxserver-lm-studio | maintained | 3000 | HTTP | See upstream application setup |
| lollypop | linuxserver-lollypop | maintained | 3000 | HTTP | See upstream application setup |
| lsio-api | linuxserver-lsio-api | Hub-only | 8000 | HTTP | See upstream application setup |
| luanti | linuxserver-luanti | maintained | 30000 | native/terminal | See upstream application setup |
| lychee | linuxserver-lychee | maintained | 80 | HTTP | Configure env: DB_CONNECTION, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_DATABASE |
| mame | linuxserver-mame | maintained | 3000 | HTTP | See upstream application setup |
| manyfold | linuxserver-manyfold | maintained | 3214 | HTTP | Configure env: DATABASE_URL, REDIS_URL, SECRET_KEY_BASE |
| mariadb | linuxserver-mariadb | maintained | 3306 | native/terminal | Configure env: MYSQL_ROOT_PASSWORD |
| mastodon | linuxserver-mastodon | maintained | 443 | HTTPS | Configure env: LOCAL_DOMAIN, REDIS_HOST, REDIS_PORT, DB_HOST, DB_USER, DB_NAME, DB_PASS, DB_PORT, ES_ENABLED, ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY, ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY, ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT, SECRET_KEY_BASE, OTP_SECRET, VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, SMTP_SERVER, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD, SMTP_FROM_ADDRESS, S3_ENABLED |
| mcmyadmin2 | linuxserver-mcmyadmin2 | Hub-only | 8080 | HTTP | See upstream application setup |
| mediaelch | linuxserver-mediaelch | maintained | 3000 | HTTP | See upstream application setup |
| medusa | linuxserver-medusa | maintained | 8081 | HTTP | See upstream application setup |
| melonds | linuxserver-melonds | maintained | 3000 | HTTP | See upstream application setup |
| minetest | linuxserver-minetest | deprecated | 30000 | native/terminal | See upstream application setup |
| minisatip | linuxserver-minisatip | maintained | 8875 | HTTP | Configure env: RUN_OPTS; Devices: /dev/dvb |
| modmanager | linuxserver-modmanager | maintained | 80 | native/terminal | Docker socket/daemon or upstream CI integration; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| modrinth | linuxserver-modrinth | maintained | 3000 | HTTP | See upstream application setup |
| monica | linuxserver-monica | deprecated | 80 | HTTP | Configure env: DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_DATABASE |
| msedge | linuxserver-msedge | maintained | 3000 | HTTP | See upstream application setup |
| mstream | linuxserver-mstream | maintained | 3000 | HTTP | See upstream application setup |
| mullvad-browser | linuxserver-mullvad-browser | maintained | 3000 | HTTP | Additional capabilities; see upstream setup |
| musicbrainz | linuxserver-musicbrainz | Hub-only | 5000 | HTTP | See upstream application setup |
| muximux | linuxserver-muximux | Hub-only | 80 | HTTP | See upstream application setup |
| mylar | linuxserver-mylar | Hub-only | 8090 | HTTP | See upstream application setup |
| mylar3 | linuxserver-mylar3 | maintained | 8090 | HTTP | See upstream application setup |
| mysql | linuxserver-mysql | Hub-only | 3306 | native/terminal | See upstream application setup |
| mysql-workbench | linuxserver-mysql-workbench | maintained | 3000 | HTTP | Additional capabilities; see upstream setup |
| nano | linuxserver-nano | Hub-only | 8075 | HTTP | See upstream application setup |
| nano-wallet | linuxserver-nano-wallet | Hub-only | 80 | HTTP | See upstream application setup |
| netbootxyz | linuxserver-netbootxyz | deprecated | 3000 | HTTP | See upstream application setup |
| netbox | linuxserver-netbox | maintained | 8000 | HTTP | Configure env: SUPERUSER_EMAIL, SUPERUSER_PASSWORD, ALLOWED_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD, REDIS_DB_TASK, REDIS_DB_CACHE |
| nextcloud | linuxserver-nextcloud | maintained | 443 | HTTPS | See upstream application setup |
| nginx | linuxserver-nginx | maintained | 80 | HTTP | See upstream application setup |
| ngircd | linuxserver-ngircd | maintained | 6667 | native/terminal | See upstream application setup |
| nntp2nntp | linuxserver-nntp2nntp | Hub-only | 1563 | native/terminal | See upstream application setup |
| nomacs | linuxserver-nomacs | maintained | 3000 | HTTP | See upstream application setup |
| nzbget | linuxserver-nzbget | maintained | 6789 | HTTP | See upstream application setup |
| nzbhydra2 | linuxserver-nzbhydra2 | maintained | 5076 | HTTP | See upstream application setup |
| obsidian | obsidian | maintained | 3000 | HTTP | See upstream application setup |
| ombi | linuxserver-ombi | maintained | 3579 | HTTP | See upstream application setup |
| onlyoffice | linuxserver-onlyoffice | maintained | 3000 | HTTP | See upstream application setup |
| openshot | linuxserver-openshot | maintained | 3000 | HTTP | See upstream application setup |
| openssh-server | linuxserver-openssh-server | maintained | 2222 | native/terminal | See upstream application setup |
| openvscode-server | linuxserver-openvscode-server | deprecated | 3000 | HTTP | See upstream application setup |
| opera | linuxserver-opera | maintained | 3000 | HTTP | See upstream application setup |
| orcaslicer | linuxserver-orcaslicer | maintained | 3000 | HTTP | See upstream application setup |
| organizr | linuxserver-organizr | Hub-only | 80 | HTTP | See upstream application setup |
| oscam | linuxserver-oscam | maintained | 8888 | HTTP | Devices: /dev/ttyUSB0 |
| overseerr | linuxserver-overseerr | deprecated | 5055 | HTTP | See upstream application setup |
| pairdrop | linuxserver-pairdrop | maintained | 3000 | HTTP | See upstream application setup |
| paperless-ng | linuxserver-paperless-ng | Hub-only | 8000 | HTTP | See upstream application setup |
| paperless-ngx | linuxserver-paperless-ngx | Hub-only | 8000 | HTTP | See upstream application setup |
| papermerge | linuxserver-papermerge | Hub-only | 8000 | HTTP | See upstream application setup |
| pcsx2 | linuxserver-pcsx2 | maintained | 3000 | HTTP | See upstream application setup |
| pelorus | linuxserver-pelorus | maintained | 3001 | HTTPS | See upstream application setup |
| photoshow | linuxserver-photoshow | Hub-only | 80 | HTTP | See upstream application setup |
| phpmyadmin | linuxserver-phpmyadmin | maintained | 80 | HTTP | See upstream application setup |
| pidgin | linuxserver-pidgin | maintained | 3000 | HTTP | See upstream application setup |
| piper | linuxserver-piper | maintained | 10200 | native/terminal | Configure env: PIPER_VOICE |
| piwigo | linuxserver-piwigo | maintained | 80 | HTTP | See upstream application setup |
| pixapop | linuxserver-pixapop | Hub-only | 80 | HTTP | See upstream application setup |
| planka | linuxserver-planka | maintained | 1337 | HTTP | Configure env: BASE_URL, DATABASE_URL, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME, SECRET_KEY, TRUST_PROXY |
| plex | linuxserver-plex | maintained | 32400 | HTTP | Configure env: VERSION; Upstream uses host networking |
| plex-meta-manager | linuxserver-plex-meta-manager | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| plexpy | linuxserver-plexpy | Hub-only | 8181 | HTTP | See upstream application setup |
| ppsspp | linuxserver-ppsspp | maintained | 3000 | HTTP | See upstream application setup |
| projectsend | linuxserver-projectsend | maintained | 80 | HTTP | See upstream application setup |
| prowlarr | linuxserver-prowlarr | maintained | 9696 | HTTP | See upstream application setup |
| pwndrop | linuxserver-pwndrop | maintained | 8080 | HTTP | See upstream application setup |
| pycharm | linuxserver-pycharm | maintained | 3000 | HTTP | See upstream application setup |
| pydio | linuxserver-pydio | Hub-only | 443 | HTTPS | See upstream application setup |
| pydio-cells | linuxserver-pydio-cells | maintained | 8080 | HTTPS | Configure env: EXTERNALURL |
| pyload | linuxserver-pyload | Hub-only | 8000 | HTTP | See upstream application setup |
| pyload-ng | linuxserver-pyload-ng | maintained | 8000 | HTTP | See upstream application setup |
| pylon | linuxserver-pylon | deprecated | 3131 | HTTP | See upstream application setup |
| python | linuxserver-python | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| qbittorrent | linuxserver-qbittorrent | maintained | 8080 | HTTP | Configure env: WEBUI_PORT, TORRENTING_PORT |
| qdirstat | linuxserver-qdirstat | maintained | 3000 | HTTP | See upstream application setup |
| qemu-static | linuxserver-qemu-static | maintained | 80 | native/terminal | Privileged container; Host binfmt_misc registration, not a guest VM; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| quassel-core | linuxserver-quassel-core | Hub-only | 4242 | native/terminal | See upstream application setup |
| quassel-web | linuxserver-quassel-web | Hub-only | 64443 | HTTPS | See upstream application setup |
| radarr | linuxserver-radarr | maintained | 7878 | HTTP | See upstream application setup |
| raneto | linuxserver-raneto | maintained | 3000 | HTTP | See upstream application setup |
| rawtherapee | linuxserver-rawtherapee | maintained | 3000 | HTTP | See upstream application setup |
| rdesktop | linuxserver-rdesktop | deprecated | 3389 | native/terminal | See upstream application setup |
| readarr | linuxserver-readarr | deprecated | 8787 | HTTP | See upstream application setup |
| readme-sync | linuxserver-readme-sync | Hub-only | 80 | native/terminal | Docker socket/daemon or upstream CI integration; CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| remmina | linuxserver-remmina | maintained | 3000 | HTTP | See upstream application setup |
| requestrr | linuxserver-requestrr | Hub-only | 4545 | HTTP | See upstream application setup |
| resilio-sync | linuxserver-resilio-sync | maintained | 8888 | HTTP | See upstream application setup |
| retroarch | linuxserver-retroarch | maintained | 3000 | HTTP | See upstream application setup |
| rpcs3 | linuxserver-rpcs3 | maintained | 3000 | HTTP | See upstream application setup |
| rsnapshot | linuxserver-rsnapshot | maintained | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| rustdesk | linuxserver-rustdesk | maintained | 3000 | HTTP | See upstream application setup |
| rutorrent | linuxserver-rutorrent | Hub-only | 80 | HTTP | See upstream application setup |
| sabnzbd | linuxserver-sabnzbd | maintained | 8080 | HTTP | See upstream application setup |
| scrutiny | linuxserver-scrutiny | Hub-only | 8080 | HTTP | Configure env: SCRUTINY_API_ENDPOINT, SCRUTINY_WEB, SCRUTINY_COLLECTOR; Devices: /dev/sda, /dev/sdb, /dev/nvme1n1; Additional capabilities; see upstream setup |
| scummvm | linuxserver-scummvm | maintained | 3000 | HTTP | See upstream application setup |
| sealskin | linuxserver-sealskin | maintained | 8443 | HTTPS | See upstream application setup |
| series-troxide | linuxserver-series-troxide | deprecated | 3000 | HTTP | See upstream application setup |
| shadps4 | linuxserver-shadps4 | maintained | 3000 | HTTP | See upstream application setup |
| shotcut | linuxserver-shotcut | maintained | 3000 | HTTP | See upstream application setup |
| sickbeard | linuxserver-sickbeard | Hub-only | 8081 | HTTP | See upstream application setup |
| sickchill | linuxserver-sickchill | deprecated | 8081 | HTTP | See upstream application setup |
| sickgear | linuxserver-sickgear | maintained | 8081 | HTTP | See upstream application setup |
| sickrage | linuxserver-sickrage | Hub-only | 8081 | HTTP | See upstream application setup |
| signal | linuxserver-signal | maintained | 3000 | HTTP | See upstream application setup |
| smokeping | linuxserver-smokeping | maintained | 80 | HTTP | See upstream application setup |
| snapdrop | linuxserver-snapdrop | deprecated | 80 | HTTP | See upstream application setup |
| snipe-it | linuxserver-snipe-it | deprecated | 80 | HTTP | Configure env: APP_KEY, APP_URL, MYSQL_PORT_3306_TCP_ADDR, MYSQL_PORT_3306_TCP_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD |
| socket-proxy | linuxserver-socket-proxy | maintained | 2375 | HTTP | Docker socket/daemon or upstream CI integration |
| sonarr | linuxserver-sonarr | maintained | 8989 | HTTP | See upstream application setup |
| speedtest-tracker | linuxserver-speedtest-tracker | maintained | 80 | HTTP | Configure env: APP_KEY, APP_URL, DB_CONNECTION, SPEEDTEST_SCHEDULE, SPEEDTEST_SERVERS |
| spotube | linuxserver-spotube | maintained | 3000 | HTTP | See upstream application setup |
| sqlitebrowser | linuxserver-sqlitebrowser | maintained | 3000 | HTTP | See upstream application setup |
| steam | linuxserver-steam | maintained | 3000 | HTTP | See upstream application setup |
| steamos | linuxserver-steamos | deprecated | 3000 | HTTP | Configure env: DRINODE; Devices: /dev/dri; Additional capabilities; see upstream setup |
| swag | linuxserver-swag | maintained | 443 | HTTPS | Configure env: URL, VALIDATION; Additional capabilities; see upstream setup |
| synclounge | linuxserver-synclounge | maintained | 8088 | HTTP | See upstream application setup |
| syncthing | linuxserver-syncthing | maintained | 8384 | HTTP | See upstream application setup |
| syslog-ng | linuxserver-syslog-ng | maintained | 5514 | native/terminal | See upstream application setup |
| taisun | linuxserver-taisun | Hub-only | 3000 | HTTP | See upstream application setup |
| tautulli | linuxserver-tautulli | maintained | 8181 | HTTP | See upstream application setup |
| telegram | linuxserver-telegram | maintained | 3000 | HTTP | See upstream application setup |
| tester | linuxserver-tester | Hub-only | 3000 | HTTP | Configure env: URL |
| thelounge | thelounge | maintained | 9000 | HTTP | See upstream application setup |
| thunderbird | linuxserver-thunderbird | maintained | 3000 | HTTP | See upstream application setup |
| transmission | linuxserver-transmission | maintained | 9091 | HTTP | See upstream application setup |
| tvheadend | linuxserver-tvheadend | maintained | 9981 | HTTP | See upstream application setup |
| ubooquity | linuxserver-ubooquity | maintained | 2202 | HTTP | See upstream application setup |
| ungoogled-chromium | linuxserver-ungoogled-chromium | maintained | 3000 | HTTP | See upstream application setup |
| unifi | linuxserver-unifi | Hub-only | 8443 | HTTPS | See upstream application setup |
| unifi-controller | linuxserver-unifi-controller | Hub-only | 8443 | HTTPS | See upstream application setup |
| unifi-network-application | linuxserver-unifi-network-application | maintained | 8443 | HTTPS | Configure env: MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DBNAME, MONGO_AUTHSOURCE |
| unrar | linuxserver-unrar | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| vivaldi | linuxserver-vivaldi | maintained | 3000 | HTTP | See upstream application setup |
| vlc | linuxserver-vlc | maintained | 3000 | HTTP | See upstream application setup |
| vscode | linuxserver-vscode | maintained | 3000 | HTTP | Additional capabilities; see upstream setup |
| vscodium | vscodium | maintained | 3000 | HTTP | Additional capabilities; see upstream setup |
| vscodium-web | linuxserver-vscodium-web | maintained | 8000 | HTTP | See upstream application setup |
| webcord | linuxserver-webcord | maintained | 3000 | HTTP | See upstream application setup |
| webgrabplus | linuxserver-webgrabplus | maintained | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| webstation | linuxserver-webstation | maintained | 3000 | HTTP | See upstream application setup |
| webtop | linuxserver-webtop | maintained | 3000 | HTTP | See upstream application setup |
| weixin | linuxserver-weixin | maintained | 3000 | HTTP | See upstream application setup |
| wikijs | linuxserver-wikijs | maintained | 3000 | HTTP | See upstream application setup |
| winegui | linuxserver-winegui | maintained | 3000 | HTTP | See upstream application setup |
| wireguard | linuxserver-wireguard | maintained | 51820 | native/terminal | Additional capabilities; see upstream setup |
| wireshark | linuxserver-wireshark | maintained | 3000 | HTTP | Upstream uses host networking; Additional capabilities; see upstream setup |
| wps-office | linuxserver-wps-office | maintained | 3000 | HTTP | See upstream application setup |
| xbackbone | linuxserver-xbackbone | maintained | 80 | HTTP | See upstream application setup |
| xemu | linuxserver-xemu | maintained | 3000 | HTTP | See upstream application setup |
| xvfb | linuxserver-xvfb | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| yaak | linuxserver-yaak | maintained | 3000 | HTTP | See upstream application setup |
| your_spotify | linuxserver-your-spotify | maintained | 80 | HTTP | Configure env: APP_URL, SPOTIFY_PUBLIC, SPOTIFY_SECRET, SPOTIFY_API_DELAY_MS, CORS, MONGO_ENDPOINT |
| yq | linuxserver-yq | Hub-only | 80 | native/terminal | CLI/background utility; configure arguments or config files; Port 80 is a schema placeholder; no listening port |
| zen | linuxserver-zen | maintained | 3000 | HTTP | See upstream application setup |
| znc | linuxserver-znc | maintained | 6501 | HTTP | See upstream application setup |
| zotero | linuxserver-zotero | maintained | 3000 | HTTP | See upstream application setup |

Existing additional variants:

- `kasm`: `linuxserver/kasm:1.19.0`
- `rdesktop-ubuntu-xfce`: `linuxserver/rdesktop:ubuntu-xfce`
- `webtop-alpine-kde`: `linuxserver/webtop:alpine-kde`
- `webtop-arch-kde`: `linuxserver/webtop:arch-kde`
- `webtop-ubuntu-xfce`: `linuxserver/webtop:ubuntu-xfce`
