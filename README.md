# dag-stack

Demo data pipeline with dbt, Airflow, Great Expectations.


## How to run

 This repo contains a runnable demo using [Astronomer](https://www.astronomer.io/) (containerized Airflow), which is a convenient option to run everything in a Docker container.
* Install the Astronomer CLI (containerized Airflow), [instructions here](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart)
  * *Note:* If you only want to run Airflow locally for development, you do not need to sign up for an Astronomer Cloud account. Simply follow the instructions to install the Astronomer CLI.
* Run `astro dev start` to start up the Airflow Docker containers
  * I had to follow the [Docker config instructions here](https://forum.astronomer.io/t/buildkit-not-supported-by-daemon-error-command-docker-build-t-airflow-astro-bcb837-airflow-latest-failed-failed-to-execute-cmd-exit-status-1/857) to handle a "buildkit not supported" error
  * I also had to set the `AIRFLOW__WEBSERVER` env variables in the Dockerfile as well as allocate more resources to Docker in order for the webserver to run on my very old very slow laptop :) (2013 MacBook Air ftw)
  * Thanks to [this post](https://dev.to/corissa/2-critical-things-about-dbt-0-19-0-installation-20j) for the `agate` version pin
* This will start up the Airflow scheduler, webserver, and a Postgres database
* Once the webserver is up (takes about 30 seconds), you can access the Airflow web UI at localhost:8080
* You can run `astro dev stop` to stop the container again

You can also run the DAG in this repo with a **standard Airflow installation** if you want. You'll have to install the relevant dependencies (Airflow, dbt, Great Expectations, the respective operators, etc) and probably handle some more configurations to get it to work.
