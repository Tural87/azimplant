# Az Implant Group website

Corporate AZ/EN website with Flask, SQLite and an editable admin panel.

## Run

```powershell
cd C:\Users\Администратор\Documents\Codex\2026-06-02\files-mentioned-by-the-user-new\work\azimplant_site
python run_server.py
```

Public site:

- http://127.0.0.1:5000/az
- http://127.0.0.1:5000/en

Admin:

- http://127.0.0.1:5000/admin/login
- Initial login: `admin`
- Initial password: `admin123`

Change the password from the admin panel before production use.

## Production

Deployment notes are in `DEPLOY.md`.

Production entrypoints:

- VPS / Gunicorn: `wsgi:application`
- cPanel / Passenger: `passenger_wsgi.py`

Important environment variables:

- `AZIMPLANT_SECRET`
- `AZIMPLANT_DB_PATH`
- `AZIMPLANT_UPLOAD_DIR`

## Editable areas

- Site settings, contact data, WhatsApp number, social links and chat script
- AZ/EN page sections
- Activity and "Why us" cards
- Brand cards and logos
- Admin password and superadmin-created users
- Incoming contact form submissions
