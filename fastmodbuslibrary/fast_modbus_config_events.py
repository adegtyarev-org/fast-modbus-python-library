import struct
import logging
import time
from .common import ModbusCommon

class ModbusConfigEvents(ModbusCommon):
    """
    A class to configure event notifications for multiple register ranges on a Modbus device.
    """

    EXTENDED_FUNCTION_CODE = 0x46
    CONFIG_EVENTS_COMMAND = 0x18

    def __init__(self, device: str, baudrate: int):
        """
        Initialize the ModbusConfigEvents with the given parameters.

        Args:
            device (str): The serial device path (e.g., /dev/ttyACM0).
            baudrate (int): The baud rate for the connection.
        """
        super().__init__(device, baudrate)
        self.logger = logging.getLogger(__name__)

    def calculate_crc(self, data: bytes) -> int:
        """
        Calculate the CRC16 checksum for the given data.

        Args:
            data (bytes): The data for which to calculate the checksum.

        Returns:
            int: The calculated CRC16 checksum.
        """
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

    def send_command(self, command: list, debug: bool = False):
        """
        Send a command to the Modbus device, appending a CRC16 checksum.

        Args:
            command (list of int): The command bytes to send.
            debug (bool): If True, print debug information.
        """
        command_bytes = bytes(command)
        crc = self.calculate_crc(command_bytes)
        command_bytes += struct.pack('<H', crc)
        self.logger.debug(f"[debug] Command generated: {' '.join(f'0x{byte:02X}' for byte in command_bytes)}")
        self.serial_port.write(command_bytes)

    def formulate_command(self, slave_id: int, reg_type: str, address: int, count: int, priority: int) -> list:
        """
        Create a command to configure event notifications for a single register range.

        Args:
            slave_id (int): The slave ID of the Modbus device.
            reg_type (str): The type of register (e.g., 'discrete', 'input').
            address (int): The starting address of the register range.
            count (int): The number of registers in the range.
            priority (int): The priority of the event notifications (0 or 1).

        Returns:
            list: The generated command bytes.
        """
        command = [slave_id, self.EXTENDED_FUNCTION_CODE, self.CONFIG_EVENTS_COMMAND]
        data = []

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

        self.logger.debug(f"[debug] Range: {reg_type} Address: {address} Count: {count} Priority: {priority}")

        command.append(len(data))
        command += data
        return command

    def parse_response(self, response: bytes) -> bytes:
        """
        Parse the response from the Modbus device.

        Args:
            response (bytes): The raw response data.

        Returns:
            bytes: The parsed mask data from the response, or None if invalid.
        """
        response = response.lstrip(b'\xFF')
        if len(response) < 4:
            self.logger.error("[error] Response too short to be valid")
            return None

        slave_id, command, sub_command, length = response[:4]
        mask_data = response[4:4+length]

        if len(mask_data) != length:
            self.logger.error("[error] Response length does not match expected length")
            return None

        return mask_data

    def configure_events(self, slave_id: int, reg_type: str, address: int, count: int, priority: int):
        """
        Configure event settings for a single register range on a Modbus device.

        Args:
            slave_id (int): The slave ID of the Modbus device.
            reg_type (str): The type of register (e.g., 'discrete', 'input').
            address (int): The starting address of the register range.
            count (int): The number of registers in the range.
            priority (int): The priority of the event notifications (0 or 1).

        Returns:
            bytes: The mask data from the device response, or None if no valid response received.
        """
        command = self.formulate_command(slave_id, reg_type, address, count, priority)
        self.send_command(command)

        # Добавляем задержку для ожидания ответа
        time.sleep(0.5)

        response = self.serial_port.read(256)
        self.logger.debug(f"RAW Response: {response}")

        mask_data = self.parse_response(response)
        if mask_data:
            return mask_data
        else:
            return None
