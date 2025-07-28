import os
from google.cloud import bigquery

def run_bigquery_sql():
    # Access environment variables
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    bq_dataset = os.getenv('BQ_DATASET')

    # Initialize the BigQuery client
    client = bigquery.Client()

    # Hourly data table for BigQuery
    sql_hourly_data = f"""
        CREATE OR REPLACE TABLE `{gcp_project_id}.{bq_dataset}.hourly_data` AS
        WITH relevant_cols_data AS (
            SELECT
                PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', transit_timestamp) AS transit_timestamp,
                borough,
                station_complex,
                transit_mode,
                payment_method,
                fare_class_category,
                CAST(ridership AS FLOAT64) AS ridership,
                CAST(transfers AS FLOAT64) AS transfers,
                latitude,
                longitude
            FROM `{gcp_project_id}.{bq_dataset}.nyc`
        )
        SELECT
            transit_timestamp,
            borough,
            station_complex,
            transit_mode,
            payment_method,
            SUM(CAST(ridership AS INT64)) AS ridership,
            SUM(CAST(transfers AS INT64)) AS transfer
        FROM relevant_cols_data
        GROUP BY
            transit_timestamp,
            borough,
            station_complex,
            transit_mode,
            payment_method;
    """

    # Execute the query
    hourly_data_query_job = client.query(sql_hourly_data)
    hourly_data_query_job.result()
    print(f"Hourly data has been written to the table: {gcp_project_id}.{bq_dataset}.hourly_data")

    # Daily data table for BigQuery
    sql_daily_data = f"""
        CREATE OR REPLACE TABLE `{gcp_project_id}.{bq_dataset}.daily_data` AS
        WITH data_grouped_by_date AS (
            SELECT
                DATE(transit_timestamp) AS transit_date,
                borough,
                station_complex,
                transit_mode,
                payment_method,
                fare_class_category,
                CAST(ridership AS FLOAT64) AS ridership,
                CAST(transfers AS FLOAT64) AS transfers,
                latitude,
                longitude
            FROM `{gcp_project_id}.{bq_dataset}.nyc`
        )
        SELECT
            transit_date,
            borough,
            station_complex,
            transit_mode,
            payment_method,
            SUM(CAST(ridership AS INT64)) AS ridership,
            SUM(CAST(transfers AS INT64)) AS transfer
        FROM data_grouped_by_date
        GROUP BY
            transit_date,
            borough,
            station_complex,
            transit_mode,
            payment_method;
    """

    # Execute the query
    daily_data_query_job = client.query(sql_daily_data)
    daily_data_query_job.result()
    print(f"Daily data has been written to the table: {gcp_project_id}.{bq_dataset}.daily_data")

run_bigquery_sql()
