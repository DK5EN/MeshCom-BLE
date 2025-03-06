This is git repo is to share ideas about Bluetooth communications with the MeshCom device.

My personal creative intent was, to:
- Share knowledge about MeshCom 4.0 BLE communications (documented by source code!)
- Help me to eliminate and UDP or Serial Connection with the MC Node
- Understand the communications between a MeshCom node (as of MeshCom 4.34p, build: Mar 1 2025 / 20:56:39
- Talk to a TLORA_V2_1_1p6
- Teach my how to code in python
- Teach me how to scan, pair and connect to BLE devices

Currntly available:
- an example to scan for BLE devices and retrieving their MAC address, as this is needed for a connection
- an example script that establishes a connection to a MC node and waits for communications to come in
- an example script to send data to the MC network (internet and LoRaWAN)

What it does show:
It contains scripts written in python.
Scripts are kept rudimentary to be easy to read.

What it does not show:
It does not show every step to get the scripts running, like setting up the python environment, downloading necessary libraries.
It doesn't have a GUI, nor a menu system.
Infinte loops must be stopped by CRTL-C.
Bluetooth stack needs a reset after a hard interruption.

You need hardware, thtat supports the proper BLE protocol.
I used a RaspberryPi 5 with 8GB Ram, running raspian, basically Debian Bookworm.

Disclaimer:
This script is provided "as is", without warranty of any kind, express or implied.

This is an educational script, that helps to understand of how to communicate to scan for Bluetooth devices

About the Autor: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date last edited : 2025-03-06 11:35h

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
