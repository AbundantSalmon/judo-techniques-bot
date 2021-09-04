import logging
import os
from datetime import datetime
from pathlib import Path

import main
from sqlalchemy.orm.session import close_all_sessions

if __name__ == "__main__":
    log_location = Path(__file__).parent / "logs/all.log"
    try:
        os.makedirs("/".join(str(log_location).split("/")[:-1]), exist_ok=False)
    except OSError:
        pass

    logging.Formatter.converter = lambda *args: datetime.utcnow().timetuple()
    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_location),
            logging.StreamHandler(),
        ],
    )

    try:
        main.main()
    except Exception as e:
        logging.exception(e)
        logging.warning("Uncaught exception occurred while running, trying again.")
        main.main()
    finally:
        close_all_sessions()
        logging.shutdown()
