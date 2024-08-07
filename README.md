# Judo Techniques Bot

[![Translating since - 2019-06-03](https://img.shields.io/badge/Translating_since-2019--06--03-2ea44f)](https://judo-techniques-bot-stats.vercel.app/) [![Run Python Tests](https://github.com/AbundantSalmon/judo-techniques-bot/actions/workflows/cy.yml/badge.svg)](https://github.com/AbundantSalmon/judo-techniques-bot/actions/workflows/cy.yml)

This is a reddit [bot](https://www.reddit.com/user/JudoTechniquesBot/)
that runs on the [r/bjj](https://www.reddit.com/r/bjj/) and [r/Ju_Jutsu](https://www.reddit.com/r/Ju_Jutsu/)
subreddits. It translates the Japanese names of judo techniques into their
commons english names and provides links to videos of those techniques.

Stats can be found at: <https://judo-techniques-bot-stats.vercel.app/>

## Stack

- Python
- PostgreSQL
- SQLAlchemy
  - Alembic
- Docker

## Todo

- [ ] Optimise some of the variant name checking
- [x] Setup local development database docker

## Development FAQ

### Run

```bash
python3 -m judo_techniques_bot
```

With local development db:

```bash
# Startup docker with database, bot and adminer
docker-compose up

# Load fixture data into the db
python judo_techniques_bot/load_data.py

or

docker exec --env-file .env judo_techniques_bot python judo_techniques_bot/load_data.py
```

### Tests

```bash
# See test coverage
coverage run -m unittest
coverage report

# run tests
python3 -m unittest
```

### Database

#### Generate Migration

```bash
alembic revision --autogenerate -m "message"
```

#### Run Migration

```bash
alembic upgrade head
```

Any unrun migrations will be run automatically when the bot is started.

## Production FAQ

~~Built when there is commit pushed to main using github actions and deployed as docker container to an EC2 instance on AWS ECS using terraform.~~

Currently the container is deployed to a portainer instance on a VPS.
