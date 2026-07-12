# Publicar Currículo PRO na VPS Hostinger

**Servidor:** `69.62.114.134` (`srv1824562.hstgr.cloud`)  
**Domínio:** `curriculo.store`

## 1. DNS (painel Hostinger do domínio)

| Tipo | Nome | Valor           |
|------|------|-----------------|
| A    | `@`  | `69.62.114.134` |
| A    | `www`| `69.62.114.134` |

Salve e aguarde propagar (minutos a algumas horas).

---

## 2. Conectar na VPS

No PowerShell:

```powershell
ssh root@69.62.114.134
```

(Se pedir senha, use a do painel Hostinger → VPS → SSH.)

---

## 3. Instalar pacotes

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip nginx git certbot python3-certbot-nginx
```

---

## 4. Enviar o projeto

Na VPS, crie a pasta:

```bash
mkdir -p /var/www
```

No PowerShell do seu PC:

```powershell
cd "c:\Users\Frede\OneDrive\Área de Trabalho\Curriculo PRO"
scp -r . root@69.62.114.134:/var/www/curriculopro
```

---

## 5. Configurar na VPS

```bash
cd /var/www/curriculopro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
nano .env
```

Cole a chave gerada em `SECRET_KEY=...`. O domínio já está configurado.

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

mkdir -p media staticfiles
chown -R www-data:www-data /var/www/curriculopro
chmod -R 755 /var/www/curriculopro
```

---

## 6. Gunicorn

```bash
cp deploy/gunicorn.service /etc/systemd/system/curriculopro.service
systemctl daemon-reload
systemctl enable curriculopro
systemctl start curriculopro
systemctl status curriculopro
```

---

## 7. Nginx

```bash
cp deploy/nginx.conf /etc/nginx/sites-available/curriculopro
ln -sf /etc/nginx/sites-available/curriculopro /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

---

## 8. HTTPS (SSL)

```bash
certbot --nginx -d curriculo.store -d www.curriculo.store
```

---

## 9. Pronto — acesse

- Site: https://curriculo.store
- Painel: https://curriculo.store/painel/
- Admin: https://curriculo.store/admin/
- Parceiro: https://curriculo.store/parceiro/login/

---

## Atualizar depois

```bash
cd /var/www/curriculopro
bash deploy/deploy.sh
```
