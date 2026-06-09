# Deploy plan

## GitHub

```powershell
cd C:\Users\Администратор\Documents\Codex\2026-06-02\files-mentioned-by-the-user-new\work\azimplant_site
git init
git add .
git commit -m "Initial Az Implant Group website"
git branch -M main
git remote add origin https://github.com/USERNAME/azimplant-site.git
git push -u origin main
```

If GitHub CLI is installed and authenticated, the repository can also be created with:

```powershell
gh repo create USERNAME/azimplant-site --private --source . --remote origin --push
```

## VPS deployment

Example Linux setup:

```bash
cd /var/www
git clone https://github.com/USERNAME/azimplant-site.git
cd azimplant-site
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export AZIMPLANT_SECRET="change-this-long-random-secret"
gunicorn -w 3 -b 127.0.0.1:8000 wsgi:application
```

Use Nginx as a reverse proxy from the domain to `127.0.0.1:8000`.

## cPanel / Passenger deployment

Upload the project folder or clone the GitHub repository.

Set Python app entrypoint:

- Application root: project folder
- Startup file: `passenger_wsgi.py`
- Application object: `application`

Install dependencies from `requirements.txt`.

## First production step

Open `/admin/login`.

- Login: `admin`
- Password: `admin123`

Change the password immediately from the admin panel.
