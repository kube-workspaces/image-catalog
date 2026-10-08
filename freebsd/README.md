# FreeBSD 15.1 workspace

`images/freebsd-vm.yaml` packages the official **FreeBSD 15.1-RELEASE amd64
BASIC-CLOUDINIT UFS** disk as a KubeVirt containerDisk. The build checks the
published SHA-256, checks the QCOW2 structure, and compresses the disk without
changing the guest filesystem. No locally installed or pre-provisioned guest
state is included. Despite the upstream `BASIC-CLOUDINIT` filename, this guest
uses FreeBSD's **nuageinit**, a limited cloud-config/NoCloud implementation,
rather than Python cloud-init. In particular, `runcmd` entries must be shell
strings, not the argument arrays commonly used in Linux cloud-config.

## Build and deploy

```bash
docker build --platform linux/amd64 -t flaccid/containerdisk-freebsd:15.1 freebsd
docker push flaccid/containerdisk-freebsd:15.1
kubectl apply --server-side -f images/freebsd-vm.yaml
kubectl apply -n YOUR_WORKSPACE_NAMESPACE -f freebsd/workspace.yaml
```

The catalog pins the published image digest. After rebuilding/publishing, update
that digest in both manifests. If publishing under a different registry/name,
update `spec.image` in the Image
and the container image in the Workspace together: the controller resolves
image defaults by exact image reference.

Use `repository@sha256:...` for CDI imports, not `repository:tag@sha256:...`:
the cluster's CDI image-reference parser rejects the combined tag/digest form.

The default Workspace uses two vCPUs and 2 GiB guest RAM. The Image requests
2304 MiB for the launcher, allowing for virtualization overhead. CDI imports
the boot disk into a 10 GiB persistent root PVC. KubeVirt, CDI, amd64 nodes and
a default StorageClass are required. The upstream guest has growfs support;
use `df -h /` to check the expanded filesystem after boot.

## Access

- Guest login: **`freebsd` / `freebsd`**, shell `/bin/sh`.
- Serial console: `virtctl console -n YOUR_WORKSPACE_NAMESPACE freebsd-15-1`.
- SSH: `virtctl port-forward -n YOUR_WORKSPACE_NAMESPACE vm/freebsd-15-1 2222:22`,
  then `ssh -p 2222 freebsd@localhost` in another terminal.
- The workspace Service maps port **80 to guest SSH port 22**; it is not an
  HTTP application. Use the workspace console or SSH connection rather than
  the HTTP reverse proxy.

Nuageinit creates the default login and enables sshd on first boot. Keeping
`users: [default]` lets it apply the controller's top-level `ssh_authorized_keys`
to the `freebsd` account. Change
the default password in your Image user-data for new guests, or with `passwd`
inside an existing guest. Persistent roots keep guest modifications and
first-boot provisioning state across stop/start. A reset creates a fresh root.

The defaults disable the upstream `firstboot-pkg-upgrade` service, so initial
provisioning does not block on package-mirror access or change the release
before login. Run `pkg upgrade -r FreeBSD-base` as root to install base-system
updates, or remove the `write_files` override to retain upstream first-boot
upgrades.

The controller can seed the workspace owner's SSH keys through cloud-init at
first boot. This image does not opt into live `qemuGuestAgent` SSH-key
propagation: cloud-init alone does not provide that capability.

## Container compatibility

Linux containers share the Linux host kernel. FreeBSD requires its own kernel,
so neither a FreeBSD root filesystem nor a KubeVirt disk-only OCI image can run
as a native container on the cluster's Linux nodes. FreeBSD jails require
FreeBSD hosts and are not supported by this Kubernetes setup.

An emulated container would need a separate Linux image containing QEMU and
the FreeBSD disk, plus networking, console and disk-lifecycle glue. Its pod
exec sessions would target the Linux wrapper rather than the guest, and
software emulation would be significantly slower than KubeVirt/KVM. The
catalog entry therefore explicitly supports only `vm` workspaces.

## Verification

See [the recorded cluster verification](VERIFICATION.md) for the published
digest, guest checks and stop/start persistence results.

```bash
make validate
kubectl get workspace,vm,vmi,dv,pvc -n YOUR_WORKSPACE_NAMESPACE
# Inside the guest:
freebsd-version -ku
uname -srm
cat /var/log/nuageinit.log
service sshd status
df -h /
```

KubeVirt `Ready` indicates that the launcher is running; verify cloud-init and
an actual guest login before considering provisioning complete.
