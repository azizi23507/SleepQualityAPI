from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
DATABASE_URL = "postgresql://postgres:shabir123@localhost:5432/Sleep_quality_API"
engine = create_engine(DATABASE_URL).connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class all ORM models inherit from — registers them with SQLAlchemy
# and tracks their table definitions via Base.metadata.
Base = declarative_base()