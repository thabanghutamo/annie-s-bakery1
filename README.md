# Annie's Bakery

A fully-featured e-commerce website and CMS for a bakery, built with Flask, Tailwind CSS, and JSON storage.

## Features

### Public Site
- Product catalog with shopping cart
- Custom cake/pastry order form
- Blog with categories and scheduling
- Contact form with Google Maps
- Secure checkout with multiple payment options
- Order status tracking

### Admin Dashboard
- Product management (add, edit, delete, visibility)
- Blog post management with scheduling
- Order processing and status updates
- Custom order management
- Payment gateway settings
- Order exports to CSV
- Analytics dashboard

### Technical Features
- Flask + Tailwind CSS architecture
- JSON file storage (no SQL database needed)
- Multiple payment gateway support:
  - Stripe integration
  - Paystack integration (placeholder)
  - Yoco integration (placeholder)
- Email notifications
- File uploads for products and blog posts
- Form validation and sanitization
- Comprehensive test suite
- Admin authentication
- Responsive design

## Quick Start

1. Create and activate virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Unix/macOS
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file:

```ini
# Flask settings
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Email settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Payment gateway (choose: stripe, paystack, yoco)
PAYMENT_PROVIDER=stripe
STRIPE_API_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Store information
STORE_NAME=Annie's Bakery
STORE_ADDRESS=123 Baker Street
STORE_PHONE=(555) 123-4567
STORE_EMAIL=hello@example.com
GOOGLE_MAPS_EMBED_KEY=your-google-maps-key
```

4. Create admin user:

```powershell
# Windows PowerShell
$env:FLASK_APP = "app.py"
python scripts/create_admin.py --email admin@example.com --password your-password

# Unix/macOS
export FLASK_APP=app.py
python scripts/create_admin.py --email admin@example.com --password your-password
```

5. Run the app:

```powershell
# Windows PowerShell
$env:FLASK_APP = "app.py"
flask run

# Unix/macOS
export FLASK_APP=app.py
flask run
```

Visit:
- Website: http://localhost:5000
- Admin: http://localhost:5000/admin

## Project Structure

```
annies/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── data/                 # JSON storage
│   ├── blog.json
│   ├── custom_orders.json
│   ├── orders.json
│   └── products.json
├── models/              # Data models
│   └── user.py
├── routes/             # Route handlers
│   ├── admin_routes.py
│   ├── auth_routes.py
│   ├── order_routes.py
│   └── public_routes.py
├── scripts/           # Utility scripts
│   └── create_admin.py
├── static/           # Assets
│   ├── js/          # JavaScript
│   │   └── cart.js  # Cart functionality
│   └── uploads/     # Uploaded files
├── templates/        # HTML templates
│   ├── admin/       # Admin interface
│   └── public/      # Public pages
├── tests/           # Test suite
│   ├── test_admin_routes.py
│   ├── test_auth.py
│   ├── test_payment.py
│   └── test_public_routes.py
└── utils/          # Utilities
    ├── email_utils.py
    ├── json_store.py
    ├── payment.py
    └── scheduler.py
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_public_routes.py

# Run with coverage
pytest --cov=.

# Generate coverage report
pytest --cov=. --cov-report=html
```

### Code Style

```bash
# Run linter
flake8 .

# Run type checker
mypy .
```

## Production Deployment

1. Set environment variables:
   - FLASK_ENV=production
   - Strong SECRET_KEY
   - SMTP settings
   - Payment keys
   - Store info

2. Set up SSL/TLS for HTTPS

3. Configure web server (nginx example):

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/annies/static;
        expires 30d;
    }
}
```

4. Use process manager (supervisor example):

```ini
[program:annies]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
directory=/path/to/annies
user=www-data
autostart=true
autorestart=true
```

5. Set up backups:

```bash
# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=/path/to/backups
mkdir -p $BACKUP_DIR/$DATE
cp /path/to/annies/data/*.json $BACKUP_DIR/$DATE/
```

Add to crontab:
```
0 0 * * * /path/to/backup.sh
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## License

MIT License - see LICENSE file
