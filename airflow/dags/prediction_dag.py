from pathlib import Path
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException


GOOD_DIR = Path("/opt/airflow/data/good_data")
STATE_FILE = Path("/opt/airflow/data/.prediction_processed")

API_URL = "http://fastapi:8000/batch-predict"


with DAG(
    dag_id="athlete_prediction_job",
    description="Scheduled batch predictions for validated athlete data",
    start_date=datetime(2026, 1, 1),
    schedule="*/2 * * * *",
    catchup=False,
    tags=["athlete", "prediction"],
) as dag:

    @task
    def check_for_new_data():
        files = sorted(GOOD_DIR.glob("*.csv"))

        processed = set()

        if STATE_FILE.exists():
            processed = set(
                STATE_FILE.read_text().splitlines()
            )

        new_files = [
            str(file)
            for file in files
            if file.name not in processed
        ]

        if not new_files:
            raise AirflowSkipException(
                "No new validated data available."
            )

        return new_files


    @task
    def make_predictions(file_paths):

        # Read all new validated files
        dataframes = [
            pd.read_csv(path)
            for path in file_paths
        ]

        # Combine into one dataframe
        combined_df = pd.concat(
            dataframes,
            ignore_index=True
        )

        # Convert combined dataframe into CSV
        csv_buffer = StringIO()

        combined_df.to_csv(
            csv_buffer,
            index=False
        )

        csv_content = csv_buffer.getvalue()

        # ONE batch API request for all files
        response = requests.post(
            API_URL,
            files={
                "file": (
                    "airflow_batch.csv",
                    csv_content,
                    "text/csv"
                )
            },
            timeout=120
        )

        response.raise_for_status()

        # Save returned prediction CSV
        output_file = Path(
            "/opt/airflow/data/prediction_results.csv"
        )

        output_file.write_bytes(response.content)

        # Mark files as processed
        already_processed = set()

        if STATE_FILE.exists():
            already_processed = set(
                STATE_FILE.read_text().splitlines()
            )

        already_processed.update(
            Path(path).name
            for path in file_paths
        )

        STATE_FILE.write_text(
            "\n".join(sorted(already_processed))
        )

        print(
            f"Successfully predicted {len(combined_df)} rows "
            f"from {len(file_paths)} files using one API call."
        )

        return {
            "rows_predicted": len(combined_df),
            "files_processed": len(file_paths)
        }


    files = check_for_new_data()

    make_predictions(files)
