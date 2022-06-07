
"""
Example for a BLE 4.0 Server using a GATT dictionary of services and
characteristics
"""

SERVICE_UUID         = "0000ffc0-0000-1000-8000-00805f9b34fb"
# use to receive from Spark by app
SPARK_RECV_CHAR_UUID = "0000ffc2-0000-1000-8000-00805f9b34fb"
# use to send to Spark from app
SPARK_SEND_CHAR_UUID = "0000ffc1-0000-1000-8000-00805f9b34fb"

import logging
import asyncio
import threading

from typing import Any, Dict

from bless import (  # type: ignore
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)
trigger: threading.Event = threading.Event()


def read_request(
        characteristic: BlessGATTCharacteristic,
        **kwargs
        ) -> bytearray:
    logger.debug(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(
        characteristic: BlessGATTCharacteristic,
        value: Any,
        **kwargs
        ):
    characteristic.value = value
    logger.debug(f"Char value set to {characteristic.value}")
    if characteristic.value == b'\x0f':
        logger.debug("Nice")


async def run(loop):

    # Instantiate the server
    gatt: Dict = {
            SERVICE_UUID : {
                SPARK_RECV_CHAR_UUID: {
                    "Properties": (GATTCharacteristicProperties.read |
                                   GATTCharacteristicProperties.notify),
                    "Permissions": (GATTAttributePermissions.readable |
                                    GATTAttributePermissions.writeable),
                    "Value": None
                    },
                SPARK_SEND_CHAR_UUID: {
                    "Properties": (GATTCharacteristicProperties.read |
                                   GATTCharacteristicProperties.write),
                    "Permissions": (GATTAttributePermissions.readable |
                                    GATTAttributePermissions.writeable),
                    "Value": None
                    }               
                }
            }
    my_service_name = "Sparksy"
    server = BlessServer(name=my_service_name, loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.add_gatt(gatt)
    await server.start()
    logger.debug(server.get_characteristic(SPARK_SEND_CHAR_UUID))
    logger.debug("Advertising")
    logger.info("Write '0xF' to the advertised characteristic: " +
                SPARK_SEND_CHAR_UUID)
    await asyncio.sleep(60)
    logger.debug("Updating")
    server.get_characteristic(SPARK_RECV_CHAR_UUID).value = (bytearray(b"i"))
    server.update_value(
            SERVICE_UUID,
            SPARK_RECV_CHAR_UUID
            )
    await asyncio.sleep(60)
    await server.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
