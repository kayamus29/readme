# ReadMore: Django News, Tasks, and Wallet Platform

## Overview
ReadMore is a Django-based web application that combines news reading, daily/manual tasks, a gamified points and coins system, and a wallet with crypto-style features. It includes user authentication, admin controls, and a responsive UI built with Tailwind CSS.

---

## Features
- **User Authentication:** Sign up, login (with username or email), logout, and profile management.
- **Dashboard:** See your points, coin balance, membership status (Regular/Premium), and quick stats.
- **News Module:** Browse news articles, mark articles as read.
- **Daily/Manual Tasks:** Complete daily and manual tasks to earn points.
- **Points & Coins:**
  - Earn points from tasks and reading.
  - Points are automatically converted to coins at a configurable rate.
  - Buy coins with BNB (crypto-style), with admin approval and QR code payment.
  - Full transaction history for coins/points.
- **Wallet:**
  - Save a wallet address and connect MetaMask.
  - Buy coins via BNB transfer (manual approval by admin).
  - Request coin withdrawals (min 30 coins, admin approval required).
  - See transaction history and withdrawal history with status.
  - See coin balance and wallet address.
- **Admin Panel:**
  - Approve/decline coin purchase and withdrawal requests using admin actions (not just by editing status).
  - Edit user points and coin balances directly.
  - Manage users, articles, tasks, and transactions.
  - Email notifications are sent to users when purchases/withdrawals are approved or declined.

---

## Installation & Deployment Guide

### 1. Requirements
- Python 3.10+
- Django 5+
- Redis (for Celery, optional)
- Node.js & npm (for Tailwind, only if you want to build custom CSS)
- PostgreSQL or SQLite (default is SQLite)

### 2. Clone the Repository
```bash
git clone <your-repo-url>
cd readmore
```

### 3. Create & Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Email Setup (for notifications)

By default, emails are printed to the console. To send real emails (Gmail SMTP example):

1. Open `readmore/readmore/settings.py`.
2. Uncomment and fill in:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your_email@gmail.com'        # <-- Your email
   EMAIL_HOST_PASSWORD = 'your_app_password_here'  # <-- App password (not your normal password)
   DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
   ```
3. For Gmail, create an "App Password" (see https://support.google.com/accounts/answer/185833).
4. Restart your Django server.

Emails will now be sent for approvals/declines of purchases and withdrawals.

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic
```

### 8. Run the Server (Development)
```bash
python manage.py runserver
```

### 9. Production Deployment
- Use **gunicorn** or **uWSGI** as the WSGI server.
- Use **nginx** or **Apache** as a reverse proxy.
- Set `DEBUG = False` in `settings.py` and configure `ALLOWED_HOSTS`.
- Use a production-ready database (e.g., PostgreSQL).
- Set up HTTPS (Let's Encrypt recommended).

---

## Withdrawal & Admin Approval Workflow

- Users can request coin withdrawals (min 30 coins) from the wallet page.
- Withdrawal requests appear in the admin panel under "Coin withdrawal requests".
- Admins must use the "Approve selected withdrawal requests" or "Decline selected withdrawal requests" actions to process requests. (Changing status manually will NOT update balances or send emails.)
- Approved/declined withdrawals trigger email notifications to the user.
- Users see their withdrawal status/history on the wallet page.

## Background Tasks & Celery

This project uses **Celery** with **Redis** as the message broker for background tasks and periodic jobs.

### Celery Setup
1. **Install Redis**
   - On Ubuntu: `sudo apt install redis-server`
   - On Mac: `brew install redis`
   - On Windows: [Install from here](https://redis.io/download)
   - Start Redis: `redis-server`
2. **Install Celery and Redis Python dependencies**
   ```bash
   pip install celery redis
   ```
3. **Celery Configuration**
   - See `readmore/settings.py` for `CELERY_BROKER_URL` and `CELERY_BEAT_SCHEDULE`.
4. **Run Celery Worker and Beat**
   - Start the Celery worker:
     ```bash
     celery -A readmore worker --loglevel=info
     ```
   - Start the Celery beat scheduler (for periodic tasks):
     ```bash
     celery -A readmore beat --loglevel=info
     ```
   - **Both must be running** in production for scheduled/background tasks to work.

### Periodic Tasks
The following periodic tasks are configured:
- **Fetch News** (`news.tasks.fetch_news`): Runs every 30 minutes to fetch and update news articles.
- **Convert Points to Coins** (`news.tasks.convert_all_points_to_coins`): Runs daily at midnight (00:00), converting all user points to coins at the rate of 1000 points = 1 coin.

You can change the schedule in `CELERY_BEAT_SCHEDULE` in `settings.py`.

### Troubleshooting
- **Tasks not running?** Make sure both the worker and beat processes are running and Redis is active.
- **Production:** Use a process manager like systemd or supervisor to keep Celery worker and beat running.
- **Logs:** Check Celery logs for errors.
- **Redis connection issues:** Ensure Redis is running and accessible at the configured URL.

- Set up environment variables for secrets.
- Configure static and media file serving.

#### Example (Gunicorn + Nginx):
- Run: `gunicorn readmore.wsgi:application --bind 0.0.0.0:8000`
- Point nginx to proxy_pass `localhost:8000` and serve `/static/` from `staticfiles` directory.

---

## App Operation & User Flow

### User Side
- **Sign Up / Login:**
  - Users can register and log in with username or email.
  - Navbar is hidden on login/signup pages.
- **Dashboard:**
  - See points, coins, membership status, wallet address, and quick stats.
- **Profile:**
  - See and edit personal info, view balances, and rank.
- **News:**
  - Browse and read articles. Mark as read to earn points.
- **Tasks:**
  - Complete daily/manual tasks for bonus points.
- **Wallet:**
  - Save wallet address or connect MetaMask.
  - Buy coins: Enter coin amount, see real-time BNB equivalent, scan QR, transfer BNB, and wait for admin approval.
  - Automatic conversion: Points are auto-converted to coins at the set rate.
  - View transaction history.

### Admin Side
- **Admin Panel:** `/admin/`
  - Approve/decline coin purchase requests (credits coins to users).
  - Edit user balances (points and coins) inline.
  - Manage users, articles, tasks, and transactions.

### Coin Purchase Flow
1. User enters coin amount on wallet page.
2. BNB equivalent is shown in real time.
3. User clicks Buy, sees payment address and QR.
4. User transfers BNB and clicks Transferred.
5. Admin sees the request in admin panel and approves it.
6. On approval, coins are credited and user is notified.

### Points to Coins
- Points are automatically converted to coins whenever possible (rate set in code).
- All conversions are logged in transaction history.

---

## Configuration & Customization
- **Conversion Rate:** Set in `views_wallet.py` as `CONVERSION_RATE`.
- **BNB Wallet Address:** Set in wallet template JS or move to settings for easy change.
- **Memberships:** Premium/Regular logic in `UserProfile`.
- **Static Files:** Place images, JS, CSS in `/static/`.
- **Email/Notifications:** Add Django email backend for notifications.

---

## Security Notes
- Always set `DEBUG = False` in production.
- Set strong `SECRET_KEY` and keep it secret.
- Use HTTPS in production.
- Set proper `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
- Use strong admin passwords and restrict admin access.

---

## Troubleshooting
- **Login Loops:** Ensure login form has both `login` and `username` fields. Check `LOGIN_REDIRECT_URL`.
- **Static Files Not Loading:** Run `collectstatic` and configure nginx to serve `/static/`.
- **Database Errors:** Run `makemigrations` and `migrate`.
- **Celery/Redis Issues:** Ensure Redis is running if using Celery.

---

## Credits
- Built with Django, Tailwind CSS, and PostgreSQL/SQLite.
- QR code generation via [QRCode.js](https://github.com/davidshimjs/qrcodejs).

---

## License
MIT License (or specify your own)
