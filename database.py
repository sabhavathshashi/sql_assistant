import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

USER = os.getenv("MYSQL_USER", "root")
PASS = os.getenv("MYSQL_PASSWORD", "")
HOST = os.getenv("MYSQL_HOST", "localhost")
PORT = os.getenv("MYSQL_PORT", "3306")
DB = os.getenv("MYSQL_DB", "test")

# Using pymysql driver
DATABASE_URL = f"mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{DB}"

# Connect engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_schema_info() -> str:
    """Extracts database schema (tables & columns) so Gemini knows the DB structure."""
    inspector = inspect(engine)
    schema_details = []
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_names = [f"{col['name']} ({col['type']})" for col in columns]
        schema_details.append(f"Table '{table_name}': " + ", ".join(col_names))
        
    return "\n".join(schema_details)

def execute_read_only_query(sql_query: str):
    """Executes SQL safely inside a read-only transaction and returns dict results."""
    with engine.connect() as connection:
        # Enforce read-only mode for the session (MySQL support)
        connection.execute(text("SET TRANSACTION READ ONLY;"))
        result = connection.execute(text(sql_query))
        
        if result.returns_rows:
            keys = result.keys()
            rows = result.fetchall()
            return [dict(zip(keys, row)) for row in rows]
        return []