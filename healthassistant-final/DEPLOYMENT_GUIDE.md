# 🚀 Deployment Guide for Multilingual Health Assistant

## Overview
This guide covers deploying the Multilingual Health Assistant with **Lingo CLI** integration and **Vultr** hosting.

---

## 📋 Prerequisites

### Required Tools
- ✅ **Docker** and **Docker Compose**
- ✅ **Node.js** and **npm** (for Lingo CLI)
- ✅ **Git**
- ✅ **Vultr Account** (for cloud deployment)

### API Keys
- 🔑 **Lingo API Key** - For translation management
- 🔑 **OpenAI API Key** (optional) - For enhanced translations
- 🔑 **Vultr API Key** - For automated deployment

---

## 🎯 Part 1: Setting Up Lingo CLI

### Step 1: Install Lingo CLI

```powershell
# Install Lingo CLI globally
npm install -g @lingo/cli

# Verify installation
lingo --version
```

### Step 2: Configure Lingo

```powershell
# Initialize Lingo in your project
cd e:\multihealthassistantfinal\healthassistant-final

# Configure environment variables
$env:LINGO_API_KEY="your_lingo_api_key_here"
$env:LINGO_PROJECT_ID="your_project_id_here"

# Test Lingo connection
lingo whoami
```

### Step 3: Sync Translations

```powershell
# Pull latest translations from Lingo
npm run lingo:pull

# Push local translations to Lingo
npm run lingo:push

# Sync bidirectionally
npm run lingo:sync
```

### Lingo Configuration Files

The project includes:
- **`.lingorc`** - Main Lingo configuration
- **`lingo.config.json`** - Legacy config (backward compatible)
- **`package.json`** - npm scripts for Lingo commands

---

## 🌐 Part 2: Local Deployment with Docker

### Step 1: Set Environment Variables

Create a `.env` file in the project root:

```env
# Lingo Configuration
LINGO_API_KEY=your_lingo_api_key
LINGO_PROJECT_ID=your_project_id

# Translation APIs
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key

# Backend Configuration
BACKEND_URL=http://localhost:8000
```

### Step 2: Build and Run

```powershell
# Navigate to project directory
cd e:\multihealthassistantfinal\healthassistant-final

# Build and start all services
docker-compose up --build -d

# Check logs
docker-compose logs -f

# Verify services are running
docker-compose ps
```

### Step 3: Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Health**: http://localhost:8000/health

---

## ☁️ Part 3: Vultr Cloud Deployment

### Option A: Automated Deployment (Recommended)

```powershell
# Set Vultr API key
$env:VULTR_API_KEY="your_vultr_api_key"

# Run deployment script
npm run deploy:vultr
```

The script will:
1. ✅ Create a Vultr instance
2. ✅ Install Docker and dependencies
3. ✅ Set up the application
4. ✅ Configure networking and ports

### Option B: Manual Deployment

#### Step 1: Create Vultr Instance

1. Log in to [Vultr Dashboard](https://my.vultr.com)
2. Click "Deploy New Server"
3. Choose:
   - **Server Type**: Cloud Compute - Shared CPU
   - **Location**: Choose closest to users (e.g., Newark)
   - **Server Image**: Ubuntu 22.04 x64
   - **Server Size**: 1 CPU, 1GB RAM ($6/month minimum)
   - **Additional Features**: Enable IPv6, Backups

#### Step 2: SSH into Server

```powershell
ssh root@your-server-ip
```

#### Step 3: Install Dependencies

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Lingo CLI
npm install -g @lingo/cli
```

#### Step 4: Deploy Application

```bash
# Create app directory
mkdir -p /app
cd /app

# Upload your code (use git, scp, or sftp)
git clone https://github.com/your-username/health-assistant.git .

# Or use SCP from local machine:
# scp -r e:\multihealthassistantfinal\healthassistant-final/* root@your-server-ip:/app/

# Create .env file
nano .env
# Add your environment variables (see Step 1 above)

# Build and run
docker-compose up -d --build
```

#### Step 5: Configure Firewall

```bash
# Allow necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 8501  # Streamlit
ufw allow 8000  # Backend API
ufw enable
```

#### Step 6: Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Install Nginx
apt-get install -y nginx

# Configure Nginx reverse proxy
nano /etc/nginx/sites-available/health-assistant

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/health-assistant /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get SSL certificate
certbot --nginx -d your-domain.com
```

---

## 🔧 Part 4: Speech-to-Text in Deployment

### Why Speech-to-Text May Not Work

The issue occurs when system dependencies are missing in Docker containers.

### Solution (Already Implemented)

The updated Dockerfiles now include:

#### Backend Dockerfile
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    portaudio19-dev \
    libportaudio2 \
    flac \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

#### Frontend Dockerfile
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    portaudio19-dev \
    libportaudio2 \
    flac \
    ffmpeg \
    libasound2-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*
```

### Testing Speech-to-Text

After deployment:

1. Access the application in your browser
2. Click "🎤 Speak Your Message"
3. Allow microphone access
4. Speak clearly in any supported language
5. Verify text appears in the input field

---

## 🌍 Supported Languages

The application now supports **11 languages**:

### South Indian Languages
- 🇮🇳 **Hindi** (हिन्दी)
- 🇮🇳 **Tamil** (தமிழ்)
- 🇮🇳 **Telugu** (తెలుగు)
- 🇮🇳 **Bengali** (বাংলা)
- 🇮🇳 **Malayalam** (മലയാളം) - **NEW!**
- 🇮🇳 **Marathi** (मराठी) - **NEW!**
- 🇮🇳 **Odia** (ଓଡ଼ିଆ) - **NEW!**

### International Languages
- 🇪🇸 **Spanish** (Español)
- 🇫🇷 **French** (Français)
- 🇸🇦 **Arabic** (العربية)
- 🇬🇧 **English**

---

## 📊 Monitoring and Maintenance

### Check Application Status

```powershell
# Local
docker-compose ps
docker-compose logs -f

# Vultr (SSH into server)
ssh root@your-server-ip
cd /app
docker-compose ps
docker-compose logs -f api
docker-compose logs -f frontend
```

### Update Application

```powershell
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up --build -d

# Sync translations
npm run lingo:sync
```

### Backup Database

```powershell
# Local
docker-compose exec api cp /app/reminders.db /app/backup/

# Vultr
ssh root@your-server-ip
cd /app
docker-compose exec api cp /app/reminders.db /app/backup/
scp root@your-server-ip:/app/backup/reminders.db ./local-backup/
```

---

## 🔍 Troubleshooting

### Issue: Backend not reachable

**Solution:**
```powershell
# Check if containers are running
docker-compose ps

# Restart services
docker-compose restart

# Check logs for errors
docker-compose logs api
```

### Issue: Speech-to-text not working

**Solution:**
1. Ensure browser has microphone permissions
2. Use Chrome or Edge (best compatibility)
3. Check if HTTPS is enabled (required for microphone access)
4. Verify Docker containers have audio dependencies (already added)

### Issue: Translations failing

**Solution:**
```powershell
# Verify API keys are set
docker-compose exec api env | grep API_KEY

# Check Lingo configuration
lingo whoami
npm run lingo:sync

# Fall back to Google Translate (automatic in code)
```

### Issue: Port already in use

**Solution:**
```powershell
# Stop conflicting services
netstat -ano | findstr :8501
netstat -ano | findstr :8000

# Kill process or change ports in docker-compose.yml
```

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ Backend health check returns `{"status": "ok"}`  
✅ Frontend loads at the correct URL  
✅ Speech-to-text works in browser  
✅ Translations work for all 11 languages  
✅ Reminders can be added and retrieved  
✅ Voice output (text-to-speech) plays correctly  

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review environment variables in `.env`
- Verify API keys are correct
- Ensure all dependencies are installed

---

## 🚀 Quick Reference Commands

```powershell
# Install Lingo CLI
npm install -g @lingo/cli

# Local deployment
docker-compose up --build -d

# Vultr deployment
npm run deploy:vultr

# Sync translations
npm run lingo:sync

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

---

**Made with ❤️ for accessible healthcare worldwide**
