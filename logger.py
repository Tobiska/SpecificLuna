import logging

_log_format = f"[%(levelname)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

def get_file_handler(filename):
    file_handler = logging.FileHandler(filename=filename)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def init_logger(log_level, filename):
    logger = logging.getLogger("LUNA")
    logger.setLevel(log_level)
    logger.addHandler(get_stream_handler())
    logger.addHandler(get_file_handler(filename))
    return logger