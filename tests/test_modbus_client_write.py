import unittest
from unittest.mock import patch, MagicMock
from fastmodbuslibrary.fast_modbus_client import ModbusClient

class TestModbusClient(unittest.TestCase):
    """
    Test suite for the ModbusClient class, focusing on writing registers.
    """

    def setUp(self):
        """
        Set up the test environment by initializing a ModbusClient instance and mocking the serial port.
        """
        self.client = ModbusClient('/dev/ttyACM0', 9600)
        self.client.serial_port = MagicMock()

    @patch('fastmodbuslibrary.common.ModbusCommon.send_command')
    @patch('fastmodbuslibrary.common.ModbusCommon.wait_for_response')
    def test_write_registers(self, mock_wait_for_response, mock_send_command):
        """
        Test writing registers to the Modbus device.

        This test mocks the response from the device and verifies that the write_registers method
        correctly processes and returns the expected success status.

        Args:
            mock_wait_for_response (MagicMock): Mock for the wait_for_response method.
            mock_send_command (MagicMock): Mock for the send_command method.
        """
        # Mock the response from the device
        mock_wait_for_response.return_value = True
        self.client.serial_port.read.return_value = b'\xFD\x46\x09\xFE\x40\x00\xAC\x10\x00\x80\x00\x01\x04\x65'

        success = self.client.write_registers(4265607340, 0x10, 128, [200])
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
