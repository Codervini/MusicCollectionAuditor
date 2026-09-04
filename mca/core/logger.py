import logging
from pathlib import Path
from datetime import date , datetime

log_file = Path("data", "log", f"{date.today()} {datetime.now().strftime("%H:%M:%S")}.log")
log_file.parent.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s:%(message)s",datefmt="%d/%m/%Y %I:%M:%S %p")

# File
file_handler = logging.FileHandler(log_file,encoding="utf-8")
file_handler.setFormatter(formatter)

# Console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Root logger
logging.basicConfig(level=logging.INFO,handlers=[file_handler, console_handler,])


def set_logger(name):
    return logging.getLogger(name)