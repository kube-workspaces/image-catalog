# MS-DOS 6.22 Image Catalog

This repository contains disk image files for MS-DOS 6.22, including both RAW and VHD formats.

## File Formats

- **`.raw`** - Raw sector-by-sector disk image (preserves exact disk structure)
- **`.vhd`** - Virtual Hard Disk format compatible with virtualization platforms

---

## Quick Start: Mounting Instructions

### For `.raw` Files

1. **Create a mount point:**
   ```bash
   sudo mkdir -p /mnt/msdos622
   ```

2. **Attach as loop device (with partition scanning):**
   ```bash
   sudo losetup --find --show --partscan msdos622.raw
   ```

3. **Mount the first partition:**
   ```bash
   sudo mount -t vfat /dev/mapper/msdos622-1 /mnt/msdos622
   ```

4. **Verify it's mounted:**
   ```bash
   ls -la /mnt/msdos622
   ```

5. **To unmount:**
   ```bash
   sudo guestunmount /mnt/msdos622
   # or
   sudo umount /mnt/msdos622
   ```

### For `.vhd` Files

**Option 1: Convert then mount (recommended)**

1. **Convert VHD to RAW:**
   ```bash
   sudo qemu-img convert -f vpc -O raw msdos622.vhd msdos622-converted.raw
   ```

2. **Then follow the `.raw` mounting instructions above.**

**Option 2: Direct mount (Linux 4.19+)**

```bash
# Attach as loop device with partition scanning
sudo losetup --find --show --partscan msdos622.vhd

# Mount the first partition
sudo mount -t vfat /dev/mapper/msdos622-1 /mnt/msdos622
```

---

## Prerequisites

Ensure you have the following tools installed:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install dosfstools util-linux-losetup qemu-utils mtools

# RHEL/CentOS/Fedora
sudo dnf install dosfstools util-linux qemu-img mtools
```

---

## Troubleshooting

### "mount: wrong fs type, bad option" errors

If you receive filesystem errors, ensure you're using the correct filesystem type:
- MS-DOS 6.22 typically uses FAT12 or FAT16
- Try `-t vfat` or `-t msdos` as the filesystem type

### Loop device already in use

```bash
# Check for existing loop devices
sudo losetup -a

# Remove existing mapping if needed
sudo losetup -d /dev/loopX
```

### Partition not found

If partitions aren't detected, ensure you used the `--partscan` flag with `losetup`. This creates device mapper entries like `/dev/mapper/msdos622-1`.

---

## CD-ROM support

The upstream VHD ships with the CD-ROM drivers enabled in `CONFIG.SYS` and `AUTOEXEC.BAT`:

```
DEVICE=C:\DOS\cd1.SYS /D:banana
MSCDEX.EXE /D:banana /L:D
```

Those drivers only probe legacy ISA IDE ports (1F0/170/1E8/168). The workspace VM runs on machine type `q35` with no CD device, so every boot ended with:

```
  CD-ROM Device Driver for IDE (Four Channels Supported)
  Device Name        : BANANA
  No drives found, aborting installation
Device driver not found: 'BANANA'.
No valid CDROM device drivers selected
```

`make patch-cd-rom` comments both lines out so the guest boots cleanly to `C:\>`. The target is idempotent and is a prerequisite of `make docker-build`, so re-running `fetch-msdos-622.sh` cannot silently bring the error back.

Note that CD-ROM access is unavailable in this VM regardless: even with a drive attached, the OAK driver cannot see an AHCI (q35) CD device.

---

## Building and publishing the containerdisk

`ms-dos-622.raw`, `ms-dos-622.vhd` and `ms-dos-622.7z` are build artifacts:
they are gitignored, so **a fresh clone does not contain them and
`make docker-build` will fail until they are regenerated.** Fetch them first:

```bash
./fetch-msdos-622.sh   # needs curl, p7zip (7z) and qemu-img
```

Then build and publish:

```bash
make docker-build      # runs patch-cd-rom first (needs mtools)
make docker-login      # prompts for Docker Hub credentials / access token
make docker-push
```

- `make docker-build` always applies `patch-cd-rom` first, so a freshly fetched
  image is fixed before it is built and pushed.
- The published tag is `latest`. An existing persistent root PVC keeps whatever
  it was imported with — only newly created workspaces pick up a new push.

---

## Running it as a kube-workspaces VM

The catalog entry lives at [`images/ms-dos-622.yaml`](../images/ms-dos-622.yaml).
`Image` is a **cluster-scoped** CR, so importing it is enough to make it
available in every namespace:

```bash
kubectl apply -f images/ms-dos-622.yaml
```

The CR alone does not run anything — a user then creates a `Workspace` with
`spec.type: vm` (the image declares `workspaceTypes: [vm]`, which is what
offers it for VM creation). Those cluster prerequisites are **not** covered by
the Image CR:

| Requirement | Why |
|---|---|
| kube-workspaces installed | Supplies the `Image`/`Workspace` CRDs plus controller, API, proxy and frontend |
| KubeVirt installed (`kubevirt.enabled: true` in the chart) | The controller checks for the KubeVirt CRDs and sets a `KubeVirtNotInstalled` condition on the workspace instead of creating a `VirtualMachine` when they are missing |
| CDI installed (`kubevirt.cdi.enabled`, default `true`) | `persistentRootDisk: true` makes the root disk a CDI registry-import `DataVolume`. There is no CDI pre-check, so a missing CDI surfaces later as `VMReconcileFailed` ("no matches for kind DataVolume") |
| A **default StorageClass** | The generated root PVC sets no `storageClassName`; the chart ships no storage class. This image requests `5Gi` |
| KVM on the node, or `kubevirt.useEmulation: true` | QEMU needs `/dev/kvm` unless software emulation is enabled |
| Outbound pull of `flaccid/containerdisk-ms-dos-622:latest` | The containerdisk is imported from Docker Hub (public). Rebuild and push it so the published tag carries this directory's fixes — already-provisioned root PVCs keep their old content, only new workspaces re-import |
| Ingress/API reachable | The serial console and noVNC display bridges dial KubeVirt's console/vnc subresources through the API |

RBAC for `virtualmachines`, `datavolumes` and the console/VNC subresources is
unconditional in the chart, so KubeVirt may come from the chart or be installed
separately.

Notes:

- `videoDevice: virtio` is correct for a DOS guest: KubeVirt emits
  `-device virtio-vga`, which stays VGA-compatible until a virtio driver takes
  over, so the BIOS/DOS text mode is visible over noVNC.
- `defaultPort: 21` is only the required port field. The guest runs no TCP/IP
  stack, so nothing listens behind the workspace Service — use the console
  (noVNC display or serial) to interact with it.
- Until the image is vendored into the chart (`make sync-images` in the
  kube-workspaces deploy repo, which pulls from a published image-catalog
  release), installing the chart does not create this Image CR — the manual
  `kubectl apply -f` above is required.

---

## Verification

After mounting, verify the filesystem integrity:

```bash
# Check filesystem type and size
sudo blkid /dev/mapper/msdos622-*

# View partition table (if available)
sudo fdisk -l /dev/loopX
```

---

**Quick Reference Command:**
```bash
sudo losetup --find --show --partscan msdos622.raw
sudo mount -t vfat /dev/mapper/msdos622-1 /mnt/msdos622
```
