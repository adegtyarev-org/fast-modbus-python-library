"""
Module for scanning Modbus devices on a network.

Classes:
    FastModbusScanner -- Scans and identifies Modbus devices.
"""

import serial
import struct
import time

class FastModbusScanner:
    def __init__(self, device, baudrate=9600):
        self.device = device
        self.baudrate = baudrate
        self.serial_port = self.init_serial()

    def init_serial(self):
        """Initialize and open the serial port."""
        return serial.Serial(port=self.device, baudrate=self.baudrate, bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0)

    def scan_devices(self, scan_command, debug=False):
        """Scan for Modbus devices on the network."""
        if debug:
            print(f"Starting scan on port {self.device} with baudrate {self.baudrate} and scan command {hex(scan_command)}...")
        devices = []
        self.send_command(struct.pack('BBB', 0xFD, scan_command, 0x01), debug)

        while self.wait_for_response(2):
            response = self.serial_port.read(256)
            if not response:
                break
            if debug:
                print(f"RCV: {self.format_bytes(response)}")
            response = response.lstrip(b'\xFF')
            if len(response) >= 10 and response[2] == 0x03:
                serial_number, modbus_id = struct.unpack('>I', response[3:7])[0], response[7]
                model = self.request_device_model(serial_number, debug)
                devices.append({"serial_number": serial_number, "modbus_id": modbus_id, "model": model})
                self.send_command(struct.pack('BBB', 0xFD, scan_command, 0x02), debug)
            elif response[2] == 0x04:
                if debug:
                    print("Scan complete.")
                break
        return devices

    def send_command(self, command, debug=False):
        """Send command to Modbus device."""
        full_command = command + struct.pack('<H', self.calculate_crc(command))
        if debug:
            print(f"SND: {self.format_bytes(full_command)}")
        self.serial_port.write(full_command)

    def format_bytes(self, data):
        """Format data as a human-readable hex string."""
        return ' '.join(f"0x{byte:02X}" for byte in data)

    def request_device_model(self, serial_number, debug=False):
        """Request the model of the Modbus device by reading specific registers."""
        model_request = struct.pack('>BBBIBHH', 0xFD, 0x46, 0x08, serial_number, 0x03, 200, 20)
        self.send_command(model_request, debug)
        if self.wait_for_response():
            response = self.serial_port.read(256)
            if debug:
                print(f"RCV: {self.format_bytes(response)}")
            if self.check_crc(response) and len(response) >= 40:
                return response[9:29].decode('ascii').strip()
        return "Unknown"

    def calculate_crc(self, data):
        """Calculate CRC for Modbus data."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return crc

    def wait_for_response(self, timeout=2):
        """Wait for response from device."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.serial_port.in_waiting > 0:
                return True
            time.sleep(0.1)
        return False

    def check_crc(self, response):
        """Verify CRC of received response."""
        return len(response) >= 3 and struct.unpack('<H', response[-2:])[0] == self.calculate_crc(response[:-2])

    def close(self):
        """Close the serial port connection."""
        self.serial_port.close()
