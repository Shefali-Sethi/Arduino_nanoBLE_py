import asyncio
import struct
from bleak import BleakClient, BleakScanner
import time

# Define UUIDs for BLE service and characteristics
ACCEL_X_UUID = "13012F04-F8C3-4F4A-A8F4-15CD926DA146"
ACCEL_Y_UUID = "13012F05-F8C3-4F4A-A8F4-15CD926DA146"
ACCEL_Z_UUID = "13012F06-F8C3-4F4A-A8F4-15CD926DA146"
GYRO_X_UUID = "13012F07-F8C3-4F4A-A8F4-15CD926DA146"
GYRO_Y_UUID = "13012F08-F8C3-4F4A-A8F4-15CD926DA146"
GYRO_Z_UUID = "13012F09-F8C3-4F4A-A8F4-15CD926DA146"

# Global variables to hold scaled sensor data
accel_x = accel_y = accel_z = 0.0
gyro_x = gyro_y = gyro_z = 0.0
accel_x_count = accel_y_count = accel_z_count = 0
gyro_x_count = gyro_y_count = gyro_z_count = 0
start_time = time.time()
loop_count = 0

# Convert bytearray to 32-bit float
def bytearray_to_float(barr):
    return struct.unpack('<f', barr)[0]

# Callback functions to handle notifications
def accel_x_callback(sender, data):
    global accel_x, accel_x_count
    if len(data) == 4:
        accel_x = bytearray_to_float(data)
        accel_x_count += 1
        

def accel_y_callback(sender, data):
    global accel_y, accel_y_count
    if len(data) == 4:
        accel_y = bytearray_to_float(data)
        accel_y_count += 1
        

def accel_z_callback(sender, data):
    global accel_z, accel_z_count
    if len(data) == 4:
        accel_z = bytearray_to_float(data)
        accel_z_count += 1
        

def gyro_x_callback(sender, data):
    global gyro_x, gyro_x_count
    if len(data) == 4:
        gyro_x = bytearray_to_float(data)
        gyro_x_count += 1
        

def gyro_y_callback(sender, data):
    global gyro_y, gyro_y_count
    if len(data) == 4:
        gyro_y = bytearray_to_float(data)
        gyro_y_count += 1
        

def gyro_z_callback(sender, data):
    global gyro_z, gyro_z_count
    if len(data) == 4:
        gyro_z = bytearray_to_float(data)
        gyro_z_count += 1
        


async def count_loops_per_second():
    global loop_count
    while True:
        await asyncio.sleep(1)  # Sleep for 1 second
        print("\n" * 10)  # Print 5 new lines before printing loop count
        print("\033[93m")
        print(f"Sampling Frequency: {loop_count}") 
        print("\033[0m") 
        loop_count = 0  # Reset loop count

# Coroutine to run BLE operations
async def run_ble():
    global loop_count
    print('ProtoStax Arduino Nano BLE Sensor Peripheral Central Service')
    print('Looking for Arduino Nano 33 BLE Sense Peripheral Device...')

    devices = await BleakScanner.discover()
    if not devices:
        print('No devices found.')
        return

    for d in devices:
        if d.name and 'Arduino Nano 33 BLE Sense' in d.name:
            print('Found Arduino Nano 33 BLE Sense Peripheral')
            async with BleakClient(d) as client:
                print(f'Connected to {d.address}')
                # Set up notifications
                try:
                    await client.start_notify(ACCEL_X_UUID, accel_x_callback)
                    await client.start_notify(ACCEL_Y_UUID, accel_y_callback)
                    await client.start_notify(ACCEL_Z_UUID, accel_z_callback)
                    await client.start_notify(GYRO_X_UUID, gyro_x_callback)
                    await client.start_notify(GYRO_Y_UUID, gyro_y_callback)
                    await client.start_notify(GYRO_Z_UUID, gyro_z_callback)
                except Exception as e:
                    print(f"Error setting notifications: {e}")
                    return

                # Start counting loops per second
                loop_count_task = asyncio.create_task(count_loops_per_second())

                try:
                    while True:
                        await asyncio.sleep(0.01)  # Sleep for 0.01 seconds (100 Hz)
                        print(f"\rAccel X: {accel_x:.2f} g, Accel Y: {accel_y:.2f} g, Accel Z: {accel_z:.2f} g, "
                              f"Gyro X: {gyro_x:.2f} dps, Gyro Y: {gyro_y:.2f} dps, Gyro Z: {gyro_z:.2f} dps", end='')
                        loop_count += 1  # Increment loop count

                except KeyboardInterrupt:
                    print('\nReceived Keyboard Interrupt')
                    loop_count_task.cancel()
                    await asyncio.gather(
                        client.stop_notify(ACCEL_X_UUID),
                        client.stop_notify(ACCEL_Y_UUID),
                        client.stop_notify(ACCEL_Z_UUID),
                        client.stop_notify(GYRO_X_UUID),
                        client.stop_notify(GYRO_Y_UUID),
                        client.stop_notify(GYRO_Z_UUID),
                        return_exceptions=True
                    )

try:
    asyncio.run(run_ble())
except KeyboardInterrupt:
    print('\nReceived Keyboard Interrupt')
