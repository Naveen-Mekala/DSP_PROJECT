from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from database.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    Age = Column(Integer)
    Gender = Column(String)
    Sport_Type = Column(String)
    Training_Type = Column(String)
    Training_Duration_Min = Column(Float)
    Training_Intensity = Column(Integer)
    Sleep_Duration_Hours = Column(Float)
    Caffeine_Intake_mg = Column(Float)
    Stress_Level = Column(Integer)
    Resting_Heart_Rate = Column(Float)
    HRV_ms = Column(Float)
    Mood_Score = Column(Float)
    Muscle_Soreness = Column(Float)
    Energy_Level = Column(Float)
    Prediction = Column(Float)


class IngestionStats(Base):
    __tablename__ = "ingestion_stats"

    id = Column(Integer, primary_key=True, index=True)

    # Information about the processed batch
    filename = Column(String, nullable=False)
    ingestion_time = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # General validation statistics
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)
    invalid_percentage = Column(Float, default=0.0)

    # Individual data-quality problems
    missing_values = Column(Integer, default=0)
    invalid_ranges = Column(Integer, default=0)
    invalid_categories = Column(Integer, default=0)
    missing_columns = Column(Integer, default=0)
    wrong_data_types = Column(Integer, default=0)
    duplicate_ids = Column(Integer, default=0)
    outliers = Column(Integer, default=0)

    # Overall validation result
    criticality = Column(String, default="None")
    validation_success = Column(String, default="True")

    # Great Expectations Data Docs report
    report_file = Column(String, nullable=True)
