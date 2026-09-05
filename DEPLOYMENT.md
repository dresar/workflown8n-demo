# SimpleFlow - cPanel Deployment Guide

This guide provides detailed instructions for deploying SimpleFlow on cPanel shared hosting.

## Prerequisites

- cPanel hosting account with Python support
- MySQL database access
- SSH access (recommended but optional)
- Domain or subdomain configured

## Step-by-Step Deployment

### 1. Prepare Your Local Project

```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt

# Collect static files locally for testing
python manage.py collectstatic --noinput
```

### 2. Create MySQL Database in cPanel

1. Login to cPanel
2. Go to **MySQL® Databases**
3. Create a new database (e.g., `username_simpleflow`)
4. Create a database user with strong password
5. Add user to database with ALL PRIVILEGES
6. Note down:
   - Database name
   - Database user
   - Database password
   - Database host (usually `localhost`)

### 3. Upload Files to cPanel

#### Option A: Using File Manager
1. Go to cPanel → File Manager
2. Navigate to your desired directory (e.g., `/home/username/simpleflow/`)
3. Upload all project files (except venv, __pycache__, *.pyc)

#### Option B: Using FTP
1. Use FTP client (FileZilla, WinSCP, etc.)
2. Connect to your server
3. Upload all project files

#### Option C: Using Git (if available)
```bash
ssh username@yourdomain.com
cd ~/
git clone your-repository-url simpleflow
cd simpleflow
```

### 4. Setup Virtual Environment

Via SSH (recommended):
```bash
ssh username@yourdomain.com
cd ~/simpleflow
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create `.env` file in project root:

```env
# Django Settings
SECRET_KEY=generate-a-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=username_simpleflow
DATABASE_USER=username_dbuser
DATABASE_PASSWORD=your-strong-password
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Google OAuth2
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/accounts/google/callback/

# WhatsApp Configuration
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id

# Security (for production)
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

**Important**: Generate a new SECRET_KEY:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 6. Update passenger_wsgi.py

Edit `passenger_wsgi.py` and update the path:

```python
# Change this line to match your cPanel username
INTERP = os.path.join(os.environ['HOME'], 'simpleflow', 'venv', 'bin', 'python')
```

### 7. Run Database Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # Create admin account
```

### 8. Setup Python App in cPanel

1. Login to cPanel
2. Find **Setup Python App** (or **Python Selector**)
3. Click **Create Application**
4. Configure:
   - **Python version**: 3.10 or higher
   - **Application root**: `/home/username/simpleflow`
   - **Application URL**: `/` or your subdomain
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`

5. Click **Create**

### 9. Configure Environment Variables in cPanel

In the Python App configuration page:
1. Scroll to **Environment variables**
2. Add each variable from your `.env` file:
   - SECRET_KEY
   - DEBUG
   - ALLOWED_HOSTS
   - DATABASE_NAME
   - DATABASE_USER
   - DATABASE_PASSWORD
   - etc.

### 10. Configure Static Files

#### Option A: Through Python App (Recommended)
The app will serve static files via WhiteNoise automatically.

#### Option B: Through Apache/nginx
Add to `.htaccess` in project root:

```apache
# Static files
RewriteEngine On
RewriteRule ^static/(.*)$ /home/username/simpleflow/staticfiles/$1 [L]
RewriteRule ^media/(.*)$ /home/username/simpleflow/media/$1 [L]
```

### 11. Set File Permissions

```bash
chmod 755 ~/simpleflow
chmod 755 ~/simpleflow/passenger_wsgi.py
chmod 644 ~/simpleflow/.env
chmod -R 755 ~/simpleflow/staticfiles
chmod -R 755 ~/simpleflow/media
```

### 12. Restart Application

In cPanel Python App interface, click **Restart**.

### 13. Test Deployment

1. Visit your domain: `https://yourdomain.com`
2. Test registration: Create a new account
3. Test login: Login with credentials
4. Test admin: Visit `/admin/` and login
5. Create a test workflow

## Troubleshooting

### Error: Application failed to start

**Check logs**:
- cPanel → Errors
- `/home/username/logs/` (if available)

**Common issues**:
1. Wrong Python version
2. Missing dependencies
3. Database connection failed
4. Incorrect passenger_wsgi.py path

### Error: Static files not loading

**Solutions**:
1. Run `python manage.py collectstatic --noinput`
2. Check STATIC_ROOT in settings.py
3. Verify file permissions
4. Check .htaccess rules

### Error: Database connection failed

**Check**:
1. Database credentials in .env
2. Database user has privileges
3. Database host is correct
4. MySQL server is running

### Error: 500 Internal Server Error

**Debug steps**:
1. Set `DEBUG=True` temporarily
2. Check error logs in cPanel
3. Verify all environment variables
4. Check file permissions

### Error: Google OAuth not working

**Fix**:
1. Add production URL to authorized redirect URIs in Google Console
2. Update GOOGLE_REDIRECT_URI in .env
3. Ensure HTTPS is enabled

## Maintenance

### Updating Code

```bash
ssh username@yourdomain.com
cd ~/simpleflow
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Restart app in cPanel.

### Backup Database

```bash
# Via command line
mysqldump -u username_dbuser -p username_simpleflow > backup.sql

# Or use cPanel phpMyAdmin
```

### Monitor Execution Logs

Check execution logs regularly in the web interface:
- Dashboard → Execution Logs
- Filter by status (success/error)
- Review failed workflows

## Performance Optimization

### 1. Enable Caching (Optional)

Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/username/django_cache',
    }
}
```

### 2. Optimize Database Queries

Monitor slow queries and add database indexes if needed.

### 3. Use Background Tasks

For long-running workflows, use django-background-tasks:
```python
from background_task import background

@background
def run_workflow_async(workflow_id, input_data):
    workflow = Workflow.objects.get(id=workflow_id)
    workflow.execute(input_data)
```

### 4. Configure WhiteNoise

Already configured in settings.py for optimal static file serving.

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] .env file not in public directory
- [ ] Database password is strong
- [ ] Admin password is strong
- [ ] Regular backups enabled

## Support

For cPanel-specific issues:
1. Contact your hosting provider
2. Check cPanel documentation
3. Review Python app error logs

For SimpleFlow issues:
1. Check README.md
2. Review Django logs
3. Check execution logs

---

**Congratulations!** Your SimpleFlow installation should now be running on cPanel. 🎉

