# Instrumenting Celery with OpenTelemetry

This example demonstrates how to instrument a Celery producer and worker with
the Splunk Distribution of OpenTelemetry Python. The sample uses Redis as the
message broker and result backend.

## Prerequisites

The following tools are required to run this example:

* Python 3.10+
* Docker, or another local Redis server

## Install Packages

Open a command line terminal and navigate to the root of the directory:

````
cd ~/splunk-opentelemetry-examples/instrumentation/python/celery
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
````

For any new terminal you use with this example, navigate to this directory and
activate the virtual environment before running commands:

````
cd ~/splunk-opentelemetry-examples/instrumentation/python/celery
source ./venv/bin/activate
````

## Choose a Telemetry Receiver

The Splunk Distribution of OpenTelemetry Python exports OTLP/gRPC telemetry to
`http://localhost:4317` by default. You can use either `otelsink` for local
validation or the Splunk OpenTelemetry Collector to forward telemetry to Splunk
Observability Cloud.

### Option 1: Validate Locally with otelsink

Install `oteltest`, which provides the `otelsink` command:

````
pip install oteltest
````

In a separate terminal, start `otelsink`:

````
otelsink
````

`otelsink` prints received OTLP telemetry to the terminal. For this example,
expect Celery spans named `apply_async/tasks.add` and `run/tasks.add`.

### Option 2: Export Through the Splunk OpenTelemetry Collector

To send telemetry to Splunk Observability Cloud, run a local Splunk
OpenTelemetry Collector instead of `otelsink`. Follow the
[collector installation instructions](https://docs.splunk.com/observability/en/gdi/opentelemetry/install-the-collector.html)
if you do not already have one available.

## Start Redis

Start Redis with Docker Compose:

````
docker compose up -d redis
````

If you already have Redis running elsewhere, set `CELERY_BROKER_URL` and
`CELERY_RESULT_BACKEND` before starting the worker and producer.

## Run the Worker

In the first terminal, start the Celery worker with `opentelemetry-instrument`:

````
OTEL_SERVICE_NAME=python-celery-worker \
  opentelemetry-instrument celery -A tasks worker --loglevel=INFO -c 2
````

## Run the Producer

In a second terminal, send a task to the worker:

````
OTEL_SERVICE_NAME=python-celery-producer \
  opentelemetry-instrument python producer.py
````

The producer should print a submitted task ID and then return:

````
Task result: 8
````

After a minute or so, traces for `python-celery-producer` and
`python-celery-worker` should appear in `otelsink` or Splunk Observability Cloud,
depending on the telemetry receiver you chose.
