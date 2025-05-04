import struct
import logging
from .common import ModbusCommon  # Import the base class with common functions

class ModbusEventReader(ModbusCommon):
    """
    A class for reading and parsing Modbus event notifications, inheriting common Modbus functions from ModbusCommon.
    """

    REQUEST_EVENTS_COMMAND = 0x10
    SUBCOMMAND_EVENT_TRANSMISSION = 0x11
    MIN_PACKET_LENGTH = 6

    def __init__(self, device: str, baudrate: int, ext_func_code: int = 0x46):
        """
        Initialize the ModbusEventReader instance with Modbus communication setup.

        Args:
            device (str): The serial device path (e.g., /dev/ttyUSB0).
            baudrate (int): The baud rate for the serial connection.
        """
        super().__init__(device, baudrate, ext_func_code)  # Initialize via the parent class ModbusCommon
        self.logger = logging.getLogger(__name__)

    def parse_event_response(self, response: bytes):
        """
        Parse the event packet according to the protocol.

        Args:
            response (bytes): The response packet in the format of hexadecimal bytes.

        Returns:
            dict: A structure containing packet data, including packet_info and events.
        """
        if len(response) < self.MIN_PACKET_LENGTH:
            self.logger.debug("Received packet is too short.")
            return {}

        if response[1] != self.ext_func_code and response[2] != self.SUBCOMMAND_EVENT_TRANSMISSION:
            self.logger.debug("Received packet is not an event transmission packet.")
            return {}

        packet_info = {}  # Dictionary to store packet information

        # Extract data from the packet
        packet_info['device_id'] = response[0]  # Device ID
        packet_info['command'] = response[1]  # Command
        packet_info['subcommand'] = response[2]  # Subcommand
        packet_info['flag'] = response[3]  # Flag
        packet_info['event_count'] = response[4]  # Event Count
        packet_info['events_data_length'] = response[5]  # Events Data Length

        # Index for processing events
        index = 6
        events = []  # List to store event information

        # Process events
        for event_index in range(response[4]):  # Based on the number of events
            # Extract event data
            event_payload_length = response[index]  # Payload length
            event_type = response[index + 1]  # Event type
            event_id = (response[index + 2] << 8) | response[index + 3]  # Event ID
            payload_value = 0

            if event_payload_length > 0:
                payload_value = response[index + 4]  # Payload (if available)

            # Add event information to the structure
            events.append({
                "event_type": event_type,  # Event type
                "event_id": event_id,  # Event ID
                "event_payload_value": payload_value  # Payload value
            })

            index += 4 + event_payload_length  # Move to the next event

        # Prepare the log output
        log_output = []
        log_output.append("Packet Structure:")
        log_output.append(f"| - ({response[0]:02X}) Device ID: {packet_info['device_id']}")
        log_output.append(f"| - ({response[1]:02X}) Command: {packet_info['command']}")
        log_output.append(f"| - ({response[2]:02X}) Subcommand: {packet_info['subcommand']}")
        log_output.append(f"| - ({response[3]:02X}) Flag: {packet_info['flag']}")
        log_output.append(f"| - ({response[4]:02X}) Event Count: {packet_info['event_count']}")
        log_output.append(f"| - ({response[5]:02X}) Events Data Length: {packet_info['events_data_length']} bytes")

        for event_index, event in enumerate(events, start=1):
            log_output.append(f"  |- Event {event_index}:")
            log_output.append(f"      |- ({event['event_payload_value']}) Event Payload Length: {event_payload_length}")
            log_output.append(f"      |- ({event['event_type']}) Event Type: {event['event_type']}")
            log_output.append(f"      |- ({event_id:02X}) Event ID: {event['event_id']}")
            log_output.append(f"      |- ({event['event_payload_value']}) Event Payload Value: {event['event_payload_value']}")

        # Log all packet information
        self.logger.debug("\n".join(log_output))

        return {
            "packet_info": packet_info,  # Return packet information
            "events": events  # Return event information
        }

    def request_events(self, min_slave_id: int, max_data_length: int, slave_id: int, flag: int):
        """
        Request event notifications from the Modbus device.

        Args:
            min_slave_id (int): The minimum slave ID to request events from.
            max_data_length (int): The maximum data length to request.
            slave_id (int): The specific slave ID to request events from.
            flag (int): The flag for the event request.

        Returns:
            list: A list of dictionaries containing event information, or an empty dictionary if the request failed.
        """
        request_command = struct.pack('>BBBBBBB', self.BROADCAST_ADDRESS, self.ext_func_code,
                                      self.REQUEST_EVENTS_COMMAND, min_slave_id, max_data_length, slave_id, flag)
        self.send_command(request_command)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            self.logger.debug(f"RCV (raw): {self.format_bytes(response)}")

            response = response.lstrip(b'\xFF')
            self.logger.debug(f"RCV (filtered): {self.format_bytes(response)}")

            if not self.check_crc(response):
                self.logger.error("Invalid CRC in response.")
                return {}  # Return an empty dictionary if CRC is invalid
            return self.parse_event_response(response)
        return {}
