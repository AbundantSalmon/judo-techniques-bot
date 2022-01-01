import logging
import os
from datetime import datetime
from pathlib import Path

import main
from sqlalchemy.orm.session import close_all_sessions

LOG_LOCATION = Path(__file__).parent.parent / "logs/all.log"

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        os.makedirs("/".join(str(LOG_LOCATION).split("/")[:-1]), exist_ok=False)
    except OSError:
        pass

    # configure root logger that will be defaulted to
    logging.Formatter.converter = lambda *args: datetime.utcnow().timetuple()
    logging.basicConfig(
        format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(LOG_LOCATION),
            logging.StreamHandler(),
        ],
    )

    while True:
        try:
            main.main()
        except Exception as e:
            logger.exception(e)
            logger.warning("Uncaught exception occurred while running, trying again.")
        finally:
            close_all_sessions()
            logging.shutdown()
