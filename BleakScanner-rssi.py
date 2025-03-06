import asyncio
from collections import OrderedDict

#BLE Scanner with Name MAC and RSSI

from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover(return_adv=True)

    devices = OrderedDict(
        sorted(devices.items(), key=lambda x: x[1][1].rssi, reverse=True)
    )

    for i, (addr, (dev, adv)) in enumerate(devices.items()):
        print(i, addr, dev.name, adv.rssi)

asyncio.run(main())
