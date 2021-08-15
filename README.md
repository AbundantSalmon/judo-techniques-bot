# Judo Techniques Bot

# Stack

- Python
- Postgresql
- SQLAlchemy
  - Alembic

# Development FAQ

## Run

```bash
python3 -m judo_techniques_bot
```

## Tests

```bash
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
