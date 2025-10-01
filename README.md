🛡️ Django Authentication API

A secure authentication system built with Django REST Framework (DRF) and JWT.
It supports:

✅ User Registration with email verification (OTP)
✅ Login with JWT tokens (Access & Refresh)
✅ Password Reset via email
✅ Google OAuth2 Sign-In
✅ Protected routes with JWT authentication


🚀 Features

Custom User Model (register.User)

JWT Authentication using SimpleJWT

Email Verification via OTP codes

Password Reset with secure token validation

Google Sign-In using OAuth2

CORS Support for frontend integration



🛠️ Tech Stack

Backend: Django, Django REST Framework

Authentication: SimpleJWT, OAuth2 (Google)

Database: SQLite (dev), PostgreSQL/MySQL (production-ready)

Email Service: Mailtrap SMTP (can be swapped for Gmail, SES, SendGrid, etc.)

Deployment: Works on any WSGI/ASGI server (Gunicorn, Nginx, etc.)

⚙️ Setup Instructions

1️⃣ Clone Repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

🔐 Authentication Flow

Register → User provides email & password.

Verify OTP → User confirms email with OTP sent to inbox.

Login → JWT tokens (access & refresh) are returned.

Password Reset → Request link via email → Set new password.

Google Sign-In → Authenticate using Google OAuth2 access token

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.
