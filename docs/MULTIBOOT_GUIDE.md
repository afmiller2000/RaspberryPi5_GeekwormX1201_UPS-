VERSION: original_guide_1.0.0
TITLE: Original (Archived) Multiboot Guide Draft
STATUS: ARCHIVED_DRAFT (Retained for historical reference – use MULTIBOOT_GUIDE_FINAL.md for execution)
NOTE: This draft contains duplicated concepts and was superseded. Non-ASCII punctuation was normalized. Do NOT run blindly; prefer the cleaned final guide.

# Original Multiboot Draft (Archived)

Below are the end-to-end, ready-to-run command blocks with clear labels, comments, and progress indicators. They assume your USB target device is /dev/sda (DOUBLE-CHECK before running). Each command is on its own line. Run each block in order. If your USB shows up as something else (e.g. /dev/sdb), substitute consistently before executing.

================================================================ STEP 0: PREREQUISITES (Install needed tools)
Install tools you may need (grub-efi-arm64 must be available on an ARM64 system; on x86 you may need cross tools or perform kernel copy later on the Pi)

sudo apt update
sudo apt install -y parted gdisk dosfstools exfatprogs rsync grub-efi-arm64-bin grub2-common
(If you are on the Raspberry Pi itself with a Debian/Ubuntu base, grub-efi-arm64 should be available.
If not, you can later build grub-mkimage manually or install after first boot into Kubuntu/Fedora.)

================================================================ STEP 1: IDENTIFY AND CONFIRM TARGET DEVICE
lsblk -o NAME,SIZE,MODEL,SERIAL,TRAN
udevadm info --query=all --name=/dev/sda | grep -Ei 'ID_MODEL=|ID_VENDOR=|ID_SERIAL='

================================================================ STEP 2: FULL WIPE (DESTRUCTIVE)
sudo umount -R /dev/sda* 2>/dev/null || true
sudo swapoff /dev/sda? 2>/dev/null || true
sudo sgdisk --zap-all /dev/sda
sudo wipefs -a /dev/sda
sudo dd if=/dev/zero of=/dev/sda bs=4M count=16 status=progress conv=fsync
sudo dd if=/dev/zero of=/dev/sda bs=1M seek=$((224573-16)) count=16 conv=fsync status=progress
sudo blkdiscard /dev/sda 2>/dev/null || true
sudo wipefs -a /dev/sda

================================================================ STEP 3: CREATE PARTITIONS
Creates:
1 FIRMWARE_A (512M FAT32)
2 BOOT_GRUB  (1G ext4)
3 FIRMWARE_B (1G FAT32)
4 BOOT_EXT   (1G ext4)
5 KUBUNTU    (50G)
6 FEDORA     (35G)
7 OPENSUSE   (35G)
8 MANJARO    (35G)
9 DATA       (40G)
10 SWAP      (20G)
Tail ~823M unallocated

sudo parted /dev/sda --script mklabel gpt unit MiB \
  mkpart FIRMWARE_A fat32 1 513 name 1 FIRMWARE_A set 1 boot on set 1 esp on \
  mkpart BOOT_GRUB ext4 516 1540 name 2 BOOT_GRUB \
  mkpart FIRMWARE_B fat32 1541 2565 name 3 FIRMWARE_B \
  mkpart BOOT_EXT ext4 2566 3590 name 4 BOOT_EXT \
  mkpart KUBUNTU 3590 54790 name 5 KUBUNTU \
  mkpart FEDORA 54790 90630 name 6 FEDORA \
  mkpart OPENSUSE 90630 126470 name 7 OPENSUSE \
  mkpart MANJARO 126470 162310 name 8 MANJARO \
  mkpart DATA 162310 203270 name 9 DATA \
  mkpart SWAP linux-swap 203270 223750 name 10 SWAP

sudo parted /dev/sda unit MiB print
lsblk -o NAME,LABEL,SIZE,FSTYPE /dev/sda

================================================================ STEP 4: FORMAT FILESYSTEMS
sudo mkfs.vfat  -F32 -n FIRMWARE_A /dev/sda1
sudo mkfs.ext4  -F -L BOOT_GRUB    /dev/sda2
sudo mkfs.vfat  -F32 -n FIRMWARE_B /dev/sda3
sudo mkfs.ext4  -F -L BOOT_EXT     /dev/sda4
sudo mkfs.ext4  -F -L KUBUNTU      /dev/sda5
sudo mkfs.ext4  -F -L FEDORA       /dev/sda6
sudo mkfs.ext4  -F -L OPENSUSE     /dev/sda7
sudo mkfs.ext4  -F -L MANJARO      /dev/sda8
sudo mkfs.exfat -n DATA            /dev/sda9
sudo mkswap     -L SWAP            /dev/sda10

================================================================ STEP 5: CREATE MOUNT POINTS
sudo mkdir -p /mnt/firmware_a /mnt/boot_grub /mnt/firmware_b /mnt/boot_ext /mnt/kubuntu /mnt/fedora /mnt/opensuse /mnt/manjaro /mnt/data
sudo mount -L FIRMWARE_A /mnt/firmware_a
sudo mount -L BOOT_GRUB   /mnt/boot_grub
sudo mount -L KUBUNTU     /mnt/kubuntu
sudo mount -L FEDORA      /mnt/fedora
sudo mount -L DATA        /mnt/data

================================================================ STEP 6: POPULATE FIRMWARE_A
sudo cp /path/to/pi-firmware/boot/start4*.elf /mnt/firmware_a/
sudo cp /path/to/pi-firmware/boot/fixup4*.dat /mnt/firmware_a/
sudo cp /path/to/pi-firmware/boot/bootcode.bin /mnt/firmware_a/ 2>/dev/null || true

cat <<'EOF' | sudo tee /mnt/firmware_a/config.txt
arm_64bit=1
enable_uart=1
kernel=efi/boot/bootaa64.efi
gpu_mem=80
EOF
sudo mkdir -p /mnt/firmware_a/EFI/BOOT

================================================================ STEP 7: (Truncated) INSTALL GRUB (Original Draft Duplicate)
[Original duplicate sections intentionally omitted]

END ORIGINAL GUIDE
