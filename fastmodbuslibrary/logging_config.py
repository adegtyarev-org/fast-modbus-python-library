import logging

def setup_logging(debug=False):
    """
    Configure the logging settings for the application.

    Args:
        debug (bool): If True, set the logging level to DEBUG. Otherwise, set it to INFO.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
