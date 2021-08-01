from sqlalchemy.orm.session import close_all_sessions

from bot import Bot
from db import recreate_database, session_scope

# from events.models import DetectedJudoTechniqueMentionEvent
from load_data import retrive_fixture_data
from models import Technique


def main():
    # print("Initialising...")
    # run_any_missing_migrations()
    # print("Initialisation Complete!")
    # print("Running...")

    # recreate_database()

    techniques_data = Technique.get_cached_techniques()
    bot = Bot(techniques_data)
    bot.run()


    close_all_sessions()


def run_any_missing_migrations():
    from alembic import command
    from alembic.config import Config

    print("Running migrations")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Migrations Complete")


if __name__ == "__main__":
    main()
