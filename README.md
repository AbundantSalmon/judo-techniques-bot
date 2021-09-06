# Judo Techniques Bot

[![Translating since - 2019-06-03](https://img.shields.io/badge/Translating_since-2019--06--03-2ea44f)](https://)

This is a reddit [bot](https://www.reddit.com/user/JudoTechniquesBot/)
that runs on the [r/bjj](https://www.reddit.com/r/bjj/)
subreddit. It translates the Japanese names of judo techniques into their
commons english names and provides links to videos of those techniques.

# Stack

- Python
- PostgreSQL
- SQLAlchemy
  - Alembic

# Todo

- Optimise some of the variant name checking
- Setup local development database docker

# Development FAQ

## Run

```bash
python3 -m judo_techniques_bot
```

## Tests

```bash
# See test coverage
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
