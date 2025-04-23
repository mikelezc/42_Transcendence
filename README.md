# 42 Transcendence

A full-featured web application with a real-time multiplayer Pong game, user authentication, chat system, and tournament features. Built with Django, PostgreSQL, and secure containerized architecture.

## About This Project

Transcendence is a web platform that offers:
- Classic Pong game with multiplayer functionality
- User authentication (local and OAuth)
- Real-time chat system
- Tournament organization
- Secure architecture with Web Application Firewall

## Quick Deployment

### 1. Setup the Environment

Run the automated setup script:

```bash
# Give execution permissions
chmod +x setup_env.sh

# Execute the script
./setup_env.sh
```

This script automatically:
- Generates secure credentials
- Sets demo values for external services
- Detects your local IP address
- Allows customization of OAuth and email settings if needed

### 2. Deploy the Application

```bash
# Deploy using Docker Compose
make
```

### 3. Access the Application

After deployment, access the application at:
- **Main URL**: https://localhost:8445

## Additional Commands

```bash
# View logs
make logs

# Stop the application
make down

# Reset the application (keeping the database)
make re

# Reset completely (including database)
make fcleandb
```

## Testing the Application

For security testing, run:
```bash
# Run the WAF security tests
chmod +x security_tests/WAF/test_waf.sh
./security_tests/WAF/test_waf.sh
```

## Important Notes

- For a publicly accessible deployment, run `./configure_ip.sh` to detect and use your external IP
- Demo mode uses placeholder OAuth credentials - real OAuth integration requires valid 42 API credentials
- Never commit the `.env` file to version control

## Authors

- mlezcano - [GitHub Profile](https://github.com/mikelezc)
- ampjimen - [GitHub Profile](https://github.com/Amparojd)
- vpeinado - [GitHub Profile](https://github.com/v-peinado)
