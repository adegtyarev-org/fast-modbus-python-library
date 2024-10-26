import argparse
from fastmodbuslibrary.fast_modbus_scanner import ModbusScanner
from fastmodbuslibrary.logging_config import setup_logging

def parse_args():
    """
    Parse command-line arguments for the Modbus Scanner Tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Modbus Scanner Tool")
    parser.add_argument('-d', '--device', required=True, help="TTY serial device (e.g., /dev/ttyACM0)")
    parser.add_argument('-b', '--baud', type=int, default=9600, help="Baudrate, default 9600")
    parser.add_argument('--command', type=lambda x: int(x, 0), default=0x46, help="Scan command (decimal or hex)")
    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    return parser.parse_args()

def print_devices(devices):
    """
    Display the scanned devices in a formatted table.

    Args:
        devices (list): A list of dictionaries containing device information.
    """
    if devices:
        # Define column widths based on the header
        header = ["Serial Number", "Modbus ID", "Model"]
        max_widths = [len(col) for col in header]

        # Format the header of the table
        header_str = " | ".join(f"{col:<{max_widths[i]}}" for i, col in enumerate(header))
        separator = "-" * len(header_str)

        print(header_str)
        print(separator)

        # Format and print each row of the table
        for device in devices:
            row = [str(device['serial_number']), str(device['modbus_id']), device['model']]
            row_str = " | ".join(f"{col:<{max_widths[i]}}" for i, col in enumerate(row))
            print(row_str)
    else:
        print("No devices found.")

def main():
    """
    Main function to execute the Modbus Scanner Tool.

    Parses command-line arguments, sets up logging, initializes the Modbus scanner,
    scans for devices, and displays the results.
    """
    args = parse_args()
    setup_logging(args.debug)
    scanner = ModbusScanner(args.device, args.baud)
    devices = scanner.scan_devices()
    scanner.serial_port.close()
    print_devices(devices)

if __name__ == "__main__":
    main()
