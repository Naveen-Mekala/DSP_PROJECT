from sqlalchemy import Column, Integer, Float, String
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