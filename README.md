# dag-stack

Demo data pipeline with dbt, Airflow, Great Expectations.

See another possible architecture for this at https://github.com/astronomer/airflow-dbt-demo

---

### ☕ Buy me a coffee ☕

If you enjoy this workshop and want to say thanks, you can buy me a coffee here: https://www.buymeacoffee.com/sambail
Thank you 😄

---


## How to run

 This repo contains a runnable demo using [Astronomer](https://www.astronomer.io/) (containerized Airflow), which is a convenient option to run everything in a Docker container.
* Install the Astronomer CLI (containerized Airflow), [instructions here](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart)
  * *Note:* If you only want to run Airflow locally for development, you do not need to sign up for an Astronomer Cloud account. Simply follow the instructions to install the Astronomer CLI.
* Run `astro dev start` to start up the Airflow Docker containers
  * I had to follow the [Docker config instructions here](https://forum.astronomer.io/t/buildkit-not-supported-by-daemon-error-command-docker-build-t-airflow-astro-bcb837-airflow-latest-failed-failed-to-execute-cmd-exit-status-1/857) to handle a "buildkit not supported" error
  * I also had to reduce the number of `AIRFLOW__WEBSERVER__WORKERS` in the Dockerfile as well as allocate more resources to Docker in order for the webserver to run on my very old very slow laptop :) (2013 MacBook Air ftw)
  * Thanks to [this post](https://dev.to/corissa/2-critical-things-about-dbt-0-19-0-installation-20j) for the `agate` version pin to work with dbt
* This will start up the Airflow scheduler, webserver, and a Postgres database
* Once the webserver is up (takes about 30 seconds), you can access the Airflow web UI at `localhost:8080`
* You can run `astro dev stop` to stop the container again

You can also run the DAG in this repo with a **standard Airflow installation** if you want. You'll have to install the relevant dependencies (Airflow, dbt, Great Expectations, the respective operators, etc) and probably handle some more configurations to get it to work.

## Development

In order to develop the dbt DAG and Great Expectations locally instead of in the containers (for faster dev loops), I created a new virtual environment with and installed relevant packages wit `pip install -r requirements.txt`

**dbt setup**

- Ran `dbt init dbt` to create the dbt directory in this repo
- I copied `~/.dbt/profiles.yml` into the root of this project and added the Astronomer postgres creds to have a database available -- **you wouldn't use this database in production or keep the file in the repo, this is just a shortcut for this demo!!**
- The `profiles.yml` target setup allows me to run the dbt pipeline both locally and within the container:
  - Container:
    - connect to shell within the scheduler container
    - run `cd dbt`
    - run `dbt run --profiles-dir /usr/local/airflow --target astro_dev`
  - Local:
    - run `cd dbt`
    - run `dbt run --profiles-dir /Users/sam/code/dag-stack --target local_dev`

**Great Expectations setup**

- Ran `great_expectations init` to create the great_expectations directory in this repo
- Created Datasources for the `data` directory and the Astronomer postgres database using the `great_expectations datasource new` command
  - Note that I have two Datasources for the different host names, similar to the two dbt targets
  - I copied the credentials from `uncommitted/config_variables.yml` into the `datasources` section in `great_expectations.yml` for the purpose of this demo, since the `uncommitted` directory is git-ignored
- Created new Expectation Suites using `great_expectations suite scaffold` against the `data_dir` and `postgres_local` Datasources and manually tweaked the scaffold output a little using `suite edit`

**Airflow DAG setup**

- I'm using the custom dbt and Great Expectations Airflow operators, but this could also be done with Python and bash operators
- Note that the source data and loaded data validation both use the same Expectation Suite, which is a neat feature of Great Expectations -- a test suite can be run against any data asset to assert the same properties

## Serving dbt and Great Expectations docs

- The DAG contains example tasks that copy the docs for each framework into the `include` folder in the container which is mapped to the host machine, so you can inspect them manually
- In production (and when deploying the container to Astronomer Cloud), both docs could (should) be copied to and hosted on an external service, e.g. on Netlify or in an S3 bucket

## Additional resources

This repo is based on several existing resources:
- [Great Expectations Airflow + dbt tutorial](https://github.com/superconductive/ge_tutorials/tree/main/ge_dbt_airflow_tutorial) (which I had originally built)
- [The example DAGs in the Great Expectations Airflow Provider](https://github.com/great-expectations/airflow-provider-great-expectations/blob/main/great_expectations_provider/example_dags/example_great_expectations_dag.py) (which I also originally built haha)
- [Building a Scalable Analytics Architecture with Airflow and dbt](https://www.astronomer.io/blog/airflow-dbt-1)
