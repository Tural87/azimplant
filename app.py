import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("AZIMPLANT_DB_PATH", BASE_DIR / "azimplant.sqlite3"))
UPLOAD_DIR = Path(os.environ.get("AZIMPLANT_UPLOAD_DIR", BASE_DIR / "static" / "uploads"))
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("AZIMPLANT_SECRET", "change-this-secret-in-production")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def db_execute(query, params=()):
    db = get_db()
    db.execute(query, params)
    db.commit()


def db_all(query, params=()):
    return get_db().execute(query, params).fetchall()


def db_one(query, params=()):
    return get_db().execute(query, params).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def superadmin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "superadmin":
            flash("Bu əməliyyat üçün superadmin icazəsi lazımdır.", "error")
            return redirect(url_for("admin_dashboard"))
        return view(*args, **kwargs)

    return wrapped


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(field_name, current_value=""):
    file = request.files.get(field_name)
    if not file or not file.filename:
        return current_value
    if not allowed_file(file.filename):
        flash("Yalnız şəkil faylları yükləmək olar.", "error")
        return current_value
    filename = secure_filename(file.filename)
    target = UPLOAD_DIR / filename
    counter = 1
    while target.exists():
        stem, suffix = Path(filename).stem, Path(filename).suffix
        target = UPLOAD_DIR / f"{stem}-{counter}{suffix}"
        counter += 1
    file.save(target)
    return f"uploads/{target.name}"


def setting(key, default=""):
    row = db_one("select value from settings where key = ?", (key,))
    return row["value"] if row else default


@app.context_processor
def inject_globals():
    if not DB_PATH.exists():
        return {}
    keys = db_all("select key, value from settings")
    return {"site_settings": {row["key"]: row["value"] for row in keys}}


def init_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    schema = """
    create table if not exists users (
        id integer primary key autoincrement,
        username text unique not null,
        password_hash text not null,
        role text not null default 'editor'
    );
    create table if not exists settings (
        key text primary key,
        value text not null default ''
    );
    create table if not exists sections (
        id integer primary key autoincrement,
        slug text unique not null,
        title_az text not null,
        title_en text not null,
        subtitle_az text not null default '',
        subtitle_en text not null default '',
        body_az text not null default '',
        body_en text not null default '',
        image text not null default '',
        sort_order integer not null default 0,
        is_active integer not null default 1
    );
    create table if not exists cards (
        id integer primary key autoincrement,
        group_key text not null,
        icon text not null default 'sparkles',
        title_az text not null,
        title_en text not null,
        body_az text not null default '',
        body_en text not null default '',
        sort_order integer not null default 0,
        is_active integer not null default 1
    );
    create table if not exists brands (
        id integer primary key autoincrement,
        name text not null,
        description_az text not null default '',
        description_en text not null default '',
        url text not null default '',
        logo text not null default '',
        sort_order integer not null default 0,
        is_active integer not null default 1
    );
    create table if not exists inquiries (
        id integer primary key autoincrement,
        first_name text not null,
        last_name text not null,
        email text not null,
        phone text not null,
        message text not null,
        created_at text not null default current_timestamp
    );
    """
    db.executescript(schema)

    if not db.execute("select id from users where username = 'admin'").fetchone():
        db.execute(
            "insert into users (username, password_hash, role) values (?, ?, ?)",
            ("admin", generate_password_hash("admin123"), "superadmin"),
        )

    default_settings = {
        "site_name": "az implant group",
        "tagline": "dental implant solutions",
        "logo": "uploads/azimplant-logo-wide.jpeg",
        "phone": "+994 XX XXX XX XX",
        "email": "info@azimplantgroup.com",
        "address_az": "Azərbaycan, Bakı şəh., Sarayevo 12",
        "address_en": "Sarayevo 12, Baku, Azerbaijan",
        "whatsapp_number": "994XXXXXXXXX",
        "instagram_url": "",
        "facebook_url": "",
        "linkedin_url": "",
        "youtube_url": "",
        "tiktok_url": "",
        "chat_script": "",
        "seo_title_az": "Az Implant Group - Dental implant solutions",
        "seo_title_en": "Az Implant Group - Dental implant solutions",
        "seo_description_az": "Beynəlxalq sertifikatlı dental implant sistemləri, biomateriallar və peşəkar tibbi təhsil.",
        "seo_description_en": "International certified dental implant systems, biomaterials and professional medical education.",
    }
    for key, value in default_settings.items():
        db.execute("insert or ignore into settings (key, value) values (?, ?)", (key, value))

    if not db.execute("select id from sections").fetchone():
        sections = [
            (
                "hero",
                "Qlobal implantologiya həlləri Azərbaycanda",
                "Global implantology solutions in Azerbaijan",
                "Rəsmi təchizat, cərrahi təşkilat, rəqəmsal planlama və davamlı tibbi təhsil.",
                "Official supply, surgical coordination, digital planning and continuing medical education.",
                "Dünyanın aparıcı istehsalçılarının beynəlxalq sertifikatlı dental implant sistemlərini, yüksək keyfiyyətli sümük materiallarını və cərrahi komponentlərini ölkə daxilində rəsmi və fasiləsiz şəkildə təmin edirik.",
                "We provide official and continuous access to internationally certified dental implant systems, premium bone materials and surgical components from leading global manufacturers.",
                "uploads/hero-smile.jpeg",
                1,
            ),
            (
                "about",
                "Biz kimik",
                "Who we are",
                "11 illik təcrübə ilə etibarlı tibbi tərəfdaş.",
                "A trusted medical partner with 11 years of experience.",
                "Təşkilatımız artıq 11 ildir ki, Azərbaycanın stomatologiya və implantologiya sektorunda yüksək keyfiyyət standartlarının tətbiqi, innovativ tibbi texnologiyaların ölkəyə gətirilməsi, cərrahi xidmətlərin təşkili və davamlı tibbi təhsil sahəsində etibarlı tərəfdaş kimi fəaliyyət göstərir.",
                "For 11 years, our organization has acted as a reliable partner in Azerbaijan's dentistry and implantology sector by introducing high quality standards, innovative medical technologies, surgical organization and continuous medical education.",
                "uploads/azimplant-symbol.jpeg",
                2,
            ),
            (
                "mission",
                "Missiyamız və dəyərlərimiz",
                "Mission and values",
                "Şəffaflıq, tibbi etika və beynəlxalq standartlara bağlılıq.",
                "Transparency, medical ethics and commitment to international standards.",
                "Əsas məqsədimiz müasir dünya implantologiyasının ən son nailiyyətlərini yerli tibb mütəxəssisləri üçün əlçatan etmək və əhalinin qabaqcıl tibbi xidmətlərə olan tələbatını yüksək səviyyədə qarşılamaqdır.",
                "Our core mission is to make the latest achievements of modern implantology accessible to local medical professionals and to meet the demand for advanced healthcare services at a high level.",
                "",
                3,
            ),
        ]
        db.executemany(
            """
            insert into sections
            (slug, title_az, title_en, subtitle_az, subtitle_en, body_az, body_en, image, sort_order)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sections,
        )

    if not db.execute("select id from cards").fetchone():
        cards = [
            ("services", "badge-check", "Qlobal brendlərin rəsmi təchizatı", "Official supply of global brands", "Beynəlxalq sertifikatlı implant sistemləri, biomateriallar və cərrahi komponentlərin rəsmi təchizatı.", "Official supply of internationally certified implant systems, biomaterials and surgical components.", 1),
            ("services", "activity", "İmplantasiya əməliyyatlarının təşkili", "Implant surgery coordination", "Dövlət və özəl tibb mərkəzləri ilə tərəfdaşlıq çərçivəsində steril və təhlükəsiz təşkilat.", "Sterile and safe coordination through partnerships with public and private medical centers.", 2),
            ("services", "graduation-cap", "Peşəkar inkişaf və AzImplant Academy", "Professional development and AzImplant Academy", "Master-klasslar, praktiki kurslar və beynəlxalq spikerlərlə davamlı tibbi təhsil.", "Hands-on courses, masterclasses and continuing medical education with international speakers.", 3),
            ("services", "scan-line", "3D görüntüləmə və planlama", "3D imaging and planning", "Yüksək dəqiqlikli 3D görüntüləmə və fərdi cərrahi bələdçilər.", "High precision 3D imaging and individual surgical guides.", 4),
            ("why", "timer", "11 illik sektor təcrübəsi", "11 years of sector experience", "Sabit, dayanıqlı və güvənilən fəaliyyət mexanizmi.", "A stable, resilient and trusted operating model.", 1),
            ("why", "shield-check", "Yüksək akademik və texniki standartlar", "High academic and technical standards", "Kliniki əsaslandırılmış qlobal brendlər və rəqəmsal mühəndislik alətləri.", "Clinically grounded global brands and digital engineering tools.", 2),
            ("why", "handshake", "Güclü tərəfdaşlıq", "Strong partnerships", "Nüfuzlu tibb mərkəzləri və peşəkar həkim icması ilə əməkdaşlıq.", "Collaboration with respected medical centers and professional doctors.", 3),
        ]
        db.executemany(
            "insert into cards (group_key, icon, title_az, title_en, body_az, body_en, sort_order) values (?, ?, ?, ?, ?, ?, ?)",
            cards,
        )

    if not db.execute("select id from brands").fetchone():
        brands = [
            ("Macros Implant", "Yüksək keyfiyyət yanaşması ilə dental implant sistemləri.", "Dental implant systems with a strong quality approach.", "https://www.macrosimplant.com.tr/", "uploads/macros-logo.jpeg", 1),
            ("Orbone", "Türkiyənin FDA təsdiqli və EATCB üzvü olan hüceyrə və toxuma bankı.", "Turkey's FDA-approved and EATCB member cell and tissue bank.", "https://www.orbone.com.tr/en/", "uploads/orbone-logo.jpeg", 2),
            ("Maggi Biotechnology", "Rəqəmsal və biotexnoloji stomatologiya həlləri.", "Digital and biotechnology-driven dentistry solutions.", "https://en.dentalmaggi.com/", "uploads/maggi-logo.jpeg", 3),
        ]
        db.executemany(
            "insert into brands (name, description_az, description_en, url, logo, sort_order) values (?, ?, ?, ?, ?, ?)",
            brands,
        )

    db.commit()
    db.close()


def page_data(lang):
    lang = "en" if lang == "en" else "az"
    sections = {row["slug"]: row for row in db_all("select * from sections where is_active = 1 order by sort_order")}
    services = db_all("select * from cards where group_key = 'services' and is_active = 1 order by sort_order")
    why = db_all("select * from cards where group_key = 'why' and is_active = 1 order by sort_order")
    brands = db_all("select * from brands where is_active = 1 order by sort_order")
    return lang, sections, services, why, brands


@app.route("/")
def home():
    return redirect(url_for("site", lang="az"))


@app.route("/<lang>")
def site(lang):
    lang, sections, services, why, brands = page_data(lang)
    return render_template("site.html", lang=lang, sections=sections, services=services, why=why, brands=brands)


@app.route("/inquiry", methods=["POST"])
def inquiry():
    lang = request.form.get("lang", "az")
    db_execute(
        "insert into inquiries (first_name, last_name, email, phone, message) values (?, ?, ?, ?, ?)",
        (
            request.form.get("first_name", "").strip(),
            request.form.get("last_name", "").strip(),
            request.form.get("email", "").strip(),
            request.form.get("phone", "").strip(),
            request.form.get("message", "").strip(),
        ),
    )
    flash("Müraciətiniz qeydə alındı.", "success")
    return redirect(url_for("site", lang=lang) + "#contact")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = db_one("select * from users where username = ?", (request.form.get("username", ""),))
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("admin_dashboard"))
        flash("Login və ya parol yanlışdır.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    stats = {
        "sections": db_one("select count(*) count from sections")["count"],
        "brands": db_one("select count(*) count from brands")["count"],
        "inquiries": db_one("select count(*) count from inquiries")["count"],
    }
    return render_template("admin_dashboard.html", stats=stats)


@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    if request.method == "POST":
        for key in request.form:
            db_execute("insert into settings (key, value) values (?, ?) on conflict(key) do update set value = excluded.value", (key, request.form[key]))
        logo = save_upload("logo", setting("logo"))
        db_execute("insert into settings (key, value) values ('logo', ?) on conflict(key) do update set value = excluded.value", (logo,))
        flash("Sayt ayarları yeniləndi.", "success")
        return redirect(url_for("admin_settings"))
    settings = db_all("select * from settings order by key")
    return render_template("admin_settings.html", settings=settings)


@app.route("/admin/sections", methods=["GET", "POST"])
@login_required
def admin_sections():
    if request.method == "POST":
        section_id = request.form.get("id")
        image = save_upload("image", request.form.get("current_image", ""))
        values = (
            request.form.get("slug", "").strip(),
            request.form.get("title_az", "").strip(),
            request.form.get("title_en", "").strip(),
            request.form.get("subtitle_az", "").strip(),
            request.form.get("subtitle_en", "").strip(),
            request.form.get("body_az", "").strip(),
            request.form.get("body_en", "").strip(),
            image,
            int(request.form.get("sort_order", 0) or 0),
            1 if request.form.get("is_active") else 0,
        )
        if section_id:
            db_execute(
                """
                update sections set slug=?, title_az=?, title_en=?, subtitle_az=?, subtitle_en=?,
                body_az=?, body_en=?, image=?, sort_order=?, is_active=? where id=?
                """,
                values + (section_id,),
            )
        else:
            db_execute(
                """
                insert into sections
                (slug, title_az, title_en, subtitle_az, subtitle_en, body_az, body_en, image, sort_order, is_active)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
        flash("Bölmə yadda saxlanıldı.", "success")
        return redirect(url_for("admin_sections"))
    rows = db_all("select * from sections order by sort_order")
    edit = db_one("select * from sections where id = ?", (request.args.get("edit"),)) if request.args.get("edit") else None
    return render_template("admin_sections.html", rows=rows, edit=edit)


@app.route("/admin/cards", methods=["GET", "POST"])
@login_required
def admin_cards():
    if request.method == "POST":
        values = (
            request.form.get("group_key", "services"),
            request.form.get("icon", "sparkles"),
            request.form.get("title_az", ""),
            request.form.get("title_en", ""),
            request.form.get("body_az", ""),
            request.form.get("body_en", ""),
            int(request.form.get("sort_order", 0) or 0),
            1 if request.form.get("is_active") else 0,
        )
        card_id = request.form.get("id")
        if card_id:
            db_execute("update cards set group_key=?, icon=?, title_az=?, title_en=?, body_az=?, body_en=?, sort_order=?, is_active=? where id=?", values + (card_id,))
        else:
            db_execute("insert into cards (group_key, icon, title_az, title_en, body_az, body_en, sort_order, is_active) values (?, ?, ?, ?, ?, ?, ?, ?)", values)
        flash("Kart yadda saxlanıldı.", "success")
        return redirect(url_for("admin_cards"))
    rows = db_all("select * from cards order by group_key, sort_order")
    edit = db_one("select * from cards where id = ?", (request.args.get("edit"),)) if request.args.get("edit") else None
    return render_template("admin_cards.html", rows=rows, edit=edit)


@app.route("/admin/brands", methods=["GET", "POST"])
@login_required
def admin_brands():
    if request.method == "POST":
        logo = save_upload("logo", request.form.get("current_logo", ""))
        values = (
            request.form.get("name", ""),
            request.form.get("description_az", ""),
            request.form.get("description_en", ""),
            request.form.get("url", ""),
            logo,
            int(request.form.get("sort_order", 0) or 0),
            1 if request.form.get("is_active") else 0,
        )
        brand_id = request.form.get("id")
        if brand_id:
            db_execute("update brands set name=?, description_az=?, description_en=?, url=?, logo=?, sort_order=?, is_active=? where id=?", values + (brand_id,))
        else:
            db_execute("insert into brands (name, description_az, description_en, url, logo, sort_order, is_active) values (?, ?, ?, ?, ?, ?, ?)", values)
        flash("Brend yadda saxlanıldı.", "success")
        return redirect(url_for("admin_brands"))
    rows = db_all("select * from brands order by sort_order")
    edit = db_one("select * from brands where id = ?", (request.args.get("edit"),)) if request.args.get("edit") else None
    return render_template("admin_brands.html", rows=rows, edit=edit)


@app.route("/admin/inquiries")
@login_required
def admin_inquiries():
    rows = db_all("select * from inquiries order by created_at desc")
    return render_template("admin_inquiries.html", rows=rows)


@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def admin_password():
    if request.method == "POST":
        user = db_one("select * from users where id = ?", (session["user_id"],))
        if not check_password_hash(user["password_hash"], request.form.get("current_password", "")):
            flash("Cari parol yanlışdır.", "error")
        elif request.form.get("new_password") != request.form.get("confirm_password"):
            flash("Yeni parollar eyni deyil.", "error")
        elif len(request.form.get("new_password", "")) < 6:
            flash("Yeni parol ən az 6 simvol olmalıdır.", "error")
        else:
            db_execute("update users set password_hash = ? where id = ?", (generate_password_hash(request.form["new_password"]), session["user_id"]))
            flash("Parol dəyişdirildi.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_password.html")


@app.route("/admin/users", methods=["GET", "POST"])
@login_required
@superadmin_required
def admin_users():
    if request.method == "POST":
        db_execute(
            "insert into users (username, password_hash, role) values (?, ?, ?)",
            (request.form.get("username", "").strip(), generate_password_hash(request.form.get("password", "admin123")), request.form.get("role", "editor")),
        )
        flash("İstifadəçi yaradıldı.", "success")
        return redirect(url_for("admin_users"))
    rows = db_all("select id, username, role from users order by id")
    return render_template("admin_users.html", rows=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="127.0.0.1", port=5000)
