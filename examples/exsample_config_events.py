import argparse
from fastmodbuslibrary.fast_modbus_config_events import ModbusConfigEvents
from fastmodbuslibrary.logging_config import setup_logging

def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Modbus Event Configuration Tool for multiple u16 register ranges")
    parser.add_argument('--device', required=True, help="Serial device (e.g., /dev/ttyACM0)")
    parser.add_argument('--baud', type=int, default=9600, help="Baud rate, default is 9600")
    parser.add_argument('--slave_id', type=lambda x: int(x, 0), required=True, help="Slave ID of the device (decimal or hex)")
    parser.add_argument('--config', required=True, help="Configuration string (e.g., 'discrete:0:3:1,discrete:6:2:0')")
    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    return parser.parse_args()

def print_settings(config: str, mask_data: bytes, slave_id: int):
    """
    Display the event settings in a human-readable format.

    Args:
        config (str): The configuration string.
        mask_data (bytes): The mask data from the device response.
        slave_id (int): The Modbus device slave ID.
    """
    byte_index = 0
    print(f"Device: {slave_id}")
    for cfg in config.split(','):
        reg_type, address, count, _ = cfg.split(':')
        address, count = int(address), int(count)

        print(f"Settings for {reg_type.capitalize()} registers:")
        for i in range(count):
            if byte_index < len(mask_data):
                mask_byte = mask_data[byte_index]
                bit_position = i % 8
                bit = (mask_byte >> bit_position) & 1
                reg_address = address + i
                status = "enabled" if bit else "disabled"
                print(f"- Register {reg_address} (u16): {status}")

            if (i + 1) % 8 == 0:
                byte_index += 1

def main():
    """
    Main entry point for configuring Modbus event notifications.

    Parses command-line arguments, initializes the serial connection,
    and configures the event settings based on the provided configuration string.
    """
    args = parse_args()
    setup_logging(args.debug)
    config_events = ModbusConfigEvents(args.device, args.baud)

    for cfg in args.config.split(','):
        reg_type, address, count, priority = cfg.split(':')
        address, count, priority = int(address), int(count), int(priority)

        mask_data = config_events.configure_events(args.slave_id, reg_type, address, count, priority)
        if mask_data:
            print_settings(cfg, mask_data, args.slave_id)
        else:
            print("[error] No valid response received")

    config_events.serial_port.close()

if __name__ == '__main__':
    main()
