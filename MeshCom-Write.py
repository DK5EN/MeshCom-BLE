#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: MeshCom-Write.py
Author: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date: 2025-03-06
Version: 2025030603
Description: The example script establishes a BLE communication to a MeshCom node and sends a message
		See results on https://srv08.oevsv.at/meshcom/# -> Â"Test" Page
MC FW: MeshCom 4.34p (build: Mar 1 2025 / 20:56:39)
MC HW: TLORA_V2_1_1p6

Disclaimer: a word of Caution: as the MeshCom firmware is under heavy development, expect to see changes on the BLE interface

        This project is based on work by: https://icssw.org/meshcom/
        With insights from: https://srv08.oevsv.at/meshcom/#

Honorable Mentions:
OE1KBC: Based on the "as is interface" provided by Kurt Baumann (oe1kbc@icssw.org) "https://github.com/icssw-org/MeshCom-Firmware/releases"
        With some source code reading and using code parts of the provided python script for reading LoRa Frames
OE3WAS: With great support of Wolfgang to hack the message interface - https://github.com/karamo/MeshAll42_MIT-AI2

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

There are reprequistes to be met, otherwise the script will fail:
        BLE MAC address of MC node must be known,
        Bluetooth must be paired already.

This is an educational script, that helps to understand of how to communicate to a MeshCom Node.
MeshCom node tested against:
        HW: TLORA_V2_1_1p6
        FW: Firmware MeshCom 4.34p (build: Mar 1 2025 / 20:56:39)
        running on a RaspberryPi 5, with 8GB RAM and Debian Bookwork

If you CRTL + c the script, be sure to reset the bluetooth stack with:
sudo systemctl restart bluetooth
"""
# Code starts here

import asyncio
from bleak import BleakClient

write_char_uuid = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" # UUID_Char_WRITE
read_char_uuid =  "6e400003-b5a3-f393-e0a9-e50e24dcca9e" # UUID_Char_NOTIFY


async def read_characteristic(client, char_uuid):
  try:
    value = await client.read_gatt_char(char_uuid)
    print(f"Read value: {value}")
  except Exception as e:
    print(f"Error reading characteristic: {e}")

async def write_characteristic(client, char_uuid, data):
  try:
    await client.write_gatt_char(char_uuid, data)
    print(f"Wrote value: {data}")
  except Exception as e:
    print(f"Error writing characteristic: {e}")


async def run(message):
  print("Searching for BLE device ...")
  async with BleakClient (MAC_ADDRESS) as client:
    if client.is_connected:
      print(f"Connected: {MAC_ADDRESS}")

    byte_array = bytearray( message.encode('utf-8'))

    laenge = len(byte_array) + 2

    byte_array = laenge.to_bytes(1, 'big') +  bytes ([0xA0]) + byte_array

    #HELLO zum Abfragen und um das Device aufzuwecken
    message = bytes([0x03, 0x10, 0x20, 0x30])
    await write_characteristic(client, write_char_uuid, message)

    #Nachricht senden
    await write_characteristic(client, write_char_uuid, byte_array)


MAC_ADDRESS = "D4:D4:DA:9E:B5:62"

grp = "DK5EN-99"
msg = "Test 57 mit Python Ã¼ber bluetooth"

message = "{" + grp + "}" + msg

loop = asyncio.get_event_loop()
loop.run_until_complete(run(message))
