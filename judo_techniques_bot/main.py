from bot import Bot
from db import recreate_database, session_scope

# from events.models import DetectedJudoTechniqueMentionEvent
from load_data import retrieve_fixture_data
from models import Technique
from sqlalchemy.orm.session import close_all_sessions
from utils import pickle_dictionary


def main():
    # print("Initialising...")
    # run_any_missing_migrations()
    # print("Initialisation Complete!")
    # print("Running...")

    # recreate_database()

    techniques_data = Technique.get_cached_techniques()
    # for generating test fixture data
    # pickle_dictionary(techniques_data, "techniques_test_data")
    bot = Bot(techniques_data)
    bot.run()

    close_all_sessions()


def run_any_missing_migrations():
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(Path(__file__).parent / "alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Migrations Complete")


if __name__ == "__main__":
    main()
