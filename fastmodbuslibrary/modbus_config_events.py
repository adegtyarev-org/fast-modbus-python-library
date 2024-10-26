"""
Module for configuring events on Modbus devices.

Classes:
    FastModbusConfigEvents -- Sets up and configures event parameters on devices.
"""

import serial
import struct
import time

class FastModbusConfigEvents:
    def __init__(self, device, baudrate=9600):
        self.device = device
        self.baudrate = baudrate
        self.serial_port = self.init_serial()

    def init_serial(self):
        """Initialize and open the serial port."""
        return serial.Serial(port=self.device, baudrate=self.baudrate, bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

    def calculate_crc(self, data):
        """Calculate CRC for Modbus data."""
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if (crc & 1) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def send_command(self, command, debug=False):
        """Send a command to the Modbus device, appending a CRC16 checksum."""
        crc = self.calculate_crc(command)
        command += struct.pack('<H', crc)
        if debug:
            print(f"SND: {self.format_bytes(command)}")
        self.serial_port.write(command)

    def format_bytes(self, data):
        """Format data as a human-readable hex string."""
        return ' '.join(f"0x{byte:02X}" for byte in data)

    def configure_events(self, slave_id, config, debug=False):
        """Configure event settings for multiple register ranges on a Modbus device."""
        for cfg in config.split(','):
            command = self.formulate_command(slave_id, cfg, debug)
            self.send_command(command, debug)
            time.sleep(1)
            response = self.serial_port.read(256)
            mask_data = self.parse_response(response, debug)
            if mask_data:
                self.print_settings(cfg, mask_data, slave_id)

    def formulate_command(self, slave_id, config, debug=False):
        """Create a command to configure event notifications for multiple register ranges."""
        command = [slave_id, 0x46, 0x18]
        data = []
        for cfg in config.split(','):
            reg_type, address, count, priority = cfg.split(':')
            address, count, priority = int(address), int(count), int(priority)
            reg_type_byte = {
                "coil": 0x01,
                "discrete": 0x02,
                "holding": 0x03,
                "input": 0x04
            }.get(reg_type.lower())
            if reg_type_byte is None:
                raise ValueError(f"Unknown register type: {reg_type}")
            data.append(reg_type_byte)
            data += list(struct.pack('>H', address))
            data.append(count)
            data += [priority] * count
        command.append(len(data))
        command += data
        return bytes(command)

    def parse_response(self, response, debug=False):
        """Parse the response from the Modbus device."""
        response = response.lstrip(b'\xFF')
        if len(response) < 4:
            return None
        length = response[3]
        return response[4:4 + length]

    def print_settings(self, config, mask_data, slave_id):
        """Display the event settings in a human-readable format."""
        byte_index = 0
        for cfg in config.split(','):
            reg_type, address, count, _ = cfg.split(':')
            address, count = int(address), int(count)
            for i in range(count):
                if byte_index < len(mask_data):
                    mask_byte = mask_data[byte_index]
                    bit_position = i % 8
                    bit = (mask_byte >> bit_position) & 1
                    reg_address = address + i
                    status = "enabled" if bit else "disabled"
                    print(f"- Register {reg_address} (u16): {status}")
                if (i + 1) % 8 == 0:
                    byte_index += 1

    def close(self):
        """Close the serial port connection."""
        self.serial_port.close()
