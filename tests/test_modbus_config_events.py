import unittest
from unittest.mock import patch, MagicMock
from fastmodbuslibrary.fast_modbus_config_events import ModbusConfigEvents

class TestModbusConfigEvents(unittest.TestCase):
    """
    Test suite for the ModbusConfigEvents class, focusing on configuring event notifications.
    """

    def setUp(self):
        """
        Set up the test environment by initializing a ModbusConfigEvents instance and mocking the serial port.
        """
        self.config_events = ModbusConfigEvents('/dev/ttyACM0', 9600)
        self.config_events.serial_port = MagicMock()

    @patch('fastmodbuslibrary.common.ModbusCommon.send_command')
    @patch('fastmodbuslibrary.common.ModbusCommon.wait_for_response')
    def test_configure_events(self, mock_wait_for_response, mock_send_command):
        """
        Test configuring event notifications for multiple register ranges.

        This test mocks the responses from the device and verifies that the configure_events method
        correctly processes and returns the expected mask data.

        Args:
            mock_wait_for_response (MagicMock): Mock for the wait_for_response method.
            mock_send_command (MagicMock): Mock for the send_command method.
        """
        # Mock the responses from the device
        mock_wait_for_response.side_effect = [True, True]
        self.config_events.serial_port.read.side_effect = [
            b'\xC9\x46\x18\x01\x07\x2D\x0D',
            b'\xC9\x46\x18\x01\x00\x6C\xCF'
        ]

        # Configure event notifications for the first block of registers
        mask_data = self.config_events.configure_events(201, "discrete", 0, 3, 1)
        self.assertEqual(mask_data, b'\x07')

        # Configure event notifications for the second block of registers
        mask_data = self.config_events.configure_events(201, "discrete", 6, 2, 0)
        self.assertEqual(mask_data, b'\x00')

if __name__ == '__main__':
    unittest.main()
