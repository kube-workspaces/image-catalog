#!/usr/bin/env python3
"""Package a sealed, standalone QCOW2 as a containerDisk layer without Docker.

Only packages the disk supplied by the operator; does not install Windows,
contact a registry, or include credentials. Requires qemu-img on PATH.
"""
import argparse
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile


def package(disk, output):
    disk = disk.resolve(strict=True)
    if not disk.is_file():
        raise ValueError("disk must be a regular file")
    if output.exists():
        raise ValueError("output already exists; choose a new path")
    info = json.loads(subprocess.check_output(
        ["qemu-img", "info", "--output=json", str(disk)], text=True))
    if info.get("format") != "qcow2" or info.get("backing-filename"):
        raise ValueError("disk must be standalone QCOW2 with no backing file")
    if info.get("encrypted") or info.get("format-specific", {}).get("data", {}).get("encrypt"):
        raise ValueError("QCOW2-level encryption is not supported")
    subprocess.run(["qemu-img", "check", str(disk)], check=True)
    # Compression varies; reserve the uncompressed disk's file size plus margin.
    if shutil.disk_usage(output.parent).free < disk.stat().st_size + 64 * 1024 * 1024:
        raise ValueError("insufficient free space for layer; use a larger filesystem")
    partial = output.with_name(output.name + ".partial")
    descriptor = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as destination:
            with gzip.GzipFile(filename="", fileobj=destination, mode="wb",
                               compresslevel=1, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT) as archive:
                    directory = tarfile.TarInfo("disk")
                    directory.type = tarfile.DIRTYPE
                    directory.mode = 0o755
                    directory.uid = directory.gid = 107
                    archive.addfile(directory)
                    entry = tarfile.TarInfo("disk/disk.qcow2")
                    entry.size = disk.stat().st_size
                    entry.mode = 0o440
                    entry.uid = entry.gid = 107
                    with disk.open("rb") as source:
                        archive.addfile(entry, source)
        # Publish atomically without overwriting an existing archive.
        os.link(partial, output)
    finally:
        partial.unlink()
    return {"virtualSize": info["virtual-size"], "layerBytes": output.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disk", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path,
                        help="new .tar.gz path in an existing private directory")
    args = parser.parse_args()
    try:
        record = package(args.disk, args.output)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Packaging failed: {error}\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
