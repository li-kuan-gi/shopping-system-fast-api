import os
from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from collections.abc import Generator

_ = load_dotenv()

# Get database URL from environment
# For Supabase: postgresql://[user]:[password]@[host]:[port]/[database]
database_url: str | None = os.environ.get("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL must be set in the .env file")

# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    poolclass=NullPool,
    pool_pre_ping=True,  # Verify connections before using them
    echo=False,  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for getting database session in FastAPI routes
def get_db() -> Generator[Session, None, None]:
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
