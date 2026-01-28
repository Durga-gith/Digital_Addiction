import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, BASE_DIR)

from app.database import Base
from app.config import settings
from app.models import *  # IMPORTANT

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online():
    from sqlalchemy import create_engine

    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
