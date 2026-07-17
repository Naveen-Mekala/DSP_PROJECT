import os
import random
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd

from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook


RAW_DIR = Path("/opt/airflow/data/raw_data")
GOOD_DIR = Path("/opt/airflow/data/good_data")
BAD_DIR = Path("/opt/airflow/data/bad_data")

REQUIRED_COLUMNS = [
    "Athlete_ID", "Day", "Day_of_Week", "Week", "Age", "Gender",
    "Sport_Type", "Training_Type", "Training_Duration_Min",
    "Training_Intensity", "Sleep_Duration_Hours", "Caffeine_Intake_mg",
    "Stress_Level", "Resting_Heart_Rate", "HRV_ms", "Mood_Score",
    "Muscle_Soreness", "Energy_Level", "Recovery_Score"
]


def row_is_invalid(row):
    try:
        if pd.isna(row.get("Athlete_ID")) or pd.isna(row.get("Age")):
            return True

        if not 0 <= float(row.get("Recovery_Score")) <= 100:
            return True

        if row.get("Gender") not in ["Male", "Female"]:
            return True

        if not 0 <= float(row.get("Sleep_Duration_Hours")) <= 24:
            return True

        if not 0 <= float(row.get("Mood_Score")) <= 10:
            return True

        if float(row.get("Training_Duration_Min")) < 0:
            return True

        if not 30 <= float(row.get("Resting_Heart_Rate")) <= 220:
            return True

    except (ValueError, TypeError):
        return True

    return False


with DAG(
    dag_id="athlete_data_ingestion",
    description="Ingest and validate athlete recovery data",
    start_date=datetime(2026, 1, 1),
    schedule="* * * * *",
    catchup=False,
    tags=["athlete", "ingestion", "data-quality"],
) as dag:

    @task
    def read_data():
        files = list(RAW_DIR.glob("*.csv"))

        if not files:
            raise ValueError("No files available in raw_data")

        selected = random.choice(files)

        # XCom-compatible data
        content = selected.read_text()

        # Delete after reading to prevent reprocessing
        selected.unlink()

        return {
            "filename": selected.name,
            "content": content
        }


    @task
    def validate_data(batch):
        from io import StringIO

        filename = batch["filename"]
        df = pd.read_csv(StringIO(batch["content"]))

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            return {
                "filename": filename,
                "content": batch["content"],
                "total_rows": len(df),
                "valid_rows": 0,
                "invalid_rows": len(df),
                "invalid_percentage": 100.0,
                "criticality": "High",
                "validation_success": False,
                "missing_columns": len(missing_columns),
                "error_summary": f"Missing columns: {missing_columns}",
                "valid_indices": [],
                "invalid_indices": list(range(len(df))),
            }

        invalid_mask = df.apply(row_is_invalid, axis=1)

        # Duplicate Athlete IDs are also invalid
        invalid_mask = invalid_mask | df["Athlete_ID"].duplicated(keep=False)

        invalid_indices = df.index[invalid_mask].tolist()
        valid_indices = df.index[~invalid_mask].tolist()

        total = len(df)
        invalid = len(invalid_indices)
        valid = len(valid_indices)

        percentage = (invalid / total * 100) if total else 0

        if percentage > 50:
            criticality = "High"
        elif percentage >= 10:
            criticality = "Medium"
        elif percentage > 0:
            criticality = "Low"
        else:
            criticality = "None"

        return {
            "filename": filename,
            "content": batch["content"],
            "total_rows": total,
            "valid_rows": valid,
            "invalid_rows": invalid,
            "invalid_percentage": round(percentage, 2),
            "criticality": criticality,
            "validation_success": invalid == 0,
            "missing_columns": 0,
            "error_summary": (
                f"{invalid}/{total} rows failed data-quality checks"
            ),
            "valid_indices": valid_indices,
            "invalid_indices": invalid_indices,
        }


    @task
    def save_statistics(result):
        hook = PostgresHook(postgres_conn_id="postgres_default")

        hook.run("""
            CREATE TABLE IF NOT EXISTS ingestion_stats (
                id SERIAL PRIMARY KEY,
                filename VARCHAR NOT NULL,
                ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_rows INTEGER,
                valid_rows INTEGER,
                invalid_rows INTEGER,
                invalid_percentage FLOAT,
                missing_columns INTEGER,
                criticality VARCHAR,
                validation_success VARCHAR,
                report_file VARCHAR
            )
        """)

        hook.run(
            """
            INSERT INTO ingestion_stats
            (
                filename,
                total_rows,
                valid_rows,
                invalid_rows,
                invalid_percentage,
                missing_columns,
                criticality,
                validation_success
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            parameters=(
                result["filename"],
                result["total_rows"],
                result["valid_rows"],
                result["invalid_rows"],
                result["invalid_percentage"],
                result["missing_columns"],
                result["criticality"],
                str(result["validation_success"]),
            ),
        )


    @task
    def send_alerts(result):
        criticality = result["criticality"]

        if criticality not in ["Medium", "High"]:
            print(
                f"No Teams alert required. Criticality: {criticality}"
            )
            return

        message = (
            f"DATA QUALITY ALERT\n"
            f"File: {result['filename']}\n"
            f"Criticality: {criticality}\n"
            f"Invalid rows: {result['invalid_rows']}"
            f"/{result['total_rows']}\n"
            f"Summary: {result['error_summary']}"
        )

        # Replace this with the Teams webhook/connection configured
        # by your team when credentials are available.
        print(message)


    @task
    def split_and_save_data(result):
        from io import StringIO

        GOOD_DIR.mkdir(parents=True, exist_ok=True)
        BAD_DIR.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(StringIO(result["content"]))

        filename = Path(result["filename"]).stem

        if result["missing_columns"] > 0:
            df.to_csv(
                BAD_DIR / f"{filename}_bad.csv",
                index=False
            )
            return

        valid_df = df.loc[result["valid_indices"]]
        invalid_df = df.loc[result["invalid_indices"]]

        if not valid_df.empty:
            valid_df.to_csv(
                GOOD_DIR / f"{filename}_good.csv",
                index=False
            )

        if not invalid_df.empty:
            invalid_df.to_csv(
                BAD_DIR / f"{filename}_bad.csv",
                index=False
            )


    batch = read_data()
    validation_result = validate_data(batch)

    save_statistics(validation_result)
    send_alerts(validation_result)
    split_and_save_data(validation_result)
