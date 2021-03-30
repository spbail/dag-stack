from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow_dbt.operators.dbt_operator import (
    DbtSeedOperator,
    DbtRunOperator
)
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
import os

def load_to_production_db(ts, **kwargs):
    """
    This is just a stub for an optional Python task that loads the output of the dbt pipeline
    to a production database or data warehouse for further consumption
    """
    print('Loading analytical output to production database.')
    print('Done.')


# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021, 1, 1)
}

# These could be set with environment variables if you want to run the DAG outside the Astro container
PROJECT_HOME = '/usr/local/airflow'
GE_ROOT_DIR = os.path.join(PROJECT_HOME, 'great_expectations')
DBT_PROJECT_DIR = os.path.join(PROJECT_HOME, 'dbt')
DBT_TARGET = 'astro_dev'


dag = DAG(
    dag_id='dag_stack_dag',
    schedule_interval=None,
    default_args=default_args
)

# This first step validates the source data files and only proceeds with loading
# if they pass validation with Great Expectations
validate_source_data = GreatExpectationsOperator(
    task_id='validate_source_data',
    assets_to_validate = [
        {
            'batch_kwargs': {
                'path': os.path.join(PROJECT_HOME, 'data', 'taxi_zone_lookup.csv'),
                'datasource': 'data_dir'
            },
            'expectation_suite_name': 'taxi_zone.source'
        },
        # For the sake of brevity, I'm only validation one data asset here,
        # but could easily add another item to this list to validate more data assets
    ],
    data_context_root_dir=GE_ROOT_DIR,
    dag=dag
)

# The dbt seed command loads files in the data directory to the database
dbt_seed = DbtSeedOperator(
    task_id='dbt_seed',
    dir=DBT_PROJECT_DIR,
    profiles_dir=PROJECT_HOME,
    target=DBT_TARGET,
    dag=dag
)

# This step validates that the load is correct. I'm re-using the same
# Expectation Suite as for the source data load, but could use a different one,
# e.g. to account for different casing or datatypes of columns
validate_load = GreatExpectationsOperator(
    task_id='validate_load',
    assets_to_validate=[
        {
            'batch_kwargs': {
                'datasource': 'postgres_astro',
                'table': 'taxi_zone_lookup'
            },
            'expectation_suite_name': 'taxi_zone.source'
        },
        # For the sake of brevity, I'm only validation one data asset here,
        # but could easily add another item to this list to validate more data assets
    ],
    data_context_root_dir=GE_ROOT_DIR,
    dag=dag
)

# This runs the transformation steps in the dbt pipeline
dbt_run = DbtRunOperator(
    task_id='dbt_run',
    dir=DBT_PROJECT_DIR,
    profiles_dir=PROJECT_HOME,
    target=DBT_TARGET,
    dag=dag
)

# This step validates the final transformation output. This could also be done
# with dbt, but I'm using Great Expectations for the sake of this demo.
validate_transform = GreatExpectationsOperator(
    task_id='validate_transform',
    expectation_suite_name='analytical_output',
    batch_kwargs={
        'datasource': 'postgres_astro',
        'table': 'pickup_dropoff_borough_counts'
    },
    data_context_root_dir=GE_ROOT_DIR,
    dag=dag
)

load_to_prod = PythonOperator(
    task_id='load_to_prod',
    python_callable=load_to_production_db,
    dag=dag
)

validate_source_data >> dbt_seed >> validate_load >> dbt_run >> validate_transform >> load_to_prod
