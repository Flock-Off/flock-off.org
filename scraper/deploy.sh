#!/usr/bin/env bash
# deploy.sh — Run once on the DigitalOcean droplet to install and schedule the scraper.
# Usage: ssh root@206.81.14.95 'bash -s' < deploy.sh
set -euo pipefail

INSTALL_DIR="/opt/flock-off-scraper"
LOG_FILE="/var/log/flock-off-scraper.log"
PYTHON="python3"

echo "=== Installing system deps ==="
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git

echo "=== Cloning / updating repo ==="
if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  git clone https://github.com/Flock-Off/flock-off.org.git "$INSTALL_DIR"
fi

SCRAPER_DIR="$INSTALL_DIR/scraper"

echo "=== Creating virtualenv ==="
$PYTHON -m venv "$SCRAPER_DIR/.venv"
source "$SCRAPER_DIR/.venv/bin/activate"

echo "=== Installing Python deps ==="
pip install -q --upgrade pip
pip install -q -r "$SCRAPER_DIR/requirements.txt"

echo "=== Installing Playwright browsers (optional — failures are non-fatal) ==="
playwright install chromium || echo "  ⚠  Playwright browser install failed — skipping (not needed for Legistar/CivicPlus)"
playwright install-deps chromium || echo "  ⚠  Playwright deps install failed — skipping"

echo "=== Checking .env ==="
if [ ! -f "$SCRAPER_DIR/.env" ]; then
  cp "$SCRAPER_DIR/.env.example" "$SCRAPER_DIR/.env"
  echo ""
  echo "  ⚠  Edit $SCRAPER_DIR/.env and set SUPABASE_SERVICE_KEY, then re-run this script"
  echo "     or manually add the cron job below."
  echo ""
else
  echo "  .env found — skipping copy"
fi

echo "=== Seeding municipalities ==="
cd "$SCRAPER_DIR"
$PYTHON seed_municipalities.py

echo "=== Installing cron job (every 2 days at 06:00 UTC) ==="
CRON_LINE="0 6 */2 * * cd $SCRAPER_DIR && .venv/bin/python main.py >> $LOG_FILE 2>&1"
# Replace any existing scraper entry so re-runs always update the schedule
( crontab -l 2>/dev/null | grep -vF "$SCRAPER_DIR/main.py"; echo "$CRON_LINE" ) | crontab -

echo ""
echo "=== Deploy complete ==="
echo "  Scraper dir : $SCRAPER_DIR"
echo "  Logs        : $LOG_FILE"
echo "  Schedule    : every 2 days at 06:00 UTC"
echo ""
echo "  To run now  : cd $SCRAPER_DIR && .venv/bin/python main.py"
