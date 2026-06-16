#!/bin/sh
set -eu

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

HOST_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4)

export OTEL_EXPORTER_OTLP_ENDPOINT="http://${HOST_IP}:4318"

exec java \
  -javaagent:/app/agent/javaagent.jar \
  -Dappdynamics.controller.hostName="${APPD_CONTROLLER_HOST}" \
  -Dappdynamics.controller.port=443 \
  -Dappdynamics.controller.ssl.enabled=true \
  -Dappdynamics.agent.applicationName="${APPD_APP_NAME}" \
  -Dappdynamics.agent.tierName="${APPD_TIER_NAME}" \
  -Dappdynamics.agent.nodeName="${APPD_NODE_NAME}" \
  -Dappdynamics.agent.accountName="${APPD_ACCOUNT_NAME}" \
  -Dappdynamics.agent.accountAccessKey="${APPD_ACCESS_KEY}" \
  -Dagent.deployment.mode=dual \
  -Dotel.traces.exporter=otlp \
  -Dotel.exporter.otlp.endpoint="${OTEL_EXPORTER_OTLP_ENDPOINT}" \
  -Dotel.service.name="${OTEL_SERVICE_NAME}" \
  -Dotel.resource.attributes="${OTEL_RESOURCE_ATTRIBUTES}" \
  -jar /app/app.jar