# ---- Build stage ----
FROM maven:3.9.9-eclipse-temurin-17 AS builder
WORKDIR /build

# Tools needed for agent download
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip jq && \
    rm -rf /var/lib/apt/lists/*

# Cache Maven dependencies
COPY pom.xml .
RUN mvn -q -DskipTests dependency:go-offline

# Copy source and build jar
COPY src ./src
RUN mvn -q -DskipTests clean package

# Download AppDynamics Java agent
RUN set -eux; \
    INSTALL_DIR="/build/agent"; \
    mkdir -p "${INSTALL_DIR}"; \
    FILE_PATH="$(curl -s https://download.appdynamics.com/download/downloadfilelatest/ | jq -r '.[].s3_path' | grep java-jdk8 | head -n 1)"; \
    DOWNLOAD_URL="https://download-files.appdynamics.com/${FILE_PATH}"; \
    echo "Downloading agent from: ${DOWNLOAD_URL}"; \
    curl -fL "${DOWNLOAD_URL}" -o /build/JavaAgent.zip; \
    unzip /build/JavaAgent.zip -d "${INSTALL_DIR}"; \
    rm -f /build/JavaAgent.zip

# ---- Runtime stage ----
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

RUN apk add --no-cache curl

# Non-root user
RUN addgroup -S spring && adduser -S spring -G spring

# Copy app jar and agent from builder
COPY --from=builder /build/target/*.jar /app/app.jar
COPY --from=builder /build/agent /app/agent

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Fix permissions for AppD dynamic service/log folders
RUN chown -R spring:spring /app && \
    chmod -R u+rwX,g+rwX /app/agent

USER spring:spring
EXPOSE 8080

ENTRYPOINT ["/app/start.sh"]