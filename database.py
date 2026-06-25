import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define the SQLite Database path
# The database file medicines.db will be created in the current working directory.
DATABASE_URL = "sqlite:///medicines.db"

# 2. Create the SQLAlchemy Engine
# connect_args={"check_same_thread": False} is required for SQLite to support multi-threading.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Create a SessionLocal class
# Each instance of SessionLocal will represent a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Declarative Base class
# All models will inherit from this base class.
Base = declarative_base()

# 5. Define the Medicines Model
class Medicine(Base):
    __tablename__ = "Medicines"

    MedicineID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    MedicineName = Column(String, index=True)
    Composition = Column(String)
    Uses = Column(String)
    SideEffects = Column(String)
    Manufacturer = Column(String)

# 6. Initialize database and seed with sample data if empty
def init_db():
    """
    Creates the database tables.
    """
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Medicine).count() == 0:
            print("Database created. Waiting for CSV import.")
        else:
            print("Database already contains records.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

# Dependency helper to get a DB session in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
