require('dotenv').config();
const express = require('express');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const multer = require('multer');
const nodemailer = require('nodemailer');
const path = require('path');
const fs = require('fs');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use('/public', express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(path.join(__dirname, 'public', 'uploads')));

app.use(session({
  secret: process.env.SESSION_SECRET || 'fallback_secret',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 1000 * 60 * 60 * 4 }
}));

// ---------- Multer (image upload) ----------
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, path.join(__dirname, 'public', 'uploads')),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, file.fieldname + '-' + Date.now() + ext);
  }
});
const upload = multer({ storage });

// ---------- Mailer ----------
function getTransporter() {
  const s = db.getSettings().smtp;
  return nodemailer.createTransport({
    host: s.host,
    port: Number(s.port) || 587,
    secure: false,
    auth: { user: s.user, pass: s.pass }
  });
}

// ---------- Auth middleware ----------
function requireAuth(req, res, next) {
  if (req.session && req.session.isAdmin) return next();
  return res.redirect('/admin/login');
}

// =================== PUBLIC SITE ===================
app.get('/', (req, res) => {
  const content = db.getContent();
  res.render('index', { content, sent: req.query.sent === '1' });
});

app.post('/contact', async (req, res) => {
  const { ad, soyad, email, tel, mesaj } = req.body;
  db.addMessage({ ad, soyad, email, tel, mesaj });

  try {
    const s = db.getSettings().smtp;
    if (s.user && s.pass) {
      const transporter = getTransporter();
      await transporter.sendMail({
        from: `"Az Implant Group Sayt" <${s.user}>`,
        to: s.mailTo,
        subject: `Yeni müraciət: ${ad} ${soyad}`,
        text: `Ad: ${ad}\nSoyad: ${soyad}\nEmail: ${email}\nTel: ${tel}\n\nMətn:\n${mesaj}`
      });
    }
  } catch (e) {
    console.error('Mail göndərilmədi:', e.message);
  }

  res.redirect('/?sent=1#contact');
});

// =================== ADMIN: AUTH ===================
app.get('/admin/login', (req, res) => {
  res.render('admin/login', { error: null });
});

app.post('/admin/login', (req, res) => {
  const { username, password } = req.body;
  const ok = username === process.env.ADMIN_USER &&
    bcrypt.compareSync(password, process.env.ADMIN_PASS_HASH || '');
  if (ok) {
    req.session.isAdmin = true;
    return res.redirect('/admin');
  }
  res.render('admin/login', { error: 'İstifadəçi adı və ya parol səhvdir.' });
});

app.get('/admin/logout', (req, res) => {
  req.session.destroy(() => res.redirect('/admin/login'));
});

// =================== ADMIN: DASHBOARD ===================
app.get('/admin', requireAuth, (req, res) => {
  const content = db.getContent();
  const messages = db.getMessages();
  const settings = db.getSettings();
  res.render('admin/dashboard', { content, messages, settings, saved: req.query.saved });
});

// Update general site/hero/about content
app.post('/admin/content', requireAuth, upload.fields([
  { name: 'heroImage', maxCount: 1 },
  { name: 'aboutBg', maxCount: 1 }
]), (req, res) => {
  const content = db.getContent();
  const b = req.body;

  content.site.title = b.siteTitle;
  content.site.phone = b.sitePhone;
  content.site.email = b.siteEmail;
  content.site.instagram = b.siteInstagram;
  content.site.footer = b.siteFooter;

  content.hero.title = b.heroTitle;
  content.hero.subtitle = b.heroSubtitle;
  if (req.files.heroImage) content.hero.image = '/uploads/' + req.files.heroImage[0].filename;

  content.about.whoTitle = b.whoTitle;
  content.about.whoText = b.whoText;
  content.about.whyTitle = b.whyTitle;
  content.about.whyItems = (b.whyItems || '').split('\n').filter(x => x.trim());
  content.about.missionTitle = b.missionTitle;
  content.about.missionText = b.missionText;
  if (req.files.aboutBg) content.about.background = '/uploads/' + req.files.aboutBg[0].filename;

  db.saveContent(content);
  res.redirect('/admin?saved=1');
});

// Update services (5 cards)
app.post('/admin/services', requireAuth, (req, res) => {
  const content = db.getContent();
  const titles = [].concat(req.body.serviceTitle || []);
  const texts = [].concat(req.body.serviceText || []);
  const icons = [].concat(req.body.serviceIcon || []);
  content.services = titles.map((t, i) => ({
    icon: icons[i] || 'tooth',
    title: t,
    text: texts[i] || ''
  }));
  db.saveContent(content);
  res.redirect('/admin?saved=1');
});

// Update partner logos
app.post('/admin/partners', requireAuth, upload.array('partnerImage', 10), (req, res) => {
  const content = db.getContent();
  const names = [].concat(req.body.partnerName || []);
  const urls = [].concat(req.body.partnerUrl || []);
  const existing = [].concat(req.body.partnerExisting || []);

  let fileIdx = 0;
  content.partners = names.map((name, i) => {
    const wantsNewFile = req.body.partnerNewFlag && [].concat(req.body.partnerNewFlag)[i] === '1';
    let image = existing[i];
    if (wantsNewFile && req.files[fileIdx]) {
      image = '/uploads/' + req.files[fileIdx].filename;
      fileIdx++;
    }
    return { name, image, url: urls[i] || '' };
  });

  db.saveContent(content);
  res.redirect('/admin?saved=1');
});

app.post('/admin/partners/add', requireAuth, upload.single('newPartnerImage'), (req, res) => {
  const content = db.getContent();
  content.partners.push({
    name: req.body.newPartnerName || 'Yeni Tərəfdaş',
    url: req.body.newPartnerUrl || '',
    image: req.file ? '/uploads/' + req.file.filename : '/uploads/placeholder.png'
  });
  db.saveContent(content);
  res.redirect('/admin?saved=1');
});

app.post('/admin/partners/delete/:idx', requireAuth, (req, res) => {
  const content = db.getContent();
  content.partners.splice(Number(req.params.idx), 1);
  db.saveContent(content);
  res.redirect('/admin?saved=1');
});

// Delete a contact message
app.post('/admin/messages/delete/:id', requireAuth, (req, res) => {
  db.deleteMessage(req.params.id);
  res.redirect('/admin?saved=1');
});

// Update SMTP/email settings
app.post('/admin/settings', requireAuth, (req, res) => {
  const settings = db.getSettings();
  settings.smtp = {
    host: req.body.smtpHost,
    port: Number(req.body.smtpPort) || 587,
    user: req.body.smtpUser,
    pass: req.body.smtpPass,
    mailTo: req.body.mailTo
  };
  db.saveSettings(settings);
  res.redirect('/admin?saved=1');
});

// Change admin password (writes new hash into .env at runtime note)
app.post('/admin/change-password', requireAuth, (req, res) => {
  const { newPassword } = req.body;
  if (!newPassword || newPassword.length < 4) return res.redirect('/admin?saved=0');
  const hash = bcrypt.hashSync(newPassword, 10);
  const envPath = path.join(__dirname, '.env');
  let envContent = fs.readFileSync(envPath, 'utf-8');
  envContent = envContent.replace(/ADMIN_PASS_HASH=.*/g, 'ADMIN_PASS_HASH=' + hash);
  fs.writeFileSync(envPath, envContent);
  process.env.ADMIN_PASS_HASH = hash;
  res.redirect('/admin?saved=1');
});

app.listen(PORT, () => {
  console.log(`Az Implant Group sayti http://localhost:${PORT} ünvanında işləyir`);
  console.log(`Admin panel: http://localhost:${PORT}/admin (default: admin / admin123)`);
});
