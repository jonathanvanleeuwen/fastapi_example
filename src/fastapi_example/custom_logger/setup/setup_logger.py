import atexit
import json
import logging.config
import logging.handlers
from pathlib import Path


def load_config() -> dict:
    config_file = Path(Path(__file__).parent.parent, "config/config.json")
    with open(config_file) as f_in:
        return json.load(f_in)


def setup_logging() -> None:
    config = load_config()
    log_file = Path(config["handlers"]["file_json"]["filename"])
    logs_dir = Path(log_file.parent)
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
