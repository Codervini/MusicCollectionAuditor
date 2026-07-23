import logging
from pathlib import Path
from datetime import date

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    filename=Path("data","log",f"{date.today()}.log"), encoding='utf-8', level=logging.DEBUG)


def set_logger(__name__):
    return logging.getLogger(__name__)