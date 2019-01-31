import logging


formatter = logging.Formatter("%(asctime)s  [%(levelname)s] : %(message)s")

log = logging.getLogger("othello")
log.setLevel(logging.DEBUG)

stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
log.addHandler(stream_hander)

