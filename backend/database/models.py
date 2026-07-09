"""
models.py
HemaGrid AI - Database Engine and ORM Models

Defines SQLite connection and SQLAlchemy models for managing hospital
blood inventories and cold chain shipment logs.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Setup
DATABASE_URL = "sqlite:///hemagrid.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ORM Models ---

class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    hospital_type = Column(String(50), nullable=False) # "General", "Trauma", "Clinic"

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    blood_type = Column(String(10), nullable=False)     # "A_POS", "O_NEG", etc.
    units_available = Column(Integer, default=0)

class ShipmentLog(Base):
    __tablename__ = "shipment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False)
    temperature = Column(Float, nullable=False)
    max_impact = Column(Float, nullable=False)
    state = Column(String(20), nullable=False)          # "SAFE", "WARNING", "COMPROMISED"
    logged_at = Column(DateTime, default=datetime.utcnow)

# --- Initializer ---

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Pre-populate sample hospital data if empty
    db = SessionLocal()
    try:
        if db.query(Hospital).count() == 0:
            hospitals = [
                Hospital(id=1, name="City Medical Center", hospital_type="General"),
                Hospital(id=2, name="Apollo Trauma Unit", hospital_type="Trauma"),
                Hospital(id=3, name="St. Jude Wellness Clinic", hospital_type="Clinic")
            ]
            db.add_all(hospitals)
            db.commit()
            
            # Populate basic stock levels
            blood_types = ['A_POS', 'A_NEG', 'B_POS', 'B_NEG', 'AB_POS', 'AB_NEG', 'O_POS', 'O_NEG']
            inventory_items = []
            for h in hospitals:
                for b in blood_types:
                    inventory_items.append(
                        Inventory(hospital_id=h.id, blood_type=b, units_available=np_random_stock())
                    )
            db.add_all(inventory_items)
            db.commit()
            print("Database pre-populated with sample hospitals and inventory.")
    finally:
        db.close()

def np_random_stock():
    # Simple deterministic random stock levels for demo setup
    import random
    return random.randint(5, 40)
