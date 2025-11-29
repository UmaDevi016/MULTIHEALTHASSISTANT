# Setup Script for Multilingual Health Assistant
# This script installs necessary dependencies including Lingo CLI

Write-Host "🚀 Setting up Multilingual Health Assistant..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "📦 Checking for Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Node.js not found. Please install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check if npm is installed
Write-Host "📦 Checking for npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ npm not found. Please install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Install project dependencies
Write-Host ""
Write-Host "📦 Installing project dependencies..." -ForegroundColor Yellow
npm install

# Install Lingo CLI globally
Write-Host ""
Write-Host "📦 Installing Lingo CLI..." -ForegroundColor Yellow
try {
    npm install -g @lingo/cli
    Write-Host "✅ Lingo CLI installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Failed to install Lingo CLI globally. Trying local install..." -ForegroundColor Yellow
    npm install --save-dev @lingo/cli
}

# Verify Lingo CLI installation
Write-Host ""
Write-Host "🔍 Verifying Lingo CLI..." -ForegroundColor Yellow
try {
    $lingoVersion = lingo --version
    Write-Host "✅ Lingo CLI version: $lingoVersion" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Lingo CLI not available in PATH. Using npx instead." -ForegroundColor Yellow
}

# Check for Docker
Write-Host ""
Write-Host "🐳 Checking for Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Docker not found. Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}

# Check for Docker Compose
Write-Host ""
Write-Host "🐳 Checking for Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose found: $composeVersion" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Docker Compose not found. It's included with Docker Desktop." -ForegroundColor Yellow
}

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "📝 Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    
    $envContent = @"
# Lingo Configuration
LINGO_API_KEY=your_lingo_api_key_here
LINGO_PROJECT_ID=your_lingo_project_id_here

# Translation APIs (Optional)
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Backend Configuration
BACKEND_URL=http://localhost:8000

# Database
DB_PATH=/app/reminders.db
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Created .env file. Please update with your API keys." -ForegroundColor Green
}
else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update .env file with your API keys" -ForegroundColor White
Write-Host "  2. Run: docker-compose up --build -d" -ForegroundColor White
Write-Host "  3. Access frontend at: http://localhost:8501" -ForegroundColor White
Write-Host "  4. Access backend at: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🌍 Supported Languages (11 total):" -ForegroundColor Yellow
Write-Host "  • Hindi, Tamil, Telugu, Bengali" -ForegroundColor White
Write-Host "  • Malayalam, Marathi, Odia" -ForegroundColor White
Write-Host "  • Spanish, French, Arabic, English" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Lingo CLI Commands:" -ForegroundColor Yellow
Write-Host "  npm run lingo:sync  - Sync translations" -ForegroundColor White
Write-Host "  npm run lingo:pull  - Pull from Lingo" -ForegroundColor White
Write-Host "  npm run lingo:push  - Push to Lingo" -ForegroundColor White
Write-Host ""
Write-Host "☁️ Vultr Deployment:" -ForegroundColor Yellow
Write-Host "  npm run deploy:vultr - Deploy to Vultr cloud" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
