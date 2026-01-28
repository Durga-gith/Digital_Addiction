from backend.app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT t.typname, e.enumlabel
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname LIKE '%assess%';
    """)).all()
    print("Enum types/labels:")
    for r in rows:
        print(r.typname, r.enumlabel)
