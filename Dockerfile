FROM quay.io/astronomer/ap-airflow:2.0.0-buster-onbuild

ENV AIRFLOW__WEBSERVER__WORKERS=1
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True