import logging
import os

class Logger:
    def __init__(self, filename='game_debug.log'):
        # Configure logging
        logging.basicConfig(
            filename=filename,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='w' # Overwrite log on each run
        )
        self.logger = logging.getLogger()
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log(self, message):
        logging.info(message)

    def debug(self, message):
        logging.debug(message)

    def warning(self, message):
        logging.warning(message)

    def error(self, message):
        logging.error(message)
