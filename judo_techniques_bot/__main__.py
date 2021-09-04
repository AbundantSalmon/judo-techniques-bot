import logging
import os
from datetime import datetime
from pathlib import Path

import main

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
    finally:
        logging.shutdown()
