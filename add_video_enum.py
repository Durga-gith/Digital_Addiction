from backend.app.database import engine
from sqlalchemy import text

sql = """
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_type t 
        JOIN pg_enum e ON e.enumtypid = t.oid 
        WHERE t.typname = 'assessmenttype' AND e.enumlabel = 'VIDEO'
    ) THEN
        ALTER TYPE assessmenttype ADD VALUE 'VIDEO';
    END IF;
END $$;
"""

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text(sql))
    print("VIDEO enum value ensured on assessmenttype (autocommit)")
