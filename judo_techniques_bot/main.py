import datetime
from pathlib import Path

from bot import Bot
from db import recreate_database
from models import Technique
from sqlalchemy.orm.session import close_all_sessions
from utils import pickle_dictionary


def main():
    print(f"{datetime.datetime.utcnow()}\tChecking migrations...")
    run_any_missing_migrations()
    print(f"{datetime.datetime.utcnow()}\tMigrations dealt with!")
    print(f"{datetime.datetime.utcnow()}\tRunning...")

    # recreate_database()

    techniques_data = Technique.get_cached_techniques()
    # for regenerating test fixture data
    # pickle_dictionary(techniques_data, "techniques_test_data")

    bot = Bot(techniques_data)
    bot.run()

    close_all_sessions()


def run_any_missing_migrations():
    from alembic import command
    from alembic.config import Config

    print(f"{datetime.datetime.utcnow()}\tRunning migrations")
    alembic_cfg = Config(Path(__file__).parent / "alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print(f"{datetime.datetime.utcnow()}\tMigrations complete")


if __name__ == "__main__":
    main()
