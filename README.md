# Fast Modbus Library

## Description
! This repository is not affiliated with and not supported by Wiren Board. Based on the scripts in the repository https://github.com/aadegtyarev/fast-modbus-python-tools

A library for working with Fast Modbus devices via a serial port (RS-485). It contains modules for configuring event notifications, scanning devices, and working with the Modbus client.

## Features
- **Device Scanning**: Detects Modbus devices on the network.
- **Data Exchange**: Reads and writes Modbus registers for real-time device communication.
- **Event Handling**: Requests and manages events from Modbus devices.
- **Event Configuration**: Sets up event parameters on Modbus devices.

## Installation

### Install Dependencies

```
pip install -r requirements.txt
```

### Install the Module

```
pip install .
```

## Usage

### Running Examples

```
cd ./fast-modbus-python-library
```
#### Device Scanning Example

```
python -m examples.example_scan -d /dev/ttyACM0 -b 9600
```
![image](https://github.com/user-attachments/assets/373503a4-6f26-424e-9704-50fe785c9fdf)


#### Modbus Client Example

```
# Read
python -m examples.example_client -d /dev/ttyACM0 -b 9600 -s 4265607340 -c 3 -r 128 -n 1

# Write
python -m examples.example_client -d /dev/ttyACM0 -b 9600 -s 4265607340 -c 0x10 -r 128 -w 201

```
![image](https://github.com/user-attachments/assets/11b5add6-54cc-43ea-a317-3e3f108940e8)

#### Event Notifications Configuration Example

```
python -m examples.example_config_events --device /dev/ttyACM0 --baud 9600 --slave_id 201 --config "discrete:0:2:1,discrete:4:3:0"
```
![image](https://github.com/user-attachments/assets/842f1ea5-6b72-446f-9310-d0d56a949d67)

#### Event Handling Example

```
python -m examples.example_events -d /dev/ttyACM0 -b 9600
```
![image](https://github.com/user-attachments/assets/fef68165-bc67-4616-8f8d-c8d9f8fd1f7c)

### Help on Parameters

```
python -m examples.example_client --help
```
![image](https://github.com/user-attachments/assets/6ca6ca34-e618-4862-9c51-79ab282f0f01)


## Module Descriptions

### fastmodbuslibrary

- **common.py**: Common functions and constants.
- **fast_modbus_client.py**: Modbus client for working with Modbus.
- **fast_modbus_config_events.py**: Module for configuring event notifications.
- **fast_modbus_events.py**: Module for handling events.
- **fast_modbus_scanner.py**: Module for scanning devices.
- **__init__.py**: Package initialization.
- **logging_config.py**: Logging configuration.

## Tests

### Running Tests
```
cd ./fast-modbus-python-library

python -m unittest discover tests
```

### Test Descriptions

- **test_modbus_client_multiple.py**: Tests for working with multiple Modbus clients.
- **test_modbus_client_single.py**: Tests for working with a single Modbus client.
- **test_modbus_client_write.py**: Tests for writing data to Modbus.
- **test_modbus_config_events.py**: Tests for configuring event notifications.
- **test_modbus_events_confirmation.py**: Tests for event confirmation.
- **test_modbus_events.py**: Tests for event handling.
- **test_modbus_scanner.py**: Tests for device scanning.


## Contributing

Initial code generated with assistance from [DeepSeek](https://chat.deepseek.com/). Contributions and improvements are welcome! Feel free to submit pull requests to improve functionality or documentation.

## License
This project is licensed under the MIT License.
