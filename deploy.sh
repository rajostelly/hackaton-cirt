#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ARO SOC — déploiement frontend vers sfyrisec.duckdns.org
#
# Usage (Git Bash / Linux / macOS) :
#   bash ARO-Hackaton/deploy.sh
#
# Ce script tourne en LOCAL. Il :
#   1. Build ARO-Hackaton/web/ → dist/
#   2. Pousse dist/ vers le serveur via rsync (ou scp en fallback)
#   3. Redémarre le backend (optionnel)
#
# Prérequis :
#   - node + npm installés localement
#   - ssh + (rsync ou scp) disponibles (inclus dans Git Bash / macOS / Linux)
#   - Clé SSH configurée OU mot de passe root disponible
# ─────────────────────────────────────────────────────────────────────────────
set -Eeuo pipefail

# ── Config ────────────────────────────────────────────────────────────────
SERVER_USER="${DEPLOY_USER:-root}"
SERVER_HOST="${DEPLOY_HOST:-64.227.181.46}"
WEBROOT="${DEPLOY_WEBROOT:-/var/www/sfyrisec}"
BACKEND_SERVICE="${DEPLOY_BACKEND_SERVICE:-aro-backend}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/web"

# ── Helpers ───────────────────────────────────────────────────────────────
log()  { printf '\n\033[1;36m▶  %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓  %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m⚠  %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m✗  %s\033[0m\n' "$*" >&2; exit 1; }

# ── Vérifications préliminaires ───────────────────────────────────────────
command -v node >/dev/null 2>&1 || die "node introuvable — installez Node.js"
command -v npm  >/dev/null 2>&1 || die "npm introuvable"
[[ -d "$FRONTEND_DIR" ]]        || die "Dossier web/ introuvable : $FRONTEND_DIR"

# ─────────────────────────────────────────────────────────────────────────
log "1/3  Construction du frontend (ARO-Hackaton/web/)"

cd "$FRONTEND_DIR"
echo "  npm ci…"
npm ci --silent
echo "  vite build…"
VITE_API_BASE_URL=/api npm run build

DIST_SIZE="$(du -sh dist/ 2>/dev/null | cut -f1 || echo '?')"
ok "dist/ construit (${DIST_SIZE})"

# ─────────────────────────────────────────────────────────────────────────
log "2/3  Déploiement → $SERVER_USER@$SERVER_HOST:$WEBROOT"

SSH_TARGET="$SERVER_USER@$SERVER_HOST"

if command -v rsync >/dev/null 2>&1; then
  # rsync est idempotent et ne transfère que les fichiers modifiés
  rsync -az --delete --progress \
    -e "ssh -o StrictHostKeyChecking=no" \
    "$FRONTEND_DIR/dist/" \
    "$SSH_TARGET:$WEBROOT/"
else
  warn "rsync absent — fallback scp (transfert complet)"
  ssh -o StrictHostKeyChecking=no "$SSH_TARGET" \
    "rm -rf '$WEBROOT' && mkdir -p '$WEBROOT'"
  scp -r -o StrictHostKeyChecking=no \
    "$FRONTEND_DIR/dist/." \
    "$SSH_TARGET:$WEBROOT/"
fi

ok "Frontend déployé sur le serveur"

# ─────────────────────────────────────────────────────────────────────────
log "3/3  Rechargement nginx + vérification backend"

ssh -o StrictHostKeyChecking=no "$SSH_TARGET" bash <<REMOTE
  set -e

  # Recharge nginx pour vider le cache des fichiers statiques
  if command -v nginx >/dev/null 2>&1; then
    nginx -t -q && systemctl reload nginx
    echo "  nginx rechargé."
  fi

  # Vérifie que le backend répond (ne redémarre pas sauf si mort)
  if systemctl is-active --quiet "$BACKEND_SERVICE" 2>/dev/null; then
    echo "  Backend $BACKEND_SERVICE : actif."
  else
    echo "  Backend $BACKEND_SERVICE inactif — tentative de (re)démarrage…"
    systemctl start "$BACKEND_SERVICE" 2>/dev/null || true
  fi

  # Vérification rapide du healthcheck
  sleep 1
  if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "  API /health : OK"
  else
    echo "  ⚠ API non joignable sur :8000 (vérifiez le service $BACKEND_SERVICE)"
  fi
REMOTE

ok "Déploiement terminé"
echo ""
echo "  🌐  https://sfyrisec.duckdns.org"
echo "  🔧  https://sfyrisec.duckdns.org/api/health"
echo ""
echo "  Pour redéployer uniquement le frontend :"
echo "    bash ARO-Hackaton/deploy.sh"
echo ""
echo "  Pour configurer SSH sans mot de passe (recommandé) :"
echo "    ssh-keygen -t ed25519 -C 'aro-deploy'"
echo "    ssh-copy-id $SERVER_USER@$SERVER_HOST"
