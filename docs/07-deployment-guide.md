# Deployment Guide



Instructions for deploying Becathlon to production environments.



## Pre-Deployment Checklist



- [ ] All tests passing: `python manage.py test`

- [ ] No DEBUG warnings: Check settings.py

- [ ] Environment variables configured

- [ ] Database migrations applied

- [ ] Static files collected

- [ ] CSS/JS minified

- [ ] Security headers configured

- [ ] HTTPS certificate ready

- [ ] Database backed up

- [ ] Error monitoring configured (e.g., Sentry)



## Environment Setup



### Production Environment Variables



Create `.env` or configure hosting platform:



```bash

# Django Settings

DEBUG=False

SECRET_KEY=<generate-secure-key>

ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

ENVIRONMENT=production



# Database (PostgreSQL recommended)

DATABASE_URL=postgres://user:password@host:5432/becathlon_prod



# AWS S3 (optional, for static/media files)

AWS_STORAGE_BUCKET_NAME=becathlon-prod

AWS_S3_REGION_NAME=us-east-1

AWS_ACCESS_KEY_ID=<key>

AWS_SECRET_ACCESS_KEY=<secret>



# Email Configuration

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

EMAIL_HOST=smtp.gmail.com

EMAIL_PORT=587

EMAIL_USE_TLS=True

EMAIL_HOST_USER=<email>

EMAIL_HOST_PASSWORD=<password>



# Security

SECURE_SSL_REDIRECT=True

SESSION_COOKIE_SECURE=True

CSRF_COOKIE_SECURE=True

```



## Deployment Platforms



### PWS (Current Platform)



Becathlon is deployed on PWS at: pbp.cs.ui.ac.id



**Deployment Process:**



1. Push to GitHub repository

2. PWS webhook detects push

3. Automatic deployment triggered

4. Tests run in CI/CD pipeline

5. Static files collected

6. Application restarted



**Configuration Files:**



`Procfile`:

```

web: gunicorn becathlon.wsgi --log-file -

release: python manage.py migrate

```



`runtime.txt`:

```

python-3.11.0

```



#### Heroku



```bash

# Install Heroku CLI

# Log in

heroku login



# Create app

heroku create becathlon-prod



# Add PostgreSQL

heroku addons:create heroku-postgresql:standard-0



# Configure environment variables

heroku config:set DEBUG=False

heroku config:set SECRET_KEY=<key>

heroku config:set ALLOWED_HOSTS=becathlon-prod.herokuapp.com



# Deploy

git push heroku main



# Run migrations

heroku run python manage.py migrate

```



## AWS EC2



```bash

# SSH into instance

ssh -i key.pem ubuntu@instance-ip



# Setup

sudo apt update && sudo apt upgrade -y

sudo apt install -y python3-pip python3-venv postgresql nginx



# Clone repo

git clone <repo-url>

cd becathlon



# Virtual environment

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt



# Database setup

python manage.py migrate



# Collect static files

python manage.py collectstatic --no-input



# Configure Gunicorn + Nginx (omitted for brevity)

```



## Database Migration



### From SQLite to PostgreSQL



```bash

# Export data from SQLite

python manage.py dumpdata > db.json



# Configure DATABASE_URL for PostgreSQL

export DATABASE_URL=postgres://user:password@host/becathlon



# Run migrations

python manage.py migrate



# Load data

python manage.py loaddata db.json

```



## Security Hardening



### Django Settings



```python

# settings.py for production



DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']



# HTTPS/SSL

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000  # 1 year

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True



# Security headers

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'



# Content Security Policy

CSP_DEFAULT_SRC = ("'self'",)

CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Tighten as needed

CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")



# CSRF

CSRF_TRUSTED_ORIGINS = [

    'https://yourdomain.com',

    'https://www.yourdomain.com',

]



# Database

if os.getenv('DATABASE_URL'):

    import dj_database_url

    DATABASES['default'] = dj_database_url.config(

        default=os.getenv('DATABASE_URL'),

        conn_max_age=600,

    )

```



## Dependencies Security



```bash

# Check for vulnerable packages

pip-audit



# Update all packages safely

pip install --upgrade pip setuptools wheel

pip install --upgrade -r requirements.txt



# Generate new requirements

pip freeze > requirements.txt

```



## Monitoring & Logging



### Sentry Integration



```bash

pip install sentry-sdk

```



```python

# settings.py

import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration



sentry_sdk.init(

    dsn=os.getenv('SENTRY_DSN'),

    integrations=[DjangoIntegration()],

    traces_sample_rate=0.1,

    send_default_pii=False,

)

```



## Logging Configuration



```python

LOGGING = {

    'version': 1,

    'disable_existing_loggers': False,

    'handlers': {

        'file': {

            'level': 'ERROR',

            'class': 'logging.FileHandler',

            'filename': '/var/log/becathlon/error.log',

        },

        'console': {

            'class': 'logging.StreamHandler',

        },

    },

    'root': {

        'handlers': ['file', 'console'],

        'level': 'INFO',

    },

}

```



### Health Check Endpoint



```python

# urls.py

from django.views.decorators.http import require_http_methods

from django.http import JsonResponse



@require_http_methods(["GET"])

def health_check(request):

    return JsonResponse({'status': 'healthy', 'version': '1.0'})



urlpatterns = [

    # ...

    path('health/', health_check),

]

```



## Performance Tuning



### Database Query Optimization



```python

# Use connection pooling

DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql',

        'CONN_MAX_AGE': 600,  # Connection pooling

        'OPTIONS': {

            'connect_timeout': 10,

        }

    }

}

```



## Caching



```python

CACHES = {

    'default': {

        'BACKEND': 'django.core.cache.backends.redis.RedisCache',

        'LOCATION': 'redis://127.0.0.1:6379/1',

        'OPTIONS': {

            'CLIENT_CLASS': 'django_redis.client.DefaultClient',

        },

        'KEY_PREFIX': 'becathlon',

        'TIMEOUT': 300,  # 5 minutes

    }

}



# Cache views

from django.views.decorators.cache import cache_page



@cache_page(60)  # Cache for 60 seconds

def catalog_home(request):

    # ...

```



## Static Files (WhiteNoise)



```python

# settings.py

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = '/static/'



STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

```



```bash

# Before deployment

python manage.py collectstatic --no-input

```



## Backup & Recovery



### Database Backup



```bash

# PostgreSQL backup

pg_dump -U postgres becathlon_prod > backup_$(date +%Y%m%d).sql



# Restore from backup

psql -U postgres becathlon_prod < backup_20251028.sql

```



## Automated Backups



Set up cron jobs:



```bash

# /etc/cron.d/becathlon_backup

0 2 * * * /home/ubuntu/becathlon/backup.sh

```



`backup.sh`:

```bash

#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -U postgres becathlon_prod > /backups/db_$DATE.sql

gzip /backups/db_$DATE.sql

```



## Rollback Procedure



### If Deployment Fails



```bash

# PWS - Revert to previous version

git revert <commit-sha>

git push origin main

# PWS will auto-deploy previous version



# Or manually rollback

git checkout <previous-commit>

git push -f origin main

```



## Database Rollback



```bash

# If migrations fail

python manage.py migrate <app> <previous-migration>



# Or restore from backup

psql -U postgres becathlon_prod < backup_20251027.sql

```



## Monitoring & Alerts



### Key Metrics to Monitor



- Error rate (500 errors)

- Response time (API latency)

- Database connection pool usage

- Disk space on server

- Memory/CPU usage

- Checkout completion rate

- Cart abandonment rate



### Setting Up Alerts



```bash

# Example with Sentry

# Configure alerts for:

# - Error rate threshold

# - Spike in 404 errors

# - Database connection failures

# - Performance regression

```



## Post-Deployment Verification



```bash

# Verify deployment

curl https://yourdomain.com/health/



# Check logs

tail -f /var/log/becathlon/error.log



# Smoke test

python manage.py shell

>>> from apps.main.models import Product

>>> Product.objects.count()

# Should return a number



# Test key features

# - Homepage loads

# - Product browsing works

# - Cart functionality

# - Checkout flow

# - Order confirmation

```



## Scaling Considerations



### Horizontal Scaling



```bash

# Multiple app servers

# - Load balancer (nginx, HAProxy)

# - Shared database (PostgreSQL)

# - Shared static files (S3, CDN)

# - Session store (Redis, database)

```



## Vertical Scaling



```bash

# Larger instances

# - More CPU cores

# - More RAM

# - Faster storage (SSD)

```



## Database Optimization



```sql

-- Index frequently queried columns

CREATE INDEX idx_product_type ON product(product_type_id);

CREATE INDEX idx_order_user ON order(user_id);

CREATE INDEX idx_cart_user ON cart(user_id);



-- Analyze query plans

EXPLAIN ANALYZE SELECT * FROM product WHERE product_type_id = 1;

```



---



**Resources**: [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

