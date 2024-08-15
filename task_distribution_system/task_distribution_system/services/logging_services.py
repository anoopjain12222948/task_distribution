import logging

logger = logging.getLogger(__name__)
import logging.config
import os
from logging.handlers import TimedRotatingFileHandler
import logging.config
import re
from copy import deepcopy


class StructLogger:
    app_name: str = None

    def __init__(self, file_name, log_level, app_name) -> None:
        self.app_name = app_name
        log_file = os.path.join(os.getcwd() + "/logs/", file_name + ".log")
        log_format = logging.Formatter(' %(levelname)s - %(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        logging.getLogger("kafka").setLevel(logging.WARNING)
        debug_rotating_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=1,
            encoding='utf-8',
        )
        debug_rotating_handler.setFormatter(log_format)
        debug_rotating_handler.setLevel(log_level)
        debug_rotating_handler.suffix = "%Y-%m-%d"
        self.logger.addHandler(debug_rotating_handler)
        logging.basicConfig(filename=log_file, format=' %(levelname)s - %(asctime)s - %(message)s',
                            level=log_level)

    def mask_pii_data_common(self, unmasked_data):
        # mask starting 6 digits of phone number,
        masked_data_1 = re.sub(r'[6789]\d{5}', r'XXXXXX', unmasked_data)
        return masked_data_1

    def _log_data(self, data, log_type):
        data = str(data)
        data = self.mask_pii_data_common(data)
        print("---------------------------1")
        if log_type.lower() == 'debug':
            self.logger.debug(data)
        elif log_type.lower() == "info":
            self.logger.info(data)
        elif log_type.lower() == "error":
            print("111---------------------------1")

            self.logger.error(data)
        elif log_type.lower() == "warning":
            self.logger.warning(data)
        else:
            self.logger.error(data)
        return True

    def log(self, log_type='error', **data):

        logging_key = f"{self.app_name}"
        log_dict = str({logging_key: {**data}})
        log = self._log_data(log_dict, log_type)
        return str(log)

    def log_dict(self, log_type: str, data: dict):
        logging_key = self.app_name
        log_dict = str({logging_key: data})
        log = self._log_data(log_dict, log_type)
        return str(log)


logging_services = StructLogger('task_distribution', "INFO", 'CIRCULAR')
