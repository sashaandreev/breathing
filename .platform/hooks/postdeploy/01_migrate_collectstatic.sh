#!/bin/bash
set -euo pipefail
set -x
cd /var/app/current
source /var/app/venv/*/bin/activate
if [ "" = "1" ]; then python manage.py migrate --noinput; fi
if [ "" = "1" ]; then python manage.py collectstatic --noinput; fi
