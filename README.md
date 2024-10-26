
# Fast Modbus Python Library
! This repository is not affiliated with or supported by Wiren Board. All code is written by ChatGPT, based on the scripts in the repository https://github.com/aadegtyarev/fast-modbus-python-tools

**FastModbusLibrary** is a Python library that provides efficient and direct interaction with Modbus devices. 
This library includes modules to scan for devices, read and write registers, manage events, and configure 
event settings for Modbus-enabled devices.

![image](https://github.com/user-attachments/assets/2bd8fab4-5f65-4814-b770-3ecbdfdfb142)

## Features
- **Device Scanning**: Detects Modbus devices on the network.
- **Data Exchange**: Reads and writes Modbus registers for real-time device communication.
- **Event Handling**: Requests and manages events from Modbus devices.
- **Event Configuration**: Sets up event parameters on Modbus devices.

## Installation
This library is compatible with Python 3.8 and above. To install the library and its dependencies:

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd FastModbusLibrary
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

The library relies on `pymodbus` and custom dependencies outlined in `requirements.txt`.

## Usage
Below are usage examples for each module. Additional examples can be found in the `examples` directory.

### 1. FastModbusScanner
Scans the Modbus network for devices.

```python
from fastmodbuspythonlibrary import FastModbusScanner

scanner = FastModbusScanner(device="/dev/ttyACM0", baudrate=9600)
devices = scanner.scan_devices(scan_command=0x46, debug=True)
for device in devices:
    print(f"Found device with Modbus ID: {device['modbus_id']}, Serial Number: {device['serial_number']}")
scanner.close()
```

### 2. FastModbusClient
Reads and writes data to Modbus registers.

```python
from fastmodbuspythonlibrary import FastModbusClient

client = FastModbusClient(device="/dev/ttyACM0", baudrate=9600)

# Read a single holding register at address 128
data = client.read_registers(serial_number=123456, command=0x03, register=128, count=1)
print("Register 128 data:", data)

# Write values to a holding register starting at address 200
success = client.write_registers(serial_number=123456, command=0x10, register=200, values=[100, 200])
print("Write successful:", success)

client.close()
```

### 3. FastModbusEvents
Requests and retrieves event data from a Modbus device.

```python
from fastmodbuspythonlibrary import FastModbusEvents

events = FastModbusEvents(device="/dev/ttyACM0", baudrate=9600)
response = events.request_events(min_slave_id=1, max_data_length=100, slave_id=1, flag=0, debug=True)

if response:
    event_data = events.parse_event_response(response)
    print("Event Data:", event_data)
else:
    print("No events available.")

events.close()
```

### 4. FastModbusConfigEvents
Configures events on a Modbus device.

```python
from fastmodbuspythonlibrary import FastModbusConfigEvents

config_events = FastModbusConfigEvents(device="/dev/ttyACM0", baudrate=9600)
config_events.configure_events(slave_id=4, config="input:60:2:1,discrete:0:8:1", debug=True)
print("Event configuration applied.")

config_events.close()
```

## Dependencies
The primary dependencies for this library are:
- `pymodbus`
- `serial`

Ensure all dependencies are listed in `requirements.txt` for a smooth installation.

## License
This project is licensed under the MIT License.
