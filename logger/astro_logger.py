import logging
import colorlog
import inspect
import os

from yaml import safe_load

class astroLogger(logging.Logger):

    """
    Creates a logging object that can be imported anywhere and 
    will automatically store logs into the logs folder in this software

    Args:
        log_level (logging.LEVEL || int || str): Decides the level of the logger 
        format (string): Decides the format of the log messages
        date_format (string): Sets the format for the date and time of the log
        enable_color (bool): Whether or not the logs should use color
    """
    #TODO: Add a way for the user to control colors

    def __init__(self, log_level=None, format='%(log_color)s%(asctime)s:%(name)s:%(levelname)-8s    %(message)s', date_format='%Y-%m-%d %H:%M:%S', enable_color = False):
        
        if log_level == None:
            parentDir = os.path.realpath(__file__).replace('/logger/astro_logger.py', '')
            with open(parentDir + '/conf_files/settings.yaml', "r") as f:
                settings = safe_load(f)
            
            match settings['DEBUG_MESSAGE_LEVEL'].lower():
                case 'debug':
                    log_level = logging.DEBUG
                case 'info':
                    log_level = logging.INFO
                case 'warning':
                    log_level = logging.WARNING
                case 'error':
                    log_level = logging.ERROR
                case 'critical':
                    log_level = logging.CRITICAL

        caller_frame = inspect.stack()[1]
        calling_module_path = inspect.getmodule(caller_frame[0]).__file__
        calling_module_name = os.path.basename(calling_module_path).replace('.py', '')

        super().__init__(calling_module_name)
        self.setLevel(log_level)

        if enable_color == True:
            formatter = colorlog.ColoredFormatter(format, date_format)
        else:
            formatter = logging.Formatter(format, date_format)

        logs_directory = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_directory, exist_ok=True)

        log_file_path = os.path.join(logs_directory, f'{calling_module_name}')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)
