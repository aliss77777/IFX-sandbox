# Dev-friendly Next.js Dockerfile (clean multi-stage)
# - Fixes malformed RUN blocks
# - Removes duplicated/invalid stages (e.g., missing `builder` previously)
# - Provides a `development` target that does not require a full build
# - Chooses package manager by detected lockfile

ARG NODE_VERSION=18-alpine

# Base image with common setup
FROM node:${NODE_VERSION} AS base
WORKDIR /app
ENV NODE_ENV=development
# libc6-compat sometimes needed on alpine
RUN apk add --no-cache libc6-compat curl
# Ensure the workdir is owned by the non-root user for dev
RUN chown -R node:node /app
USER node

# deps: install node_modules based on the lockfile present
FROM base AS deps
# Only copy the manifest + lockfiles to maximize Docker cache efficiency
COPY --chown=node:node package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./
# Install with the appropriate manager. Do not fail hard if no lockfile exists in skeleton.
RUN set -eux; \
  if [ -f yarn.lock ]; then \
    yarn install --frozen-lockfile; \
  elif [ -f package-lock.json ]; then \
    npm ci; \
  elif [ -f pnpm-lock.yaml ]; then \
    npm i -g pnpm@8 && pnpm i --frozen-lockfile; \
  else \
    echo "No lockfile found; skipping install for now (dev skeleton)"; \
  fi; \
  mkdir -p node_modules

# development: ready for docker-compose mounts; runs the dev server
FROM base AS development
# Bring in node_modules from deps (if any were installed)
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
# Copy app sources (safe even if volumes will mount over them)
COPY --chown=node:node . .

# Switch to root to install fixuid and place entrypoint
USER root

# --- <fixuid install> ---
ARG FIXUID_VERSION=0.6.0
RUN curl -fsSL https://github.com/boxboat/fixuid/releases/download/v${FIXUID_VERSION}/fixuid-${FIXUID_VERSION}-linux-amd64.tar.gz \
    | tar -C /usr/local/bin -xz \
 && chown root:root /usr/local/bin/fixuid \
 && chmod 4755 /usr/local/bin/fixuid
RUN mkdir -p /etc/fixuid \
 && printf '%s\n' \
    'user: node' \
    'group: node' \
    > /etc/fixuid/config.yml
# --- </fixuid install> ---

# Copy entrypoint script and make executable
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
 && chown root:root /usr/local/bin/docker-entrypoint.sh

# Default to root so script can chown, then it will re-exec via fixuid as node
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD [""]

EXPOSE 3000
ENV PORT=3000
