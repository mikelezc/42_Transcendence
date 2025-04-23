#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

ENV_FILE="srcs/.env"
ENV_EXAMPLE="srcs/env_example.md"

# Function to generate a random key
generate_key() {
    local length=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LC_ALL=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c $length
    else
        # Linux
        tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c $length
    fi
}

# Function to generate a 32-byte base64 key
generate_base64_key() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        head -c 32 /dev/urandom | base64
    else
        # Linux
        head -c 32 /dev/urandom | base64 -w 0
    fi
}

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}       Transcendence Environment Configuration           ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Check if .env file already exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Warning: $ENV_FILE already exists.${NC}"
    read -p "Do you want to overwrite it? [y/N]: " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Configuration cancelled. Existing .env file was not modified.${NC}"
        exit 0
    fi
fi

# Check if example file exists
if [ ! -f "$ENV_EXAMPLE" ]; then
    echo -e "${RED}Error: $ENV_EXAMPLE file not found${NC}"
    exit 1
fi

# Create .env based on example but without comments
echo -e "${GREEN}Creating .env file with default values...${NC}"

# Default values
DB_PASSWORD=$(generate_key 32)
DJANGO_SECRET=$(generate_key 50)
ENCRYPTION_KEY=$(generate_base64_key)
JWT_SECRET=$(generate_key 64)

# Detect local IP
IP_ADDRESS="localhost"
if command -v ip >/dev/null 2>&1; then
    # Linux
    DETECTED_IP=$(ip -4 addr show scope global | grep inet | head -n 1 | awk '{print $2}' | cut -d/ -f1)
    if [ -n "$DETECTED_IP" ]; then
        IP_ADDRESS=$DETECTED_IP
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DETECTED_IP=$(ipconfig getifaddr en0 2>/dev/null)
    if [ -n "$DETECTED_IP" ]; then
        IP_ADDRESS=$DETECTED_IP
    fi
fi

# Create .env file with default values
cat > "$ENV_FILE" << EOL
# PostgreSQL Configuration
SQL_ENGINE=django.db.backends.postgresql
POSTGRES_DB=transcendence
POSTGRES_USER=transcendence_user
POSTGRES_PASSWORD=${DB_PASSWORD}
SQL_HOST=db
SQL_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=${DJANGO_SECRET}
DJANGO_ALLOWED_HOSTS=localhost

# GDPR Configuration
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# IP server 
IP_SERVER=${IP_ADDRESS}

# 42 OAuth Web Application (demo values - for testing only)
FORTYTWO_CLIENT_ID=u-demo-app-id
FORTYTWO_CLIENT_SECRET=s-demo-app-secret
FORTYTWO_REDIRECT_URI=https://${IP_ADDRESS}:8445/login/

# 42 API Configuration (demo values - for testing only)
FORTYTWO_API_UID=u-demo-app-id
FORTYTWO_API_SECRET=s-demo-app-secret
FORTYTWO_API_URL=https://${IP_ADDRESS}:8445/login/

# Email Configuration (demo - won't send real emails)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=demo-sendgrid-key
DEFAULT_FROM_EMAIL=demo@example.com
SITE_URL=https://${IP_ADDRESS}:8443

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME=3600

# Vault Configuration (development only)
#VAULT_ROOT_TOKEN=myroot
#VAULT_LOG_TOKENS=true

# SSL Certificate Configuration
SSL_COUNTRY=ES
SSL_STATE=Madrid
SSL_LOCALITY=Madrid
SSL_ORGANIZATION=42
SSL_ORGANIZATIONAL_UNIT=42Madrid
SSL_COMMON_NAME=${IP_ADDRESS}
SSL_DAYS=365
SSL_KEY_SIZE=2048

# Celery Configuration
CELERY_USER=celeryuser

# Celery PostgreSQL SSL Configuration
CELERY_PGSSLMODE=require
CELERY_PGAPPNAME=celery_worker
CELERY_PGSSLCERT=/home/celeryuser/.postgresql/postgresql.crt
CELERY_PGSSLKEY=/home/celeryuser/.postgresql/postgresql.key
EOL

echo -e "${GREEN}.env file successfully created!${NC}"
echo -e "${YELLOW}Note: This file contains demo values for OAuth and Email.${NC}"
echo -e "${YELLOW}For a real production environment, you'll need to update these values.${NC}"

echo -e "\n${BLUE}Would you like to configure real credentials for external services?${NC}"
read -p "Configure 42 OAuth [y/N]: " setup_oauth
if [[ "$setup_oauth" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Enter your 42 Client ID:${NC}"
    read client_id
    echo -e "${BLUE}Enter your 42 Client Secret:${NC}"
    read client_secret
    
    # Update .env file with real credentials
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/FORTYTWO_CLIENT_ID=.*/FORTYTWO_CLIENT_ID=${client_id}/" "$ENV_FILE"
        sed -i '' "s/FORTYTWO_CLIENT_SECRET=.*/FORTYTWO_CLIENT_SECRET=${client_secret}/" "$ENV_FILE"
        sed -i '' "s/FORTYTWO_API_UID=.*/FORTYTWO_API_UID=${client_id}/" "$ENV_FILE"
        sed -i '' "s/FORTYTWO_API_SECRET=.*/FORTYTWO_API_SECRET=${client_secret}/" "$ENV_FILE"
    else
        # Linux
        sed -i "s/FORTYTWO_CLIENT_ID=.*/FORTYTWO_CLIENT_ID=${client_id}/" "$ENV_FILE"
        sed -i "s/FORTYTWO_CLIENT_SECRET=.*/FORTYTWO_CLIENT_SECRET=${client_secret}/" "$ENV_FILE"
        sed -i "s/FORTYTWO_API_UID=.*/FORTYTWO_API_UID=${client_id}/" "$ENV_FILE"
        sed -i "s/FORTYTWO_API_SECRET=.*/FORTYTWO_API_SECRET=${client_secret}/" "$ENV_FILE"
    fi
fi

read -p "Configure SendGrid for real emails [y/N]: " setup_email
if [[ "$setup_email" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Enter your SendGrid API Key:${NC}"
    read sendgrid_key
    echo -e "${BLUE}Enter your sender email address:${NC}"
    read from_email
    
    # Update .env file with real credentials
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/EMAIL_HOST_PASSWORD=.*/EMAIL_HOST_PASSWORD=${sendgrid_key}/" "$ENV_FILE"
        sed -i '' "s/DEFAULT_FROM_EMAIL=.*/DEFAULT_FROM_EMAIL=${from_email}/" "$ENV_FILE"
    else
        # Linux
        sed -i "s/EMAIL_HOST_PASSWORD=.*/EMAIL_HOST_PASSWORD=${sendgrid_key}/" "$ENV_FILE"
        sed -i "s/DEFAULT_FROM_EMAIL=.*/DEFAULT_FROM_EMAIL=${from_email}/" "$ENV_FILE"
    fi
fi

echo -e "\n${GREEN}Configuration completed!${NC}"
echo -e "Detected IP: ${IP_ADDRESS}"
echo -e "\n${BLUE}Instructions:${NC}"
echo -e "1. If you're using 42 OAuth, update your OAuth app in 42 to use:"
echo -e "   ${YELLOW}Redirect URI: https://${IP_ADDRESS}:8445/login/${NC}"
echo -e "2. Start the project with: ${YELLOW}make${NC}"
echo -e "3. To view logs and important messages: ${YELLOW}make logs${NC}"

# Make the script executable
chmod +x "$0"
