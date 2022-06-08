# requires pip install winrt

import asyncio

from winsdk.windows.devices.bluetooth import BluetoothAdapter

async def main():
    adapter = await BluetoothAdapter.get_default_async()
    # https://docs.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.bluetoothadapter?view=winrt-22000
    print("are_classic_secure_connections_supported",       adapter.are_classic_secure_connections_supported)
    print("are_low_energy_secure_connections_supported",    adapter.are_low_energy_secure_connections_supported)
    print("bluetooth_address",                              adapter.bluetooth_address)
    print("device_id",                                      adapter.device_id)
    print("is_advertisement_offload_supported",             adapter.is_advertisement_offload_supported)
    print("is_central_role_supported",                      adapter.is_central_role_supported)
    print("is_classic_supported",                           adapter.is_classic_supported)
    #print("is_extended_advertising_supported",             adapter.is_extended_advertising_supported)
    print("is_low_energy_supported",                        adapter.is_low_energy_supported)
    print("is_peripheral_role_supported",                   adapter.is_peripheral_role_supported)
    #print("max_advertisement_data_length",                 adapter.max_advertisement_data_length)

asyncio.run(main())
