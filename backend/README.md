# magellan API

This repository contains the code for magellan's main REST API.

It is developed using Python with Flask.
Deployment is done on Elastic Beanstalk, with CI/CD using CircleCI.

## Running locally

- Make sure you have python 3.6+ installed
- Create a virtual environment: `python -m venv venv` and activate it `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Create a `.env` file in `magellan` and populate it with the required environment variables (running the server will tell you which are missing. Ask an administrator for the full list if needed.)
- Run: `python application.py`

You can also run an interactive shell using `python shell.py`

The LOCAL environment variable is necessary if running outside of the AWS VPC, as the Redis host is not accessible.

## Testing

In order to best mimick a production environment, unit tests require a PostgreSQL database connection to function.
Other AWS (or other) services are mocked to the best extent.

To run unit tests locally, you will need `docker` installed on your machine.

Simply run `./run-tests.sh`. This will spin a docker container with PostgreSQL to work with.
The container is destroyed after running.

If you can't work with docker or want to use a local postgresql database, run `./run-tests-local.sh` instead. This requires a POSTGRES instance listening on localhost:5432, and an account with user=postgres / password=test with full privileges on the datbaase
**_NOTE: running tests on your own instance will delete all data in that instance under the "users" database, so be extra careful._**

## Deployment

Just push to master, and check CircleCI for build / deployment progress.
