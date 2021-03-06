import logging
import sys
from amaranthie import config

current_handler = None
format_string = "[%(asctime)s:%(msecs)03d][unknown_id][%(levelname)s] %(name)s.%(funcName)s.%(lineno)d: %(message)s"
format_string.replace("unknown_id", config.get(config.my_id))

date_format_string = "%Y:%m:%d-%H:%M:%S"
id_abbrev_length = 6

def init_setup():
    global current_handler

    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    current_handler = logging.StreamHandler(sys.stdout)
    current_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(format_string, date_format_string)
    current_handler.setFormatter(formatter)
    root.addHandler(current_handler)

    set_id(config.get(config.my_id))

def set_id(new_id):
    if len(new_id) > id_abbrev_length+1:
        new_id = new_id[0:6] + "-"
    id_format_string = format_string.replace("unknown_id", new_id)
    current_handler.setFormatter(logging.Formatter(id_format_string, date_format_string))
