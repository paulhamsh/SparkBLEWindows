import asyncio
import sys
from time import sleep
import logging
import threading
from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice
from typing import Any, Dict
from bless import (  # type: ignore
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

SPARK_SVR_SERVICE_UUID   = "0000ffc0-0000-1000-8000-00805f9b34fb"
SPARK_SVR_RECV_CHAR_UUID = "0000ffc2-0000-1000-8000-00805f9b34fb"
SPARK_SVR_SEND_CHAR_UUID = "0000ffc1-0000-1000-8000-00805f9b34fb"

SPARK_CLI_SERVICE_UUID   = "0000ffc0-0000-1000-8000-00805f9b34fb"
# use to receive from Spark
SPARK_CLI_RECV_CHAR_UUID = "0000ffc2-0000-1000-8000-00805f9b34fb"
# use to send to Spark
SPARK_CLI_SEND_CHAR_UUID = "0000ffc1-0000-1000-8000-00805f9b34fb"



preset=[
"01fe000053fead000000000000000000f0013a15010124040000007f59"+
"24004344453939353900312d433035442d00344145302d39450033342d"+
"45433441003831463346383402462c537765657400204d656d6f727911"+
"23302e3727312d20436c65616e286900636f6e2e706e67654a42700000"+
"172e00626961732e6e6f00697365676174655b421300114a3d4b18441c"+
"01114a3f121a2c5c02114a000004000028426c756510436f6d7042f7",
"01fe000053fead000000000000000000f0013a1501016c040100140011"+
"4a6a3e5c6c5b01114a643f294d7002114a6e3e35485a03114a143f0e18"+
"782d44690073746f7274696f306e54533942130033114a3d6d1c710113"+
"114a3f3d617e0253114a3f180e7a2b0039344d61746368304443563243"+
"150023114a3f0767320103114a3f003b4f0203114a3e7c1227033b114a"+
"3e55101f0443114a3f48445b2700466c616e6765721b421300114af7",
"01fe000053fead000000000000000000f0013a150101740402003e535c"+
"2d2601114a3f293d302602114a3f27395a012a44656c61795230653230"+
"314315002b114a3d483f55011b114a3e1f5652022b114a3e786946030b"+
"114a3e3d4174044b114a3f0000002b00626961732e7265307665726243"+
"170033114a3f0f29520113114a3f013467021b114a3e55715a032b114a"+
"3e1a081e0403114a3f1a2f7b0503114a3f18181e0603114a000000f7",
"01fe000053fe1d000000000000000000f0013a15010110040302006bf7",
]

def read_request(
        characteristic: BlessGATTCharacteristic,
        **kwargs
        ) -> bytearray:
    print(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(
        characteristic: BlessGATTCharacteristic,
        value: Any,
        **kwargs
        ):
    characteristic.value = value
    print(f"Char value set to {characteristic.value}")
    if characteristic.value == b'\x0f':
        print("Nice")

async def spark():
    def match_uuid(device: BLEDevice, adv: AdvertisementData):
        if SPARK_CLI_SERVICE_UUID in adv.service_uuids:
            return True
        return False



    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        #for task in asyncio.all_tasks():
        #    task.cancel()

    def handle_rx(_: int, data: bytearray):
        print("received:", data, "\n")
        
 
    # Instantiate the client
    print("Create client")
    device = await BleakScanner.find_device_by_filter(match_uuid)
    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        print("Scan")   
        ###client = BleakClient(device, disconnected_callback=handle_disconnect)
        await client.start_notify(SPARK_CLI_RECV_CHAR_UUID, handle_rx)
        print("Connected client")


    
        # Instantiate the server
        gatt: Dict = {
                SPARK_SVR_SERVICE_UUID : {
                    SPARK_SVR_RECV_CHAR_UUID: {
                        "Properties": (GATTCharacteristicProperties.read |
                                   GATTCharacteristicProperties.notify),
                        "Permissions": (GATTAttributePermissions.readable |
                                    GATTAttributePermissions.writeable),
                        "Value": (bytearray(b"A"))
                        },
                    SPARK_SVR_SEND_CHAR_UUID: {
                        "Properties": (GATTCharacteristicProperties.read |
                                   GATTCharacteristicProperties.write),
                        "Permissions": (GATTAttributePermissions.readable |
                                    GATTAttributePermissions.writeable),
                        "Value": (bytearray(b"B"))
                        }               
                    }
                }

        print("Create server")
        my_service_name = "Spar"
        server = BlessServer(name = my_service_name)
        server.read_request_func = read_request
        server.write_request_func = write_request

        await server.add_gatt(gatt)
        await server.start()
        print(server.get_characteristic(SPARK_SVR_SEND_CHAR_UUID))
        print("Advertising")




        await client.write_gatt_char(SPARK_CLI_SEND_CHAR_UUID, bytes.fromhex("01fe000053fe1a000000000000000000f00124000138000000f7"))
        print("Sent hardware preset")
        await asyncio.sleep(5)
        for hexdat in preset:
            await client.write_gatt_char(SPARK_CLI_SEND_CHAR_UUID, bytes.fromhex(hexdat))
            print(hexdat)
            await asyncio.sleep(0.5)
        await client.write_gatt_char(SPARK_CLI_SEND_CHAR_UUID, bytes.fromhex("01fe000053fe1a000000000000000000f0012400013800007ff7"))   
        print("Sent full preset")
        print("Now just waiting to receive data")
        print("Write '0xF' to the advertised characteristic: " + SPARK_SVR_SEND_CHAR_UUID)
        await asyncio.sleep(60)
        print("Updating")
        server.get_characteristic(SPARK_SVR_RECV_CHAR_UUID).value = (bytearray(b"i"))
        server.update_value(
            SPARK_SVR_SERVICE_UUID,
            SPARK_SVR_RECV_CHAR_UUID
            )
        await asyncio.sleep(60)
        print("Finished")
        await server.stop() 

asyncio.run(spark())

