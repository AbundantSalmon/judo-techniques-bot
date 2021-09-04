import logging
from datetime import datetime
from pathlib import Path

import main

if __name__ == "__main__":
    logging.Formatter.converter = lambda *args: datetime.utcnow().timetuple()
    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(Path(__file__).parent / "logs/all.log"),
            logging.StreamHandler(),
        ],
    )

    try:
        main.main()
    finally:
        logging.shutdown()
