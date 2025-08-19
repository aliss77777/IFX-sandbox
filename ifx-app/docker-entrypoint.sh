#!/bin/sh
set -euo pipefail
set -x

# If running as root, prepare mounts then re-exec via fixuid as node
if [ "${FIXUID_STAGE:-}" != "done" ] && [ "$(id -u)" -eq 0 ]; then
  echo "[entrypoint] running as root; preparing mounts then re-exec via fixuid"
  mkdir -p /app/.next /app/node_modules
  chown -R node:node /app/.next /app/node_modules || true
  # Re-exec this script via fixuid which will drop to the configured user (node)
  export FIXUID_STAGE=done
  echo "+ env FIXUID_STAGE=done fixuid -q -- /usr/local/bin/docker-entrypoint.sh"
  exec env FIXUID_STAGE=done fixuid -q -- /usr/local/bin/docker-entrypoint.sh
fi

# From here we are non-root (node)
echo "[entrypoint] effective user: $(whoami) (uid=$(id -u), gid=$(id -g))"
cd /app

# Ensure binding to all interfaces by default inside Docker
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-3000}"
# Verbose logs for npm/yarn where applicable
export NPM_CONFIG_LOGLEVEL="${NPM_CONFIG_LOGLEVEL:-verbose}"
export npm_config_loglevel="$NPM_CONFIG_LOGLEVEL"

# Ensure pnpm exists if pnpm-lock.yaml is present (so npx can resolve local bins properly)
if [ -f pnpm-lock.yaml ]; then
  command -v pnpm >/dev/null 2>&1 || npm i -g pnpm@8
fi

# Prefer local next binary if present, fallback to npx
if [ -x ./node_modules/.bin/next ]; then
  CMD="./node_modules/.bin/next dev --hostname \"$HOST\" --port \"$PORT\""
else
  CMD="npx next dev --hostname \"$HOST\" --port \"$PORT\""
fi
echo "+ $CMD"
exec sh -lc "$CMD"
