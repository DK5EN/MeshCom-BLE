#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: MeshCom-readudp.py
Author: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date: 2025-03-96
Version: 2025030901
Description: The example script sends a message with UDP to a MeshCom node
MC FW: MeshCom 4.34p (build: Mar 1 2025 / 20:56:39)
MC HW: HeltecV3

        This project is based on work by: https://icssw.org/meshcom/
        With insights from: https://srv08.oevsv.at/meshcom/#

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
        The IP address must be known of the MC node
	--extudp must be on

This is an educational script, that helps to understand of how to communicate to a MeshCom Node.
MeshCom node tested against:
        running on a RaspberryPi 5, with 8GB RAM and Debian Bookwork

"""
# Code starts here
import asyncio
import sys
import signal

ip = "0.0.0.0"
port = 1799 #	 RX TX Port
#port = 1798 #	 stadard Port für MC

async def read_udp_message(ip_address: str, port: int):
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(),
        local_addr=(ip_address, port)
    )

    stop_event = asyncio.Event()
    async def check_for_exit():
        while True:
            char = await asyncio.to_thread(sys.stdin.read, 1)  # Liest ein Zeichen
            if char.lower() == 'q':  # Falls "a" gedrückt wurde
                print("Taste 'q' erkannt, beende UDP-Listener...")
                stop_event.set()
                break

    asyncio.create_task(check_for_exit())  # Startet die Überwachung als Hintergrundtask

    def stop_loop():
        print("Beenden erkannt, schließe UDP-Listener...")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, stop_loop)  # Fängt Strg+C ab
    await stop_event.wait()  # Warten, bis Strg+C gedrückt wird
    transport.close()

class UDPServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
        print("UDP-Server gestartet und lauscht...")

    def datagram_received(self, data, addr):
        message = data.decode("utf-8", errors="replace")  
        print(f"Empfangen von {addr}: {message}")

    def connection_lost(self, exc):
        print("Verbindung verloren, UDP-Listener wird beendet.")

if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(read_udp_message(ip, port))
    except KeyboardInterrupt:
        print("UDP-Listener durch KeyboardInterrupt beendet.")
    finally:
        loop.close()
