# Multi-Boot USB (Raspberry Pi 5)

This section provides a GRUB-first multi-boot USB build for the Raspberry Pi 5 supporting multiple Linux distributions (Kubuntu, Fedora, openSUSE, Manjaro) plus a shared exFAT data partition and optional future U-Boot/extlinux path.

Quick Links:
- MULTIBOOT_OVERVIEW.md – Rationale and staged process breakdown
- MULTIBOOT_SCRIPT_FULL.sh – Master script (all stages)
- SCRIPTS/stage1_wipe_and_partition.sh – Just the destructive partitioning stage
- SCRIPTS/kernel_sync_helper.sh – Post-update kernel re-staging helper
- SCRIPTS/add_new_distro_template.sh – Template for adding another distro
- SCRIPTS/extlinux_uboot_notes.md – Future alternate boot path notes
- CONVERSATION_ARCHIVE.md – Summary + transcript placeholders
- repo_map_addendum.md – How this integrates with overall repo purpose

WARNING: Stage 2 (wipe/partition) is destructive for /dev/sda (preset here). Double-check your target device.

Prerequisites (host workstation):
- Ubuntu/Debian-based with: parted gdisk dosfstools exfatprogs rsync grub-efi-arm64-bin
- Access to Raspberry Pi firmware files (start4*.elf, fixup4*.dat, bootcode.bin optional)

Edit DEV and PI_FIRMWARE_DIR in the master script before executing. Default pre-filled here:
- DEV=/dev/sda
- PI_FIRMWARE_DIR=/boot/firmware
