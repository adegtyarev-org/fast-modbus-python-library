import struct
import logging
from .common import ModbusCommon

class ModbusScanner(ModbusCommon):
    """
    A class for scanning Modbus devices on the network.

    Attributes:
        SCAN_START_COMMAND (int): The command to start the scan.
        SCAN_CONTINUE_COMMAND (int): The command to continue the scan.
        SCAN_RESPONSE_COMMAND (int): The command for the scan response.
        SCAN_END_COMMAND (int): The command to end the scan.
        MODEL_REQUEST_FUNCTION_CODE (int): The function code for requesting the device model.
        MODEL_REQUEST_START_REGISTER (int): The starting register for the model request.
        MODEL_REQUEST_REGISTER_COUNT (int): The number of registers to read for the model request.
    """

    SCAN_START_COMMAND = 0x01
    SCAN_CONTINUE_COMMAND = 0x02
    SCAN_RESPONSE_COMMAND = 0x03
    SCAN_END_COMMAND = 0x04
    MODEL_REQUEST_FUNCTION_CODE = 0x03
    MODEL_REQUEST_START_REGISTER = 200
    MODEL_REQUEST_REGISTER_COUNT = 20

    def __init__(self, device: str, baudrate: int):
        """
        Initialize the ModbusScanner instance.

        Args:
            device (str): The serial device path (e.g., /dev/ttyUSB0).
            baudrate (int): The baud rate for the serial connection.
        """
        super().__init__(device, baudrate)
        self.logger = logging.getLogger(__name__)

    def request_device_model(self, serial_number: int) -> str:
        """
        Request the device model information from the Modbus device.

        Args:
            serial_number (int): The serial number of the device.

        Returns:
            str: The device model information, or "Invalid CRC" if the CRC check fails, or "Unknown" if no response is received.
        """
        model_request = struct.pack(
            '>BBBIBHH',
            self.BROADCAST_ADDRESS,
            self.EXTENDED_FUNCTION_CODE,
            0x08,
            serial_number,
            self.MODEL_REQUEST_FUNCTION_CODE,
            self.MODEL_REQUEST_START_REGISTER,
            self.MODEL_REQUEST_REGISTER_COUNT
        )
        self.send_command(model_request)

        if self.wait_for_response():
            response = self.serial_port.read(256)
            self.logger.debug(f"RCV: {self.format_bytes(response)}")
            if self.check_crc(response) and len(response) >= 40:
                return response[9:29].decode('ascii').strip()
            return "Invalid CRC"
        return "Unknown"

    def send_continue_scan(self):
        """
        Send a command to continue the scan.
        """
        self.send_command(struct.pack('BBB', self.BROADCAST_ADDRESS, self.EXTENDED_FUNCTION_CODE, self.SCAN_CONTINUE_COMMAND))

    def scan_devices(self):
        """
        Scan for Modbus devices on the network.

        Returns:
            list: A list of dictionaries containing the serial number, Modbus ID, and model of each detected device.
        """
        self.logger.info(f"Starting scan on port {self.device} with baudrate {self.baudrate} and scan command {hex(self.EXTENDED_FUNCTION_CODE)}...")

        devices = []
        self.send_command(struct.pack('BBB', self.BROADCAST_ADDRESS, self.EXTENDED_FUNCTION_CODE, self.SCAN_START_COMMAND))

        while self.wait_for_response(2):
            response = self.serial_port.read(256)
            if not response:
                break

            self.logger.debug(f"RCV: {self.format_bytes(response)}")

            response = response.lstrip(b'\xFF')
            if len(response) >= 10 and response[2] == self.SCAN_RESPONSE_COMMAND:
                serial_number, modbus_id = struct.unpack('>I', response[3:7])[0], response[7]
                model = self.request_device_model(serial_number)
                devices.append({"serial_number": serial_number, "modbus_id": modbus_id, "model": model})
                self.send_continue_scan()
            elif response[2] == self.SCAN_END_COMMAND:
                self.logger.info("Scan complete.")
                break

        return devices
