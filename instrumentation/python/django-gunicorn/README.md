# Instrumenting Django and Gunicorn with OpenTelemetry

This example demonstrates how to instrument a Django application running under
Gunicorn with the Splunk Distribution of OpenTelemetry Python.

## Prerequisites

The following tools are required to run this example:

* Python 3.10+

## Install Packages

Open a command line terminal and navigate to the root of the directory:

````
cd ~/splunk-opentelemetry-examples/instrumentation/python/django-gunicorn
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
````

For any new terminal you use with this example, navigate to this directory and
activate the virtual environment before running commands:

````
cd ~/splunk-opentelemetry-examples/instrumentation/python/django-gunicorn
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
expect a Django server span named `GET hello/`.

### Option 2: Export Through the Splunk OpenTelemetry Collector

To send telemetry to Splunk Observability Cloud, run a local Splunk
OpenTelemetry Collector instead of `otelsink`. Follow the
[collector installation instructions](https://docs.splunk.com/observability/en/gdi/opentelemetry/install-the-collector.html)
if you do not already have one available.

## Run the Application

Start Gunicorn with `opentelemetry-instrument`:

````
DJANGO_SETTINGS_MODULE=django_gunicorn_example.settings \
OTEL_SERVICE_NAME=python-django-gunicorn \
  opentelemetry-instrument gunicorn \
  -b 127.0.0.1:8000 \
  --workers 1 \
  django_gunicorn_example.wsgi:application
````

In another terminal, send a request to the application:

````
curl http://localhost:8000/hello/
````

The application should return:

````
Hello, World!
````

After a minute or so, traces for `python-django-gunicorn` should appear in
`otelsink` or Splunk Observability Cloud, depending on the telemetry receiver
you chose.
