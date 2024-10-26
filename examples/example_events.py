import argparse
import time
import traceback
import logging
from fastmodbuslibrary.fast_modbus_events import ModbusEventReader
from fastmodbuslibrary.logging_config import setup_logging

def parse_args():
    """
    Parse command-line arguments for the Fast Modbus Event Reader.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Fast Modbus Event Reader with full event request support")
    parser.add_argument('-d', '--device', required=True, help="TTY serial device (e.g., /dev/ttyACM0)")
    parser.add_argument('-b', '--baud', type=int, default=9600, help="Baudrate, default 9600")
    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    return parser.parse_args()

def print_events(events):
    """
    Display the received events in a formatted table.

    Args:
        events (list): A list of dictionaries containing event information.
    """
    if events:
        # Define column widths based on the header
        header = ["Device ID", "Event Count", "Flag", "Event Data Len", "Event Type", "Event Payload"]
        max_widths = [len(col) for col in header]

        # Format the header of the table
        header_str = " | ".join(f"{col:<{max_widths[i]}}" for i, col in enumerate(header))
        separator = "-" * len(header_str)

        # Print the header only once
        if not hasattr(print_events, "header_printed"):
            print(header_str)
            print(separator)
            print_events.header_printed = True

        # Format and print each row of the table
        for event in events:
            row = [str(event['device_id']), str(event['event_count']), str(event['flag']), str(event['event_data_len']), str(event['event_type']), str(event['event_payload'])]
            row_str = " | ".join(f"{col:<{max_widths[i]}}" for i, col in enumerate(row))
            print(row_str)

def main():
    """
    Main function to execute the Fast Modbus Event Reader.

    Parses command-line arguments, sets up logging, initializes the Modbus event reader,
    and continuously requests and displays event notifications.
    """
    args = parse_args()
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    event_reader = None

    min_slave_id = 1
    max_data_length = 100
    slave_id = 0
    flag = 0

    while True:
        try:
            if event_reader is None:
                event_reader = ModbusEventReader(args.device, args.baud)

            events = event_reader.request_events(min_slave_id, max_data_length, slave_id, flag)
            print_events(events)
            if events:
                slave_id = events[0]["device_id"]
                flag = events[0]["flag"]
            else:
                slave_id = 0
                flag = 0
        except Exception as e:
            logger.error(f"Error: {e}")
            traceback.print_exc()
            print("An error occurred. Retrying...")
            event_reader = None

        time.sleep(0.5)

    if event_reader:
        event_reader.serial_port.close()

if __name__ == "__main__":
    main()
