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

def print_header():
    """
    Print the header for the event table and return the widths of the columns.

    Returns:
        list: A list of maximum widths for each column in the header.
    """
    header = ["Device ID", "Flag", "Event Type", "Event ID", "Event Payload"]
    max_widths = [len(col) for col in header]

    header_str = " | ".join(f"{col:<{max_widths[i]}}" for i, col in enumerate(header))
    separator = "-" * len(header_str)

    print(header_str)
    print(separator)

    return max_widths  # Return column widths for further use

def print_events(events, device_id, flag, max_widths):
    """
    Print the events in a formatted table.

    Args:
        events (list): A list of event dictionaries.
        device_id (int): The device ID to display.
        flag (int): The flag to display.
        max_widths (list): A list of maximum widths for each column.
    """
    # Print rows of the table
    for event in events:
        if isinstance(event, dict):  # Check if it is a dictionary
            row = [
                str(device_id),  # Use the provided device_id
                str(flag),       # Use the provided flag
                str(event['event_type']),
                str(event['event_id']),
                str(event['event_payload_value']),
            ]
            row_str = " | ".join(f"{col:<{max_widths[i]}}" for i, col in enumerate(row))
            print(row_str)

def main():
    """
    Main function to execute the Fast Modbus Event Reader.

    It parses command-line arguments, sets up logging, initializes the Modbus event reader,
    and continuously requests and displays event notifications.
    """
    args = parse_args()
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    event_reader = ModbusEventReader(args.device, args.baud)

    min_slave_id = 1
    max_data_length = 100
    slave_id = 0
    flag = 0

    # Print the header once
    max_widths = print_header()

    while True:
        try:
            response = event_reader.request_events(min_slave_id, max_data_length, slave_id, flag)

            if isinstance(response, dict):  # Check if the response is a dictionary
                events = response.get('events', [])  # Extract the list of events from the dictionary
                packet_info = response.get('packet_info', {})
                device_id = packet_info.get('device_id', 0)  # Extract device_id or default to 0
                flag = packet_info.get('flag', 0)              # Extract flag or default to 0

                # Logic for updating slave_id and flag
                if events:
                    slave_id = device_id  # If there are events, take device_id from packet_info
                else:
                    slave_id = 0          # If there are no events, set slave_id to 0
                    flag = 0              # If packet_info is empty, set flag to 0

                print_events(events, slave_id, flag, max_widths)  # Pass slave_id and flag to the function
            else:
                logger.error(f"Unexpected response: {response}")  # Log an error if it's not a dictionary

        except Exception as e:
            logger.error(f"Error: {e}")
            traceback.print_exc()
            print("An error occurred. Retrying...")
            event_reader = ModbusEventReader(args.device, args.baud)

        time.sleep(0.5)

if __name__ == "__main__":
    main()
