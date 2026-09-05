# SimpleFlow - Quick Start Guide

Get up and running with SimpleFlow in 5 minutes!

## 🚀 Quick Setup (Development)

### 1. Install Dependencies

```bash
# Activate virtual environment (if not already activated)
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Dependencies should already be installed, but if not:
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Start development server
python manage.py runserver
```

Visit: `http://localhost:8000`

### 3. Create Your First Account

1. Click **Register**
2. Fill in username, email, password
3. Click **Register**
4. You'll be automatically logged in

### 4. Add API Keys (Optional)

1. Go to **Profile**
2. Add your API keys:
   - **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Groq API Key**: Get from [Groq Console](https://console.groq.com/keys)
   - **WhatsApp Token**: Get from [Meta Developer Portal](https://developers.facebook.com/)
3. Click **Update API Keys**

### 5. Create Your First Workflow

1. Click **Create New Workflow**
2. Enter title: "Test Workflow"
3. Enter description: "My first automation"
4. Click **Create Workflow**

### 6. Add Nodes to Your Workflow

#### Example 1: Simple AI Text Generation

**Add Node:**
- **Name**: Generate Text
- **Type**: Gemini AI
- **Configuration**:
```json
{
  "prompt": "Write a short poem about automation",
  "model": "gemini-pro",
  "temperature": 0.7,
  "max_tokens": 500
}
```

#### Example 2: Read from Google Sheets (Requires Google OAuth)

**First, connect Google:**
1. Go to **Profile**
2. Click **Connect Google**
3. Authorize the app

**Add Node:**
- **Name**: Read Data
- **Type**: Google Sheets - Read
- **Configuration**:
```json
{
  "spreadsheet_id": "your-spreadsheet-id-here",
  "range": "Sheet1!A1:C10"
}
```

#### Example 3: Send WhatsApp Message (Requires WhatsApp Token)

**Add Node:**
- **Name**: Send Notification
- **Type**: WhatsApp - Send Message
- **Configuration**:
```json
{
  "to": "6281234567890",
  "message": "Workflow completed! Result: {{input}}"
}
```

### 7. Run Your Workflow

1. Click **Run Now** button
2. View execution in **Execution Logs**
3. Check the results!

### 8. Use Webhook Triggers

**Copy webhook URL** from workflow edit page:
```
http://localhost:8000/webhook/your-unique-token/
```

**Trigger via cURL:**
```bash
curl -X POST http://localhost:8000/webhook/your-unique-token/ \
  -H "Content-Type: application/json" \
  -d '{"data": "test input"}'
```

## 🎯 Common Workflow Patterns

### Pattern 1: AI Content Generator

```
1. Webhook Trigger (Receive topic)
   ↓
2. Gemini AI (Generate content)
   ↓
3. Google Docs Create (Save to document)
```

**Node 2 Config:**
```json
{
  "prompt": "Write a blog post about: {{input}}",
  "model": "gemini-pro",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Node 3 Config:**
```json
{
  "title": "Generated Content - {{input}}"
}
```

### Pattern 2: Spreadsheet Analyzer

```
1. Google Sheets Read (Get data)
   ↓
2. Groq AI (Analyze data)
   ↓
3. Google Sheets Write (Write analysis)
```

**Node 2 Config:**
```json
{
  "prompt": "Analyze this data and provide insights: {{input}}",
  "model": "mixtral-8x7b-32768",
  "temperature": 0.5,
  "max_tokens": 1000
}
```

### Pattern 3: Automated Reporter

```
1. Google Sheets Read (Get sales data)
   ↓
2. Gemini AI (Generate report)
   ↓
3. WhatsApp Send (Notify team)
```

## 📱 Mobile Access

SimpleFlow is mobile-responsive! Access from your phone:
- `http://your-ip:8000` (same network)
- Use ngrok for external access: `ngrok http 8000`

## 🔧 Troubleshooting

### Issue: "API key not configured"
**Solution**: Add your API keys in Profile page

### Issue: "Google credentials not found"
**Solution**: Click "Connect Google" in Profile page

### Issue: Workflow execution failed
**Solution**: 
1. Check Execution Log Details
2. Verify node configuration
3. Test individual nodes

### Issue: WhatsApp message not sending
**Solution**:
1. Verify WhatsApp token in Profile
2. Check phone number format (with country code)
3. Verify phone_number_id in settings

## 🎓 Next Steps

1. **Explore Templates**: Check PROJECT_SUMMARY.md for more examples
2. **Read Documentation**: See README.md for detailed info
3. **Deploy to Production**: Follow DEPLOYMENT.md guide
4. **Join Community**: Share your workflows!

## 💡 Pro Tips

1. **Use {{input}} placeholder** to reference previous node output
2. **Test nodes individually** before chaining
3. **Check execution logs** for debugging
4. **Copy webhook URLs** for external triggers
5. **Keep API keys secure** - never share them
6. **Start simple** - add complexity gradually
7. **Use descriptive node names** for clarity
8. **Document your workflows** in descriptions

## 🆘 Need Help?

- **README.md**: Comprehensive documentation
- **DEPLOYMENT.md**: Production deployment guide
- **PROJECT_SUMMARY.md**: Technical details
- **Django Docs**: https://docs.djangoproject.com

## 🎉 You're Ready!

Start automating your workflows with SimpleFlow!

---

**Happy Automating! 🚀**

