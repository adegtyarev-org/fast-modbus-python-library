import serial
import struct
import time
import logging
from .logging_config import setup_logging

class ModbusCommon:
    """
    Common methods and utilities for Modbus communication.

    Attributes:
        BROADCAST_ADDRESS (int): The broadcast address for Modbus communication.
        EXTENDED_FUNCTION_CODE (int): The extended function code for Modbus communication.
    """

    BROADCAST_ADDRESS = 0xFD
    EXTENDED_FUNCTION_CODE = 0x46

    def __init__(self, device: str, baudrate: int):
        """
        Initialize the ModbusCommon instance.

        Args:
            device (str): The serial device path (e.g., /dev/ttyUSB0).
            baudrate (int): The baud rate for the serial connection.
        """
        self.device = device
        self.baudrate = baudrate
        self.logger = logging.getLogger(__name__)
        self.serial_port = self.init_serial()

    def init_serial(self) -> serial.Serial:
        """
        Initialize the serial connection.

        Returns:
            serial.Serial: The initialized serial connection.

        Raises:
            serial.SerialException: If there is an error initializing the serial port.
        """
        try:
            return serial.Serial(
                port=self.device,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0
            )
        except serial.SerialException as e:
            self.logger.error(f"Error initializing serial port: {e}")
            raise

    def calculate_crc(self, data: bytes) -> int:
        """
        Calculate the CRC16 checksum for the given data.

        Args:
            data (bytes): The data for which to calculate the checksum.

        Returns:
            int: The calculated CRC16 checksum.
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return crc

    def check_crc(self, response: bytes) -> bool:
        """
        Check if the CRC in the response is valid.

        Args:
            response (bytes): The response data from the Modbus device.

        Returns:
            bool: True if the CRC is valid, False otherwise.
        """
        return len(response) >= 3 and struct.unpack('<H', response[-2:])[0] == self.calculate_crc(response[:-2])

    def format_bytes(self, data: bytes) -> str:
        """
        Format the given bytes into a human-readable string.

        Args:
            data (bytes): The bytes to format.

        Returns:
            str: The formatted string.
        """
        return ' '.join(f"0x{byte:02X}" for byte in data)

    def send_command(self, command: bytes):
        """
        Send a command to the Modbus device, appending a CRC16 checksum.

        Args:
            command (bytes): The command bytes to send.
        """
        full_command = command + struct.pack('<H', self.calculate_crc(command))
        self.logger.debug(f"SND: {self.format_bytes(full_command)}")
        self.serial_port.write(full_command)

    def wait_for_response(self, timeout: int = 2) -> bool:
        """
        Wait for a response from the Modbus device.

        Args:
            timeout (int): The maximum time to wait for a response (in seconds).

        Returns:
            bool: True if a response is received within the timeout, False otherwise.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if self.serial_port.in_waiting > 0:
                    return True
            except serial.SerialException as e:
                self.logger.error(f"Error waiting for response: {e}")
                return False
            time.sleep(0.1)
        return False
