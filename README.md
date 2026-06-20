# Az Implant Group — Sayt + Admin Panel

## Quraşdırma
```
npm install
cp .env.example .env
node scripts/hash-password.js sizinParolunuz
```
Çıxan `ADMIN_PASS_HASH` sətrini `.env` faylına yapışdırın.

## İşə salma
```
node server.js
```
- Sayt: http://localhost:3000
- Admin panel: http://localhost:3000/admin (default: `admin` / `admin123` — MÜTLƏQ DƏYİŞİN!)

## .env ayarları
- `SMTP_HOST/PORT/USER/PASS` — əlaqə formu mesajlarının e-poçtla göndərilməsi üçün (Gmail üçün "App Password" istifadə edin)
- `MAIL_TO` — mesajların göndəriləcəyi email ünvanı
- `ADMIN_USER` / `ADMIN_PASS_HASH` — admin giriş məlumatları

## Struktur
```
server.js          → Express server, bütün route-lar
db.js               → JSON-fayl əsaslı sadə "DB"
data/content.json   → bütün sayt mətnləri/şəkil yolları (admin paneldən idarə olunur)
data/messages.json  → əlaqə formundan gələn müraciətlər
views/               → EJS şablonları (sayt + admin)
public/              → CSS, JS, yüklənmiş şəkillər
scripts/hash-password.js → admin parolu üçün bcrypt hash generator
```

## Serverdə daimi işə salma (tövsiyə)
```
npm install -g pm2
pm2 start server.js --name azimplant
pm2 save
pm2 startup
```

## GitHub-a yükləmə
`.env` faylı `.gitignore`-dadır — repoya düşmür. Serverə köçürəndə `.env.example`-dən `.env` yaradıb öz məlumatlarınızı yazın.
