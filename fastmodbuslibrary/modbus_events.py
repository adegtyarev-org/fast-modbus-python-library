"""
Module for requesting and managing Modbus device events.

Classes:
    FastModbusEvents -- Sends requests and processes event data from devices.
"""

import serial
import struct
import time

class FastModbusEvents:
    def __init__(self, device, baudrate=9600):
        if isinstance(device, str):  # Убедимся, что device передан как строка
            self.serial_port = serial.Serial(port=device, baudrate=baudrate, bytesize=serial.EIGHTBITS,
                                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0)
        else:
            raise ValueError("The 'device' parameter must be a string representing the port name.")

    def calculate_crc(self, data):
        """Calculate CRC for Modbus data."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return crc

    def send_command(self, command, debug=False):
        """Send command to Modbus device with CRC."""
        full_command = command + struct.pack('<H', self.calculate_crc(command))
        if debug:
            print(f"SND: {self.format_bytes(full_command)}")
        self.serial_port.write(full_command)

    def format_bytes(self, data):
        """Format data as a human-readable hex string."""
        return ' '.join(f"0x{byte:02X}" for byte in data)

    def request_events(self, min_slave_id, max_data_length, slave_id, flag, debug=False):
        """Request events from the Modbus device."""
        request_command = struct.pack('>BBBBBBB', 0xFD, 0x46, 0x10, min_slave_id, max_data_length, slave_id, flag)
        self.send_command(request_command, debug)

        if self.wait_for_response():
            response = self.serial_port.read(256).lstrip(b'\xFF')
            if not self.check_crc(response):
                return None
            return response
        return None

    def parse_event_response(self, response):
        """Parse the event response."""
        if len(response) < 12:
            return "NO EVENTS" if len(response) < 7 else "[error] Response too short to be valid"

        device_id = response[0]
        command = response[1]
        subcommand = response[2]
        flag = response[3]
        event_count = response[4]
        event_data_len = struct.unpack('>H', response[5:7])[0]
        event_type = struct.unpack('>H', response[7:9])[0]
        event_payload = struct.unpack('>H', response[9:11])[0]
        frame_len = len(response)

        return {
            "device_id": device_id,
            "command": command,
            "subcommand": subcommand,
            "flag": flag,
            "event_count": event_count,
            "event_data_len": event_data_len,
            "frame_len": frame_len,
            "event_type": event_type,
            "event_payload": event_payload
        }

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
