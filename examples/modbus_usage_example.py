
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmodbuslibrary import FastModbusScanner, FastModbusClient, FastModbusEvents, FastModbusConfigEvents

def print_section(title):
    print("\n" + "="*50)
    print(f"{title}")
    print("="*50)

# Device scanning example
print_section("Scanning for devices on the Modbus network...")
scanner = FastModbusScanner(device="/dev/ttyACM0", baudrate=9600)
devices = scanner.scan_devices(scan_command=0x46, debug=False)
scanner.close()

if devices:
    print("Devices found:")
    for device in devices:
        print(f"  - Model: {device['model']}, Modbus ID: {device['modbus_id']}, Serial Number: {device['serial_number']}")
else:
    print("No devices found.")

# Register reading example
print_section("Reading registers from each device...")
client = FastModbusClient(device="/dev/ttyACM0", baudrate=9600)
for device in devices:
    serial_number = device["serial_number"]
    model = device["model"]
    modbus_id = device["modbus_id"]
    print(f"Device {model} (Modbus ID {modbus_id}, Serial {serial_number}):")
    
    # Read single register at 128
    register_128 = client.read_registers(serial_number=serial_number, command=0x03, register=128, count=1, debug=False)
    print(f"  - Register 128 Value: {register_128}")
    
    # Read multiple registers starting from 200
    registers_200_204 = client.read_registers(serial_number=serial_number, command=0x03, register=200, count=5, debug=False)
    print(f"  - Registers 200-204 Values: {registers_200_204}")

# Example of writing to a register
print_section("Writing values to register 200 on example device...")
if devices:
    serial_number = devices[1]["serial_number"] if len(devices) > 1 else devices[0]["serial_number"]
    success = client.write_registers(serial_number=serial_number, command=0x10, register=200, values=[15, 30], debug=False)
    print(f"Write to Serial {serial_number} successful: {success}")

client.close()

# Events handling example
print_section("Requesting events from the first found device...")
if devices:
    events = FastModbusEvents(device="/dev/ttyACM0", baudrate=9600)
    response = events.request_events(min_slave_id=1, max_data_length=100, slave_id=1, flag=0, debug=False)
    print("Event data:", response)
    events.close()

# Event configuration example
print_section("Configuring events on first available device...")
if devices:
    config_events = FastModbusConfigEvents(device="/dev/ttyACM0", baudrate=9600)
    config_events.configure_events(slave_id=4, config="input:60:2:1,discrete:0:8:1", debug=False)
    print(f"Event configuration applied successfully on device with Modbus ID {devices[0]['modbus_id']}")
    config_events.close()
