#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: MeshCom-sendudp.py
Author: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date: 2025-03-24

Description: The example script sends a message with UDP to a MeshCom node
MC FW: MeshCom 4.34v (build: Mar 22 2025 / 07:01:38)
MC HW: TLORA_V2_1_1p6 / Heltec v3
There are reprequistes to be met, otherwise the script will fail:
        The IP address must be known of the MC node
	--extudp must be on

This is an educational script, that helps to understand of how to communicate to a MeshCom Node.
        running on a RaspberryPi 5, with 8GB RAM and Debian Bookwork
"""
"""
A word of Caution: as the MeshCom firmware is under heavy development, expect to see changes on the BLE interface
        This project is based on work by: https://icssw.org/meshcom/
        With insights from: https://srv08.oevsv.at/meshcom/

Honorable Mentions:
OE1KBC: Based on the "as is interface" provided by Kurt Baumann (oe1kbc@icssw.org) "https://github.com/icssw-org/MeshCom-Firmware/releases"

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
import socket

def send_udp_message (message, ip_address, port):
  try:
    # Create an UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send a Message
    sock.sendto(message.encode(), (ip_address,port))

    # Close the socket
    sock.close()

    return True
  except Exception as e:
    print(f"Error: {e}")
    return False

#grp="999"
#grp="DK5EN-99"
#grp="*"
grp="TEST"

#Standard Text an APRS.fi
#msg="APRS:Test auf die " + grp + " via UDP + DNS Auflösung zusammengesetzt"
#msg="APRS: mal alles raus an aprsi.fi "

#Standard Text an MeshCom
msg="Test auf die " + grp + " via UDP + DNS Auflösung zusammengesetzt"

message = "{\"type\":\"msg\",\"dst\":\"" + grp + "\",\"msg\":\"" + msg + "\"}"

print(f"Message : {message}")
port = 1799 #	 stadard Port für MC

hostname = "dk5en-99.local"
ip_address = socket.gethostbyname(hostname)

if send_udp_message(message,ip_address,port):
    print("Message sent sccessful!")
else:
    print("Failed to send message.")
