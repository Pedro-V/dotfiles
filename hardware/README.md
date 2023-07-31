# Hardware

Some hardware devices aren't really pluggable in Linux, as they're in
proprietary systems. Thererefore, they require extra configuration. Each of
these configs should go in `/etc/<config_dir>`, except when noted otherwise.

I currently use two laptops as main workstations:

* Laptop 1

```sh
$ inxi -MCGNERD # with some filtering
Machine:
  Type: Laptop System: LENOVO product: 81FE v: Lenovo ideapad 330-15IKB
    serial: <superuser required>
  Mobo: LENOVO model: LNVNB161216 v: SDK0J40688 WIN
  UEFI: LENOVO v: 8TCN61WW date: 05/19/2021
CPU:
  Info: quad core model: Intel Core i7-8550U bits: 64 type: MT MCP cache:
    L2: 1024 KiB
  Speed (MHz): avg: 800 min/max: 400/4000 cores: 1: 800 2: 800 3: 800 4: 800
    5: 800 6: 800 7: 800 8: 800
Graphics:
  Device-1: Intel UHD Graphics 620 driver: i915 v: kernel
  Device-2: NVIDIA GP108M [GeForce MX150] driver: nouveau v: kernel
  Device-3: SunplusIT EasyCamera driver: uvcvideo type: USB
Network:
  Device-1: Realtek RTL8111/8168/8411 PCI Express Gigabit Ethernet
    driver: r8169
  Device-2: Qualcomm Atheros QCA9377 802.11ac Wireless Network Adapter
    driver: ath10k_pci
Bluetooth:
  Device-1: N/A driver: btusb type: USB
  Report: rfkill ID: hci0 rfk-id: 2 state: down bt-service: not found
    rfk-block: hardware: no software: yes address: see --recommends
RAID:
  Hardware-1: Intel 82801 Mobile SATA Controller [RAID mode] driver: ahci
Drives:
  Local Storage: total: 931.51 GiB used: 16.1 GiB (1.7%)
  ID-1: /dev/sda vendor: Western Digital model: WD10SPZX-24Z10T0
    size: 931.51 GiB
```
 
* Laptop 2

```
```

## Descriptions

* `
