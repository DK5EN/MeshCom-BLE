#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: MeshCom-Read.py
Author: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date: 2025-03-06
Version: 2025030659
Description: The example script establishes a BLE communication to a MeshCom node and waits for new messages, outputs json
MC FW: MeshCom 4.34p (build: Mar 1 2025 / 20:56:39)
MC HW: TLORA_V2_1_1p6

A word of Caution: as the MeshCom firmware is under heavy development, expect to see changes on the BLE interface

	This project is based on work by: https://icssw.org/meshcom/
	With insights from: https://srv08.oevsv.at/meshcom/#

Honorable Mentions:
OE1KBC: Based on the "as is interface" provided by Kurt Baumann (oe1kbc@icssw.org) "https://github.com/icssw-org/MeshCom-Firmware/releases"
	With some source code reading and using code parts of the provided python script for reading LoRa Frames
OE3WAS: With great support of Wolfgang to hack the binary message interface - https://github.com/karamo/MeshAll42_MIT-AI2
	That helped me to establish a connection and further read the "binary junk"
OE1KFR: Rainer for responing to queries about the iOS Version of the MeshCom App

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
	running on a RaspberryPi 5, with 8GB RAM and Debian Bookwork

If you CRTL + c the script, be sure to reset the bluetooth stack with:
sudo systemctl restart bluetooth 
"""
# Code starts here
import json
import asyncio
import aioconsole
from bleak import BleakClient
from datetime import datetime
from struct import *

#Constants
write_char_uuid = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" # UUID_Char_WRITE
read_char_uuid =  "6e400003-b5a3-f393-e0a9-e50e24dcca9e" # UUID_Char_NOTIFY
hello_byte = bytes([0x04, 0x10, 0x20, 0x30])

dataFlag = False #global flag to check for new data

def calc_fcs(msg):
    fcs = 0
    for x in range(0,len(msg)):
        fcs = fcs + msg[x]
    
    # SWAP MSB/LSB
    fcs = ((fcs & 0xFF00) >> 8) | ((fcs & 0xFF) << 8 )
    
    #print("calc_fcs=" + hex(fcs))
    return fcs

def notification_handler(sender, clean_msg):

    # JSON-Nachrichten beginnen mit 'D{'
    if clean_msg.startswith(b'D{'):

         var = decode_json_message(clean_msg)

         typ_mapping = {
               "MH": "MHead update",
               "SA": "APRS",
               "G": "GPS",
               "W": "weather",
               "SN": "System Settings",
               "SE": "pressure und Co sensors",
               "SW": "Wifi ttings",
               "I": "Info page",
               "CONFFIN": "Habe fertig"
         }

         try:
           typ = var.get('TYP')

           #print(typ_mapping.get(var.get('TYP'), var))

           if typ == 'MH': # MH update
             print(var)

           #elif typ == "SA": # APRS.fi Info
           #  print("APRS")

           #elif typ == "G": # GPS Info
           #  print("GPS")

           #elif typ == "W": # Wetter Info
           #  print("Wetter")

           #elif typ == "SN": # System Settings wie Buttung 
           #  print("System Settings")

           #elif typ == "SE": # System Settings wie Buttung 
           #  print("Druck und Co Sensoren")

           #elif typ == "SW": # WIFI + IP Settings
           #  print("Wifi Settings")

           #elif typ == "I": # Info Seite
           #  print("Info Seite")

           #elif typ == "CONFFIN": # Habe Fertig! Mehr gibt es nicht
           #  print("Habe fertig")

         except KeyError:
             print(error) 
             print(var)

    # Binärnachrichten beginnen mit '@'
    elif clean_msg.startswith(b'@'):
      print(decode_binary_message(clean_msg))

    else:
        print("Unbekannter Nachrichtentyp.")

    global dataFlag
    dataFlag = True

def decode_json_message(byte_msg):
    try:
        json_str = byte_msg.rstrip(b'\x00').decode("utf-8")[1:]
        return json.loads(json_str)

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Fehler beim Dekodieren der JSON-Nachricht: {e}")
        return None

def decode_binary_message(byte_msg):

    # little-endian unpack
    raw_header = byte_msg[1:7]
    [payload_type, msg_id, max_hop_raw] = unpack('<BIB', raw_header)

    #Bits schieben
    max_hop = max_hop_raw & 0x0F
    mesh_info = max_hop_raw >> 4

    #Frame checksum berechnen
    calced_fcs = calc_fcs(byte_msg[1:-11])

    remaining_msg = byte_msg[7:].rstrip(b'\x00')  # Alles nach Hop

    if byte_msg[:2] == b'@A':  # Prüfen, ob es sich umACK Frames handel

       #remaining_msg = byte_msg[8:].rstrip(b'\x00')  # Alles nach Hop
       message = remaining_msg.hex().upper()

       #Etwas bit banging, weil die Binaerdaten am Ende immer gleich aussehen
       #[zero, hardware_id, lora_mod, fcs, fw, lasthw, fw_subver, ending, time_ms ] = unpack('<BBBHBBBBI', byte_msg[-14:-1])
       [ack_id] = unpack('<I', byte_msg[-5:-1])

       json_obj = {k: v for k, v in locals().items() if k in [
          "payload_type",
	        "msg_id",
	        "max_hop",
	        "mesh_info",
	        "message",
	        "ack_id",
	        "calced_fcs" ]}

       return json_obj

    elif bytes(byte_msg[:2]) in {b'@:', b'@!'}:
      #remaining_msg = byte_msg[7:]  # Alles nach Hop
      # Extrahiere den Path

      split_idx = remaining_msg.find(b'>')
      if split_idx == -1:
        return "Kein gültiges Routing-Format"

      path = remaining_msg[:split_idx+1].decode("utf-8", errors="ignore")
      remaining_msg = remaining_msg[split_idx + 1:]

      # Extrahiere Dest-Type (`dt`)

      if payload_type == 58:
        split_idx = remaining_msg.find(b':')
      elif payload_type == 33:
        split_idx = remaining_msg.find(b'*')+1
      else:
        print(f"Payload type not matched! {payload_type}")

      if split_idx == -1:
         return "Destination not found"

      dest = remaining_msg[:split_idx].decode("utf-8", errors="ignore")

      message = remaining_msg[split_idx:remaining_msg.find(b'\00')].decode("utf-8", errors="ignore").strip()

      #Etwas bit banging, weil die Binaerdaten am Ende immer gleich aussehen
      [zero, hardware_id, lora_mod, fcs, fw, lasthw, fw_subver, ending, time_ms ] = unpack('<BBBHBBBBI', byte_msg[-14:-1])

      #Frame checksum checken
      fcs_ok = (calced_fcs == fcs)

      if message.startswith(":{CET}"):
        dest_type = "Datum & Zeit Broadcast an alle"
      
      elif path.startswith("response"):
        dest_type = "user input response"

      elif message.startswith("!"):
        dest_type = "Positionsmeldung"

      elif dest == "*":
        dest_type = "Broadcast an alle"

      elif dest.isdigit():
        dest_type = f"Gruppennachricht an {dest}"

      else:
        dest_type = f"Direktnachricht an {dest}"

      json_obj = {k: v for k, v in locals().items() if k in [
          "payload_type", 
          "msg_id",
          "max_hop",
          "mesh_info",
          "dest_type",
          "path",
          "dest",
          "message",
          "hardware_id", 
          "lora_mod", 
          "fcs", 
          "fcs_ok", 
          "fw", 
          "fw_subver", 
          "lasthw", 
          "time_ms",
          "ending" 
          ]}

      return json_obj

    else:
       return "Kein gueltiges Mesh-Format"


async def write_characteristic(client, char_uuid, data):
  #used to sending data
  try:
    await client.write_gatt_char(char_uuid, data)
    #print(f"Wrote value: {data}")
  except Exception as e:
    print(f"Error writing characteristic: {e}")

async def user_input_task(stop_event):
    """Task to listen for user input to stop the loop."""
    while not stop_event.is_set():
        user_input = await aioconsole.ainput("Enter 'q' to quit: \n")
        if user_input.strip().lower() == 'q':
            print("Stopping...")
            stop_event.set()

async def run(address, loop):

  print("trying to connect ...")

  stop_event = asyncio.Event()

  async with BleakClient(address, loop=loop) as client:
    # wait for BLE client to be connected
    if client.is_connected:
      print(f"Connected to: {address}")

    #install hanlder for data collection
    await client.start_notify(read_char_uuid, notification_handler)
    print("handler gesetzt")

    #HELLO ausgeben, damit die Kommunikation los geht
    await write_characteristic(client, write_char_uuid, hello_byte)
    print("HELLO sent ..")

    # Start user input listener
    asyncio.create_task(user_input_task(stop_event))

    while not stop_event.is_set():
      #waiting for q + enter

      global dataFlag

      if dataFlag :
         #oh yea, we have new messages waiting
         dataFlag = False

	       #collect valueable data
         data = await client.read_gatt_char(write_char_uuid)

      else:
        #give some time to do other tasks
        await asyncio.sleep(1)
      
if __name__ == "__main__":
   #Device MC-b560-DK5EN-99, Address: D4:D4:DA:9E:B5:62
   #Device MC-83ac-DK5EN-99, Address: 48:CA:43:3A:83:AD
   
   address = ( "48:CA:43:3A:83:AD" )

   loop = asyncio.new_event_loop()
   asyncio.set_event_loop(loop)

   loop.run_until_complete(run(address, loop))
