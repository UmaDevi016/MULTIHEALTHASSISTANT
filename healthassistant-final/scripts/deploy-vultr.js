#!/usr/bin/env node

/**
 * Vultr Deployment Script for Multilingual Health Assistant
 * This script automates deployment to Vultr cloud infrastructure
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuration
const VULTR_API_KEY = process.env.VULTR_API_KEY;
const VULTR_API_URL = 'https://api.vultr.com/v2';

if (!VULTR_API_KEY) {
    console.error('❌ Error: VULTR_API_KEY environment variable not set');
    console.log('Please set your Vultr API key:');
    console.log('  export VULTR_API_KEY=your_api_key_here');
    process.exit(1);
}

// Load deployment configuration
const deployConfig = require('../vultr-deploy.yml');

console.log('🚀 Starting Vultr Deployment...\n');

/**
 * Make API request to Vultr
 */
function vultrRequest(method, endpoint, data = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.vultr.com',
            port: 443,
            path: `/v2${endpoint}`,
            method: method,
            headers: {
                'Authorization': `Bearer ${VULTR_API_KEY}`,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(JSON.parse(body || '{}'));
                } else {
                    reject(new Error(`API Error: ${res.statusCode} - ${body}`));
                }
            });
        });

        req.on('error', reject);

        if (data) {
            req.write(JSON.stringify(data));
        }

        req.end();
    });
}

/**
 * Deploy to Vultr
 */
async function deploy() {
    try {
        console.log('📋 Step 1: Checking Vultr account...');
        const account = await vultrRequest('GET', '/account');
        console.log(`✅ Account verified: ${account.account.email || 'Active'}\n`);

        console.log('🔍 Step 2: Fetching available regions...');
        const regions = await vultrRequest('GET', '/regions');
        console.log(`✅ Found ${regions.regions?.length || 0} regions\n`);

        console.log('📦 Step 3: Creating server instance...');
        const instanceData = {
            region: 'ewr',
            plan: 'vc2-1c-1gb',
            os_id: 387, // Ubuntu 22.04 x64
            label: 'health-assistant',
            hostname: 'health-assistant',
            enable_ipv6: true,
            backups: 'enabled',
            user_data: generateUserData()
        };

        const instance = await vultrRequest('POST', '/instances', instanceData);
        console.log(`✅ Server created: ${instance.instance?.id || 'pending'}\n`);

        console.log('⏳ Step 4: Waiting for server to be ready...');
        console.log('   This may take 2-5 minutes...\n');

        console.log('✅ Deployment initiated successfully!');
        console.log('\n📝 Next steps:');
        console.log('   1. Wait for server to finish provisioning');
        console.log('   2. SSH into server and verify deployment');
        console.log('   3. Configure DNS to point to server IP');
        console.log('   4. Set up SSL certificate with Let\'s Encrypt');
        console.log('\n🌐 Access your app at: http://<server-ip>:8501');

    } catch (error) {
        console.error('\n❌ Deployment failed:', error.message);
        process.exit(1);
    }
}

/**
 * Generate cloud-init user data script
 */
function generateUserData() {
    return `#!/bin/bash
# Health Assistant Auto-Setup Script

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Lingo CLI
npm install -g @lingo/cli

# Create app directory
mkdir -p /app
cd /app

# Clone repository (update with your repo URL)
# git clone https://github.com/your-username/health-assistant.git .

# Set environment variables
cat > /app/.env << EOF
LINGO_API_KEY=${process.env.LINGO_API_KEY || 'your_lingo_api_key'}
LINGO_PROJECT_ID=${process.env.LINGO_PROJECT_ID || 'your_project_id'}
GROQ_API_KEY=${process.env.GROQ_API_KEY || ''}
OPENAI_API_KEY=${process.env.OPENAI_API_KEY || ''}
BACKEND_URL=http://localhost:8000
EOF

# Start application
# docker-compose up -d --build

echo "✅ Server setup complete!"
echo "Please upload your application files and run: docker-compose up -d --build"
`;
}

// Run deployment
deploy();
