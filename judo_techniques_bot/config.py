import os

_PRODUCTION = "production"
_DEVELOPMENT = "development"

ENVIRONMENT = (
    _DEVELOPMENT
    if os.getenv("ENVIRONMENT", "production") != _PRODUCTION
    else _PRODUCTION
)

DEBUG = ENVIRONMENT == _DEVELOPMENT

USER_AGENT = os.environ["USER_AGENT"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]

DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]

SUBREDDITS = os.environ["SUBREDDITS"]

SENTRY_DSN = os.environ["SENTRY_DSN"]

VERSION = "0.7"

DATABASE_URI = (
    f"postgresql+psycopg2://{DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
)
