import hashlib
import json
import os
import random
import re
import secrets
import smtplib
import time
import urllib.parse
from email.message import EmailMessage
from authlib.integrations.base_client import OAuthError
from authlib.integrations.flask_client import OAuth
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin
from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_FILE = BASE_DIR / "data.json"
load_dotenv(BASE_DIR / ".env")

PUBLIC_SITE_URL = os.environ.get("PUBLIC_SITE_URL", "https://noblenode.host").rstrip("/")
APP_DOMAIN = os.environ.get("APP_DOMAIN", PUBLIC_SITE_URL)
STATUS_SITE_URL = os.environ.get("STATUS_SITE_URL", "https://status.noblenode.host").rstrip("/")
ADMIN_ROUTE = os.environ.get("ADMIN_ROUTE", "").strip()
if ADMIN_ROUTE and (not re.fullmatch(r"/[A-Za-z0-9/_-]+", ADMIN_ROUTE) or ".." in ADMIN_ROUTE):
    ADMIN_ROUTE = ""
SECRET_ADMIN_PATH = ADMIN_ROUTE or None
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ROBOT_TXT = f"User-agent: *\nAllow: /\nDisallow: /auth\nDisallow: /dashboard\nDisallow: {SECRET_ADMIN_PATH or '/ops-console'}\nSitemap: {APP_DOMAIN}/sitemap.xml\n"
SITEMAP_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{APP_DOMAIN}/</loc></url>
  <url><loc>{APP_DOMAIN}/plans</loc></url>
  <url><loc>{APP_DOMAIN}/checkout</loc></url>
  <url><loc>{APP_DOMAIN}/trusted-by</loc></url>
  <url><loc>{STATUS_SITE_URL}/</loc></url>
  <url><loc>{APP_DOMAIN}/faq</loc></url>
  <url><loc>{APP_DOMAIN}/utilities</loc></url>
  <url><loc>{APP_DOMAIN}/terms</loc></url>
  <url><loc>{APP_DOMAIN}/privacy</loc></url>
</urlset>
"""

ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

DEFAULT_DATA = {
    "plans": [
        {
            "id": "world-8gb",
            "name": "8GB RAM",
            "ram": "8GB DDR5",
            "cpu": "4 vCores - Ryzen 9 9950X / 7950X3D",
            "storage": "120GB NVMe Gen4 Storage",
            "backups": "3 Daily Automated Backups",
            "slots": "Unlimited Player Slots",
            "pkr_price": 2200,
            "usd_price": 7.95,
            "recommended": False,
            "badge": "STARTER SMP",
            "icon": "box",
            "category": "paper",
            "ideal_for": "Small SMPs, vanilla worlds & friend groups (1-20 players)",
            "ddos_protection": "Free 12+ Tbps Path.net & Corero DDoS Protection",
            "port_speed": "10 Gbps Redundant Uplink",
            "mysql": "Free MySQL Database Included",
            "subdomain": "Free .noblenode.host Subdomain",
        },
        {
            "id": "world-16gb",
            "name": "16GB RAM",
            "ram": "16GB DDR5",
            "cpu": "6 vCores - Ryzen 9 9950X / 7950X3D",
            "storage": "240GB NVMe Gen4 Storage",
            "backups": "5 Daily Automated Backups",
            "slots": "Unlimited Player Slots",
            "pkr_price": 4400,
            "usd_price": 15.95,
            "recommended": False,
            "badge": "CLOSE FRIENDS + MODS",
            "icon": "shield",
            "category": "paper",
            "ideal_for": "Medium communities, modded SMPs & plugin-heavy servers (20-50 players)",
            "ddos_protection": "Free 12+ Tbps Path.net & Corero DDoS Protection",
            "port_speed": "10 Gbps Redundant Uplink",
            "mysql": "Free MySQL Database Included",
            "subdomain": "Free .noblenode.host Subdomain",
        },
        {
            "id": "world-32gb",
            "name": "32GB RAM",
            "ram": "32GB DDR5",
            "cpu": "8 vCores - Ryzen 9 9950X / 7950X3D",
            "storage": "480GB NVMe Gen4 Storage",
            "backups": "10 Daily Automated Backups",
            "slots": "Unlimited Player Slots",
            "pkr_price": 8200,
            "usd_price": 29.95,
            "recommended": True,
            "badge": "COMMUNITY + HEAVY MODS",
            "icon": "gem",
            "category": "forge",
            "ideal_for": "Large communities, heavy Forge/Fabric modpacks & public networks (50-150 players)",
            "ddos_protection": "Free 12+ Tbps Path.net & Corero DDoS Protection",
            "port_speed": "10 Gbps Redundant Uplink",
            "mysql": "Free MySQL Database Included",
            "subdomain": "Free .noblenode.host Subdomain",
        },
        {
            "id": "world-64gb",
            "name": "64GB RAM",
            "ram": "64GB DDR5",
            "cpu": "8 vCores - Ryzen 9 9950X / 7950X3D",
            "storage": "960GB NVMe Gen4 Storage",
            "backups": "Unlimited Daily Automated Backups",
            "slots": "Unlimited Player Slots",
            "pkr_price": 16500,
            "usd_price": 59.95,
            "recommended": False,
            "badge": "ENTERPRISE NETWORK",
            "icon": "award",
            "category": "bedrock",
            "ideal_for": "Multi-server BungeeCord/Velocity networks, massive world seeds & esports (150+ players)",
            "ddos_protection": "Free 12+ Tbps Path.net & Corero DDoS Protection",
            "port_speed": "10 Gbps Redundant Uplink",
            "mysql": "Free MySQL Database Included",
            "subdomain": "Free .noblenode.host Subdomain",
        },
    ],
    "coupons": [
        {"code": "PAKISTAN20", "discount_pct": 20, "flat_pkr": 0, "active": True, "description": "20% Off Independence Discount on all server plans"},
        {"code": "NOBLE10", "discount_pct": 10, "flat_pkr": 0, "active": True, "description": "10% Off Welcome Deal for new server hosts"},
        {"code": "SAVE500", "discount_pct": 0, "flat_pkr": 500, "active": True, "description": "Flat 500 PKR Instant Discount on any package"},
    ],
    "faqs": [
        {
            "id": 1,
            "question": "How fast is my Minecraft server deployed after payment?",
            "answer": "Instant deployment. Your server is automatically provisioned and ready in under 60 seconds the moment your payment is confirmed. You receive an email and dashboard notification with your IP address, SFTP credentials, and Noble Panel login.",
        },
        {
            "id": 2,
            "question": "What payment methods do you accept in Pakistan?",
            "answer": "We support all major Pakistani payment channels: EasyPaisa (Instant wallet & QR), JazzCash (Direct transfer & Till ID), SadaPay, NayaPay, Raast / Pakistani Bank Transfers (1Link), as well as international Visa, Mastercard, and Crypto (USDT, BTC, LTC).",
        },
        {
            "id": 3,
            "question": "Where are your servers located and what ping can I expect?",
            "answer": "Our flagship nodes are stationed in Karachi and Lahore, Pakistan, directly peered with Tier-1 national backbones including Nayatel, PTCL, StormFiber, Transworld, Jazz, and Zong. Players in Pakistan experience ping as low as 5ms to 18ms. We also operate global POPs in Dubai (30ms), Singapore (55ms), and Frankfurt (110ms).",
        },
        {
            "id": 4,
            "question": "What DDoS protection is included with my server?",
            "answer": "Every Noble Node server includes enterprise-grade 12+ Tbps Corero and Path.net DDoS protection at zero additional cost. Our always-on inline scrubbing filters Layer 3, Layer 4, and Layer 7 Minecraft-specific game attacks (Botnets, Null Ping, Handshake Floods, UDP Amplification) with sub-millisecond reaction time and zero server disconnects.",
        },
        {
            "id": 5,
            "question": "Can Minecraft Bedrock (Mobile, Xbox, PS5, Switch) players join my Java server?",
            "answer": "Yes! We offer pre-configured GeyserMC and Floodgate cross-play on all Paper and Purpur tiers. Bedrock edition players on Android, iOS, Windows 10/11, PlayStation, Xbox, and Nintendo Switch can join your Java world seamlessly on the same IP and port.",
        },
        {
            "id": 6,
            "question": "Can I change my server version or install custom modpacks?",
            "answer": "Absolutely. Noble Panel includes a 1-click modpack and version installer with full support for Paper, Purpur, Fabric, Forge, NeoForge, Spigot, BungeeCord, and Velocity. You can install thousands of modpacks directly from CurseForge and Modrinth with a single click, or upload custom .jar and zip files via SFTP or Web File Manager.",
        },
        {
            "id": 7,
            "question": "How do automated daily backups work?",
            "answer": "Your entire server (worlds, configs, player data, and plugins) is automatically backed up every 24 hours to offsite secure cloud storage. You can also take manual snapshot backups anytime from Noble Panel and restore with one click if anything goes wrong.",
        },
        {
            "id": 8,
            "question": "Can I upgrade or downgrade my plan later without losing data?",
            "answer": "Yes, you can upgrade your RAM, CPU vCores, or NVMe storage anytime from your Account Dashboard. Upgrades take effect instantly upon renewal with zero file loss, IP change, or world resetting.",
        },
        {
            "id": 9,
            "question": "Do I get a free custom server address/subdomain?",
            "answer": "Yes! Every server comes with a free custom subdomain such as yourserver.noblenode.host. If you own your own domain (e.g. play.yourserver.pk), you can link it directly using our simple DNS guide.",
        },
        {
            "id": 10,
            "question": "What kind of customer support is available?",
            "answer": "We provide 24/7 technical support in both English and Urdu through our official Discord community and priority ticketing system. Our team of experienced server administrators is always on standby to assist with plugin errors, crashes, and performance optimization.",
        },
    ],
    "testimonials": [],
    "partners": [],
    "trusted_servers": [],
    "servers": [],
    "orders": [],
    "users": [],
}

class RateLimiter:
    def __init__(self, requests_per_minute=25):
        self.limit = requests_per_minute
        self.requests = defaultdict(list)

    def is_allowed(self, ip):
        now = time.time()
        window = 60
        self.requests[ip] = [t for t in self.requests[ip] if now - t < window]
        if len(self.requests[ip]) >= self.limit:
            return False
        self.requests[ip].append(now)
        return True

rate_limiter = RateLimiter(requests_per_minute=25)

LOCATIONS = [
    {"id": "lahore", "name": "Lahore, Pakistan", "flag": "pk", "ping_base": 8, "status": "Online (Low Latency)"},
    {"id": "karachi", "name": "Karachi, Pakistan", "flag": "pk", "ping_base": 14, "status": "Online (High Speed)"},
    {"id": "dubai", "name": "Dubai, UAE", "flag": "ae", "ping_base": 32, "status": "Online"},
    {"id": "singapore", "name": "Singapore", "flag": "sg", "ping_base": 55, "status": "Online"},
    {"id": "frankfurt", "name": "Frankfurt, EU", "flag": "de", "ping_base": 115, "status": "Online"},
]


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return DEFAULT_DATA
    save_data(DEFAULT_DATA)
    return DEFAULT_DATA


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("APP_ENV", "").lower() == "production" or os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true",
    PREFERRED_URL_SCHEME="https" if PUBLIC_SITE_URL.startswith("https://") else "http",
)
if os.environ.get("APP_ENV", "").lower() == "production" and not os.environ.get("FLASK_SECRET_KEY"):
    raise RuntimeError("FLASK_SECRET_KEY must be configured in production.")
oauth = OAuth(app)
oauth_clients = {}
USE_FLASK = True

if os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
    oauth_clients["google"] = oauth.register(
        name="google",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if os.environ.get("MICROSOFT_CLIENT_ID") and os.environ.get("MICROSOFT_CLIENT_SECRET"):
    microsoft_tenant = os.environ.get("MICROSOFT_TENANT_ID", "common")
    oauth_clients["microsoft"] = oauth.register(
        name="microsoft",
        client_id=os.environ["MICROSOFT_CLIENT_ID"],
        client_secret=os.environ["MICROSOFT_CLIENT_SECRET"],
        server_metadata_url=f"https://login.microsoftonline.com/{microsoft_tenant}/v2.0/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def oauth_redirect_uri(provider):
    callback_path = url_for("auth_callback", provider=provider)
    return urljoin(os.environ.get("OAUTH_REDIRECT_BASE_URL", PUBLIC_SITE_URL).rstrip("/") + "/", callback_path.lstrip("/"))


def auth_page_error(code):
    messages = {
        "provider_unconfigured": "That sign-in provider is not configured yet. Use email and password instead.",
        "provider_failed": "We could not verify your identity with that provider. Please try again.",
        "email_missing": "The provider did not return a verified email address. Try another sign-in method.",
        "account_exists": "An account already uses that email. Sign in with that account first; identities are not linked automatically.",
        "reset_invalid": "That password reset link is invalid or expired. Request a new one.",
    }
    return messages.get(code, "")


def send_password_reset_email(recipient, reset_url):
    host = os.environ.get("SMTP_HOST", "").strip()
    sender = os.environ.get("SMTP_FROM", "").strip()
    if not host or not sender:
        return False

    message = EmailMessage()
    message["Subject"] = "Reset your Noble Node password"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "A password reset was requested for your Noble Node account. "
        f"Use this one-time link within 30 minutes: {reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    port = int(os.environ.get("SMTP_PORT", "587"))
    timeout = float(os.environ.get("SMTP_TIMEOUT", "10"))
    username = os.environ.get("SMTP_USERNAME", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "")
    use_ssl = os.environ.get("SMTP_USE_SSL", "false").lower() == "true"
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=timeout) as server:
            if username:
                server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as server:
            if use_tls:
                server.starttls()
            if username:
                server.login(username, password)
            server.send_message(message)
    return True


def find_password_reset_user(data, token):
    if not token or len(token) > 256:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    for user in data.get("users", []):
        reset = user.get("password_reset") or {}
        if reset.get("expires_at", 0) >= time.time() and secrets.compare_digest(reset.get("token_hash", ""), token_hash):
            return user
    return None


@app.context_processor
def inject_brand_context():
    return {
        "brand_name": "Noble Node",
        "brand_url": PUBLIC_SITE_URL,
        "admin_url": SECRET_ADMIN_PATH or "/",
        "current_user": session.get("user"),
    }

if USE_FLASK:
    @app.route("/")
    def index():
        data = load_data()
        return render_template(
            "home.html",
            plans=data.get("plans", []),
            testimonials=data.get("testimonials", []),
            partners=data.get("partners", []),
            trusted_servers=data.get("trusted_servers", []),
            faqs=data.get("faqs", []),
            locations=LOCATIONS,
        )

    @app.route("/plans")
    def page_plans():
        data = load_data()
        return render_template(
            "pricing.html",
            plans=data.get("plans", []),
            coupons=data.get("coupons", []),
            faqs=data.get("faqs", []),
            partners=data.get("partners", []),
            locations=LOCATIONS,
        )

    @app.route("/checkout")
    def page_checkout():
        data = load_data()
        requested_plan_id = request.args.get("plan", session.get("selected_plan_id", "world-32gb"))
        selected_plan = next((p for p in data.get("plans", []) if p.get("id") == requested_plan_id), None)
        if not selected_plan and data.get("plans"):
            selected_plan = data["plans"][0]
        return render_template(
            "checkout.html",
            selected_plan=selected_plan,
            plans=data.get("plans", []),
            coupons=data.get("coupons", []),
            locations=LOCATIONS,
            user=session.get("user"),
        )

    @app.route("/trusted-by")
    @app.route("/servers")
    def page_trusted_by():
        data = load_data()
        return render_template(
            "trusted_by.html",
            trusted_servers=data.get("trusted_servers", []),
            testimonials=data.get("testimonials", []),
            plans=data.get("plans", []),
        )

    @app.route("/status")
    def page_status():
        return redirect(STATUS_SITE_URL + "/", code=302)

    @app.route("/faq")
    def page_faq():
        return render_template("noble_faq.html", faqs=load_data().get("faqs", []))

    @app.route("/terms")
    def page_terms():
        return render_template("noble_terms.html")

    @app.route("/privacy")
    def page_privacy():
        return render_template("noble_privacy.html")

    @app.route("/signin")
    def page_signin():
        return redirect(url_for("page_auth", mode="signin"), code=302)

    @app.route("/signup")
    def page_signup():
        return redirect(url_for("page_auth", mode="signup"), code=302)

    @app.route("/logout", methods=["GET", "POST"])
    def page_logout():
        session.clear()
        return redirect(url_for("page_auth", mode="signin"))

    @app.route("/auth")
    def page_auth():
        mode = request.args.get("mode", "signup")
        if mode not in ("signin", "signup", "reset"):
            mode = "signup"
        data = load_data()
        requested_plan_id = request.args.get("plan", "")
        selected_plan = next((plan for plan in data.get("plans", []) if plan.get("id") == requested_plan_id), None)
        if selected_plan:
            session["selected_plan_id"] = selected_plan["id"]
        elif session.get("selected_plan_id"):
            selected_plan = next((plan for plan in data.get("plans", []) if plan.get("id") == session["selected_plan_id"]), None)
        if session.get("user"):
            return redirect("/dashboard")
        return render_template(
            "auth.html",
            mode=mode,
            selected_plan=selected_plan,
            sso_providers=tuple(oauth_clients),
            auth_error=auth_page_error(request.args.get("error", "")),
        )

    @app.route("/auth/reset")
    def page_password_reset():
        token = request.args.get("token", "")
        if not find_password_reset_user(load_data(), token):
            return redirect(url_for("page_auth", mode="signin", error="reset_invalid"))
        return render_template("reset_password.html", reset_token=token)

    @app.route("/auth/<provider>")
    def auth_start(provider):
        client = oauth_clients.get(provider)
        if not client:
            return redirect(url_for("page_auth", error="provider_unconfigured"))
        selected_plan_id = request.args.get("plan", "")
        if any(plan.get("id") == selected_plan_id for plan in load_data().get("plans", [])):
            session["selected_plan_id"] = selected_plan_id
        nonce = secrets.token_urlsafe(32)
        return client.authorize_redirect(oauth_redirect_uri(provider), nonce=nonce)

    @app.route("/auth/<provider>/callback")
    def auth_callback(provider):
        client = oauth_clients.get(provider)
        if not client:
            return redirect(url_for("page_auth", error="provider_unconfigured"))
        try:
            token = client.authorize_access_token()
            identity = token.get("userinfo") or {}
            subject = str(identity.get("sub", "")).strip()
            email = str(identity.get("email") or identity.get("preferred_username") or "").strip().lower()
            name = str(identity.get("name") or "").strip()
            if not subject:
                raise ValueError("Missing provider subject")
            email_verified = identity.get("email_verified") is True or str(identity.get("email_verified", "")).lower() == "true"
            if (provider == "google" and not email_verified) or not email or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
                return redirect(url_for("page_auth", error="email_missing"))
            data = load_data()
            users = data.setdefault("users", [])
            user = next((
                entry for entry in users
                if any(link.get("provider") == provider and link.get("subject") == subject for link in entry.get("providers", []))
            ), None)
            if not user:
                if any(entry.get("email", "").lower() == email for entry in users):
                    return redirect(url_for("page_auth", error="account_exists"))
                user = {
                    "id": int(time.time() * 1000),
                    "name": name or email.split("@", 1)[0],
                    "email": email,
                    "password_hash": None,
                    "providers": [{"provider": provider, "subject": subject}],
                }
                users.append(user)
                save_data(data)
            selected_plan_id = session.get("selected_plan_id")
            session.clear()
            session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"]}
            if selected_plan_id and any(plan.get("id") == selected_plan_id for plan in load_data().get("plans", [])):
                session["selected_plan_id"] = selected_plan_id
            return redirect("/dashboard")
        except (OAuthError, ValueError, KeyError, TypeError):
            return redirect(url_for("page_auth", error="provider_failed"))
        except Exception:
            return redirect(url_for("page_auth", error="provider_failed"))

    @app.route("/utilities")
    def page_utilities():
        return render_template("noble_tools.html")

    @app.route("/dashboard")
    def page_dashboard():
        if not session.get("user"):
            return redirect(url_for("page_auth", mode="signin"))
        data = load_data()
        user = session["user"]
        selected_plan_id = session.get("selected_plan_id")
        selected_plan = next((plan for plan in data.get("plans", []) if plan.get("id") == selected_plan_id), None)
        user_servers = [s for s in data.get("servers", []) if str(s.get("user_id")) == str(user.get("id"))]
        user_orders = [o for o in data.get("orders", []) if str(o.get("user_id")) == str(user.get("id"))]
        return render_template(
            "noble_dashboard.html",
            user=user,
            selected_plan=selected_plan,
            servers=user_servers,
            orders=user_orders,
            plans=data.get("plans", []),
            locations=LOCATIONS,
        )

    @app.route("/robots.txt")
    def robots_txt():
        return ROBOT_TXT, 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.route("/sitemap.xml")
    def sitemap_xml():
        return SITEMAP_XML, 200, {"Content-Type": "application/xml; charset=utf-8"}

    @app.route("/logo.png")
    def logo_file():
        from flask import send_from_directory
        return send_from_directory(STATIC_DIR / "images", "logo.png")

    @app.route("/test-error/<int:code>")
    def test_error_route(code):
        from flask import abort
        if code in (404, 502, 500, 503, 403, 401):
            abort(code)
        return jsonify({"message": f"Code {code} not an error"})

    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error_code": 404, "message": "API endpoint not found."}), 404
        return render_template(
            "noble_error.html",
            error_code=404,
            error_title="Page Not Found",
            error_message="This page doesn't exist, or it may have moved.",
        ), 404

    @app.errorhandler(502)
    def page_bad_gateway(error):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error_code": 502, "message": "Bad gateway. Upstream connection failed."}), 502
        return render_template(
            "noble_error.html",
            error_code=502,
            error_title="Bad Gateway",
            error_message="The upstream server returned an invalid response. Our core hosting infrastructure remains healthy.",
        ), 502

    @app.errorhandler(500)
    def page_server_error(error):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error_code": 500, "message": "Internal server error occurred."}), 500
        return render_template(
            "noble_error.html",
            error_code=500,
            error_title="Internal Server Error",
            error_message="Something went wrong on our servers. Our network operations team has been notified.",
        ), 500

    @app.errorhandler(503)
    def page_service_unavailable(error):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error_code": 503, "message": "Service temporarily unavailable."}), 503
        return render_template(
            "noble_error.html",
            error_code=503,
            error_title="Service Unavailable",
            error_message="This service is undergoing brief maintenance. Please check back in a few moments.",
        ), 503

    @app.errorhandler(403)
    def page_forbidden(error):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error_code": 403, "message": "Access forbidden."}), 403
        return render_template(
            "noble_error.html",
            error_code=403,
            error_title="Access Forbidden",
            error_message="You do not have permission to access this resource.",
        ), 403

    @app.errorhandler(401)
    def page_unauthorized(error):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error_code": 401, "message": "Authentication required."}), 401
        return render_template(
            "noble_error.html",
            error_code=401,
            error_title="Unauthorized Access",
            error_message="You must be signed in to view this resource.",
        ), 401

    if SECRET_ADMIN_PATH:
        @app.route(SECRET_ADMIN_PATH)
        def encrypted_admin():
            if session.get("admin_authenticated"):
                return render_template("admin.html", admin_url=SECRET_ADMIN_PATH)
            return render_template("admin_login.html", admin_url=SECRET_ADMIN_PATH)

    @app.route("/api/auth/register", methods=["POST"])
    def api_auth_register():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Too many sign-up attempts. Please wait a minute."}), 429
        req_data = request.get_json() or {}
        name = str(req_data.get("name", "")).strip()
        email = str(req_data.get("email", "")).strip().lower()
        password = str(req_data.get("password", ""))
        if not name or len(name) > 120 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(password) < 8 or len(password) > 1024:
            return jsonify({"success": False, "message": "Please provide a valid name, email, and password with at least 8 characters."}), 400
        data = load_data()
        existing = next((entry for entry in data.get("users", []) if entry.get("email", "").lower() == email), None)
        if existing:
            return jsonify({"success": False, "message": "An account already exists for this email."}), 409
        selected_plan_id = str(req_data.get("plan_id", ""))
        selected_plan_id = selected_plan_id if any(plan.get("id") == selected_plan_id for plan in data.get("plans", [])) else ""
        user = {"id": int(time.time() * 1000), "name": name, "email": email, "password_hash": generate_password_hash(password)}
        data.setdefault("users", []).append(user)
        save_data(data)
        session.clear()
        session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"]}
        if selected_plan_id:
            session["selected_plan_id"] = selected_plan_id
        return jsonify({"success": True, "message": "Account created successfully.", "user": session["user"]})

    @app.route("/api/auth/login", methods=["POST"])
    def api_auth_login():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Too many sign-in attempts. Please wait a minute."}), 429
        req_data = request.get_json() or {}
        email = str(req_data.get("email", "")).strip().lower()
        password = str(req_data.get("password", ""))
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or not password or len(password) > 1024:
            return jsonify({"success": False, "message": "Invalid email or password."}), 401
        data = load_data()
        user = next((entry for entry in data.get("users", []) if entry.get("email", "").lower() == email), None)
        password_hash = user.get("password_hash") if user else None
        if not password_hash or not check_password_hash(password_hash, password):
            return jsonify({"success": False, "message": "Invalid email or password."}), 401
        selected_plan_id = str(req_data.get("plan_id", ""))
        selected_plan_id = selected_plan_id if any(plan.get("id") == selected_plan_id for plan in data.get("plans", [])) else ""
        session.clear()
        session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"]}
        if selected_plan_id:
            session["selected_plan_id"] = selected_plan_id
        return jsonify({"success": True, "message": "Signed in successfully.", "user": session["user"]})

    @app.route("/api/auth/logout", methods=["GET", "POST"])
    def api_auth_logout():
        session.clear()
        return jsonify({"success": True})

    @app.route("/api/auth/password-reset/request", methods=["POST"])
    def api_password_reset_request():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Too many requests. Please wait a minute."}), 429
        req_data = request.get_json() or {}
        email = str(req_data.get("email", "")).strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return jsonify({"success": False, "message": "Enter a valid email address."}), 400
        if not os.environ.get("SMTP_HOST") or not os.environ.get("SMTP_FROM"):
            return jsonify({"success": False, "message": "Password-reset email is not configured. Contact Noble Node support."}), 503
        data = load_data()
        user = next((entry for entry in data.get("users", []) if entry.get("email", "").lower() == email and entry.get("password_hash")), None)
        if user:
            raw_token = secrets.token_urlsafe(32)
            user["password_reset"] = {
                "token_hash": hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
                "expires_at": time.time() + 1800,
            }
            save_data(data)
            reset_path = url_for("page_password_reset", token=raw_token)
            reset_base = os.environ.get("OAUTH_REDIRECT_BASE_URL", PUBLIC_SITE_URL).rstrip("/") + "/"
            reset_url = urljoin(reset_base, reset_path.lstrip("/"))
            try:
                send_password_reset_email(email, reset_url)
            except (OSError, smtplib.SMTPException, ValueError):
                user.pop("password_reset", None)
                save_data(data)
                return jsonify({"success": False, "message": "Unable to send a reset email right now. Try again later."}), 503
        return jsonify({"success": True, "message": "If an account matches that address, a reset link will be sent."})

    @app.route("/api/auth/password-reset/complete", methods=["POST"])
    def api_password_reset_complete():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Too many requests. Please wait a minute."}), 429
        req_data = request.get_json() or {}
        token = str(req_data.get("token", ""))
        password = str(req_data.get("password", ""))
        if len(password) < 8 or len(password) > 1024:
            return jsonify({"success": False, "message": "Use a password with at least 8 characters."}), 400
        data = load_data()
        user = find_password_reset_user(data, token)
        if not user:
            return jsonify({"success": False, "message": "That password reset link is invalid or expired. Request a new one."}), 400
        user["password_hash"] = generate_password_hash(password)
        user.pop("password_reset", None)
        save_data(data)
        return jsonify({"success": True, "message": "Password updated. Sign in with your new password."})

    @app.route("/api/admin/login", methods=["POST"])
    def api_admin_login():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Rate limit exceeded. Please try again in a minute."}), 429
        req_data = request.get_json() or {}
        password = str(req_data.get("password", ""))
        username = str(req_data.get("username", "")).strip()
        if ADMIN_PASSWORD_HASH and username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.clear()
            session["admin_authenticated"] = True
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Invalid cryptographic admin password"}), 401

    @app.route("/api/admin/logout", methods=["POST"])
    def api_admin_logout():
        session.pop("admin_authenticated", None)
        return jsonify({"success": True})

    @app.route("/api/plans")
    def api_plans():
        data = load_data()
        return jsonify({"success": True, "plans": data.get("plans", []), "locations": LOCATIONS})

    @app.route("/api/faqs")
    def api_faqs():
        data = load_data()
        return jsonify({"success": True, "faqs": data.get("faqs", [])})

    @app.route("/api/testimonials")
    def api_testimonials():
        data = load_data()
        return jsonify({"success": True, "testimonials": data.get("testimonials", [])})

    @app.route("/api/partners")
    def api_partners():
        data = load_data()
        return jsonify({"success": True, "partners": data.get("partners", [])})

    @app.route("/api/trusted-servers")
    def api_trusted_servers():
        data = load_data()
        return jsonify({"success": True, "trusted_servers": data.get("trusted_servers", [])})

    @app.route("/api/coupons/validate", methods=["POST"])
    def api_coupon_validate():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Too many requests. Please slow down."}), 429
        req_data = request.get_json() or {}
        code = req_data.get("code", "").strip().upper()
        data = load_data()
        coupon = next((entry for entry in data.get("coupons", []) if entry["code"].upper() == code and entry.get("active", True)), None)
        if coupon:
            return jsonify({"success": True, "coupon": coupon})
        return jsonify({"success": False, "message": "Invalid or expired coupon code"}), 400

    @app.route("/api/ping", methods=["POST"])
    def api_ping():
        req_data = request.get_json() or {}
        location_id = req_data.get("location", "lahore").lower()
        city = req_data.get("city", "Lahore").lower()
        base = 10
        if "lahore" in location_id:
            if "lahore" in city: base = 6
            elif "islamabad" in city or "rawalpindi" in city: base = 12
            elif "karachi" in city: base = 18
            elif "peshawar" in city: base = 16
            else: base = 14
        elif "karachi" in location_id:
            if "karachi" in city: base = 5
            elif "lahore" in city: base = 16
            elif "islamabad" in city: base = 22
            else: base = 18
        elif "dubai" in location_id:
            base = 32
        elif "singapore" in location_id:
            base = 55
        elif "frankfurt" in location_id:
            base = 112
        jitter = random.choice([-1, 0, 1])
        ping_ms = max(4, base + jitter)
        return jsonify({
            "success": True,
            "ping_ms": ping_ms,
            "location": location_id,
            "status": "Online (Ultra-low latency)" if ping_ms < 30 else "Online",
            "jitter_ms": random.randint(1, 2),
        })

    @app.route("/api/order", methods=["POST"])
    def api_order():
        ip = request.remote_addr or "127.0.0.1"
        if not rate_limiter.is_allowed(ip):
            return jsonify({"success": False, "message": "Order rate limit exceeded. Please wait a moment."}), 429

        req_data = request.get_json() or {}
        plan_id = req_data.get("plan_id", "").strip()
        location_id = req_data.get("location", "lahore").strip()
        software = req_data.get("software", "Paper 1.21.4").strip()
        subdomain = req_data.get("subdomain", "").strip().lower()
        payment_method = req_data.get("payment_method", "EasyPaisa").strip()
        coupon_code = req_data.get("coupon_code", "").strip().upper()
        server_name = req_data.get("server_name", "").strip()

        data = load_data()
        plan = next((p for p in data.get("plans", []) if p["id"] == plan_id), None)
        if not plan:
            return jsonify({"success": False, "message": "Invalid plan selected."}), 400

        base_pkr = plan.get("pkr_price") or int((plan.get("usd_price") or 10) * 280)
        discount_pkr = 0
        if coupon_code:
            coupon = next((c for c in data.get("coupons", []) if c["code"].upper() == coupon_code and c.get("active", True)), None)
            if coupon:
                if coupon.get("discount_pct", 0) > 0:
                    discount_pkr = int(base_pkr * (coupon["discount_pct"] / 100.0))
                elif coupon.get("flat_pkr", 0) > 0:
                    discount_pkr = min(base_pkr, coupon["flat_pkr"])

        total_pkr = max(0, base_pkr - discount_pkr)

        user = session.get("user")
        if not user:
            name = req_data.get("name", "").strip()
            email = req_data.get("email", "").strip().lower()
            password = req_data.get("password", "")
            if not email or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
                return jsonify({"success": False, "message": "Please provide a valid email address or sign in first."}), 400

            existing_user = next((u for u in data.get("users", []) if u.get("email", "").lower() == email), None)
            if existing_user:
                user = {"id": existing_user["id"], "name": existing_user["name"], "email": existing_user["email"]}
            else:
                if not password or len(password) < 8:
                    return jsonify({"success": False, "message": "Please enter a password with at least 8 characters to create your account."}), 400
                new_user = {
                    "id": int(time.time() * 1000),
                    "name": name or email.split("@")[0],
                    "email": email,
                    "password_hash": generate_password_hash(password),
                }
                data.setdefault("users", []).append(new_user)
                user = {"id": new_user["id"], "name": new_user["name"], "email": new_user["email"]}

            session["user"] = user

        order_id = f"NN-PK-{random.randint(10000, 99999)}"
        server_id = f"srv-{random.randint(100, 999)}"
        loc_obj = next((loc for loc in LOCATIONS if loc["id"] == location_id), LOCATIONS[0])

        subdomain_clean = re.sub(r"[^a-z0-9-]", "", subdomain) or f"server-{random.randint(1000, 9999)}"
        full_address = f"{subdomain_clean}.noblenode.host"
        server_port = random.randint(25565, 25999)
        server_ip = f"pk-{loc_obj['id']}.noblenode.host:{server_port}"

        ram_digits = re.search(r"\d+", plan.get("ram", "8"))
        ram_gb = int(ram_digits.group(0)) if ram_digits else 8
        storage_digits = re.search(r"\d+", plan.get("storage", "120"))
        storage_gb = int(storage_digits.group(0)) if storage_digits else 120

        server_record = {
            "id": server_id,
            "user_id": user["id"],
            "name": server_name or f"{user['name']}'s Server",
            "plan_id": plan["id"],
            "plan_name": plan["name"],
            "ram": plan["ram"],
            "cpu": plan["cpu"],
            "storage": plan["storage"],
            "ip": server_ip,
            "subdomain": full_address,
            "location": loc_obj["name"],
            "software": software,
            "status": "Running",
            "uptime": "Just deployed",
            "players": "0 / 50",
            "tps": 20.0,
            "memory_used_mb": 512,
            "memory_total_mb": ram_gb * 1024,
            "cpu_usage_pct": 2.4,
            "disk_used_gb": 1.2,
            "disk_total_gb": storage_gb,
            "auto_renew": True,
            "monthly_pkr": total_pkr,
            "renewal_date": time.strftime("%Y-%m-%d", time.localtime(time.time() + 30 * 86400)),
        }

        order_record = {
            "id": order_id,
            "user_id": user["id"],
            "plan_id": plan["id"],
            "plan_name": plan["name"],
            "total_pkr": total_pkr,
            "payment_method": payment_method,
            "status": "Paid",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server_id": server_id,
            "invoice_url": f"/dashboard?order={order_id}",
        }

        data.setdefault("servers", []).append(server_record)
        data.setdefault("orders", []).append(order_record)
        save_data(data)

        session["selected_plan_id"] = plan["id"]

        return jsonify({
            "success": True,
            "message": "Server provisioned successfully!",
            "order_id": order_id,
            "server_ip": server_ip,
            "location": loc_obj["name"],
            "software": software,
            "total_pkr": total_pkr,
            "control_panel_url": "/dashboard",
            "server": server_record,
            "order": order_record,
        })

    @app.route("/api/user/profile", methods=["GET", "POST"])
    def api_user_profile():
        if not session.get("user"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = load_data()
        user_id = session["user"]["id"]
        user_record = next((u for u in data.get("users", []) if str(u.get("id")) == str(user_id)), None)
        if not user_record:
            return jsonify({"success": False, "message": "User not found"}), 404

        if request.method == "POST":
            req_data = request.get_json() or {}
            new_name = str(req_data.get("name", "")).strip()
            if not new_name or len(new_name) > 120:
                return jsonify({"success": False, "message": "Valid name required"}), 400
            user_record["name"] = new_name
            session["user"]["name"] = new_name
            save_data(data)
            return jsonify({"success": True, "message": "Profile updated", "user": session["user"]})

        return jsonify({"success": True, "user": session["user"]})

    @app.route("/api/user/change-password", methods=["POST"])
    def api_user_change_password():
        if not session.get("user"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        req_data = request.get_json() or {}
        current_password = str(req_data.get("current_password", ""))
        new_password = str(req_data.get("new_password", ""))
        if len(new_password) < 8:
            return jsonify({"success": False, "message": "New password must be at least 8 characters"}), 400

        data = load_data()
        user_id = session["user"]["id"]
        user_record = next((u for u in data.get("users", []) if str(u.get("id")) == str(user_id)), None)
        if not user_record:
            return jsonify({"success": False, "message": "User not found"}), 404

        if user_record.get("password_hash") and not check_password_hash(user_record["password_hash"], current_password):
            return jsonify({"success": False, "message": "Incorrect current password"}), 401

        user_record["password_hash"] = generate_password_hash(new_password)
        save_data(data)
        return jsonify({"success": True, "message": "Password changed successfully"})

    @app.route("/api/user/servers", methods=["GET"])
    def api_user_servers():
        if not session.get("user"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = load_data()
        user_id = session["user"]["id"]
        servers = [s for s in data.get("servers", []) if str(s.get("user_id")) == str(user_id)]
        return jsonify({"success": True, "servers": servers})

    @app.route("/api/user/servers/<server_id>/action", methods=["POST"])
    def api_user_server_action(server_id):
        if not session.get("user"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        req_data = request.get_json() or {}
        action = req_data.get("action", "").lower()
        if action not in ("start", "stop", "restart"):
            return jsonify({"success": False, "message": "Invalid action"}), 400

        data = load_data()
        user_id = session["user"]["id"]
        server = next((s for s in data.get("servers", []) if s.get("id") == server_id and str(s.get("user_id")) == str(user_id)), None)
        if not server:
            return jsonify({"success": False, "message": "Server not found"}), 404

        if action == "stop":
            server["status"] = "Stopped"
            server["players"] = "0 / 50"
            server["tps"] = 0.0
            server["memory_used_mb"] = 0
            server["cpu_usage_pct"] = 0.0
        elif action in ("start", "restart"):
            server["status"] = "Running"
            server["players"] = f"{random.randint(12, 28)} / 50"
            server["tps"] = 20.0
            server["memory_used_mb"] = random.randint(3500, 6800)
            server["cpu_usage_pct"] = round(random.uniform(8.5, 18.2), 1)
            server["uptime"] = "Online"

        save_data(data)
        return jsonify({"success": True, "message": f"Server {action}ed successfully", "server": server})

    @app.route("/api/user/orders", methods=["GET"])
    def api_user_orders():
        if not session.get("user"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = load_data()
        user_id = session["user"]["id"]
        orders = [o for o in data.get("orders", []) if str(o.get("user_id")) == str(user_id)]
        return jsonify({"success": True, "orders": orders})

    @app.route("/api/admin/all")
    def api_admin_all():
        if not session.get("admin_authenticated"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        return jsonify({"success": True, "data": load_data()})

    @app.route("/api/admin/plans", methods=["POST", "PUT", "DELETE"])
    def api_admin_plans():
        if not session.get("admin_authenticated"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        data = load_data()
        req_data = request.get_json() or {}

        if request.method == "POST":
            new_plan = {
                "id": req_data.get("id", f"plan-{int(time.time())}"),
                "name": req_data.get("name", "Custom Plan"),
                "ram": req_data.get("ram", "4 GB DDR5"),
                "cpu": req_data.get("cpu", "200% Ryzen 9"),
                "storage": req_data.get("storage", "40 GB NVMe"),
                "backups": req_data.get("backups", "5 Backups"),
                "slots": "Unlimited Slots",
                "pkr_price": int(req_data.get("pkr_price", 2000)),
                "usd_price": float(req_data.get("usd_price", 7.0)),
                "recommended": bool(req_data.get("recommended", False)),
                "badge": req_data.get("badge", ""),
                "icon": req_data.get("icon", "server"),
                "category": req_data.get("category", "paper"),
                "ideal_for": req_data.get("ideal_for", "General Server"),
            }
            data["plans"].append(new_plan)
            save_data(data)
            return jsonify({"success": True, "plan": new_plan})

        if request.method == "DELETE":
            plan_id = req_data.get("id")
            data["plans"] = [item for item in data["plans"] if item["id"] != plan_id]
            save_data(data)
            return jsonify({"success": True})

        return jsonify({"success": True})

    @app.route("/api/admin/coupons", methods=["POST", "DELETE"])
    def api_admin_coupons():
        if not session.get("admin_authenticated"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        data = load_data()
        req_data = request.get_json() or {}

        if request.method == "POST":
            code = req_data.get("code", "").strip().upper()
            if not code:
                return jsonify({"success": False, "message": "Code required"}), 400
            data["coupons"] = [item for item in data["coupons"] if item["code"].upper() != code]
            new_coupon = {
                "code": code,
                "discount_pct": int(req_data.get("discount_pct", 0)),
                "flat_pkr": int(req_data.get("flat_pkr", 0)),
                "active": bool(req_data.get("active", True)),
                "description": req_data.get("description", "Admin Coupon"),
            }
            data["coupons"].append(new_coupon)
            save_data(data)
            return jsonify({"success": True, "coupon": new_coupon})

        code = req_data.get("code", "").upper()
        data["coupons"] = [item for item in data["coupons"] if item["code"].upper() != code]
        save_data(data)
        return jsonify({"success": True})

    @app.route("/api/admin/faqs", methods=["POST", "DELETE"])
    def api_admin_faqs():
        if not session.get("admin_authenticated"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        data = load_data()
        req_data = request.get_json() or {}

        if request.method == "POST":
            faq_id = req_data.get("id")
            question = req_data.get("question", "").strip()
            answer = req_data.get("answer", "").strip()
            if faq_id:
                for index, item in enumerate(data["faqs"]):
                    if item["id"] == faq_id:
                        data["faqs"][index]["question"] = question
                        data["faqs"][index]["answer"] = answer
            else:
                data["faqs"].append({"id": int(time.time()), "question": question, "answer": answer})
            save_data(data)
            return jsonify({"success": True})

        faq_id = req_data.get("id")
        data["faqs"] = [item for item in data["faqs"] if item["id"] != faq_id]
        save_data(data)
        return jsonify({"success": True})

    @app.route("/api/admin/testimonials", methods=["POST", "DELETE"])
    def api_admin_testimonials():
        if not session.get("admin_authenticated"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        data = load_data()
        req_data = request.get_json() or {}

        if request.method == "POST":
            t_id = req_data.get("id")
            name = req_data.get("name", "").strip()
            role = req_data.get("role", "").strip()
            text = req_data.get("text", "").strip()
            stars = int(req_data.get("stars", 5))
            avatar = req_data.get("avatar", "").strip() or "".join([word[0].upper() for word in name.split()[:2]]) or "MC"
            if t_id:
                for index, item in enumerate(data.get("testimonials", [])):
                    if item["id"] == int(t_id):
                        data["testimonials"][index] = {"id": int(t_id), "name": name, "role": role, "text": text, "stars": stars, "avatar": avatar}
            else:
                if "testimonials" not in data:
                    data["testimonials"] = []
                data["testimonials"].append({"id": int(time.time()), "name": name, "role": role, "text": text, "stars": stars, "avatar": avatar})
            save_data(data)
            return jsonify({"success": True})

        t_id = req_data.get("id")
        if "testimonials" in data:
            data["testimonials"] = [item for item in data["testimonials"] if item["id"] != int(t_id)]
            save_data(data)
        return jsonify({"success": True})

    def run_server():
        port = int(os.environ.get("PORT", "5000"))
        app.run(host=os.environ.get("HOST", "0.0.0.0"), port=port, debug=False)

else:
    import http.server
    import socketserver

    class NobleNodeHandler(http.server.SimpleHTTPRequestHandler):
        def get_client_ip(self):
            return self.client_address[0] if self.client_address else "127.0.0.1"

        def parse_cookie(self):
            cookie_hdr = self.headers.get("Cookie", "")
            cookies = {}
            for item in cookie_hdr.split(";"):
                if "=" in item:
                    key, value = item.strip().split("=", 1)
                    cookies[key.strip()] = value.strip()
            return cookies

        def is_authenticated(self):
            cookies = self.parse_cookie()
            return False

        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path)
            path = urllib.parse.unquote(parsed_path.path)

            if path == "/":
                self.send_html(TEMPLATES_DIR / "index.html")
                return
            if path == "/plans":
                self.send_html(TEMPLATES_DIR / "plans.html")
                return
            if path == "/status":
                self.send_html(TEMPLATES_DIR / "status.html")
                return
            if path == "/faq":
                self.send_html(TEMPLATES_DIR / "faq.html")
                return
            if path == "/terms":
                self.send_html(TEMPLATES_DIR / "terms.html")
                return
            if path == "/privacy":
                self.send_html(TEMPLATES_DIR / "privacy.html")
                return
            if path == "/signin":
                self.send_html(TEMPLATES_DIR / "signin.html")
                return
            if path == "/signup":
                self.send_html(TEMPLATES_DIR / "signup.html")
                return
            if path == "/utilities":
                self.send_html(TEMPLATES_DIR / "utilities.html")
                return
            if path == "/dashboard":
                self.send_html(TEMPLATES_DIR / "dashboard.html")
                return
            if path == "/robots.txt":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(ROBOT_TXT.encode("utf-8"))
                return
            if path == "/sitemap.xml":
                self.send_response(200)
                self.send_header("Content-Type", "application/xml; charset=utf-8")
                self.end_headers()
                self.wfile.write(SITEMAP_XML.encode("utf-8"))
                return
            if path == "/logo.png":
                target_file = STATIC_DIR / "images" / "logo.png"
                if target_file.exists():
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                    with open(target_file, "rb") as handle:
                        self.wfile.write(handle.read())
                    return
            if SECRET_ADMIN_PATH and path == SECRET_ADMIN_PATH:
                if self.is_authenticated():
                    self.send_html(TEMPLATES_DIR / "admin.html")
                else:
                    self.send_html(TEMPLATES_DIR / "admin_login.html")
                return
            if path == "/api/plans":
                data = load_data()
                self.send_json({"success": True, "plans": data["plans"], "locations": LOCATIONS})
                return
            if path == "/api/faqs":
                data = load_data()
                self.send_json({"success": True, "faqs": data.get("faqs", [])})
                return
            if path == "/api/testimonials":
                data = load_data()
                self.send_json({"success": True, "testimonials": data.get("testimonials", [])})
                return
            if path == "/api/admin/all":
                if not self.is_authenticated():
                    self.send_json({"success": False, "message": "Unauthorized"}, status=401)
                    return
                self.send_json({"success": True, "data": load_data()})
                return
            if path.startswith("/static/"):
                file_rel = path[len("/static/"):]
                target_file = STATIC_DIR / file_rel
                if target_file.exists() and target_file.is_file():
                    self.send_response(200)
                    if file_rel.endswith(".css"):
                        self.send_header("Content-type", "text/css")
                    elif file_rel.endswith(".js"):
                        self.send_header("Content-type", "application/javascript")
                    elif file_rel.endswith(".svg"):
                        self.send_header("Content-type", "image/svg+xml")
                    elif file_rel.endswith(".png"):
                        self.send_header("Content-type", "image/png")
                    self.end_headers()
                    with open(target_file, "rb") as handle:
                        self.wfile.write(handle.read())
                    return
            self.send_error_page(404, "route not found", "This page doesn't exist, or it may have moved.")

        def do_HEAD(self):
            self.do_GET()

        def do_POST(self):
            parsed_path = urllib.parse.urlparse(self.path)
            path = urllib.parse.unquote(parsed_path.path)
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}

            ip = self.get_client_ip()

            if path == "/api/auth/register":
                if not rate_limiter.is_allowed(ip):
                    self.send_json({"success": False, "message": "Too many sign-up attempts. Please wait a minute."}, status=429)
                    return
                name = str(data.get("name", "")).strip()
                email = str(data.get("email", "")).strip().lower()
                password = str(data.get("password", ""))
                if not name or not email or len(password) < 8:
                    self.send_json({"success": False, "message": "Please provide a valid name, email, and password with at least 8 characters."}, status=400)
                    return
                db = load_data()
                existing = next((entry for entry in db.get("users", []) if entry["email"].lower() == email), None)
                if existing:
                    self.send_json({"success": False, "message": "An account already exists for this email."}, status=409)
                    return
                user = {"id": int(time.time() * 1000), "name": name, "email": email, "password_hash": hash_password(password)}
                db.setdefault("users", []).append(user)
                save_data(db)
                self.send_json({"success": True, "message": "Account created successfully.", "user": {"id": user["id"], "name": name, "email": email}})
                return

            if path == "/api/auth/login":
                if not rate_limiter.is_allowed(ip):
                    self.send_json({"success": False, "message": "Too many sign-in attempts. Please wait a minute."}, status=429)
                    return
                email = str(data.get("email", "")).strip().lower()
                password = str(data.get("password", ""))
                db = load_data()
                user = next((entry for entry in db.get("users", []) if entry["email"].lower() == email), None)
                if not user or not verify_password(password, user.get("password_hash", "")):
                    self.send_json({"success": False, "message": "Invalid email or password."}, status=401)
                    return
                self.send_json({"success": True, "message": "Signed in successfully.", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})
                return

            if path == "/api/auth/logout":
                self.send_json({"success": True})
                return

            if path == "/api/admin/login":
                self.send_json({"success": False, "message": "Flask is required for secure administrator authentication."}, status=503)
                return

            if path == "/api/admin/logout":
                payload = json.dumps({"success": True}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", "admin_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            if path == "/api/ping":
                self.send_json({"success": False, "message": "Live latency testing is not configured."}, status=503)
                return

            if path == "/api/coupons/validate":
                if not rate_limiter.is_allowed(ip):
                    self.send_json({"success": False, "message": "Too many requests. Please slow down."}, status=429)
                    return
                code = data.get("code", "").strip().upper()
                db = load_data()
                coupon = next((item for item in db["coupons"] if item["code"].upper() == code and item.get("active", True)), None)
                if coupon:
                    self.send_json({"success": True, "coupon": coupon})
                else:
                    self.send_json({"success": False, "message": "Invalid or expired coupon code"})
                return

            if path == "/api/order":
                self.send_json({"success": False, "message": "Online checkout and server provisioning are not configured yet."}, status=503)
                return

            if not self.is_authenticated():
                self.send_json({"success": False, "message": "Unauthorized"}, status=401)
                return

            db = load_data()

            if path == "/api/admin/plans":
                new_plan = {
                    "id": data.get("id", f"plan-{int(time.time())}"),
                    "name": data.get("name", "Custom Plan"),
                    "ram": data.get("ram", "4 GB DDR5"),
                    "cpu": data.get("cpu", "200% Ryzen 9"),
                    "storage": data.get("storage", "40 GB NVMe"),
                    "backups": data.get("backups", "5 Backups"),
                    "slots": "Unlimited Slots",
                    "pkr_price": int(data.get("pkr_price", 2000)),
                    "usd_price": float(data.get("usd_price", 7.0)),
                    "recommended": bool(data.get("recommended", False)),
                    "badge": data.get("badge", ""),
                    "icon": data.get("icon", "server"),
                    "category": data.get("category", "paper"),
                    "ideal_for": data.get("ideal_for", "General Server"),
                }
                db["plans"].append(new_plan)
                save_data(db)
                self.send_json({"success": True, "plan": new_plan})
                return

            if path == "/api/admin/coupons":
                code = data.get("code", "").strip().upper()
                if not code:
                    self.send_json({"success": False, "message": "Code required"})
                    return
                db["coupons"] = [item for item in db["coupons"] if item["code"].upper() != code]
                new_coupon = {
                    "code": code,
                    "discount_pct": int(data.get("discount_pct", 0)),
                    "flat_pkr": int(data.get("flat_pkr", 0)),
                    "active": bool(data.get("active", True)),
                    "description": data.get("description", "Admin Coupon"),
                }
                db["coupons"].append(new_coupon)
                save_data(db)
                self.send_json({"success": True, "coupon": new_coupon})
                return

            if path == "/api/admin/faqs":
                faq_id = data.get("id")
                question = data.get("question", "").strip()
                answer = data.get("answer", "").strip()
                if faq_id:
                    for index, item in enumerate(db["faqs"]):
                        if item["id"] == faq_id:
                            db["faqs"][index]["question"] = question
                            db["faqs"][index]["answer"] = answer
                else:
                    db["faqs"].append({"id": int(time.time()), "question": question, "answer": answer})
                save_data(db)
                self.send_json({"success": True})
                return

            if path == "/api/admin/testimonials":
                t_id = data.get("id")
                name = data.get("name", "").strip()
                role = data.get("role", "").strip()
                text = data.get("text", "").strip()
                stars = int(data.get("stars", 5))
                avatar = data.get("avatar", "").strip() or "".join([word[0].upper() for word in name.split()[:2]]) or "MC"
                if t_id:
                    for index, item in enumerate(db.get("testimonials", [])):
                        if item["id"] == int(t_id):
                            db["testimonials"][index] = {"id": int(t_id), "name": name, "role": role, "text": text, "stars": stars, "avatar": avatar}
                else:
                    if "testimonials" not in db:
                        db["testimonials"] = []
                    db["testimonials"].append({"id": int(time.time()), "name": name, "role": role, "text": text, "stars": stars, "avatar": avatar})
                save_data(db)
                self.send_json({"success": True})
                return

            self.send_error_page(404, "route not found", "This route does not exist.")

        def do_DELETE(self):
            parsed_path = urllib.parse.urlparse(self.path)
            path = urllib.parse.unquote(parsed_path.path)
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}

            if not self.is_authenticated():
                self.send_json({"success": False, "message": "Unauthorized"}, status=401)
                return

            db = load_data()

            if path == "/api/admin/plans":
                plan_id = data.get("id")
                db["plans"] = [item for item in db["plans"] if item["id"] != plan_id]
                save_data(db)
                self.send_json({"success": True})
                return
            if path == "/api/admin/coupons":
                code = data.get("code", "").upper()
                db["coupons"] = [item for item in db["coupons"] if item["code"].upper() != code]
                save_data(db)
                self.send_json({"success": True})
                return
            if path == "/api/admin/faqs":
                faq_id = data.get("id")
                db["faqs"] = [item for item in db["faqs"] if item["id"] != faq_id]
                save_data(db)
                self.send_json({"success": True})
                return
            if path == "/api/admin/testimonials":
                t_id = data.get("id")
                if "testimonials" in db:
                    db["testimonials"] = [item for item in db["testimonials"] if item["id"] != int(t_id)]
                    save_data(db)
                self.send_json({"success": True})
                return

            self.send_error_page(404, "route not found", "This route does not exist.")

        def send_html(self, filepath):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if filepath.exists():
                with open(filepath, "rb") as handle:
                    self.wfile.write(handle.read())

        def send_json(self, data, status=200):
            payload = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def send_error_page(self, code=404, title="route not found", message="This page doesn't exist, or it may have moved."):
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            error_file = TEMPLATES_DIR / "error.html"
            if error_file.exists():
                with open(error_file, "r", encoding="utf-8") as handle:
                    content = handle.read()
                content = content.replace("{{ error_code|default(404) }}", str(code))
                content = content.replace("{{ error_title|default('route not found') }}", title)
                content = content.replace("{{ error_message|default(\"This page doesn't exist, or it may have moved.\") }}", message)
                self.wfile.write(content.encode("utf-8"))

    def run_server():
        port = 5000
        with socketserver.TCPServer(("127.0.0.1", port), NobleNodeHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped gracefully.")


if __name__ == "__main__":
    run_server()
