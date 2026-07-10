#!/usr/bin/env bash
# Deploy shtimung weba na Plus Hosting preko SSH-a (rsync).
# Konfiguracija se čita iz scripts/deploy.env (nije u gitu — sadrži podatke servera).
#
# Prvi setup:
#   cp scripts/deploy.env.example scripts/deploy.env   # pa upiši svoje podatke
#   ssh-copy-id -p $DEPLOY_PORT $DEPLOY_USER@$DEPLOY_HOST   # ključ umjesto lozinke
#
# Korištenje:
#   ./scripts/deploy.sh          # dry-run (pokaže što bi se mijenjalo)
#   ./scripts/deploy.sh --go     # stvarni deploy

set -euo pipefail
cd "$(dirname "$0")/.."

ENV_FILE="scripts/deploy.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Nedostaje $ENV_FILE — kopiraj scripts/deploy.env.example i upiši podatke." >&2
  exit 1
fi
source "$ENV_FILE"

: "${DEPLOY_HOST:?DEPLOY_HOST nije postavljen}"
: "${DEPLOY_USER:?DEPLOY_USER nije postavljen}"
: "${DEPLOY_PORT:=22}"
: "${DEPLOY_PATH:?DEPLOY_PATH nije postavljen}"

# deploya se kompletan www/ (web root); _src (fontovi) i smtp-config ne idu
RSYNC_FLAGS=(-avz --delete
  --exclude='brand/_src'
  --exclude='.DS_Store'
  --exclude='nashtimaj/smtp-config.php')

if [[ "${1:-}" == "--go" ]]; then
  rsync "${RSYNC_FLAGS[@]}" -e "ssh -p $DEPLOY_PORT" ./www/ "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/"
  echo "✓ Deploy gotov → https://shtimung.hr"
else
  echo "── DRY RUN (dodaj --go za stvarni deploy) ──"
  rsync "${RSYNC_FLAGS[@]}" --dry-run -e "ssh -p $DEPLOY_PORT" ./www/ "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/"
fi
