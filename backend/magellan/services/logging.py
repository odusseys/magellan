import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - (%(process)d) - [%(levelname)s] - %(name)s : %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
