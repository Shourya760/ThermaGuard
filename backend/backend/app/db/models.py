"""
app/db/models.py

SQLAlchemy database models for CoolBlock.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class DBZone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_type = Column(String, nullable=False)
    description = Column(String)
    data_status = Column(String, nullable=False)
    coordinate_source = Column(String, nullable=False)
    data_provenance = Column(String, nullable=False)
    last_verified_utc = Column(String)
    
    # We store the heat indicators as a JSON column for flexibility
    heat_indicators = Column(JSON, nullable=True)


class DBActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    zone_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    budget = Column(Float, nullable=False)
    total_estimated_cost = Column(Float, nullable=False)
    remaining_budget = Column(Float, nullable=False)
    is_feasible = Column(Boolean, nullable=False)
    
    # Store the list of interventions evaluated for this plan as JSON
    interventions = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
