#!/usr/bin/env bash
# Daily data refresh and release pipeline for SimTradeData.
#
# Usage (from crontab or systemd timer):
#   MARKET=cn PUBLISH_TARGETS=all COS_BUCKET=my-bucket COS_REGION=ap-guangzhou \
#   bash scripts/run_daily.sh
#
# Environment variables:
#   MARKET              Market to refresh: cn | us (default: cn)
#   PUBLISH_TARGETS     github | cos | all (default: github)
#   SIMTRADE_DATA_DIR   Path to SimTradeData repo (default: ../SimTradeData)
#   COS_BUCKET          COS bucket name (required for cos target)
#   COS_REGION          COS region (required for cos target)
#   COS_KEY_PREFIX      COS key prefix (default: "")
#   ALERT_WEBHOOK_URL   Webhook URL for failure alerts (optional)
#   LOCK_FILE           Path to lock file (default: /tmp/simtradedata_daily.lock)
#   LOG_DIR             Directory for run logs (default: logs/daily)
#   LOG_RETENTION_DAYS  Days to keep logs (default: 30)

set -euo pipefail

# ── Configuration ───────────────────────────────────────────────────
MARKET="${MARKET:-cn}"
PUBLISH_TARGETS="${PUBLISH_TARGETS:-github}"
SIMTRADE_DATA_DIR="${SIMTRADE_DATA_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
COS_BUCKET="${COS_BUCKET:-}"
COS_REGION="${COS_REGION:-}"
COS_KEY_PREFIX="${COS_KEY_PREFIX:-}"
ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"
LOCK_FILE="${LOCK_FILE:-/tmp/simtradedata_daily_${MARKET}.lock}"
LOG_DIR="${LOG_DIR:-$SIMTRADE_DATA_DIR/logs/daily}"
LOG_RETENTION_DAYS="${LOG_RETENTION_DAYS:-30}"

# ── Acquire single-instance lock ────────────────────────────────────
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Another instance holds $LOCK_FILE, exiting."
  exit 0
fi

# ── Setup logging ───────────────────────────────────────────────────
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y%m%d_%H%M%S)_${MARKET}.log"
exec > >(tee -a "$LOG_FILE") 2>&1

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

alert() {
  local msg="$*"
  log "ALERT: $msg"
  if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
    curl -s -X POST "$ALERT_WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "{\"text\":\"SimTradeData daily pipeline [${MARKET}]: ${msg}\"}" \
      >/dev/null 2>&1 || true
  fi
}

cleanup_logs() {
  find "$LOG_DIR" -name "*.log" -mtime "+$LOG_RETENTION_DAYS" -delete 2>/dev/null || true
}

# ── Determine DuckDB path by market ─────────────────────────────────
get_version() {
  local market="$1"
  cd "$SIMTRADE_DATA_DIR"
  poetry run python -c "
import duckdb
from pathlib import Path
from simtradedata.utils.paths import DATA_PATH

db_map = {'cn': DATA_PATH / 'cn.duckdb', 'us': DATA_PATH / 'us.duckdb'}
db_path = str(db_map.get('$market', db_map['cn']))
p = Path(db_path)
if not p.exists():
    print('')
    exit(0)
conn = duckdb.connect(db_path, read_only=True)
try:
    result = conn.execute('SELECT MAX(date) FROM stocks').fetchone()
    print(result[0] if result and result[0] else '')
finally:
    conn.close()
"
}

# ── Main pipeline ───────────────────────────────────────────────────
log "=== SimTradeData Daily Pipeline Start ==="
log "  Market:          $MARKET"
log "  Publish targets: $PUBLISH_TARGETS"
log "  Data dir:        $SIMTRADE_DATA_DIR"
log "  Log file:        $LOG_FILE"

cd "$SIMTRADE_DATA_DIR"

# 1. Snapshot version before download
OLD_VERSION=$(get_version "$MARKET")
log "Version before download: ${OLD_VERSION:-none}"

# 2. Run download
log "--- Running download.py ---"
if ! poetry run python scripts/download.py; then
  rc=$?
  alert "download.py failed (exit code: ${rc})"
  cleanup_logs
  exit $rc
fi

# 3. Check for new data
NEW_VERSION=$(get_version "$MARKET")
log "Version after download:  ${NEW_VERSION:-none}"

if [[ -z "$NEW_VERSION" ]]; then
  alert "No data in stocks table after download"
  cleanup_logs
  exit 1
fi

if [[ "$OLD_VERSION" == "$NEW_VERSION" ]]; then
  log "No new data (version unchanged: $NEW_VERSION). Skipping release."
  log "=== Pipeline Complete (no-op) ==="
  cleanup_logs
  exit 0
fi

log "New data detected: ${OLD_VERSION:-none} → $NEW_VERSION"

# 4. Run release pipeline (export + package + publish)
log "--- Running release_data.sh ---"
RELEASE_ARGS="--market $MARKET --publish-targets $PUBLISH_TARGETS"
if [[ "$PUBLISH_TARGETS" == "cos" || "$PUBLISH_TARGETS" == "all" ]]; then
  if [[ -n "$COS_BUCKET" ]]; then RELEASE_ARGS="$RELEASE_ARGS --cos-bucket $COS_BUCKET"; fi
  if [[ -n "$COS_REGION" ]]; then RELEASE_ARGS="$RELEASE_ARGS --cos-region $COS_REGION"; fi
  if [[ -n "$COS_KEY_PREFIX" ]]; then RELEASE_ARGS="$RELEASE_ARGS --cos-key-prefix $COS_KEY_PREFIX"; fi
fi

if ! bash scripts/release_data.sh $RELEASE_ARGS; then
  alert "release_data.sh failed"
  cleanup_logs
  exit 1
fi

# 5. Freshness gate: verify exported manifest version matches DB
MANIFEST_FILE="$SIMTRADE_DATA_DIR/data/export/$MARKET/manifest.json"
if [[ -f "$MANIFEST_FILE" ]]; then
  MANIFEST_VERSION=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE')).get('version',''))")
  if [[ "$MANIFEST_VERSION" != "$NEW_VERSION" ]]; then
    alert "Freshness FAILED: manifest=${MANIFEST_VERSION}, db=${NEW_VERSION}"
    cleanup_logs
    exit 1
  fi
  log "Freshness verified: ${MANIFEST_VERSION}"
else
  alert "Manifest missing: $MANIFEST_FILE"
  cleanup_logs
  exit 1
fi

log "=== Pipeline Complete (published $NEW_VERSION) ==="
cleanup_logs
