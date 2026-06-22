from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_boxes_table()


def _migrate_boxes_table():
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    existing_cols = {c["name"] for c in insp.get_columns("boxes")}
    migrations = [
        ("expires_at", "ALTER TABLE boxes ADD COLUMN expires_at DATETIME"),
        ("status", "ALTER TABLE boxes ADD COLUMN status VARCHAR(20) DEFAULT 'active'"),
    ]
    with engine.connect() as conn:
        for col_name, sql in migrations:
            if col_name not in existing_cols:
                conn.execute(text(sql))
        conn.commit()
