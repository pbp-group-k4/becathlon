# Deployment Guide

Instructions for deploying Becathlon to production environments.

## Deployment Platforms

### Current Deployment

**Platform:** PWS (Python Web Service)  
**URL:** https://pbp.cs.ui.ac.id/muhammad.vegard/becathlon  
**Database:** PostgreSQL  
**Server:** Gunicorn via WSGI  

### Supported Platforms

- PWS (Python Web Service) - Current
- Heroku (if configured)
- AWS / Azure (with proper setup)
- DigitalOcean App Platform
- PythonAnywhere

## Pre-Deployment Checklist

Before deploying, verify:

- [ ] All tests pass locally
- [ ] No hardcoded secrets in code
- [ ] `.gitignore` includes sensitive files
- [ ] Static files collected
- [ ] Database migrations up-to-date
- [ ] Environment variables documented
- [ ] Error logging configured
- [ ] DEBUG=False for production
- [ ] ALLOWED_HOSTS includes domain
- [ ] Email configuration working

## Environment Variables

Create `.env` file (not committed) or set system variables:

```bash
# Django Configuration
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# Database
DATABASE_URL=postgres://user:password@host:5432/becathlon_db

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (if sending emails)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (if using S3 for static/media)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
```

## PWS Deployment Steps

### 1. Prepare Repository

Ensure `.gitignore` contains:
```
*.pyc
__pycache__/
*.env
db.sqlite3
.DS_Store
node_modules/
venv/
staticfiles/
media/
.coverage
```

### 2. Create Procfile

```
web: gunicorn becathlon.wsgi:application --log-file -
worker: python manage.py process_tasks
clock: python manage.py clock
```

### 3. Prepare requirements.txt

```bash
pip freeze > requirements.txt
```

Or manually ensure includes:
```
Django==5.2.5
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
python-dotenv==0.21.0
pillow==12.0.0
```

### 4. Create runtime.txt (Optional)

```
python-3.11.0
```

### 5. Configure settings.py for Production

```python
import os
import dj_database_url

# Security
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Headers
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]

# Allowed Hosts
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
```

### 6. Create PWS Configuration

Contact PWS support or use their management panel to:

1. Set environment variables from `.env`
2. Configure PostgreSQL database
3. Set Python version to 3.9+
4. Configure domain and SSL

### 7. Deploy

**Via Git Push (if configured):**
```bash
git push origin main
```

**Via PWS Dashboard:**
1. Connect GitHub repository
2. Select main branch
3. Set environment variables
4. Deploy

### 8. Post-Deployment

```bash
# Via PWS shell or SSH

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Create superuser
python manage.py createsuperuser

# Load seed data
python seed_product_types.py
```

## Heroku Deployment (Alternative)

### 1. Create Heroku App

```bash
heroku create your-app-name
```

### 2. Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### 3. Set Environment Variables

```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
```

### 4. Deploy

```bash
git push heroku main
```

### 5. Run Migrations

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## AWS S3 for Static/Media Files

### 1. Install boto3

```bash
pip install boto3
```

### 2. Configure settings.py

```python
if os.environ.get('USE_S3') == 'True':
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### 3. Set AWS Credentials

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

## Monitoring & Logging

### Error Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### Health Check Endpoint

```python
# urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns += [
    path('health/', health_check),
]
```

Monitor with:
```bash
curl https://yourdomain.com/health/
```

### Sentry Integration (Error Tracking)

```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

## Database Backup

### Manual Backup (PostgreSQL)

```bash
# Backup
pg_dump becathlon_db > backup.sql

# Restore
psql becathlon_db < backup.sql
```

### Automated Backups

Most hosting platforms (PWS, Heroku) include automatic backups. Verify in dashboard.

## Performance Optimization for Production

### 1. Database Connection Pooling

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 2. Caching

```python
# Use Redis for caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 3. Compress Static Files

```python
# settings.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 4. Image Optimization

```bash
# Install
pip install Pillow

# Configure
# Use Pillow to compress images on upload
```

## Security Hardening

### 1. HTTPS/SSL

Ensure your domain uses:
- HTTPS for all traffic
- Valid SSL certificate
- HSTS headers enabled

```python
# settings.py
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. CSRF Protection

Verify all forms include CSRF token:
```html
<form method="post">
  {% csrf_token %}
  ...
</form>
```

### 3. SQL Injection Prevention

Always use Django ORM (parameterized queries):
```python
# Good
User.objects.filter(username=username)

# Bad (never do this!)
User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{username}'")
```

### 4. XSS Prevention

Always escape user input in templates:
```html
<!-- Good -->
<p>{{ user.bio }}</p>

<!-- Bad (never use safe without sanitizing!) -->
<p>{{ user.bio|safe }}</p>
```

### 5. Dependency Updates

```bash
# Check for security vulnerabilities
pip-audit

# Update packages
pip install --upgrade -r requirements.txt
```

## Rollback Plan

If deployment fails:

### 1. Identify Issue
- Check error logs
- Review recent commits
- Test locally

### 2. Rollback

**Via Git (if available):**
```bash
git revert <commit-hash>
git push origin main
```

**Via PWS:**
1. Redeploy previous version from dashboard
2. Restore database from backup if needed

### 3. Post-Rollback

- Verify application works
- Investigate issue offline
- Test thoroughly before re-deploying

## Monitoring Checklist

Daily:
- [ ] Check error logs for exceptions
- [ ] Monitor database disk usage
- [ ] Verify email notifications working
- [ ] Check slow query logs

Weekly:
- [ ] Review performance metrics
- [ ] Check security logs
- [ ] Verify backups completing
- [ ] Update packages (if security patches)

Monthly:
- [ ] Review cost and resource usage
- [ ] Update documentation
- [ ] Plan maintenance window
- [ ] Audit security settings

## Troubleshooting

### Deployment Hangs

**Cause:** Long-running migrations  
**Solution:** Run migrations locally first, test thoroughly

### Static Files Not Loading

**Cause:** collectstatic not run  
**Solution:**
```bash
python manage.py collectstatic --no-input
```

### Database Connection Error

**Cause:** DATABASE_URL not set correctly  
**Solution:**
```bash
# Verify URL format
postgres://user:password@host:5432/dbname
```

### Out of Memory

**Cause:** Memory limit exceeded  
**Solution:**
1. Optimize queries (add indexes)
2. Implement caching
3. Upgrade server tier

---

**Helpful Resources:**
- [Django Deployment Documentation](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
