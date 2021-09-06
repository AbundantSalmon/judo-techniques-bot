import datetime
import logging
from pathlib import Path

from bot import Bot
from db import recreate_database
from models import Technique
from sqlalchemy.orm.session import close_all_sessions
from utils import pickle_dictionary


def main():
    close_all_sessions()
    logging.info(f"Checking migrations...")
    # run_any_missing_migrations()
    logging.info("Migrations dealt with!")
    logging.info("Running...")

    # recreate_database()

    techniques_data = Technique.get_cached_techniques()
    # for regenerating test fixture data
    # pickle_dictionary(techniques_data, "techniques_test_data")

    bot = Bot(techniques_data)
    bot.run()


def run_any_missing_migrations():
    """
    Currently hangs on the below message, can manually run instead.
        2021-09-06 12:18:00,359 INFO    Checking migrations...
        2021-09-06 12:18:00,396 INFO    Running migrations
        INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
        INFO  [alembic.runtime.migration] Will assume transactional DDL.
    """
    from alembic import command
    from alembic.config import Config

    logging.info("Running migrations")
    alembic_cfg = Config(Path(__file__).parent / "alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logging.info("Migrations complete")


if __name__ == "__main__":
    main()
