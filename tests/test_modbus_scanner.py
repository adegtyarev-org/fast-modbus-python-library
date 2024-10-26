import unittest
from unittest.mock import patch, MagicMock
from fastmodbuslibrary.fast_modbus_scanner import ModbusScanner

class TestModbusScanner(unittest.TestCase):
    """
    Test suite for the ModbusScanner class, focusing on scanning devices.
    """

    def setUp(self):
        """
        Set up the test environment by initializing a ModbusScanner instance and mocking the serial port.
        """
        self.scanner = ModbusScanner('/dev/ttyACM0', 9600)
        self.scanner.serial_port = MagicMock()

    @patch('fastmodbuslibrary.common.ModbusCommon.send_command')
    @patch('fastmodbuslibrary.common.ModbusCommon.wait_for_response')
    def test_scan_devices(self, mock_wait_for_response, mock_send_command):
        """
        Test scanning devices on the Modbus network.

        This test mocks the responses from the device and verifies that the scan_devices method
        correctly processes and returns the expected device data.

        Args:
            mock_wait_for_response (MagicMock): Mock for the wait_for_response method.
            mock_send_command (MagicMock): Mock for the send_command method.
        """
        # Mock the responses from the device
        mock_wait_for_response.side_effect = [True, True, True, False]
        self.scanner.serial_port.read.side_effect = [
            b'\xFF' * 19 + b'\xFD\x46\x03\x00\x01\xBA\x5D\x04\xB0\x6B',
            b'\xFF' * 19 + b'\xFD\x46\x03\xFE\x40\x00\xAC\xC9\x28\x63',
            b'\xFF' * 19 + b'\xFD\x46\x03\xFF\xFF\xFF\xFF\x01\x3D\x21',
            b'\xFF' * 19 + b'\xFD\x46\x04\xD3\x93'
        ]

        # Mock the responses for device model requests
        self.scanner.request_device_model = MagicMock(side_effect=[
            "WBMAO4",
            "WBMCM8",
            "WBMWAC-v2"
        ])

        devices = self.scanner.scan_devices()

        # Verify that the scan returned the correct devices
        self.assertEqual(len(devices), 3)
        self.assertEqual(devices[0]['serial_number'], 113245)
        self.assertEqual(devices[0]['modbus_id'], 4)
        self.assertEqual(devices[0]['model'], "WBMAO4")
        self.assertEqual(devices[1]['serial_number'], 4265607340)
        self.assertEqual(devices[1]['modbus_id'], 201)
        self.assertEqual(devices[1]['model'], "WBMCM8")
        self.assertEqual(devices[2]['serial_number'], 4294967295)
        self.assertEqual(devices[2]['modbus_id'], 1)
        self.assertEqual(devices[2]['model'], "WBMWAC-v2")

if __name__ == '__main__':
    unittest.main()
