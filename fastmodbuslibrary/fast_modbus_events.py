import struct
import logging
from .common import ModbusCommon

class ModbusEventReader(ModbusCommon):
    """
    A class for reading and parsing Modbus event notifications.

    Attributes:
        REQUEST_EVENTS_COMMAND (int): The command for requesting event notifications.
    """

    REQUEST_EVENTS_COMMAND = 0x10

    def __init__(self, device: str, baudrate: int):
        """
        Initialize the ModbusEventReader instance.

        Args:
            device (str): The serial device path (e.g., /dev/ttyUSB0).
            baudrate (int): The baud rate for the serial connection.
        """
        super().__init__(device, baudrate)
        self.logger = logging.getLogger(__name__)

    def parse_event_response(self, response: bytes):
        """
        Parse the event response from the Modbus device.

        Args:
            response (bytes): The raw response data.

        Returns:
            list: A list of dictionaries containing event information.
        """
        events = []
        if len(response) < 7:
            return events

        if len(response) < 12:
            self.logger.error("Response too short to be valid")
            return events

        device_id = response[0]
        command = response[1]
        subcommand = response[2]
        flag = response[3]
        event_count = response[4]
        event_data_len = struct.unpack('>H', response[5:7])[0]  # event data length
        event_type = struct.unpack('>H', response[7:9])[0]
        event_payload = struct.unpack('>H', response[9:11])[0]

        events.append({
            "device_id": device_id,
            "event_count": event_count,
            "flag": flag,
            "event_data_len": event_data_len,
            "event_type": event_type,
            "event_payload": event_payload
        })

        return events

    def request_events(self, min_slave_id: int, max_data_length: int, slave_id: int, flag: int):
        """
        Request event notifications from the Modbus device.

        Args:
            min_slave_id (int): The minimum slave ID to request events from.
            max_data_length (int): The maximum data length to request.
            slave_id (int): The specific slave ID to request events from.
            flag (int): The flag for the event request.

        Returns:
            list: A list of dictionaries containing event information, or None if the request failed.
        """
        request_command = struct.pack('>BBBBBBB', self.BROADCAST_ADDRESS, self.EXTENDED_FUNCTION_CODE, self.REQUEST_EVENTS_COMMAND, min_slave_id, max_data_length, slave_id, flag)
        self.send_command(request_command)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            self.logger.debug(f"RCV (raw): {self.format_bytes(response)}")

            response = response.lstrip(b'\xFF')

            self.logger.debug(f"RCV (filtered): {self.format_bytes(response)}")

            if not self.check_crc(response):
                self.logger.error("Invalid CRC in response.")
                return None
            return self.parse_event_response(response)
        return None
