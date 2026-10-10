# Noble Node

Noble Node is a Flask-based Minecraft server hosting website. Its plan comparison and homepage use the current plan records in `data.json`. Email/password account access is available at `/auth`; `/signin` and `/signup` redirect to the unified page.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

The default address is `http://127.0.0.1:5000`. Set `PORT` to use another port. The standard-library fallback has been removed because it cannot securely support sessions or OIDC.

Settings are loaded from the ignored root `.env` file, included here with empty Google, Microsoft, and SMTP credential fields. Keep it private and rotate the initial administrator password before deploying.

## Google and Microsoft sign-in

OAuth providers are shown only when their client ID and client secret are set. Register the following callback URLs in each provider’s application configuration:

- Google: `https://noblenode.host/auth/google/callback`
- Microsoft: `https://noblenode.host/auth/microsoft/callback`

Configure these environment variables on the server:

```text
FLASK_SECRET_KEY=<long random secret>
APP_ENV=production
PUBLIC_SITE_URL=https://noblenode.host
OAUTH_REDIRECT_BASE_URL=https://noblenode.host
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=common
SESSION_COOKIE_SECURE=true
```

Google email claims must be verified. Microsoft account identity is validated from its OIDC ID token; matching an existing local account by email never links it automatically. Provider errors return to `/auth` without logging tokens or credentials.

Password reset links use SMTP when configured. Fill in `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS`, and `SMTP_USE_SSL` in `.env`. Links expire after 30 minutes and can only be used once. Without SMTP settings, the reset form reports that email delivery is unavailable.

The local administrator console is available at the private path in `ADMIN_ROUTE`; its initial username is `admin`. The password is stored only in the ignored `.env`, with a Werkzeug hash used for verification. Change the username, password, hash, and route before production. Do not put secrets in source control.

The `/status` route redirects to `https://status.noblenode.host/`. The Discord entry point is `https://discord.noblenode.host`.

## Features

- **PKR Plans & Comparison Matrix**: Real-time PKR/USD currency toggle on `/plans` with side-by-side spec comparison across CPU architecture, RAM, Gen4 NVMe, and DDoS protection tiers.
- **Account Manager (`/dashboard`)**: Full-featured server dashboard with live status metrics, server power actions (Start, Stop, Restart), Web Console terminal simulator, SFTP credentials, order history, and account profile controls.
- **Checkout Flow (`/checkout`)**: 4-step deployment process with plan selection, custom subdomain and software configuration, guest/account creation, coupon code validation, and Pakistani payment rails (EasyPaisa, JazzCash, SadaPay, Raast, Cards).
- **Trusted by Servers Directory (`/trusted-by`, `/servers`)**: Showcase of Pakistani SMPs and Bungee networks with player statistics, verified tags, and 1-click IP copy.
- **DDoS Defense & Fast Networking Showcase**: Highlights 12+ Tbps Corero and Path.net mitigation and ping estimates for Pakistani ISPs (Nayatel, StormFiber, PTCL, Transworld).
- **Comprehensive Error Handling**: Dual-mode handlers for 404, 502, 500, 503, 403, and 401 returning JSON for API endpoints and branded HTML pages for browsers.
- **SEO & Performance**: JSON-LD structured schemas (`Organization`, `Product`, `FAQPage`, `ItemList`), lazy-loaded media, and optimized assets.

## Current integration boundaries

Plan comparison, checkout flow, account management, server controls, and authentication are fully operational. Live Pterodactyl node provisioning and external payment gateway webhooks can be connected via environment variables when live API keys are provided.
