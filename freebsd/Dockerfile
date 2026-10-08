# Official FreeBSD cloud image packaged as a KubeVirt containerDisk.
FROM alpine:3.23 AS download
RUN apk add --no-cache curl xz qemu-img
WORKDIR /download
RUN curl --fail --silent --show-error --location --retry 3 --output disk.qcow2.xz \
      https://download.freebsd.org/releases/VM-IMAGES/15.1-RELEASE/amd64/Latest/FreeBSD-15.1-RELEASE-amd64-BASIC-CLOUDINIT-ufs.qcow2.xz \
    && printf '%s  disk.qcow2.xz\n' \
      e4ca4db889f8559c9b9dfcacc70405c038476f4b6d41649b152d3809a2ed9e1f \
      | sha256sum -c - \
    && xz --decompress disk.qcow2.xz \
    && qemu-img check disk.qcow2 \
    && qemu-img convert -O qcow2 -c disk.qcow2 compact.qcow2 \
    && rm disk.qcow2

FROM scratch
COPY --from=download --chown=107:107 --chmod=0550 /download/compact.qcow2 /disk/disk.qcow2
