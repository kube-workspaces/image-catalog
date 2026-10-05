# Build from a private context containing ONLY this file and sealed disk.qcow2.
# The disk must be a standalone, generalised Windows root (no backing file).
FROM scratch
# COPY can apply this mode to the newly created /disk parent too. Preserve
# search permission so UID 107 can actually reach the read-only disk file.
COPY --chown=107:107 --chmod=0550 disk.qcow2 /disk/disk.qcow2
