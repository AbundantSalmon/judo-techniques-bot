# Judo Techniques Bot

[![Translating since - 2019-06-03](https://img.shields.io/badge/Translating_since-2019--06--03-2ea44f)](https://judo-techniques-bot-stats.vercel.app/)

This is a reddit [bot](https://www.reddit.com/user/JudoTechniquesBot/)
that runs on the [r/bjj](https://www.reddit.com/r/bjj/) and [r/Ju_Jutsu](https://www.reddit.com/r/Ju_Jutsu/)
subreddits. It translates the Japanese names of judo techniques into their
commons english names and provides links to videos of those techniques.

Stats can be found at: https://judo-techniques-bot-stats.vercel.app/

# Stack

- Python
- PostgreSQL
- SQLAlchemy
  - Alembic
- Docker

# Todo

- Optimise some of the variant name checking
- Setup local development database docker

# Development FAQ

## Run

```bash
python3 -m judo_techniques_bot
```

With local development db:
```bash
# Startup docker with database, bot and adminer
docker-compose up

# Load fixture data into the db
python judo_techniques_bot/load_data.py
```

## Tests

```bash
# See test coverage
coverage run -m unittest
coverage report

# run tests
python3 -m unittest
```

## Database

### Generate Migration

```bash
alembic revision --autogenerate -m "message"
```

### Run Migration

```bash
alembic upgrade head
```

Any unrun migrations will be run automatically when the bot is started.

# Production FAQ
## Run
```bash
./production_script.sh
```