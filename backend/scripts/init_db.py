import sqlite3
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from sqlalchemy import create_engine, text


def resolve_sqlite_path(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("init_db.py currently supports sqlite URLs only")
    return Path(database_url.replace("sqlite:///", "", 1)).resolve()


def main() -> None:
    migrations_path = BACKEND_ROOT / "migrations" / "001_init_schema.sql"
    sql_script = migrations_path.read_text(encoding="utf-8")

    if settings.database_url.startswith("sqlite:///"):
        db_path = resolve_sqlite_path(settings.database_url)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as connection:
            connection.executescript(sql_script)
            connection.commit()
        print(f"Initialized SQLite schema at {db_path}")
        return

    engine = create_engine(settings.database_url)
    statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
    with engine.begin() as connection:
        for statement in statements:
            if statement.startswith("PRAGMA"):
                continue
            connection.execute(text(statement))

    print("Initialized database schema for non-sqlite database")


if __name__ == "__main__":
    main()
