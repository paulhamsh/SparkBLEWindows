import asyncio
import sys
from time import sleep

from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

SERVICE_UUID         = "0000ffc0-0000-1000-8000-00805f9b34fb"
SPARK_RECV_CHAR_UUID = "0000ffc2-0000-1000-8000-00805f9b34fb"
SPARK_SEND_CHAR_UUID = "0000ffc1-0000-1000-8000-00805f9b34fb"


preset=[
"01fe000053fead000000000000000000f0013a15010124040000007f5924004344453939353900312d433035442d00344145302d39450033342d45433441003831463346383402462c537765657400204d656d6f72791123302e3727312d20436c65616e286900636f6e2e706e67654a42700000172e00626961732e6e6f00697365676174655b421300114a3d4b18441c01114a3f121a2c5c02114a000004000028426c756510436f6d7042f7",
"01fe000053fead000000000000000000f0013a1501016c0401001400114a6a3e5c6c5b01114a643f294d7002114a6e3e35485a03114a143f0e18782d44690073746f7274696f306e54533942130033114a3d6d1c710113114a3f3d617e0253114a3f180e7a2b0039344d61746368304443563243150023114a3f0767320103114a3f003b4f0203114a3e7c1227033b114a3e55101f0443114a3f48445b2700466c616e6765721b421300114af7",
"01fe000053fead000000000000000000f0013a150101740402003e535c2d2601114a3f293d302602114a3f27395a012a44656c61795230653230314315002b114a3d483f55011b114a3e1f5652022b114a3e786946030b114a3e3d4174044b114a3f0000002b00626961732e7265307665726243170033114a3f0f29520113114a3f013467021b114a3e55715a032b114a3e1a081e0403114a3f1a2f7b0503114a3f18181e0603114a000000f7",
"01fe000053fe1d000000000000000000f0013a15010110040302006bf7",
]

async def spark():
    def match_uuid(device: BLEDevice, adv: AdvertisementData):
        if SERVICE_UUID in adv.service_uuids:
            return True
        return False

    device = await BleakScanner.find_device_by_filter(match_uuid)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        #for task in asyncio.all_tasks():
        #    task.cancel()

    def handle_rx(_: int, data: bytearray):
        print("received:", data)

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(SPARK_RECV_CHAR_UUID, handle_rx)

        print("Connected")

#       loop = asyncio.get_running_loop()

        while True:
            await client.write_gatt_char(SPARK_SEND_CHAR_UUID, bytes.fromhex("01fe000053fe1a000000000000000000f00124000138000000f7"))
#            dat = await client.read_gatt_char(SPARK_RECV_CHAR_UUID)
#            print (dat)
            print("sent preset")
            await asyncio.sleep(5)
            for hexdat in preset:
               await client.write_gatt_char(SPARK_SEND_CHAR_UUID, bytes.fromhex(hexdat))
               print(hexdat)
               await asyncio.sleep(0.5)
            await client.write_gatt_char(SPARK_SEND_CHAR_UUID, bytes.fromhex("01fe000053fe1a000000000000000000f0012400013800007ff7"))   
            print("sent full preset")
            await asyncio.sleep(10)            

if __name__ == "__main__":
    try:
        asyncio.run(spark())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
