from pydantic import BaseModel


class AthleteInput(BaseModel):
    Age: int
    Gender: str
    Sport_Type: str
    Training_Type: str
    Training_Duration_Min: float
    Training_Intensity: int
    Sleep_Duration_Hours: float
    Caffeine_Intake_mg: float
    Stress_Level: int
    Resting_Heart_Rate: float
    HRV_ms: float
    Mood_Score: float
    Muscle_Soreness: float
    Energy_Level: float