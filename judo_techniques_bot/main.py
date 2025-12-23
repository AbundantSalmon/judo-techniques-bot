import logging
from pathlib import Path

from .bot import Bot
from .models import Technique
from sqlalchemy.orm.session import close_all_sessions

logger = logging.getLogger(__name__)


def main():
    close_all_sessions()
    logger.info("Checking migrations...")
    run_any_missing_migrations()
    logger.info("Migrations dealt with!")
    logger.info("Running...")

    techniques_data = Technique.get_cached_techniques()

    bot = Bot(techniques_data)
    bot.run()


def run_any_missing_migrations():
    from alembic import command
    from alembic.config import Config

    logger.info("Running migrations")
    alembic_cfg = Config(
        Path(__file__).parent / "alembic.ini",
        attributes={
            "configure_logger": False,  # Prevent alembic default logging from overriding the apps
        },
    )
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations complete")


if __name__ == "__main__":
    main()
