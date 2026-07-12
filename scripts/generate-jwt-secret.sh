#!/usr/bin/env sh
# Generate a cryptographically strong JWT secret for HS256.
# Copy the output into your deployment .env as JWT_SECRET=...

set -e

if command -v openssl >/dev/null 2>&1; then
  secret=$(openssl rand -base64 32 | tr -d '\n')
else
  echo "openssl is required to generate JWT_SECRET" >&2
  exit 1
fi

printf '\nAdd this to your .env file (do NOT commit .env):\n\n'
printf 'JWT_SECRET=%s\n\n' "$secret"
