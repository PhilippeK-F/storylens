from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="data_engineer_template_pipeline",
    start_date=datetime(2025,1,1),
    schedule="@daily",
    catchup=False,
) as dag:

    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command="python -m src.pipelines.run_pipeline"
    )
