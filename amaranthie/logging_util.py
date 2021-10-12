import logging
import sys

current_handler = None
format_string = "[%(asctime)s:%(msecs)03d][unknown_id][%(levelname)s] %(name)s.%(funcName)s.%(lineno)d: %(message)s"
id_abbrev_length = 6

def init_setup():
    global current_handler

    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    current_handler = logging.StreamHandler(sys.stdout)
    current_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(format_string)
    current_handler.setFormatter(formatter)
    root.addHandler(current_handler)

def set_id(new_id):
    if len(new_id) > id_abbrev_length+1:
        new_id = new_id[0:6] + "-"
    id_format_string = format_string.replace("unknown_id", new_id)
    current_handler.setFormatter(logging.Formatter(id_format_string, "%Y:%m:%d-%H:%M:%S"))
