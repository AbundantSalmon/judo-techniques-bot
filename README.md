# Judo Techniques Bot

# Stack

- Python
- Postgresql
- SQLAlchemy
    - Alembic

# Development FAQ

## Database

### Generate Migration

```bash
alembic revision --autogenerate -m "message"
```

### Run Migration

```bash
alembic upgrade head
```