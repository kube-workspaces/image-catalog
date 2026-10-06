#!/usr/bin/env python3
"""Create a credential-free bootstrap-ready derivative of a sealed Windows root.

Requires qemu-img, guestfish and virt-win-reg (libguestfs-tools). The input is
read-only backing storage for a temporary overlay; only the new output changes.
Never boot or concurrently modify either disk during preparation.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def run(command, **kwargs):
    return subprocess.run(command, check=True, text=True, **kwargs)


def prepare(disk, output, drive):
    disk = disk.resolve(strict=True)
    if output.exists():
        raise ValueError("output already exists; choose a new path")
    info = json.loads(subprocess.check_output(["qemu-img", "info", "--output=json", str(disk)], text=True))
    if info.get("format") != "qcow2" or info.get("backing-filename"):
        raise ValueError("input must be standalone QCOW2")
    state = subprocess.check_output([
        "virt-win-reg", "--unsafe-printable-strings", str(disk),
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\State"], text=True)
    if not re.search(r'^"ImageState"=str\(1\):"IMAGE_STATE_GENERALIZE_RESEAL_TO_OOBE"$', state, re.MULTILINE):
        raise ValueError("input is not a Sysprep-generalised, shut-down OOBE template")
    if shutil.disk_usage(output.parent).free < info.get("actual-size", disk.stat().st_size) + 1024**3:
        raise ValueError("insufficient space for standalone derivative")
    with tempfile.TemporaryDirectory(prefix="windows-sealed-", dir=output.parent) as directory:
        root = Path(directory)
        overlay = root / "overlay.qcow2"
        run(["qemu-img", "create", "-f", "qcow2", "-F", "qcow2", "-b", str(disk), str(overlay)])
        pointer = root / "bootstrap.reg"
        pointer.write_text('Windows Registry Editor Version 5.00\n\n'
                           '[HKEY_LOCAL_MACHINE\\SYSTEM\\Setup]\n'
                           f'"UnattendFile"="{drive}:\\\\autounattend.xml"\n')
        run(["virt-win-reg", "--merge", str(overlay), str(pointer)])
        # Sysprep can retain unattend-original.xml even after the active answer
        # file is removed. Purge backup/cache variants without reading secrets.
        caches = []
        for base in ("/Windows/Panther", "/Windows/System32/Sysprep"):
            listing = run(["guestfish", "--ro", "-a", str(overlay), "-i", "find", base],
                          stdout=subprocess.PIPE).stdout
            # guestfish find returns paths relative to the supplied directory.
            caches.extend(base + line for line in listing.splitlines()
                          if line.startswith("/") and line.lower().endswith(".xml")
                          and "unattend" in line.rsplit("/", 1)[-1].lower())
        caches = sorted(set(caches))
        caches += ["/autounattend.xml", "/unattend.xml"]
        commands = "".join("rm-f " + json.dumps(path) + "\n" for path in caches)
        run(["guestfish", "--rw", "-a", str(overlay), "-i"], input=commands)
        standalone = root / "prepared.qcow2"
        run(["qemu-img", "convert", "-O", "qcow2", str(overlay), str(standalone)])
        run(["qemu-img", "check", str(standalone)])
        standalone.chmod(0o600)
        os.link(standalone, output)
    return {"virtualSize": info["virtual-size"], "answerFilePathsScrubbed": len(caches),
            "bootstrapSource": f"{drive}:\\autounattend.xml"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disk", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new QCOW2 in an existing private directory")
    parser.add_argument("--sysprep-drive", choices=tuple("DEFGHIJKLMNOPQRSTUVWXYZ"), default="D",
                        help="CD-ROM drive letter in clone profile (root plus one Sysprep CD defaults to D)")
    args = parser.parse_args()
    os.umask(0o077)
    try:
        record = prepare(args.disk, args.output, args.sysprep_drive)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Sealed-root preparation failed: {error}\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
