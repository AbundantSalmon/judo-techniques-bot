import os

_PRODUCTION = "production"
_DEVELOPMENT = "development"

ENVIRONMENT = (
    _DEVELOPMENT
    if os.getenv("ENVIRONMENT", "production") != _PRODUCTION
    else _PRODUCTION
)

DEBUG = ENVIRONMENT == _DEVELOPMENT

DATABASE_URI = os.environ["DATABASE_URI"]

USER_AGENT = os.environ["USER_AGENT"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]

SUBREDDITS = os.environ["SUBREDDITS"]

SENTRY_DSN = os.environ["SENTRY_DSN"]

VERSION = "0.7"
