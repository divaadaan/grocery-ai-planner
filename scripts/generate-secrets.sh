#!/bin/bash
set -e

echo "🔐 Generating Docker Secrets"

# Create secrets directory
mkdir -p secrets
chmod 700 secrets

# Generate strong secret key
echo "Generating secret key..."
openssl rand -base64 32 > secrets/secret_key.txt

# Create template files with instructions
cat > secrets/database_url.txt << 'EOF'
postgresql://postgres:your_password@postgres:5432/grocery_planner
EOF

cat > secrets/redis_url.txt << 'EOF'
redis://redis:6379/0
EOF

cat > secrets/llm_api_url.txt << 'EOF'
http://host.docker.internal:11434/api/generate
EOF

# Optional secrets (empty by default)
touch secrets/google_maps_api_key.txt
touch secrets/mail_username.txt
touch secrets/mail_password.txt

# Set proper permissions
chmod 600 secrets/*.txt

echo "✅ Secret files created in ./secrets/"
echo "⚠️  Edit the files with your actual values before running docker-compose"
echo ""
echo "Required edits:"
echo "  - secrets/database_url.txt (set your DB password)"
echo "  - secrets/redis_url.txt (if using Redis auth)"
echo "  - secrets/llm_api_url.txt (your LLM endpoint)"
echo ""
echo "Optional edits:"
echo "  - secrets/google_maps_api_key.txt"
echo "  - secrets/mail_username.txt"
echo "  - secrets/mail_password.txt"