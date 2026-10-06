# Private Windows 11 prepared root recipe

This is a **Phase 0 proof recipe**, not an enabled Image CR. Windows product
schema, provisioning and lifecycle integration must pass the
[cross-repo plan](https://github.com/kube-workspaces/tracking/blob/main/windows-vm-workspaces-plan.md)
before a Windows catalog entry is shipped. Microsoft binaries, installer media,
license keys and per-guest credentials are operator supplied and private.

For the complete operator workflow, follow
[Build your own Windows 11 image from an official ISO](./BUILD-GUIDE.md).
It includes media upload, native answer-file installation, guest checks,
unencrypted Sysprep sealing, root-only export, Docker-free packaging, private CDI
authentication and independent-clone validation. Reusable tooling lives here:
`render-bootstrap.py`, `render-import-secret.py`, `Configure-Guest.ps1`,
`Collect-Evidence.ps1`, `Test-PersistentState.ps1`, `Remove-Bootstrap.ps1`,
`prepare-sealed-root.py`, and `package-layer.py`.
Keep generated media/disks/credentials outside this checkout.

## Inputs and build record

Use Windows 11 x86-64 **Pro or Enterprise** on eligible Linux amd64 KVM workers.
Before installation pin a currently supported feature release and record:

| Input | Required record |
|---|---|
| Windows media | Edition, feature release, build, language, acquisition source, SHA256 |
| VirtIO media | Exact version, acquisition URL, SHA256, Secure Boot signature results |
| Runtime | KubeVirt/CDI versions, actual host CPU, root/state StorageClasses |
| Recipe | This repository commit, chosen access services and setup settings |
| Sealed artifact | Disk SHA256, virtual size, OCI manifest digest, build completion time |

Do not use `latest` installer/driver inputs. Keep licensing/activation details in
operator records; do not put keys or entitlement documents in public metadata.
An evaluation image is only usable within its evaluation terms and lifetime.

## Install and validate

Use the isolated direct VM fixtures and operator instructions in
[deploy/docs/windows-vm.md](https://github.com/kube-workspaces/deploy/blob/main/docs/windows-vm.md).
The proof template uses q35, host-passthrough CPU, persistent EFI/Secure Boot,
SMM, persistent TPM, VirtIO root/network, VGA display, USB tablet and SATA media.
Install signed **viostor**, **NetKVM**, the guest-agent serial driver and QEMU
guest agent from the pinned driver media. Verify guest agent connectivity from
the VMI condition, not just the Windows service.

Run `Collect-Evidence.ps1 -OutputPath C:\proof-evidence.json` elevated. Run
`dxdiag /t C:\dxdiag.txt` separately and inspect it for the supported workload
envelope. Redact hostnames, identities and environment details before publishing.
The script records no passwords or BitLocker recovery material. Its Windows
runtime execution remains part of live guest acceptance.

Test Windows Update, DHCP/DNS, login/display, secure-attention, absolute pointer
and graceful lifecycle before sealing. Do not enable RDP/OpenSSH/auto-logon as
implicit defaults. No installer requirement bypasses or CPU-name spoofing.

## Generalise and export

1. Remove build-only accounts, downloaded private files, tokens, activation
   keys and cached answer files. Keep the template root **unencrypted**; do not
   clone TPM-bound BitLocker state. Any encryption starts in each provisioned
   clone with its own TPM and independently stored recovery material.
   Check `Get-BitLockerVolume -MountPoint C:` after OOBE and after a restart:
   Windows can automatically encrypt the volume while `ProtectionStatus` is
   still Off. That status alone does not establish an unencrypted template.
   If needed, run `Disable-BitLocker -MountPoint C:` on the disposable build
   guest and wait until `VolumeStatus` is FullyDecrypted and the encryption
   percentage is zero before sealing. Prevent automatic device encryption in
   the build-template policy; cloned guests can explicitly enable their own
   protection after provisioning. Remove any test TPM-bound keys before export.
2. Generalise from elevated PowerShell with
   `C:\Windows\System32\Sysprep\Sysprep.exe /generalize /shutdown /oobe /mode:vm`.
   Verify Sysprep succeeded for the pinned build. Do not restart the sealed root.
3. Stop the direct build VM and wait for its VMI/launcher to disappear. Export
   **only the root disk** using the version-matched KubeVirt export workflow or
   offline `virtctl guestfs`/operator disk tooling. Do not export its TPM/EFI
   backend PVC, ISO media, Secrets or answer-file caches.
4. Convert the offline root into a standalone disk:

   ```sh
   qemu-img convert -p -O qcow2 exported-root.img sealed-root.qcow2
   python3 windows11/prepare-sealed-root.py --disk sealed-root.qcow2 --output disk.qcow2
   qemu-img check disk.qcow2
   qemu-img info --output=json disk.qcow2
   sha256sum disk.qcow2
   ```

   Verify no backing file and a virtual size compatible with the 80Gi target
   (CDI filesystem overhead needs capacity beyond the guest virtual disk size).
   Avoid storing raw disks inside this source checkout.

   The offline preparation step checks the generalised OOBE state, removes
   backup/cached answer files and sets a credential-free native setup pointer
   to `D:\autounattend.xml`. The tested post-Sysprep guest did not implicitly
   discover its SATA answer CD. Keep the clone profile to root plus one Sysprep
   CD (D), and remove the pointer after confirmed setup. See the
   [guide's discovery details](./BUILD-GUIDE.md#native-answer-file-discovery-in-the-sealed-root).

## Package and privately import

For a Docker-free path, `package-layer.py --disk /PRIVATE/disk.qcow2 --output
/PRIVATE/root-layer.tar.gz` creates the UID-107 layer for `crane append`. See the
[guide](./BUILD-GUIDE.md#7-package-and-publish-privately) for commands and capacity
planning; Docker's builder cache is additional to the exported disk.

In a separate private build context containing this Dockerfile and the sealed
`disk.qcow2` only:

```sh
docker build --platform linux/amd64 -t REGISTRY/PRIVATE/windows11:RECIPE_BUILD .
docker push REGISTRY/PRIVATE/windows11:RECIPE_BUILD
docker buildx imagetools inspect REGISTRY/PRIVATE/windows11:RECIPE_BUILD
```

The scratch containerDisk contains `/disk/disk.qcow2`, readable by KubeVirt's
UID 107. Record and use its **sha256 OCI digest** in clone fixtures. Test CDI's
actual pod registry import with a same-namespace Opaque Secret containing
`accessKeyId` (username) and `secretKey` (password/token), referenced by
`registry.secretRef`. `render-import-secret.py` converts private inline Docker
auth to this CDI 1.61 pod-import contract. Do not rely on just a
successful local Docker pull. A future launcher containerDisk path would need
its own imagePullSecrets as well; this recipe's clones use imported PVC roots.

Generate private bootstrap files outside this checkout:

```sh
python3 windows11/render-bootstrap.py --mode clone --secret-name clone-a-bootstrap \
  --hostname KW-CLONE-A --output-dir /PRIVATE/clone-a
kubectl apply -f /PRIVATE/clone-a/bootstrap-secret.json
```

The new output directory is mode 0700 and its Secret/credential files are mode
0600. The tool generates a unique initial password, XML-escapes values, refuses
to overwrite an existing output directory, and never prints credentials. For an
isolated blank-root installer fixture use `--mode install`; **this mode wipes
disk 0**, selects Windows 11 Pro, loads viostor in WinPE, injects boot-critical
drivers through native offline servicing, and installs the agent during
specialise. Loading a driver with `drvload` alone is insufficient: the installed
root also needs that driver before its first boot. The installer aliases the
discovered driver ISO as `V:` for its WinPE/offline-servicing session.
Install Secrets also contain `configure.ps1`; the short specialise command
discovers and runs it from the Sysprep CD. Keep the script on the media: native
Deployment RunSynchronous command paths have a 259-character limit.
See Microsoft's [offline driver paths contract](https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-pnpcustomizationsnonwinpe-driverpaths).
Clone mode has no disk-partitioning or driver
media dependency. Neither mode enables auto-logon or installer requirement
bypasses. Validate the answer file against the pinned Windows build with Windows
System Image Manager. Clone-mode native provisioning has passed the direct
two-clone runtime proof with the offline discovery-pointer preparation step.
Fresh install-mode acceptance of the final wrapper/helper combination and
platform-managed provisioning remain open.

Use the clone fixture twice, with distinct Secret-backed SATA Sysprep media,
different firmware UUIDs, local credentials and hostnames. Generate answer files
with Windows System Image Manager for the pinned edition/build; XML-escape all
variable values. Do not use a shared password, plaintext password in Image CRs,
or an answer file baked into the disk. OOBE behaviour must pass the actual guest
proof before automating it in the product.

Confirm both clones finish setup and log in, have independent identities and
TPMs, and survive stop/start plus VMI replacement without setup replay. Detach
Sysprep media while stopped after confirmed setup; clean guest answer-file
caches and delete the bootstrap Secret after detaching. Record import duration,
first-desktop duration, private-registry authentication and root/state PVC
ownership/deletion results. Only promote the artifact after this proof passes.

The direct two-clone proof now confirms independent accounts/credentials,
desktop login, root/firmware/TPM-key persistence across changed VMI UIDs, and
bootstrap cleanup/removal without OOBE replay. This does not close Windows
Update/BitLocker recovery, application connection-path or product lifecycle
acceptance. Keep those results separate when validating your own build.

## Current limits

No prepared Windows root or media is bundled. No enabled `images/windows11.yaml`
is emitted by catalog builds yet. Display is hypervisor VNC; RDP, OpenSSH,
clipboard/audio/resize, accelerated graphics, Windows data-volume formatting
and nested Hyper-V require separate implementation and acceptance evidence.
