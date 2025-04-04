#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: BLE-Scan.py
Author: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date: 2025-03-24

Description: The example script scans for Bluetooth Devices

There are reprequistes to be met, otherwise the script will fail:
	only not yet connected devices show up (have you disconnected your phone from your bluetooth device?)
    HW must have Bluetooth Chip, check for LE support if unsure: 
        $ hciconfig hci0 features|grep LE
		<AFH cls. perip.> <LE support> <3-slot EDR ACL> 
		<LE and BR/EDR> <simple pairing> <encapsulated PDU> 

This is an educational script, that helps to understand of how to communicate to scan for Bluetooth devices
        running on a RaspberryPi 5, with 8GB RAM and Debian Bookwork
"""
"""
Sometimes it is nessaserry to restart the Bluetooth stack:
sudo systemctl restart bluetooth

Additional helpful commands. After you have discovered your devive, you need to pair it. pairing only avaibale during scan on
 $ bluetoothctl
scan on
   > gibt aus Device MC-b560-DK5EN-99, Address: D4:D4:DA:9E:B5:62
pair D4:D4:DA:9E:B5:62
scan off
connect D4:D4:DA:9E:B5:62
exit

 $ bluetoothctl info D4:D4:DA:9E:B5:62
Device D4:D4:DA:9E:B5:62 (public)
	Name: MC-b560-DK5EN-99
	Alias: MC-b560-DK5EN-99
	Paired: yes
	Bonded: yes
	Trusted: no
	Blocked: no
	Connected: yes
	LegacyPairing: no
	UUID: Generic Access Profile    (00001800-0000-1000-8000-00805f9b34fb)
	UUID: Generic Attribute Profile (00001801-0000-1000-8000-00805f9b34fb)
	UUID: Nordic UART Service       (6e400001-b5a3-f393-e0a9-e50e24dcca9e)

 $ bluetoothctl disconnect D4:D4:DA:9E:B5:62
Attempting to disconnect from D4:D4:DA:9E:B5:62
[CHG] Device D4:D4:DA:9E:B5:62 ServicesResolved: no
Successful disconnected

""" 
"""
License:
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Copyright (c) 2025 Martin S. Werner

You are free to:
- Share - copy and redistribute the material in any medium or format
- Adapt - remix, transform, and build upon the material

Under the following terms:
- Attribution - You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- ShareAlike - If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

Disclaimer:
This script is provided "as is", without warranty of any kind, express or implied.
"""
import asyncio
from bleak import BleakScanner

async def scan_ble_devices():
  print("Please give me a second to complete bluetooth scan for MC-* ..")
  devices = await BleakScanner.discover()
  for device in devices:
    if device.name.startswith("MC-"):
      print(f"Device {device.name}, Address: {device.address}, RSSI: {device._rssi}")

# Run the BLE scan
#loop = asyncio.get_event_loop()
#loop.run_until_complete(scan_ble_devices())

asyncio.run(scan_ble_devices())