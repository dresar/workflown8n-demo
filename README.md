# SimpleFlow - Workflow Automation Platform

A lightweight workflow automation platform similar to n8n or Zapier, specifically designed for cPanel shared hosting environments. Built with Django 5.x, SimpleFlow allows you to create automation workflows connecting AI services (Gemini, Groq), Google Services (Sheets, Docs, Drive, Photos), and WhatsApp messaging.

## 🚀 Features

- **AI Integration**: Connect with Google Gemini and Groq AI for intelligent text generation
- **Google Services**: Integrate with Sheets, Docs, Drive, and Photos
- **WhatsApp Messaging**: Send automated messages via Meta's Cloud API
- **Webhook Triggers**: Trigger workflows from external services
- **Secure Storage**: Encrypted API key storage
- **Execution Logs**: Complete monitoring and logging of workflow executions
- **cPanel Ready**: Optimized for shared hosting deployment

## 📋 Prerequisites

- Python 3.10 or higher
- Virtual environment (venv)
- SQLite (development) or MySQL (production)
- cPanel hosting (for production deployment)

## 🛠️ Installation

### 1. Clone and Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env_template` to `.env` and configure your settings:

```bash
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for dev, MySQL for production)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Google OAuth2 Credentials
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/accounts/google/callback/

# API Keys (Optional - users can set in profile)
DEFAULT_GEMINI_API_KEY=
DEFAULT_GROQ_API_KEY=

# WhatsApp Cloud API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=
```

### 4. Initialize Database

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 🎯 Usage

### Creating a Workflow

1. **Register/Login**: Create an account or login
2. **Set API Keys**: Go to Profile and add your API keys
3. **Connect Google**: (Optional) Connect your Google account for Google services
4. **Create Workflow**: Click "Create New Workflow"
5. **Add Nodes**: Add nodes to build your automation
6. **Configure Nodes**: Set up each node with appropriate configuration
7. **Activate**: Enable the workflow to make it active
8. **Test**: Run manually or trigger via webhook

### Node Types

#### AI Services
- **Gemini AI**: Text generation using Google's Gemini
- **Groq AI**: Fast inference with open-source models

#### Google Services
- **Google Sheets Read**: Read data from spreadsheets
- **Google Sheets Write**: Write data to spreadsheets
- **Google Docs Create**: Create new documents
- **Google Docs Append**: Append text to documents
- **Google Drive Upload**: Upload files to Drive
- **Google Drive List**: List files in Drive
- **Google Photos Upload**: Upload photos
- **Google Photos List**: List media items

#### Messaging
- **WhatsApp Send**: Send WhatsApp messages

### Node Configuration Examples

#### Gemini AI Node
```json
{
  "prompt": "Analyze this text: {{input}}",
  "model": "gemini-pro",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

#### Google Sheets Read Node
```json
{
  "spreadsheet_id": "your-spreadsheet-id",
  "range": "Sheet1!A1:C10"
}
```

#### WhatsApp Send Node
```json
{
  "to": "6281234567890",
  "message": "Hello! Here's your data: {{input}}"
}
```

### Using Webhooks

Each workflow has a unique webhook URL that can trigger execution:

```
POST https://yourdomain.com/webhook/your-webhook-token/
Content-Type: application/json

{
  "data": "your input data"
}
```

## 🚀 cPanel Deployment

### 1. Upload Files

Upload all project files to your cPanel hosting directory (e.g., `/home/username/simpleflow/`)

### 2. Setup Virtual Environment on cPanel

```bash
cd ~/simpleflow
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Database (MySQL)

Update `.env` with your MySQL credentials:

```
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

### 4. Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Setup Python App in cPanel

1. Go to cPanel → Setup Python App
2. Set Python version: 3.10 or higher
3. Application root: `/home/username/simpleflow`
4. Application URL: Your domain or subdomain
5. Application startup file: `passenger_wsgi.py`
6. Application Entry point: `application`

### 6. Configure Environment Variables

Add environment variables in cPanel Python App configuration:
- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS
- Database credentials
- API keys

### 7. Restart Application

Click "Restart" in cPanel Python App interface.

## 📁 Project Structure

```
simpleflow/
├── accounts/               # User authentication & profiles
│   ├── models.py          # UserProfile, Credential models
│   ├── views.py           # Auth views
│   └── urls.py
├── workflows/             # Workflow management
│   ├── models.py          # Workflow, Node, ExecutionLog
│   ├── views.py           # Workflow CRUD & execution
│   ├── executor.py        # Workflow execution engine
│   ├── node_executor.py   # Node execution logic
│   ├── services/          # Integration services
│   │   ├── ai_service.py      # Gemini & Groq
│   │   ├── google_service.py  # Google APIs
│   │   └── whatsapp_service.py # WhatsApp API
│   └── urls.py
├── templates/             # HTML templates (Tailwind CSS)
├── static/                # Static files
├── media/                 # User uploads
├── simpleflow/           # Django project settings
│   ├── settings.py
│   └── urls.py
├── passenger_wsgi.py     # cPanel WSGI configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔐 Security

- **API Key Encryption**: All API keys are encrypted using Fernet (symmetric encryption)
- **OAuth2 Tokens**: Refresh tokens stored encrypted
- **CSRF Protection**: Enabled for all forms
- **HTTPS**: Recommended for production
- **Environment Variables**: Sensitive data in `.env` file

## 🧪 API Keys Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Add to profile in SimpleFlow

### Groq API
1. Visit [Groq Console](https://console.groq.com/keys)
2. Create API key
3. Add to profile in SimpleFlow

### Google OAuth2
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth2 credentials
3. Add authorized redirect URI: `http://yourdomain.com/accounts/google/callback/`
4. Add to `.env` file

### WhatsApp Cloud API
1. Visit [Meta Developer Portal](https://developers.facebook.com/)
2. Create WhatsApp Business API app
3. Get access token and phone number ID
4. Add to profile in SimpleFlow

## 📝 Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Access
Visit `/admin/` to access Django admin panel.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available for personal and commercial use.

## 🆘 Support

For issues and questions:
1. Check this README
2. Review Django documentation
3. Check API provider documentation

## 🎉 Credits

Built with:
- Django 5.x
- Tailwind CSS (via CDN)
- Google APIs
- Groq AI
- Meta WhatsApp Cloud API

---

**SimpleFlow** - Automate your workflows, simplify your life! 🚀

