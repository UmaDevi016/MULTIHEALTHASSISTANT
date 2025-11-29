# 🚀 Quick Reference - Multilingual Health Assistant

## 📋 Quick Start Commands

### Setup (First Time)
```powershell
# Run automated setup
.\setup.ps1

# Or manually:
npm install
npm install -g @lingo/cli
docker-compose up --build -d
```

### Daily Development
```powershell
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Restart services
docker-compose restart
```

## 🌍 Supported Languages (11 Total)

| Language | Code | Script | Voice Support |
|----------|------|--------|---------------|
| Hindi | `hi` | हिन्दी | ✅ |
| Tamil | `ta` | தமிழ் | ✅ |
| Telugu | `te` | తెలుగు | ✅ |
| Bengali | `bn` | বাংলা | ✅ |
| **Malayalam** | `ml` | മലയാളം | ✅ ⭐ NEW |
| **Marathi** | `mr` | मराठी | ✅ ⭐ NEW |
| **Odia** | `or` | ଓଡ଼ିଆ | ✅ ⭐ NEW |
| Spanish | `es` | Español | ✅ |
| French | `fr` | Français | ✅ |
| Arabic | `ar` | العربية | ✅ |
| English | `en` | English | ✅ |

## 🎤 Voice Features

### Speech-to-Text (Input)
1. Click "🎤 Speak Your Message"
2. Allow microphone access
3. Speak in any supported language
4. Text appears automatically

### Text-to-Speech (Output)
1. Translate your message
2. Click "🔊 Listen to Translation"
3. Audio plays in target language

## 🔧 Lingo CLI Commands

```powershell
# Sync translations (bidirectional)
npm run lingo:sync

# Pull from Lingo platform
npm run lingo:pull

# Push to Lingo platform
npm run lingo:push

# Check Lingo status
lingo whoami
lingo status
```

## ☁️ Deployment

### Local (Docker)
```powershell
docker-compose up --build -d
```
- Frontend: http://localhost:8501
- Backend: http://localhost:8000

### Vultr Cloud
```powershell
$env:VULTR_API_KEY="your_key"
npm run deploy:vultr
```

## 📁 Important Files

### Configuration
- `.env` - Environment variables & API keys
- `docker-compose.yml` - Container orchestration
- `.lingorc` - Lingo CLI configuration
- `vultr-deploy.yml` - Vultr deployment config

### Application
- `frontend/streamlit_app.py` - Main UI
- `backend/app.py` - API server
- `backend/reminders.db` - Database

### Documentation
- `DEPLOYMENT_GUIDE.md` - Full deployment steps
- `UPDATE_SUMMARY.md` - Recent changes
- `VOICE_FEATURES.md` - Voice capabilities
- `QUICK_REFERENCE.md` - This file!

## 🔑 Environment Variables

Required in `.env` file:
```env
# Lingo (Translation Management)
LINGO_API_KEY=your_lingo_key
LINGO_PROJECT_ID=your_project_id

# OpenAI (Optional - Fallback)
OPENAI_API_KEY=your_openai_key

# Backend
BACKEND_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Container won't start
```powershell
docker-compose down
docker-compose up --build -d
```

### Speech not working
- Use Chrome or Edge browser
- Enable microphone permissions
- Ensure HTTPS (for production)
- Rebuild containers if needed

### Translation fails
- Check API keys in `.env`
- Verify backend is running: `docker-compose ps`
- Check logs: `docker-compose logs api`
- Falls back to Google Translate automatically

### Port already in use
```powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Change port in docker-compose.yml or kill process
```

## 📊 API Endpoints

### Backend (http://localhost:8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/translate` | POST | Translate text |
| `/speak` | POST | Text-to-speech |
| `/add-reminder` | POST | Add medicine reminder |
| `/reminders` | GET | Get all reminders |
| `/reminders/{id}` | DELETE | Delete reminder |

### Example API Call
```powershell
# Health check
curl http://localhost:8000/health

# Translate
curl -X POST http://localhost:8000/translate `
  -H "Content-Type: application/json" `
  -d '{"text":"Take medicine","target_lang":"hi"}'
```

## 💾 Backup & Restore

### Backup Database
```powershell
# Copy from container
docker-compose exec api cp /app/reminders.db /app/backup/

# Download to local
docker cp healthassistant_api:/app/reminders.db ./backup/
```

### Restore Database
```powershell
# Upload to container
docker cp ./backup/reminders.db healthassistant_api:/app/

# Restart container
docker-compose restart api
```

## 🔄 Update Application

```powershell
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up --build -d

# Sync translations
npm run lingo:sync
```

## 📱 Browser Compatibility

| Browser | STT | TTS | Notes |
|---------|-----|-----|-------|
| Chrome | ✅ | ✅ | Recommended |
| Edge | ✅ | ✅ | Recommended |
| Safari | ⚠️ | ✅ | Limited STT |
| Firefox | ❌ | ✅ | No STT support |

## 🎯 Testing Checklist

- [ ] Frontend loads at localhost:8501
- [ ] Backend responds at localhost:8000/health
- [ ] All 11 languages in dropdown
- [ ] Translation works for each language
- [ ] Voice input captures speech
- [ ] Voice output plays audio
- [ ] Can add/view reminders
- [ ] No errors in logs

## 📞 Quick Links

- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🎉 Success Indicators

✅ Backend returns `{"status": "ok"}`  
✅ Frontend loads without errors  
✅ Microphone works in browser  
✅ Translations appear correctly  
✅ Voice playback works  
✅ Reminders save successfully  

## ⚡ Performance Tips

1. **Restart containers** if slow: `docker-compose restart`
2. **Clear browser cache** for UI updates
3. **Check logs** for errors: `docker-compose logs -f`
4. **Monitor resources**: `docker stats`

## 🆘 Emergency Commands

```powershell
# Complete reset
docker-compose down -v
docker-compose up --build -d

# View all logs
docker-compose logs --tail=100

# Access container shell
docker-compose exec api bash
docker-compose exec frontend bash

# Check disk space
docker system df
docker system prune  # Clean up
```

---

**Version**: 2.0.0  
**Last Updated**: 2025-11-29  

**Made with ❤️ for accessible healthcare** 🌍
