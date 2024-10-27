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
        """
        # Mock the responses from the device
        mock_wait_for_response.return_value = True
        self.event_reader.serial_port.read.side_effect = [
            b'\xFF' * 9 + b'\xC9\x46\x11\x00\x05\x1B\x01\x02\x00\x00\x01\x02\x04\x01\xD0\x0C\x00\x02\x04\x01\xE0\x03\x00\x02\x04\x01\xF0\x0B\x00\x00\x0F\x00\x00\x5C\xD2',
            b'\xFF' * 9 + b'\xFD\x46\x12\x52\x5D'  # This should return {}
        ]

        # Test for valid response
        events = self.event_reader.request_events(1, 100, 0, 0)

        # Expected structure based on provided data
        expected_response = {
            'packet_info': {
                'device_id': 201,
                'command': 70,
                'subcommand': 17,
                'flag': 0,
                'event_count': 5,
                'events_data_length': 27,
            },
            'events': [
                {'event_type': 2, 'event_id': 0, 'event_payload_value': 1},
                {'event_type': 4, 'event_id': 464, 'event_payload_value': 12},
                {'event_type': 4, 'event_id': 480, 'event_payload_value': 3},
                {'event_type': 4, 'event_id': 496, 'event_payload_value': 11},
                {'event_type': 15, 'event_id': 0, 'event_payload_value': 0},
            ]
        }

        # Assertions for first response
        self.assertEqual(events['packet_info']['device_id'], expected_response['packet_info']['device_id'])
        self.assertEqual(events['packet_info']['command'], expected_response['packet_info']['command'])
        self.assertEqual(events['packet_info']['subcommand'], expected_response['packet_info']['subcommand'])
        self.assertEqual(events['packet_info']['flag'], expected_response['packet_info']['flag'])
        self.assertEqual(events['packet_info']['event_count'], expected_response['packet_info']['event_count'])
        self.assertEqual(events['packet_info']['events_data_length'], expected_response['packet_info']['events_data_length'])
        self.assertEqual(len(events['events']), len(expected_response['events']))  # Check length of events

        for i, event in enumerate(events['events']):
            self.assertEqual(event['event_type'], expected_response['events'][i]['event_type'])
            self.assertEqual(event['event_id'], expected_response['events'][i]['event_id'])
            self.assertEqual(event['event_payload_value'], expected_response['events'][i]['event_payload_value'])

        # Test for response that returns {}
        events = self.event_reader.request_events(1, 100, 1, 0)  # Using arbitrary parameters for the second request
        self.assertEqual(events, {})  # Should return an empty dictionary for FD 46 12 52 5D

if __name__ == '__main__':
    unittest.main()
