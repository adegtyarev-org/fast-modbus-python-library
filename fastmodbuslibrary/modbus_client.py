"""
Module for reading and writing Modbus registers.

Classes:
    FastModbusClient -- Provides methods to read and write registers.
"""

import serial
import struct
import time

class FastModbusClient:
    def __init__(self, device, baudrate=9600):
        self.device = device
        self.baudrate = baudrate
        self.serial_port = self.init_serial()

    def init_serial(self):
        """Initialize and open the serial port."""
        return serial.Serial(port=self.device, baudrate=self.baudrate, bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0)

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

    def read_registers(self, serial_number, command, register, count=1, debug=False):
        """Read registers from Modbus device."""
        request_command = struct.pack('>BBBIBHH', 0xFD, 0x46, 0x08, serial_number, command, register, count)
        self.send_command(request_command, debug)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            if not self.check_crc(response) or len(response) < 9 + 2 * count:
                if debug:
                    print("[error] Invalid or short response.")
                return None
            return response[9:9 + 2 * count]
        return None

    def write_registers(self, serial_number, command, register, values, debug=False):
        """Write values to registers on Modbus device."""
        register_count = len(values)
        write_command = struct.pack('>BBBIBHHB', 0xFD, 0x46, 0x08, serial_number, command, register, register_count, register_count * 2)
        write_command += struct.pack(f'>{register_count}H', *values)
        self.send_command(write_command, debug)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            return self.check_crc(response)
        return False

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
