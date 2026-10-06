# Build your own Windows 11 image from an official ISO

This guide takes an operator-owned Windows ISO through installation, validation,
Sysprep, private OCI packaging and two independent KubeVirt VM clones. The
repository supplies scripts and recipes; **it distributes no Windows binaries**.
You download the media from Microsoft and keep the installed image in your own
private registry. Windows workspace catalog/API/UI integration is still in
development: the result here is a direct KubeVirt VM in your cluster.

## 1. Prepare the cluster, workstation and inputs

You need:

- Linux amd64 workers with KVM and a Windows 11-eligible physical CPU; KubeVirt
  1.9.x and CDI 1.61.0 are the initial proof target.
- Working persistent root storage and persistent EFI/TPM backend storage. Read
  [the deployment prerequisites](https://github.com/kube-workspaces/deploy/blob/main/docs/windows-vm.md),
  especially the RWO/StorageProfile caveat. Node-local disks require root, state
  and media placement on the same worker.
- `kubectl`, version-matched `virtctl`, Python 3, `qemu-img` (usually the
  `qemu-utils` package), `guestfish` and `virt-win-reg` (usually
  `libguestfs-tools`), and either Docker or
  [`crane`](https://github.com/google/go-containerregistry/tree/main/cmd/crane).
  The examples use the Docker-free route to avoid a second large builder cache.
- Checkouts of `image-catalog` and `deploy` at recorded commits.
- Windows Pro/Enterprise installation and virtualisation entitlements. Activation
  and remote-access rights are operator responsibilities; Sysprep does not grant
  a license. Keep keys and entitlement records outside source control.
- Capacity for a 4-vCPU/8Gi guest plus launcher overhead, an 80Gi guest disk,
  installer/driver PVCs, CDI scratch space, and a backend-state PVC. If needed,
  `--cpus 2 --memory-gi 4` is the validation floor. Test clones sequentially on
  constrained workers. Check **physical** memory/disk headroom as well as quotas.
- A private local working directory with room for the export, QCOW2 and layer.
  An 80Gi raw export, about 18Gi QCOW2 and about 10Gi layer can coexist; allow at
  least 150Gi free for this example. Actual usage depends on updates/software.
  Avoid exporting, converting or building large images on a control-plane node.

Download Windows 11 x64 from Microsoft's
[official ISO download page](https://www.microsoft.com/software-download/windows11).
Select a supported release and edition available under your entitlement. For
Enterprise use Microsoft's appropriate licensed distribution channel. Do not
substitute an unofficial preinstalled disk. Record the ISO name, source, SHA256,
edition, language and exact build; Microsoft's newest download can change.
Use Microsoft's download-page hash verification where available.

Download signed VirtIO media from the
[Fedora virtio-win distribution](https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/).
Pin an exact version rather than a moving `latest` URL; the initial driver proof
used **0.1.271-1**. Inspect that the ISO has `viostor`, `NetKVM`, `vioserial` and
`Balloon` under `w11/amd64`, and the guest-agent installer. Record its SHA256 and
verify driver signing with Secure Boot enabled during guest validation.

Run from your image-catalog checkout (replace example paths/settings):

```sh
CATALOG="$PWD"
DEPLOY="$(realpath ../deploy)"
PRIVATE="$HOME/windows11-private-build"
NODE=your-eligible-worker
STORAGE_CLASS=your-storage-class
NS=windows11-proof
umask 077
mkdir -m 700 "$PRIVATE"
sha256sum /path/to/windows11.iso /path/to/virtio-win.iso
python3 "$DEPLOY/scripts/windows-vm-proof.py" preflight \
  --node "$NODE" --storage-class "$STORAGE_CLASS"
kubectl create namespace "$NS"
```

The preflight is read-only and does not certify Windows CPU eligibility or free
physical capacity. Stop and resolve its errors before proceeding.

## 2. Upload the installer and driver media

Use a trusted HTTPS CDI upload proxy, for example
`https://upload.example.com`. Configure its CA trust; do not default to
`--insecure`. Large media transfers need a reliable direct endpoint. A management
proxy or short-lived port-forward may time out even while Kubernetes is healthy.
Use your distribution's supported CDI upload exposure and remove any temporary
endpoint when finished.

For node-local storage, pre-create the media PVCs with the selected-node
annotation so the upload and build VM use the same worker:

```sh
for entry in windows11-iso:10Gi virtio-iso:2Gi; do
  NAME=${entry%:*}
  SIZE=${entry#*:}
  kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: $NAME
  namespace: $NS
  annotations:
    volume.kubernetes.io/selected-node: $NODE
    cdi.kubevirt.io/storage.upload.target: ""
spec:
  storageClassName: $STORAGE_CLASS
  accessModes: [ReadWriteOnce]
  volumeMode: Filesystem
  resources:
    requests:
      storage: $SIZE
EOF
done
virtctl image-upload pvc windows11-iso -n "$NS" --no-create \
  --image-path=/path/to/windows11.iso --uploadproxy-url=https://upload.example.com
virtctl image-upload pvc virtio-iso -n "$NS" --no-create \
  --image-path=/path/to/virtio-win.iso --uploadproxy-url=https://upload.example.com
kubectl get pvc -n "$NS"
```

Use default `kubevirt` content type, not archive content type. Increase PVC sizes
if your media needs it. Check their PV node affinity before starting the VM.

## 3. Create a disposable installer VM

Generate a unique local account and native answer file in the private directory:

```sh
python3 "$CATALOG/windows11/render-bootstrap.py" --mode install \
  --namespace "$NS" --secret-name build-bootstrap --hostname KW-BUILD \
  --image-name 'Windows 11 Pro' --output-dir "$PRIVATE/build-bootstrap"
kubectl apply -f "$PRIVATE/build-bootstrap/bootstrap-secret.json"
python3 "$DEPLOY/scripts/windows-vm-proof.py" render --mode install \
  --namespace "$NS" --node "$NODE" --storage-class "$STORAGE_CLASS" \
  --name windows11-build --installer-pvc windows11-iso --drivers-pvc virtio-iso \
  --sysprep-secret build-bootstrap > "$PRIVATE/install.json"
kubectl apply --dry-run=server -f "$PRIVATE/install.json"
kubectl apply -f "$PRIVATE/install.json"
virtctl start windows11-build -n "$NS"
virtctl vnc windows11-build -n "$NS"
```

**Install mode wipes disk 0. Use only this disposable blank-root fixture.** The
renderer selects the exact WIM image name, defaults to en-US/UTC, does not enable
auto-logon and does not bypass Windows hardware requirements. Adjust edition and
locale with supported Windows answer-file settings for your own media; validate
against that build using Windows System Image Manager.

The Secret includes `autounattend.xml` and `configure.ps1`. WinPE loads viostor;
offline servicing stages boot-critical drivers into the installed root. The
specialise pass installs remaining drivers and QEMU guest agent. Loading a driver
only with `drvload` can produce `INACCESSIBLE_BOOT_DEVICE` on first boot. The
specialise command is deliberately short: Windows limits its Path to 259
characters, so keep the helper script on the Sysprep CD.

The account password is in `$PRIVATE/build-bootstrap/credentials.json`, mode
0600. Read it privately and sign in over VNC; do not paste it into logs/issues.
Kubernetes Secrets and guest answer-file caches contain bootstrap credentials.

## 4. Validate the real guest before sealing

From elevated PowerShell, copy/run `windows11/Collect-Evidence.ps1` using your
normal private file-transfer mechanism, then run:

```powershell
Confirm-SecureBootUEFI
Get-Tpm
Get-Service QEMU-GA
Get-BitLockerVolume -MountPoint C:
dxdiag /t C:\dxdiag.txt
.\Collect-Evidence.ps1 -OutputPath C:\proof-evidence.json
```

Require Secure Boot true, ready TPM 2.0, signed viostor/NetKVM/vioserial drivers,
working DHCP/DNS and a connected guest agent. Also check from the workstation:

```sh
kubectl get vmi windows11-build -n "$NS" -o jsonpath='{.status.conditions}'
```

Require `AgentConnected=True`, not just a running Windows service. Validate
login, keyboard/layout, absolute pointer, Ctrl+Alt+Delete and reconnect. Record
`dxdiag` graphics limitations; a usable VGA/basic desktop does not establish GPU
acceleration, audio, clipboard or automatic resize.

Install intended updates and test a guest reboot. Then test graceful
`virtctl stop`/`start` with installer/driver/Sysprep media detached while stopped.
Record a changed VMI UID and unchanged VM/root/state PVC identities. Verify a
guest file and, where required, a TPM-bound test key survive. Clean up test keys
before sealing. Keep Windows Update and BitLocker recovery results separate from
basic persistence evidence.

The retained `Test-PersistentState.ps1` helper creates a non-exportable machine
RSA key in **Microsoft Platform Crypto Provider** and a root-file record of its
public-key hash/marker. In elevated PowerShell, run `-Action Create` before the
stop and `-Action Verify` after the VMI UID changes. Verification reopens the
existing key, checks the same public hash/root marker and signs/verifies a new
nonce; it never recreates a missing key. Run `-Action Remove` before sealing a
build root. This establishes TPM-key/root persistence, not BitLocker recovery.

## 5. Generalise an unencrypted, credential-free template

Do this in the disposable build guest, after the intended updates finish:

1. Check `Get-BitLockerVolume -MountPoint C:`. **ProtectionStatus Off alone is
   insufficient**: Windows can encrypt the disk while protection remains Off.
   If encrypted, run `Disable-BitLocker -MountPoint C:` and wait for
   `VolumeStatus=FullyDecrypted`, `EncryptionPercentage=0`, protection Off.
2. Prevent automatic device encryption during template preparation with the
   supported Windows policy for the selected build, e.g. from elevated PowerShell:

   ```powershell
   New-Item 'HKLM:\SYSTEM\CurrentControlSet\Control\BitLocker' -Force
   New-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\BitLocker' `
     -Name PreventDeviceEncryption -PropertyType DWord -Value 1 -Force
   ```

   Record that template setting. Each clone may later explicitly enable its own
   encryption and independently retain recovery material; never clone the build
   VM's TPM/BitLocker secrets.
3. Remove build-only accounts/profiles, credentials, account tokens, private
   downloads, test TPM keys and cached answer files. Remove build activation
   material as required by your licensing process. Check Panther and Sysprep
   answer-file caches, including `C:\Windows\Panther\unattend.xml` and
   `C:\Windows\System32\Sysprep\unattend.xml`; a stale answer file can override
   clone provisioning. Use an appropriate temporary administrative context to
   remove the build account rather than retaining it in the template.
4. Set the VM to Manual before Sysprep so an automatic run strategy cannot restart
   the generalised root:

   ```sh
   kubectl patch vm windows11-build -n "$NS" --type merge \
     -p '{"spec":{"runStrategy":"Manual"}}'
   ```

5. From elevated PowerShell run:

   ```powershell
   C:\Windows\System32\Sysprep\Sysprep.exe /generalize /shutdown /oobe /mode:vm
   ```

   Confirm successful shutdown; if Sysprep fails inspect its Panther logs and
   resolve the actual error. **Do not boot the sealed root again.**
6. After guest shutdown, set `runStrategy: Halted` and wait for the VMI to be
   deleted before offline export:

   ```sh
   kubectl patch vm windows11-build -n "$NS" --type merge \
     -p '{"spec":{"runStrategy":"Halted"}}'
   kubectl wait --for=delete vmi/windows11-build -n "$NS" --timeout=240s
   ```

## 6. Export only the stopped root and convert locally

Use the root PVC as the export source so no backend TPM/EFI PVC is included:

```sh
virtctl vmexport download windows11-root-export -n "$NS" \
  --pvc=windows11-build-rootdisk --port-forward --format=raw \
  --output="$PRIVATE/exported-root.img" --delete-vme
qemu-img convert -p -O qcow2 "$PRIVATE/exported-root.img" "$PRIVATE/sealed-root.qcow2"
python3 "$CATALOG/windows11/prepare-sealed-root.py" \
  --disk "$PRIVATE/sealed-root.qcow2" --output "$PRIVATE/disk.qcow2"
qemu-img check "$PRIVATE/disk.qcow2"
qemu-img info --output=json "$PRIVATE/disk.qcow2"
sha256sum "$PRIVATE/disk.qcow2"
```

This requires the cluster's KubeVirt VM export support. Configure it through your
operator's version-matched deployment if absent, or use offline `virtctl guestfs`
and your supported storage export process. Do not hot-export a running root.
Do not copy the state PVC, ISO media or bootstrap Secret into the export.

The QCOW2 must have **no backing file**, no QCOW2-level encryption and the
intended virtual size. Guest BitLocker decryption is a separate guest check;
`qemu-img` cannot establish it. CDI adds filesystem-overhead capacity around the
80Gi virtual disk; check the actual requested/allocated PVC sizes and free space.
After verifying the standalone QCOW2 and retaining the cluster source, you can
remove the redundant raw export to reclaim space.

### Native answer-file discovery in the sealed root

The tested Windows build did not implicitly discover the attached SATA answer
CD during post-Sysprep specialise/OOBE, although `D:\autounattend.xml` was present.
`prepare-sealed-root.py` therefore creates a **new derivative** with the supported
`HKLM\SYSTEM\Setup\UnattendFile` pointer to `D:\autounattend.xml`. Windows uses
that file through its native setup engine. The pointer contains no password or
per-clone identity; the actual answer file still comes from each clone's Secret.
See Microsoft's [implicit answer-file search order](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-setup-automation-overview#implicit-answer-file-search-order).

The script checks the source's `IMAGE_STATE_GENERALIZE_RESEAL_TO_OOBE`, modifies a
temporary copy-on-write overlay, removes cached/backup answer files (including
`unattend-original.xml` that can survive Sysprep), then flattens a standalone
QCOW2. The original sealed input stays unchanged. Run this **offline, after
Sysprep**, and package the derivative, not the original export. Do not boot either
template. Keep clone hardware at one root disk plus one SATA Sysprep CD, which
must receive drive letter D. If changing that profile, select and validate the
appropriate `--sysprep-drive`; silently adding installer/driver CDs can break the
pointer. Remove the pointer and setup caches after clone setup completes.

## 7. Package and publish privately

Create a **private** registry repository before publishing. Use a token scoped
for your registry operation. Keep its Docker-format auth in a private directory:

```sh
export DOCKER_CONFIG="$PRIVATE/registry-auth"
mkdir -m 700 "$DOCKER_CONFIG"
crane auth login registry.example.com -u YOUR_USER --password-stdin
IMAGE=registry.example.com/private/windows11:YOUR_RECIPE_BUILD
python3 "$CATALOG/windows11/package-layer.py" \
  --disk "$PRIVATE/disk.qcow2" --output "$PRIVATE/root-layer.tar.gz"
crane append --oci-empty-base --platform linux/amd64 \
  --new_layer "$PRIVATE/root-layer.tar.gz" --new_tag "$IMAGE"
crane digest "$IMAGE"
```

Enter the registry token through standard input and finish input as prompted by
your shell/tool. The packaging script checks the QCOW2, refuses overwrites and
requires conservative free-space headroom. Its only layer entries are `/disk`
(UID/GID 107, mode 0755) and `/disk/disk.qcow2` (UID/GID 107, mode 0440). No
Windows data is added to this repository. Keep the disk offline during packaging.

Alternatively, copy `windows11/Dockerfile` and `disk.qcow2` into a separate private
build context, then use `docker build --platform linux/amd64` and `docker push`.
Account for Docker cache space as well as the disk and archive; pruning the cache
during an upload can discard the only locally built image.

An interrupted large registry push is not a completed artifact. Retry against
the same repository/layer; registries can reuse completed blobs, but unfinished
uploads may need restarting. Check the registry's upload limits/timeouts and use
its supported resumable/chunked uploader if single-request pushes stall. For
example, [GitHub Container Registry documents a 10GB per-layer limit and a
10-minute upload timeout](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#troubleshooting).
A Windows disk layer can exceed either limit. Select a private registry that
accommodates the measured layer size and transfer duration; Docker-free packaging
does not remove registry limits, and not all registries implement resumable
chunks. Do not
promote the image until its manifest digest can be resolved and its repository
visibility is confirmed private.

Record the immutable reference `registry.example.com/private/windows11@sha256:...`,
disk hash, media/driver hashes, runtime versions, build/edition, recipe commit and
validation results in private build metadata.

## 8. Import and provision two independent clones

Create the CDI registry import Secret from the actual Docker-format auth file:

```sh
python3 "$CATALOG/windows11/render-import-secret.py" \
  --docker-config "$DOCKER_CONFIG/config.json" --registry-host registry.example.com \
  --namespace "$NS" --secret-name registry-import --output "$PRIVATE/registry-import.json"
kubectl apply -f "$PRIVATE/registry-import.json"
```

The file must contain usable registry auth, not only a workstation
`credsStore`/`credHelpers` reference. `crane auth login` in the dedicated directory
above produces inline auth. The renderer creates an Opaque Secret with
`accessKeyId` (registry username) and `secretKey` (password/token), the keys
required by **CDI 1.61's pod importer**. A Secret containing only
`.dockerconfigjson` produces `CreateContainerConfigError` because those keys are
missing. CDI's `registry.secretRef` supplies importer auth;
ordinary Pod `imagePullSecrets` do not replace it.

If the registry uses a private CA, also create a same-namespace ConfigMap:

```sh
kubectl create configmap registry-ca -n "$NS" --from-file=ca.crt=/path/to/registry-ca.crt
```

Add `--import-cert-configmap registry-ca` to the clone render command below.
This configures CDI importer trust, independently from workstation/Docker trust.
Verify the registry's certificate and hostname; do not disable TLS verification.

Set `SEALED_IMAGE` to your complete immutable OCI reference, then repeat this for
clone-a and clone-b (on constrained workers import/boot/validate/stop one first):

```sh
SEALED_IMAGE=registry.example.com/private/windows11@sha256:YOUR_FULL_DIGEST
CLONE=clone-a
HOSTNAME=KW-CLONE-A
python3 "$CATALOG/windows11/render-bootstrap.py" --mode clone \
  --namespace "$NS" --secret-name "$CLONE-bootstrap" --hostname "$HOSTNAME" \
  --output-dir "$PRIVATE/$CLONE-bootstrap"
kubectl apply -f "$PRIVATE/$CLONE-bootstrap/bootstrap-secret.json"
python3 "$DEPLOY/scripts/windows-vm-proof.py" render --mode clone \
  --namespace "$NS" --node "$NODE" --storage-class "$STORAGE_CLASS" \
  --name "windows11-$CLONE" --image "$SEALED_IMAGE" \
  --import-secret registry-import --sysprep-secret "$CLONE-bootstrap" \
  > "$PRIVATE/$CLONE.json"
kubectl apply --dry-run=server -f "$PRIVATE/$CLONE.json"
kubectl apply -f "$PRIVATE/$CLONE.json"
virtctl start "windows11-$CLONE" -n "$NS"
kubectl get dv,pvc,pods -n "$NS"
virtctl vnc "windows11-$CLONE" -n "$NS"
```

Each render makes a new firmware UUID/MAC; **save and reuse** each manifest rather
than regenerating its identity on restart. Clone mode does not partition disks
or need installer/driver media. Each bootstrap directory has independent initial
credentials. Confirm both guests finish OOBE, accept their own password, have
distinct computer names/account SIDs/firmware identities/TPMs, and connect their
guest agent. An imported disk or `VMI Running` alone is not proof of a ready
Windows desktop.

After confirmed setup, clean guest answer-file caches. Stop the clone, wait for
VMI deletion, remove `sysprep` from both its saved manifest's disks and volumes,
apply the saved manifest while stopped, then delete that clone's bootstrap
Secret. Restart and require no setup replay. Verify files and TPM-bound state
across changed VMI UIDs. Keep recovery material private for any BitLocker tests.

Before detaching bootstrap media, remove the explicit discovery pointer from an
elevated PowerShell session in the provisioned clone:

```powershell
.\Remove-Bootstrap.ps1
```

The retained helper requires `IMAGE_STATE_COMPLETE`, removes the explicit
`HKLM:\SYSTEM\Setup\UnattendFile` pointer and cached/backup `*unattend*.xml`
files from the Panther/Sysprep setup directories. Do not remove these during an
active configuration pass. Then detach media/delete the Secret as described above.

Record actual private-CDI-import success, import/desktop timings, graceful
stop/start, Windows Update behaviour, display limitations and ownership cleanup.
Only then mark the image accepted for the tested VM profile. Product-managed
Windows workspace support requires the remaining controller/API/UI integration.

## Troubleshooting and cleanup

| Symptom | Check |
|---|---|
| Root/state/media PVCs cannot bind together | Node affinity, selected-node annotations, StorageProfile/access modes, physical capacity and quota. |
| Secure Boot or TPM missing | EFI persistent state, SMM, persistent TPM, signed drivers and eligible worker hardware; do not bypass requirements. |
| `INACCESSIBLE_BOOT_DEVICE` on first boot | viostor must be staged into the installed root, not only loaded into WinPE. |
| Specialise fails before agent setup | Keep the command below 259 characters; ensure Secret-backed `configure.ps1` is present. Inspect setup logs privately. |
| Driver helper reports exit 259 | It can mean already-current packages; the shipped helper verifies DriverStore membership rather than ignoring arbitrary failures. |
| VMI runs but no agent | Signed vioserial, installed QEMU-GA service and `AgentConnected` condition. |
| Clone repeats old account/setup | Cached/baked-in answer file, non-generalised root or sealed root restarted before packaging. |
| Clone shows interactive OOBE despite attached answer CD | Use the offline sealed-root preparation step; verify the registry pointer's drive letter and remove stale answer-file backups. |
| BitLocker Off but disk not decrypted | Check `VolumeStatus` and encryption percentage; wait for full decryption before sealing. |
| Large export/push stalls | Direct trusted endpoint, upload limits/timeouts, local free space and supported resumable uploader; retain the source disk. |
| CDI import unauthorized | Same-namespace `registry.secretRef`, correct inline auth/registry host and token pull permission. |
| Importer `CreateContainerConfigError` | CDI 1.61 pod import requires `accessKeyId` and `secretKey`; a Docker pull Secret alone has different keys. |

Stop each disposable VM and wait for VMI deletion before deleting it. Confirm its
owned root DataVolume/PVC and backend-state PVC disappear. Uploaded media PVCs and
manual bootstrap/import Secrets are independent: remove them separately after
saving the accepted artifact/evidence. Remove temporary upload/export resources
and local registry auth when finished. Retain only the private artifacts and
records your operating process needs.
