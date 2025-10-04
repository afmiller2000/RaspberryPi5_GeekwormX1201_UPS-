# GRUB Bootloader Setup Guide for Raspberry Pi 5

## Overview

This guide provides comprehensive instructions for setting up GRUB as the main firmware bootloader on Raspberry Pi 5, enabling multi-OS boot capabilities and integration with the Geekworm X1201 UPS monitoring system.

## Why Use GRUB on Raspberry Pi?

- **Multi-OS Support**: Boot multiple operating systems (Raspberry Pi OS, Ubuntu, MX Linux, etc.)
- **Boot Menu**: Visual boot menu for OS selection
- **Advanced Boot Options**: Kernel parameter customization and recovery modes
- **System Integrity**: Automated GRUB regeneration after partition changes
- **UPS Integration**: Enhanced power management and safe shutdown capabilities

---

## Prerequisites

### Hardware Requirements
- Raspberry Pi 5
- Geekworm X1201 v1.1 UPS
- MicroSD card or NVMe drive (recommended: 32GB or larger)
- USB keyboard for boot menu navigation

### Software Requirements
- Raspberry Pi OS (64-bit) or Ubuntu 22.04+ for ARM64
- Root/sudo access
- Internet connection for package installation

---

## Part 1: Preparing the Raspberry Pi Boot Partition

### Step 1: Understand Raspberry Pi Boot Process

The Raspberry Pi 5 uses a different boot process than traditional x86 systems:

1. **Stage 1**: GPU firmware loads from boot partition
2. **Stage 2**: Raspberry Pi bootloader (bootcode.bin or EEPROM)
3. **Stage 3**: GRUB (as secondary bootloader)
4. **Stage 4**: Linux kernel

### Step 2: Check Current Boot Configuration

```bash
# Check current boot partition
lsblk -f

# View current bootloader version
sudo rpi-eeprom-update

# Check boot partition mount
mount | grep boot
```

Expected output should show `/boot` or `/boot/firmware` mounted.

### Step 3: Backup Current Boot Configuration

**CRITICAL**: Always backup before making boot changes!

```bash
# Create backup directory
sudo mkdir -p /root/boot-backup

# Backup boot partition
sudo cp -r /boot/* /root/boot-backup/
# OR if using /boot/firmware
sudo cp -r /boot/firmware/* /root/boot-backup/

# Backup EEPROM configuration
sudo rpi-eeprom-config > /root/boot-backup/eeprom-config.txt

# Note: Keep this backup on a separate storage device for safety
```

---

## Part 2: Installing GRUB on Raspberry Pi 5

### Step 1: Install GRUB Package

```bash
# Update package list
sudo apt update

# Install GRUB for ARM64
sudo apt install -y grub-efi-arm64 grub-efi-arm64-bin

# Install GRUB customization tools (optional but recommended)
sudo apt install -y grub-customizer
```

### Step 2: Identify Boot Device

```bash
# List all block devices
lsblk -f

# Find your boot device (usually /dev/mmcblk0 for SD card or /dev/nvme0n1 for NVMe)
# Note the device name and boot partition
```

Example output:
```
NAME        FSTYPE LABEL       UUID                                 MOUNTPOINT
mmcblk0                                                             
├─mmcblk0p1 vfat   bootfs      ABCD-1234                            /boot/firmware
└─mmcblk0p2 ext4   rootfs      12345678-1234-1234-1234-123456789012 /
```

### Step 3: Install GRUB to Boot Partition

```bash
# Set your boot device (adjust if needed)
BOOT_DEVICE="/dev/mmcblk0"
BOOT_PARTITION="/dev/mmcblk0p1"

# Mount boot partition if not already mounted
sudo mount ${BOOT_PARTITION} /boot/firmware

# Install GRUB to boot partition
sudo grub-install --target=arm64-efi --efi-directory=/boot/firmware --bootloader-id=GRUB --recheck

# Generate GRUB configuration
sudo update-grub
```

### Step 4: Configure Raspberry Pi to Boot GRUB

Create or edit the Raspberry Pi boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

Add at the end:
```ini
# GRUB Bootloader Configuration
[all]
kernel=grub/grubaa64.efi
arm_64bit=1
```

---

## Part 3: GRUB Configuration for Multiple Operating Systems

### Step 1: Create GRUB Custom Configuration

```bash
sudo nano /etc/grub.d/40_custom
```

Add custom menu entries:
```bash
#!/bin/sh
exec tail -n +3 $0
# Custom GRUB menu entries

menuentry 'Raspberry Pi OS (Default)' --class raspbian --class gnu-linux --class gnu --class os {
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos2'
    linux /boot/vmlinuz root=/dev/mmcblk0p2 rootwait console=serial0,115200 console=tty1
    initrd /boot/initrd.img
}

menuentry 'Ubuntu Server' --class ubuntu --class gnu-linux --class gnu --class os {
    insmod gzio
    insmod part_gpt
    insmod ext2
    search --no-floppy --fs-uuid --set=root YOUR-UBUNTU-UUID
    linux /boot/vmlinuz root=UUID=YOUR-UBUNTU-UUID ro quiet splash
    initrd /boot/initrd.img
}

menuentry 'Recovery Mode' --class recovery {
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos2'
    linux /boot/vmlinuz root=/dev/mmcblk0p2 rootwait single
    initrd /boot/initrd.img
}
```

### Step 2: Configure GRUB Defaults

```bash
sudo nano /etc/default/grub
```

Recommended settings for Raspberry Pi 5:
```bash
# GRUB Configuration for Raspberry Pi 5

# Default boot entry
GRUB_DEFAULT=0

# Timeout in seconds (10 seconds recommended for UPS systems)
GRUB_TIMEOUT=10

# Show menu even if only one OS
GRUB_TIMEOUT_STYLE=menu

# Kernel command line
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="console=serial0,115200 console=tty1"

# Terminal configuration
GRUB_TERMINAL=console

# Resolution (optional)
GRUB_GFXMODE=1920x1080

# Disable OS prober if not needed (speeds up boot)
# GRUB_DISABLE_OS_PROBER=false

# Save last selected OS
GRUB_SAVEDEFAULT=true
```

### Step 3: Update GRUB Configuration

```bash
# Update GRUB with new configuration
sudo update-grub

# Verify GRUB configuration was created
ls -l /boot/firmware/grub/grub.cfg
```

---

## Part 4: Integration with Geekworm X1201 UPS

### Step 1: Configure UPS-Aware Boot Settings

The UPS system needs to handle power events during boot:

```bash
sudo nano /etc/default/grub
```

Add UPS-specific parameters:
```bash
# UPS Integration Settings
GRUB_CMDLINE_LINUX="${GRUB_CMDLINE_LINUX} usbhid.quirks=0x0001:0x0000:0x00000004"
GRUB_RECORDFAIL_TIMEOUT=10
```

### Step 2: Create GRUB Regeneration Script

This ensures GRUB is automatically regenerated after partition changes (as mentioned in Features):

```bash
sudo nano /usr/local/bin/regenerate-grub.sh
```

```bash
#!/bin/bash
# Automatic GRUB Regeneration Script for UPS System
# Part of Geekworm X1201 UPS Monitoring System

set -e

LOG_FILE="/var/log/grub-regen.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting GRUB regeneration..."

# Verify GRUB is installed
if ! command -v grub-install &> /dev/null; then
    log_message "ERROR: GRUB is not installed"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_message "ERROR: This script must be run as root"
    exit 1
fi

# Backup current GRUB configuration
if [ -f /boot/firmware/grub/grub.cfg ]; then
    cp /boot/firmware/grub/grub.cfg /boot/firmware/grub/grub.cfg.backup
    log_message "Backed up current GRUB configuration"
fi

# Update GRUB
update-grub 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    log_message "GRUB regeneration completed successfully"
else
    log_message "ERROR: GRUB regeneration failed"
    exit 1
fi

# Verify new configuration exists
if [ -f /boot/firmware/grub/grub.cfg ]; then
    log_message "New GRUB configuration verified"
else
    log_message "ERROR: New GRUB configuration not found"
    exit 1
fi

exit 0
```

Make the script executable:
```bash
sudo chmod +x /usr/local/bin/regenerate-grub.sh
```

### Step 3: Create Systemd Service for GRUB Monitoring

```bash
sudo nano /etc/systemd/system/grub-watchdog.service
```

```ini
[Unit]
Description=GRUB Configuration Watchdog for UPS System
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/regenerate-grub.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
sudo systemctl enable grub-watchdog.service
```

---

## Part 5: Testing and Validation

### Step 1: Verify GRUB Installation

```bash
# Check GRUB files exist
ls -l /boot/firmware/grub/
ls -l /boot/firmware/EFI/GRUB/

# Verify GRUB configuration
sudo grub-script-check /boot/firmware/grub/grub.cfg
```

### Step 2: Test Boot Process

**WARNING**: Only proceed if you have physical access to the Raspberry Pi!

```bash
# Test boot (this will reboot the system)
sudo reboot
```

What to expect:
1. GRUB menu appears after Raspberry Pi firmware
2. Default OS is highlighted
3. 10-second countdown before auto-boot
4. OS boots normally

### Step 3: Test UPS Integration

```bash
# Check UPS service status
sudo systemctl status ups-monitor.service

# Run UPS monitor to verify boot completed
cd /home/runner/work/RaspberryPi5_GeekwormX1201_UPS-/RaspberryPi5_GeekwormX1201_UPS-
python3 UPSMonitorv35.py
```

---

## Part 6: Multi-OS Setup (Advanced)

### Installing Additional Operating Systems

#### Option A: Ubuntu Server Alongside Raspberry Pi OS

1. **Shrink Existing Partition**:
```bash
# Use parted to resize
sudo parted /dev/mmcblk0
(parted) print
(parted) resizepart 2 16GB
(parted) mkpart primary ext4 16GB 100%
(parted) quit

# Format new partition
sudo mkfs.ext4 /dev/mmcblk0p3
```

2. **Install Ubuntu** to new partition using standard installation process

3. **Update GRUB** to detect Ubuntu:
```bash
sudo update-grub
```

#### Option B: Using Separate Boot Partitions

Create dedicated boot partition for each OS for cleaner separation.

---

## Part 7: Troubleshooting

### Common Issues and Solutions

#### Issue 1: GRUB Menu Doesn't Appear

**Symptoms**: Boots directly to Raspberry Pi OS

**Solution**:
```bash
# Check config.txt
cat /boot/firmware/config.txt | grep grub

# Should contain: kernel=grub/grubaa64.efi
# If missing, add it:
echo "kernel=grub/grubaa64.efi" | sudo tee -a /boot/firmware/config.txt
```

#### Issue 2: "Error: file '/grub/grubaa64.efi' not found"

**Solution**:
```bash
# Reinstall GRUB
sudo grub-install --target=arm64-efi --efi-directory=/boot/firmware --bootloader-id=GRUB --recheck --force

# Verify file exists
ls -l /boot/firmware/grub/grubaa64.efi
```

#### Issue 3: System Won't Boot After GRUB Installation

**Solution** (Recovery):
1. Insert SD card into another Linux computer
2. Mount boot partition
3. Edit `config.txt` and remove the `kernel=grub/grubaa64.efi` line
4. Boot Raspberry Pi (will use default bootloader)
5. Investigate GRUB installation issues

#### Issue 4: GRUB Timeout Too Short/Long

**Solution**:
```bash
sudo nano /etc/default/grub
# Change GRUB_TIMEOUT value (in seconds)
sudo update-grub
sudo reboot
```

#### Issue 5: UPS Causes Boot Loop

**Symptoms**: System reboots repeatedly when on battery

**Solution**:
```bash
# Add kernel parameter to prevent premature reboot
sudo nano /etc/default/grub
# Add to GRUB_CMDLINE_LINUX: "panic=0"
sudo update-grub
```

### Debug Commands

```bash
# View GRUB configuration
cat /boot/firmware/grub/grub.cfg

# Check boot messages
sudo dmesg | grep -i grub

# View systemd boot log
sudo journalctl -b | grep -i grub

# Test GRUB configuration syntax
sudo grub-script-check /boot/firmware/grub/grub.cfg
```

---

## Part 8: Maintenance and Best Practices

### Regular Maintenance Tasks

1. **Update GRUB After Kernel Updates**:
```bash
sudo apt update && sudo apt upgrade
sudo update-grub
```

2. **Backup GRUB Configuration Monthly**:
```bash
sudo cp /boot/firmware/grub/grub.cfg /root/grub-backup-$(date +%Y%m%d).cfg
```

3. **Monitor GRUB Logs**:
```bash
sudo journalctl -u grub-watchdog.service
tail -f /var/log/grub-regen.log
```

### Best Practices

1. **Always Keep a Backup SD Card**: With working Raspberry Pi OS installation
2. **Test UPS Shutdown**: Ensure proper shutdown sequence with GRUB
3. **Document Custom Menu Entries**: Keep notes on custom configurations
4. **Use UUID Instead of Device Names**: For partition references (more stable)
5. **Keep EEPROM Updated**: `sudo rpi-eeprom-update -a`

### Unified /mnt/data Partition Setup

For cross-OS data sharing (as mentioned in Features):

```bash
# Create shared data partition
sudo mkdir -p /mnt/data

# Add to /etc/fstab for all operating systems
echo "UUID=your-data-partition-uuid /mnt/data ext4 defaults 0 2" | sudo tee -a /etc/fstab

# Mount
sudo mount -a
```

---

## Part 9: GRUB Customization (Optional)

### Custom GRUB Theme

```bash
# Install GRUB theme
sudo apt install -y grub2-themes

# Or download custom theme
sudo git clone https://github.com/vinceliuice/grub2-themes.git /tmp/grub2-themes
cd /tmp/grub2-themes
sudo ./install.sh -b -t vimix

# Update GRUB
sudo update-grub
```

### Adding Custom Boot Options

Edit `/etc/grub.d/40_custom` to add:
- Different kernel parameters
- Recovery modes
- Memory test utilities
- Different init systems

### GRUB Security (Password Protection)

```bash
# Generate password hash
grub-mkpasswd-pbkdf2

# Add to /etc/grub.d/40_custom:
# set superusers="admin"
# password_pbkdf2 admin <your-hash>
```

---

## Part 10: Integration Checklist

### Post-Installation Verification

- [ ] GRUB menu appears on boot
- [ ] All operating systems are detected
- [ ] Default OS boots after timeout
- [ ] UPS monitoring starts correctly
- [ ] GRUB regeneration script works
- [ ] Recovery mode is accessible
- [ ] Boot logs show no GRUB errors
- [ ] Shutdown/reboot works properly
- [ ] Power loss recovery works with UPS

### UPS System Integration

- [ ] UPS service starts after boot
- [ ] Battery monitoring is active
- [ ] AC power detection works
- [ ] Low battery shutdown triggers properly
- [ ] GRUB configuration survives UPS events
- [ ] Logs capture boot-time UPS status

---

## Additional Resources

### Documentation Links

- [Raspberry Pi Boot Documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-bootloader-configuration)
- [GNU GRUB Manual](https://www.gnu.org/software/grub/manual/grub/)
- [Raspberry Pi EEPROM Bootloader](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-4-bootloader-configuration)

### Related Project Documentation

- [UPS Monitoring Features](../Features.txt)
- [Quick Start Guide](../QUICKSTART.MD)
- [Repository Structure](../REPO_MAP.md)

### Support

For issues specific to this UPS monitoring system with GRUB:
1. Check [Troubleshooting](#part-7-troubleshooting) section above
2. Review logs: `/var/log/grub-regen.log`
3. Open an issue on GitHub with:
   - GRUB configuration (`/boot/firmware/grub/grub.cfg`)
   - Boot logs (`sudo journalctl -b`)
   - UPS status snapshot

---

## Conclusion

You now have a comprehensive GRUB bootloader setup on your Raspberry Pi 5, integrated with the Geekworm X1201 UPS monitoring system. This configuration provides:

- Multi-OS boot capabilities
- UPS-aware boot management
- Automatic GRUB regeneration
- Recovery options
- Professional boot experience

Remember to maintain regular backups and test power loss scenarios to ensure system reliability.

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Maintained By**: Raspberry Pi 5 Geekworm X1201 UPS Monitoring Project  
**License**: MIT (same as project)
