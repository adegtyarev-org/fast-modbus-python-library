import struct
import logging
from .common import ModbusCommon

class ModbusClient(ModbusCommon):
    """
    A class for interacting with Modbus devices using read and write commands.
    """

    def __init__(self, device: str, baudrate: int, ext_func_code: int = 0x46):
        """
        Initialize the ModbusClient instance.

        Args:
            device (str): The serial device path (e.g., /dev/ttyUSB0).
            baudrate (int): The baud rate for the serial connection.
        """
        super().__init__(device, baudrate, ext_func_code)
        self.logger = logging.getLogger(__name__)

    def read_registers(self, serial_number: int, command: int, register: int, count: int = 1):
        """
        Read registers from the Modbus device.

        Args:
            serial_number (int): The serial number of the device.
            command (int): The command to execute (e.g., 0x03 for Read Holding Registers).
            register (int): The starting register address.
            count (int): The number of registers to read.

        Returns:
            bytes: The data read from the registers, or None if the response is invalid.
        """
        request_command = struct.pack('>BBBIBHH', self.BROADCAST_ADDRESS, self.ext_func_code, 0x08, serial_number, command, register, count)
        self.send_command(request_command)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            self.logger.debug(f"RCV: {self.format_bytes(response)}")
            if not self.check_crc(response) or len(response) < 9 + 2 * count:
                self.logger.error("Invalid or short response.")
                return None
            return response[9:9 + 2 * count]
        return None

    def write_registers(self, serial_number: int, command: int, register: int, values: list):
        """
        Write registers to the Modbus device.

        Args:
            serial_number (int): The serial number of the device.
            command (int): The command to execute (e.g., 0x10 for Write Multiple Registers).
            register (int): The starting register address.
            values (list): The list of values to write to the registers.

        Returns:
            bool: True if the write operation was successful, False otherwise.
        """
        register_count = len(values)
        write_command = struct.pack('>BBBIBHHB', self.BROADCAST_ADDRESS, self.ext_func_code, 0x08, serial_number, command, register, register_count, register_count * 2)
        write_command += struct.pack(f'>{register_count}H', *values)
        self.send_command(write_command)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            self.logger.debug(f"RCV: {self.format_bytes(response)}")
            if self.check_crc(response):
                expected_response = struct.pack('>BBBIBHH', self.BROADCAST_ADDRESS, self.ext_func_code, 0x09, serial_number, command, register, register_count)
                if response[:-2] == expected_response:
                    return True
                else:
                    self.logger.error("Write response does not match expected format.")
            else:
                self.logger.error("Invalid CRC in response.")
        return False
