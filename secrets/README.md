# Docker Secrets

This directory contains sensitive configuration data mounted as Docker secrets.

## Required Secret Files

Create these files with actual values before running docker-compose:

- `database_url.txt` - PostgreSQL connection string
- `redis_url.txt` - Redis connection string  
- `secret_key.txt` - Application secret key
- `google_maps_api_key.txt` - Google Maps API key (optional)
- `mail_password.txt` - Email SMTP password (optional)
- `mail_username.txt` - Email SMTP username (optional)
- `llm_api_url.txt` - LLM API endpoint URL

## File Format

Each file should contain only the secret value, no quotes or extra whitespace: