from unittest import mock
import unittest
from unittest.mock import patch, MagicMock
from fastmodbuslibrary.fast_modbus_client import ModbusClient

class TestModbusClientErrors(unittest.TestCase):
    def setUp(self):
        # Mock serial.Serial to avoid needing real port
        self.patcher = mock.patch('serial.Serial')
        self.mock_serial = self.patcher.start()
        self.client = ModbusClient('/dev/ttyACM0', 9600)
        self.client.serial_port = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    @patch('fastmodbuslibrary.common.ModbusCommon.send_command')
    @patch('fastmodbuslibrary.common.ModbusCommon.wait_for_response')
    def test_read_registers_invalid_crc(self, mock_wait_for_response, mock_send_command):
        mock_wait_for_response.return_value = True
        self.client.serial_port.read.return_value = b'\xFD\x46\x09\xFE\x40\x00\xAC\x03\x02\x00\xC9\x00\x00'  # Invalid CRC

        result = self.client.read_registers(4265607340, 0x03, 128, 1)
        self.assertIsNone(result)

    @patch('fastmodbuslibrary.common.ModbusCommon.send_command')
    @patch('fastmodbuslibrary.common.ModbusCommon.wait_for_response')
    def test_write_registers_invalid_response(self, mock_wait_for_response, mock_send_command):
        mock_wait_for_response.return_value = True
        self.client.serial_port.read.return_value = b'\xFD\x46\x09\xFE\x40\x00\xAC\x10\x00\x80\x00\x01\x00\x00'  # Invalid response

        success = self.client.write_registers(4265607340, 0x10, 128, [200])
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
