# MS-DOS 6.22 containerDisk Image

.PHONY: help all docker-build docker-login docker-push patch-cd-rom mount-raw mount-vhd unmount-raw unmount-vhd clean check-deps docker-show-image-files

# Docker tag variable (can be overridden)
DOCKER_TAG ?= flaccid/containerdisk-ms-dos-622

# Disk image consumed by the Docker build, and the byte offset of its FAT16
# partition (LBA start 63 * 512) for mtools access without root mounts
DISK_IMAGE ?= ms-dos-622.raw
PARTITION_OFFSET := 32256

# Default target
all: help

# Help target - displays available commands
help:
	@echo "MS-DOS 6.22 Image"
	@echo "=================="
	@echo ""
	@echo "Available targets:"
	@echo "  make all                     - Display help (default target)"
	@echo "  make check-deps              - Check for required dependencies"
	@echo "  make clean                   - Clean up all mounts"
	@echo "  make docker-build            - Build the MS-DOS 6.22 Docker image"
	@echo "  make patch-cd-rom            - Disable the CD-ROM boot driver in the disk image"
	@echo "  make docker-login            - Log into Docker Hub (prompts for credentials)"
	@echo "  make docker-push             - Push the built Docker image to Docker Hub"
	@echo "  make docker-show-image-files - List files in the built Docker image"
	@echo "  make help                    - Show this help message"
	@echo "  make mount-raw               - Mount the RAW disk image"
	@echo "  make mount-vhd               - Mount the VHD disk image"
	@echo "  make unmount-raw             - Unmount the RAW disk image"
	@echo "  make unmount-vhd             - Unmount the VHD disk image"
	@echo ""
	@echo "Image files (automatically detected):"
	@echo "  ms-dos-622.raw       - RAW disk image"
	@echo "  ms-dos-622.vhd       - VHD disk image"

# Check for required dependencies
check-deps:
	@command -v losetup >/dev/null 2>&1 || { echo "Error: losetup not found. Install util-linux."; exit 1; }
	@command -v mount >/dev/null 2>&1 || { echo "Error: mount not found. This is typically pre-installed."; exit 1; }
	@echo "All required dependencies are installed."

# Clean up all mounts and loop devices
clean: unmount-raw unmount-vhd
	@echo "Cleaning up..."
	@if sudo losetup -a | grep -q ms-dos-622; then \
		sudo DEV=$(sudo losetup -p 2>/dev/null | grep ms-dos-622 | cut -d: -f1) && \
		if [ -n "$$DEV" ]; then \
			sudo losetup -d $$DEV && echo "All loop devices detached."; \
		else \
			sudo DEV=$(sudo losetup -a | grep ms-dos-622 | cut -d: -f1) && \
			if [ -n "$$DEV" ]; then \
				sudo losetup -d /dev/$$DEV && echo "All loop devices detached."; \
			else \
				echo "Failed to get loop devices. Detaching all matching ms-dos-622 devices..."; \
				sudo DEV=$(sudo losetup -a | grep ms-dos-622 | cut -d: -f1) && \
				for dev in $$DEV; do sudo losetup -d /dev/$$dev 2>/dev/null || true; done && \
				echo "Loop devices detached."; \
			fi; \
		fi; \
	else \
		echo "No loop devices found to detach, or losetup -p not available. Detaching manually..."; \
		sudo DEV=$(sudo losetup -a | grep ms-dos-622 | cut -d: -f1) && \
		if [ -n "$$DEV" ]; then \
			sudo losetup -d /dev/$$DEV && echo "All loop devices detached."; \
		else \
			echo "No loop devices found for ms-dos-622."; \
		fi; \
	fi

# Disable the CD-ROM boot drivers inside the disk image.
#
# The guest runs on machine type q35 with no CD device, and the OAK driver
# (C:\DOS\cd1.SYS) only probes legacy ISA IDE ports, so it always fails with
# "No drives found, aborting installation" and MSCDEX then aborts the boot
# with "Device driver not found: 'BANANA'". Commenting the two lines out
# keeps the boot clean while preserving the original entries for reference.
# Idempotent: already commented lines no longer match.
patch-cd-rom:
	@command -v mcopy >/dev/null 2>&1 || { echo "Error: mcopy not found. Install mtools (apt install mtools)."; exit 1; }
	@command -v sed >/dev/null 2>&1 || { echo "Error: sed not found."; exit 1; }
	@set -e; \
	mount_spec="$(DISK_IMAGE)@@$(PARTITION_OFFSET)"; \
	tmpdir=$$(mktemp -d); \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	for f in CONFIG.SYS AUTOEXEC.BAT; do \
		mcopy -i "$$mount_spec" ::$$f "$$tmpdir/$$f"; \
		sed -i \
			-e 's|^\(DEVICE=C:\\DOS\\cd1\.SYS .*\)$$|rem \1|' \
			-e 's|^\(MSCDEX\.EXE .*\)$$|rem \1|' \
			"$$tmpdir/$$f"; \
		mcopy -i "$$mount_spec" -o "$$tmpdir/$$f" ::$$f; \
	done; \
	echo "CD-ROM driver lines disabled in $(DISK_IMAGE) (CONFIG.SYS, AUTOEXEC.BAT)"

docker-build: patch-cd-rom
	docker build -t $(DOCKER_TAG) .

docker-login:
	@echo "Logging into Docker Hub..."
	@docker login

docker-push:
	@if [ -z "$$(docker images -q $(DOCKER_TAG) 2>/dev/null)" ]; then \
		echo "Error: No '$(DOCKER_TAG)' image found. Run 'make docker-build' first."; \
		exit 1; \
	fi
	@echo "Pushing Docker image '$(DOCKER_TAG)' to Docker Hub..."
	docker push $(DOCKER_TAG)
	@echo "Docker image '$(DOCKER_TAG)' pushed successfully to Docker Hub"

# Show files and layer analysis using dive (Container Image Visualizer)
docker-show-image-files: docker-build
	@if [ -z "$$(docker images -q $(DOCKER_TAG) 2>/dev/null)" ]; then \
		echo "Error: No '$(DOCKER_TAG)' image found. Run 'make docker-build' first."; \
		exit 1; \
	fi
	@echo "Analyzing MS-DOS 6.22 Docker image layers with dive:"
	@dive ms-dos-622:latest || { echo "dive failed or not installed"; exit 1; }

# Flush generated/downloaded files
flush:
	rm -Rf ./Microsoft* msdos-622.7z ./msdos-622* ./*.raw ./*.vhd *.7z *.deb

# Mount the RAW disk image
mount-raw: check-deps
	@if [ ! -f ms-dos-622.raw ]; then \
		echo "Error: ms-dos-622.raw not found in current directory."; \
		exit 1; \
	fi
	@echo "Mounting RAW image (ms-dos-622.raw)..."
	@sudo losetup --find --show --partscan ms-dos-622.raw || { echo "Failed to create loop device"; exit 1; }
	@if sudo blkid /dev/mapper/ms-dos-622-* >/dev/null 2>&1; then \
		sudo mkdir -p /mnt/ms-dos-622 && \
		sudo mount -t vfat /dev/mapper/ms-dos-622-1 /mnt/ms-dos-622 && \
		echo "RAW image mounted successfully at /mnt/ms-dos-622"; \
	else \
		echo "Partition mapper not found. Creating block device symlink..." && \
		sudo mkdir -p /dev/disk/by-blockdevice 2>/dev/null || true && \
		sudo rm -f /dev/disk/by-blockdevice/ms-dos-622 2>/dev/null || true && \
		sudo ln -s /dev/loop$(sudo losetup -p 2>/dev/null | grep ms-dos-622.raw | cut -d: -f1 | sed 's/:.*//') /dev/disk/by-blockdevice/ms-dos-622 2>/dev/null || true && \
		sudo mkdir -p /mnt/ms-dos-622 && \
		sudo mount -t vfat /dev/mapper/ms-dos-622-1 /mnt/ms-dos-622 2>/dev/null || \
		echo "Mount failed. Please try manually:"; \
	fi

# Mount the VHD disk image (converts to raw first if needed)
mount-vhd: check-deps
	@if [ ! -f ms-dos-622.vhd ]; then \
		echo "Error: ms-dos-622.vhd not found in current directory."; \
		exit 1; \
	fi
	@echo "Mounting VHD image (ms-dos-622.vhd)..."
	@sudo losetup --find --show --partscan ms-dos-622-converted.raw || { echo "Failed to create loop device"; exit 1; }
	@if sudo blkid /dev/mapper/ms-dos-622-* >/dev/null 2>&1; then \
		sudo mkdir -p /mnt/ms-dos-622 && \
		sudo mount -t vfat /dev/mapper/ms-dos-622-1 /mnt/ms-dos-622 && \
		echo "VHD image mounted successfully at /mnt/ms-dos-622"; \
	else \
		echo "Partition mapper not found. Creating block device symlink..." && \
		sudo mkdir -p /dev/disk/by-blockdevice 2>/dev/null || true && \
		sudo rm -f /dev/disk/by-blockdevice/ms-dos-622 2>/dev/null || true && \
		sudo ln -s /dev/loop$(sudo losetup -p 2>/dev/null | grep ms-dos-622-converted.raw | cut -d: -f1 | sed 's/:.*//') /dev/disk/by-blockdevice/ms-dos-622 2>/dev/null || true && \
		sudo mkdir -p /mnt/ms-dos-622 && \
		sudo mount -t vfat /dev/mapper/ms-dos-622-1 /mnt/ms-dos-622 2>/dev/null || \
		echo "Mount failed. Please try manually:"; \
	fi

# Unmount the RAW disk image
unmount-raw:
	@echo "Unmounting RAW image..."
	@if sudo mountpoint -q /mnt/ms-dos-622; then \
		sudo guestunmount /mnt/ms-dos-622 2>/dev/null || sudo umount -l /mnt/ms-dos-622 && \
		echo "Filesystem unmounted."; \
	else \
		echo "Image is not mounted at /mnt/ms-dos-622."; \
	fi
	@if sudo losetup -a | grep -q ms-dos-622.raw; then \
		sudo DEV=$(sudo losetup -p 2>/dev/null | grep ms-dos-622.raw | cut -d: -f1) && \
		if [ -n "$$DEV" ]; then \
			sudo losetup -d $$DEV && echo "Loop device detached."; \
		else \
			sudo DEV=$(sudo losetup -a | grep ms-dos-622.raw | cut -d: -f1) && \
			if [ -n "$$DEV" ]; then \
				sudo losetup -d /dev/$$DEV && echo "Loop device detached."; \
			else \
				echo "Failed to get loop device for ms-dos-622.raw. Detaching all matching devices..."; \
				sudo DEV=$(sudo losetup -a | grep ms-dos-622.raw | cut -d: -f1) && \
				for dev in $$DEV; do sudo losetup -d /dev/$$dev 2>/dev/null || true; done && \
				echo "Loop devices detached."; \
			fi; \
		fi; \
	else \
		echo "No loop device found for ms-dos-622.raw, or losetup -p not available. Detaching manually..."; \
		sudo DEV=$(sudo losetup -a | grep ms-dos-622.raw | cut -d: -f1) && \
		if [ -n "$$DEV" ]; then \
			sudo losetup -d /dev/$$DEV && echo "Loop device detached."; \
		else \
			echo "No loop devices found for ms-dos-622.raw."; \
		fi; \
	fi

# Unmount the VHD disk image
unmount-vhd:
	@echo "Unmounting VHD image..."
	@if sudo mountpoint -q /mnt/ms-dos-622; then \
		sudo guestunmount /mnt/ms-dos-622 2>/dev/null || sudo umount -l /mnt/ms-dos-622 && \
		echo "Filesystem unmounted."; \
	else \
		echo "Image is not mounted at /mnt/ms-dos-622."; \
	fi
	@if sudo losetup -a | grep -q ms-dos-622-converted.raw; then \
		sudo DEV=$(sudo losetup -p 2>/dev/null | grep ms-dos-622-converted.raw | cut -d: -f1) && \
		if [ -n "$$DEV" ]; then \
			sudo losetup -d $$DEV && echo "Loop device detached."; \
		else \
			sudo DEV=$(sudo losetup -a | grep ms-dos-622-converted.raw | cut -d: -f1) && \
			if [ -n "$$DEV" ]; then \
				sudo losetup -d /dev/$$DEV && echo "Loop device detached."; \
			else \
				echo "Failed to get loop device for converted VHD. Detaching all matching devices..."; \
				sudo DEV=$(sudo losetup -a | grep ms-dos-622-converted.raw | cut -d: -f1) && \
				for dev in $$DEV; do sudo losetup -d /dev/$$dev 2>/dev/null || true; done && \
				echo "Loop devices detached."; \
			fi; \
		fi; \
	else \
		echo "No loop device found for converted VHD image, or losetup -p not available. Detaching manually..."; \
		sudo DEV=$(sudo losetup -a | grep ms-dos-622-converted.raw | cut -d: -f1) && \
		if [ -n "$$DEV" ]; then \
			sudo losetup -d /dev/$$DEV && echo "Loop device detached."; \
		else \
			echo "No loop devices found for converted VHD image."; \
		fi; \
	fi
