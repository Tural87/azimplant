# Linux server commands

These commands assume Ubuntu/Debian and deploy the project to `/var/www/azimplant`.

Replace:

- `azimplantgroup.com` with the real domain
- `www.azimplantgroup.com` with the real www domain if used
- `change-this-long-random-secret` with a strong random value

## 1. Install packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx
```

## 2. Clone project

```bash
sudo mkdir -p /var/www
sudo git clone https://github.com/Tural87/azimplant.git /var/www/azimplant
sudo chown -R $USER:www-data /var/www/azimplant
cd /var/www/azimplant
```

## 3. Python environment

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Environment file

```bash
cat > .env <<'EOF'
AZIMPLANT_SECRET=change-this-long-random-secret
AZIMPLANT_DB_PATH=/var/www/azimplant/instance/azimplant.sqlite3
AZIMPLANT_UPLOAD_DIR=/var/www/azimplant/static/uploads
EOF

mkdir -p instance static/uploads
sudo chown -R www-data:www-data instance static/uploads
```

## 5. Test app manually

```bash
. .venv/bin/activate
gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:application
```

Open another terminal and run:

```bash
curl -I http://127.0.0.1:8000/az
```

Stop the manual Gunicorn process with `Ctrl+C`.

## 6. systemd service

```bash
sudo cp deploy/azimplant.service /etc/systemd/system/azimplant.service
sudo systemctl daemon-reload
sudo systemctl enable azimplant
sudo systemctl start azimplant
sudo systemctl status azimplant
```

## 7. Nginx

Edit `deploy/nginx-azimplant.conf` and set the real domain.

```bash
sudo cp deploy/nginx-azimplant.conf /etc/nginx/sites-available/azimplant
sudo ln -s /etc/nginx/sites-available/azimplant /etc/nginx/sites-enabled/azimplant
sudo nginx -t
sudo systemctl reload nginx
```

## 8. HTTPS

After the domain DNS points to the server:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d azimplantgroup.com -d www.azimplantgroup.com
```

## 9. Update after new GitHub changes

```bash
cd /var/www/azimplant
sudo git pull
. .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart azimplant
```
