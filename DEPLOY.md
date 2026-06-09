# Deploy plan

Repository:

- https://github.com/Tural87/azimplant

## Linux server

Use the files in `deploy/`.

- `deploy/server-commands.md`: step-by-step Ubuntu/Debian deployment commands
- `deploy/azimplant.service`: systemd service for Gunicorn
- `deploy/nginx-azimplant.conf`: Nginx reverse proxy template

Default production path:

- `/var/www/azimplant`

Default app port behind Nginx:

- `127.0.0.1:8000`

## Required production variables

- `AZIMPLANT_SECRET`
- `AZIMPLANT_DB_PATH`
- `AZIMPLANT_UPLOAD_DIR`

## First production step

Open `/admin/login`.

- Login: `admin`
- Password: `admin123`

Change the password immediately from the admin panel.
