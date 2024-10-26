import argparse
from fastmodbuslibrary.fast_modbus_client import ModbusClient
from fastmodbuslibrary.logging_config import setup_logging

def parse_args():
    """
    Parse command-line arguments for the Fast Modbus Client Tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Fast Modbus Client Tool")
    parser.add_argument('-d', '--device', required=True, help="TTY serial device (e.g., /dev/ttyACM0)")
    parser.add_argument('-b', '--baud', type=int, default=9600, help="Baudrate, default 9600")
    parser.add_argument('-s', '--serial', type=lambda x: int(x, 0), required=True, help="Device serial number (decimal or hex)")
    parser.add_argument('-c', '--command', type=lambda x: int(x, 0), required=True, help="Modbus command (decimal or hex)")
    parser.add_argument('-r', '--register', type=lambda x: int(x, 0), required=True, help="Register to read/write (decimal or hex)")
    parser.add_argument('-n', '--count', type=int, default=1, help="Number of registers to read (default 1)")
    parser.add_argument('-w', '--write', nargs='*', type=lambda x: int(x, 0), help="Values to write (if write operation, decimal or hex)")
    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    parser.add_argument('--decimal-output', action='store_true', help="Display register values in decimal format")
    return parser.parse_args()

def main():
    """
    Main function to execute the Fast Modbus Client Tool.

    Parses command-line arguments, sets up logging, initializes the Modbus client,
    and performs read or write operations based on the provided arguments.
    """
    args = parse_args()
    setup_logging(args.debug)
    client = ModbusClient(args.device, args.baud)

    if args.write:
        success = client.write_registers(args.serial, args.command, args.register, args.write)
        print(f"Successfully wrote {len(args.write)} registers." if success else "Failed to write registers.")
    else:
        result = client.read_registers(args.serial, args.command, args.register, args.count)
        if result:
            if args.decimal_output:
                registers = ' '.join(str(int.from_bytes(result[i:i + 2], byteorder='big')) for i in range(0, len(result), 2))
            else:
                registers = ' '.join(f"0x{int.from_bytes(result[i:i + 2], byteorder='big'):04X}" for i in range(0, len(result), 2))
            print(f"Read {args.count} registers from device {args.serial}: {registers}")
        else:
            print("Failed to read registers.")

    client.serial_port.close()

if __name__ == "__main__":
    main()
