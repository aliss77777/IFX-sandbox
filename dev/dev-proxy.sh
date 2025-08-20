#!/usr/bin/env sh
set -euo pipefail

PROXY_PORT="${PROXY_PORT:-3000}"
TARGET_HOST="${TARGET_HOST:-ifx-app}"
TARGET_PORT="${TARGET_PORT:-3000}"
LOG_FILE="${PROXY_LOG_FILE:-/home/dev/proxy-${PROXY_PORT}.log}"
PROXY_BIND="${PROXY_BIND:-0.0.0.0}"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[dev-proxy] starting: listen ${PROXY_BIND}:${PROXY_PORT} -> ${TARGET_HOST}:${TARGET_PORT}" | tee -a "$LOG_FILE"
echo "[dev-proxy] log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "[dev-proxy] date: $(date)" | tee -a "$LOG_FILE"

# Wait for the target host and port to become available.
# This uses bash's built-in /dev/tcp for a clean, dependency-free check.
echo "[dev-proxy] Waiting for ${TARGET_HOST}:${TARGET_PORT} to be ready..." | tee -a "$LOG_FILE"
while ! bash -c "exec 3<>/dev/tcp/${TARGET_HOST}/${TARGET_PORT}" 2>/dev/null; do
  echo "[dev-proxy] still waiting for ${TARGET_HOST}:${TARGET_PORT}... ($(date))" | tee -a "$LOG_FILE"
  sleep 1
done
echo "[dev-proxy] Target ${TARGET_HOST}:${TARGET_PORT} is ready!" | tee -a "$LOG_FILE"


# Endless supervisor loop; if target is down, socat exits and we retry
while true; do
  echo "[dev-proxy] (re)starting socat at $(date)" | tee -a "$LOG_FILE"
  # -d -d for extra debug if needed; use reuseaddr and fork
  socat -d -d TCP-LISTEN:${PROXY_PORT},fork,reuseaddr,bind=${PROXY_BIND} TCP:${TARGET_HOST}:${TARGET_PORT} 2>>"$LOG_FILE" || true
  echo "[dev-proxy] socat exited; sleeping 1s" | tee -a "$LOG_FILE"
  sleep 1
done