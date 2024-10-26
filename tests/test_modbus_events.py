import unittest
from unittest.mock import patch, MagicMock
from fastmodbuslibrary.fast_modbus_events import ModbusEventReader

class TestModbusEventReader(unittest.TestCase):
    """
    Test suite for the ModbusEventReader class, focusing on requesting event notifications.
    """

    def setUp(self):
        """
        Set up the test environment by initializing a ModbusEventReader instance and mocking the serial port.
        """
        self.event_reader = ModbusEventReader('/dev/ttyACM0', 9600)
        self.event_reader.serial_port = MagicMock()

    @patch('fastmodbuslibrary.common.ModbusCommon.send_command')
    @patch('fastmodbuslibrary.common.ModbusCommon.wait_for_response')
    def test_request_events(self, mock_wait_for_response, mock_send_command):
        """
        Test requesting event notifications from the Modbus device.

        This test mocks the responses from the device and verifies that the request_events method
        correctly processes and returns the expected event data.

        Args:
            mock_wait_for_response (MagicMock): Mock for the wait_for_response method.
            mock_send_command (MagicMock): Mock for the send_command method.
        """
        # Mock the responses from the device
        mock_wait_for_response.side_effect = [True, True, True, True, True, True, True, True, True]
        self.event_reader.serial_port.read.side_effect = [
            b'\xFF' * 9 + b'\x01\x46\x11\x00\x01\x04\x00\x0F\x00\x00\x3B\x73',
            b'\xFF' * 9 + b'\x04\x46\x11\x00\x01\x04\x00\x0F\x00\x00\x2B\x63',
            b'\xFF' * 9 + b'\xC9\x46\x11\x00\x01\x04\x00\x0F\x00\x00\xBF\xA5',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D'
        ]

        events = self.event_reader.request_events(1, 100, 0, 0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['device_id'], 1)
        self.assertEqual(events[0]['event_count'], 1)
        self.assertEqual(events[0]['flag'], 0)
        self.assertEqual(events[0]['event_data_len'], 1024)
        self.assertEqual(events[0]['event_type'], 3840)
        self.assertEqual(events[0]['event_payload'], 59)

        events = self.event_reader.request_events(1, 100, 1, 0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['device_id'], 4)
        self.assertEqual(events[0]['event_count'], 1)
        self.assertEqual(events[0]['flag'], 0)
        self.assertEqual(events[0]['event_data_len'], 1024)
        self.assertEqual(events[0]['event_type'], 3840)
        self.assertEqual(events[0]['event_payload'], 43)

        events = self.event_reader.request_events(1, 100, 4, 0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['device_id'], 201)
        self.assertEqual(events[0]['event_count'], 1)
        self.assertEqual(events[0]['flag'], 0)
        self.assertEqual(events[0]['event_data_len'], 1024)
        self.assertEqual(events[0]['event_type'], 3840)
        self.assertEqual(events[0]['event_payload'], 191)

        events = self.event_reader.request_events(1, 100, 201, 0)
        self.assertEqual(len(events), 0)

if __name__ == '__main__':
    unittest.main()
