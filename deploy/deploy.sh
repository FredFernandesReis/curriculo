#!/usr/bin/env bash
# Atualiza o app na VPS (rode dentro de /var/www/curriculopro)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Ativando venv"
source venv/bin/activate

echo "==> Dependências"
pip install -r requirements.txt

echo "==> Migrações"
python manage.py migrate --noinput

echo "==> Arquivos estáticos"
python manage.py collectstatic --noinput

echo "==> Reiniciando Gunicorn"
sudo systemctl restart curriculopro

echo "==> OK — app atualizado"
sudo systemctl status curriculopro --no-pager
