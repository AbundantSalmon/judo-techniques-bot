import logging
import os
from pathlib import Path

import config  # ty:ignore[unresolved-import]
import main  # ty:ignore[unresolved-import]
import sentry_sdk
from sqlalchemy.orm.session import close_all_sessions

from judo_techniques_bot.custom_logging import CustomFormatter

# Sentry
sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    debug=config.DEBUG,
    environment=config.ENVIRONMENT,
    traces_sample_rate=1.0,
    enable_logs=True,
)

# Logging
LOG_LOCATION = Path(__file__).parent.parent / "logs/all.log"

try:
    os.makedirs("/".join(str(LOG_LOCATION).split("/")[:-1]), exist_ok=False)
except OSError:
    pass
# configure root logger settings that will be defaulted to
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_formatter = CustomFormatter("%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")

root_file_handler = logging.FileHandler(LOG_LOCATION)
root_file_handler.setFormatter(root_formatter)
root_stream_handler = logging.StreamHandler()
root_stream_handler.setFormatter(root_formatter)
root_logger.handlers = [
    root_file_handler,
    root_stream_handler,
]

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    while True:
        try:
            main.main()
        except Exception as e:
            logger.exception(e)
            sentry_sdk.capture_exception(e)
            logger.warning("Uncaught exception occurred while running, trying again.")
        finally:
            close_all_sessions()
            logging.shutdown()
