# FreeBSD 15.1 verification

Verified on **2026-10-08** using the `rancher` Kubernetes context and the
kube-workspaces controller, KubeVirt v1.9.0 and CDI v1.61.0.

## Published image

- Public tag: `docker.io/flaccid/containerdisk-freebsd:15.1`
- Catalog reference:
  `flaccid/containerdisk-freebsd@sha256:ade6d7265d8f0e683572e5d46f4d3598416d7d6cbf6f4521410b06e5e3b6e0ac`
- Upstream compressed-disk SHA-256:
  `e4ca4db889f8559c9b9dfcacc70405c038476f4b6d41649b152d3809a2ed9e1f`
- Upstream checksum and `qemu-img check` passed during the build.
- Docker Hub repository is public; CDI imported it without registry credentials.

## Workspace test

Workspace `chris-at-fordham-id-au/freebsd-15-1` was scheduled on `angry`
(Linux/amd64), with two vCPUs, 2 GiB guest RAM, a 2304 MiB launcher memory
request/limit and a 10 GiB local-path root disk. Only one FreeBSD VM ran at a
time. The in-cluster build Job and its credential Secret were removed before
this test.

Results:

1. CDI DataVolume reached `Succeeded`.
2. KubeVirt VMI reached `Running`/`Ready` on `angry`.
3. Password SSH login as `freebsd` succeeded through `virtctl port-forward`.
4. `freebsd-version -ku` returned `15.1-RELEASE` for both kernel and userland.
5. `uname -srm` returned `FreeBSD 15.1-RELEASE amd64`.
6. `service sshd status` confirmed a running sshd.
7. `df -h /` reported an expanded 8.1 GiB UFS filesystem on the 10 GiB CDI PVC
   (CDI filesystem overhead and guest partitions account for the difference).
8. The login belonged to `wheel`; owner keys were present in
   `/home/freebsd/.ssh/authorized_keys`.
9. Stop/start through the Workspace `kubeworkspaces.io/stopped` annotation
   preserved `/home/freebsd/workspace-proof.txt` and the seeded SSH keys.
10. `fetch -T 15 -q -o /dev/null https://www.freebsd.org` succeeded after restart,
    exercising guest DNS and outbound HTTPS.

The test Workspace was **left stopped**, retaining its root disk while
releasing guest/launcher RAM. Resume it from the UI or with:

```bash
kubectl annotate workspace freebsd-15-1 -n chris-at-fordham-id-au \
  kubeworkspaces.io/stopped-
```

A separate local QEMU/TCG test also booted the official disk using the catalog
user-data and successfully verified login, version, sshd and root-disk growth.

## Compatibility fixes found during testing

- FreeBSD's `nuageinit` accepts shell-string `runcmd` entries, not command
  argument arrays. `users: [default]` preserves top-level SSH-key seeding for
  the default `freebsd` user.
- The upstream image enables first-boot base-package upgrades. The catalog
  disables that service through an rc.conf override to avoid blocking initial
  login on a package mirror.
- CDI v1.61.0 rejects combined `repository:tag@sha256:...` references. The
  catalog uses the compatible digest-only form.

These results cover a VM workspace. Native FreeBSD container workspaces are
not supported by the cluster's Linux kernel/runtime; no container-mode entry
is advertised.
