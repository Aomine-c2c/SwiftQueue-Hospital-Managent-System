import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Allow overriding the DB URL via environment variable for tests and deployments
# Use in-memory SQLite for ephemeral environments (like Render free tier)
default_db = "sqlite:///./queue_management.db"
if os.getenv("ENVIRONMENT") == "production" and not os.getenv("DATABASE_URL"):
    # Use in-memory SQLite for production if no DATABASE_URL provided
    # This handles Render's read-only filesystem
    print("⚠️  Using in-memory SQLite database (data will reset on restart)")
    print("   For persistent data, set DATABASE_URL environment variable")
    default_db = "sqlite:///:memory:"

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL") or os.getenv("DATABASE_URL") or default_db

# SQLite specific: disable same-thread check for SQLAlchemy usage across threads
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    # Import models so they are registered on the Base metadata before creating tables
    try:
        # import here to avoid circular imports at module import time
        import app.models.workflow_models  # noqa: F401
    except Exception:
        pass
    
    # Use checkfirst=True to avoid recreating existing indexes
    Base.metadata.create_all(bind=engine, checkfirst=True)

