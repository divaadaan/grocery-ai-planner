#!/bin/bash
set -e

echo "🚀 Setting up secrets for Grocery AI Planner"

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Warning: Running as root. Consider using a non-root user."
fi

# Generate secrets if they don't exist
if [ ! -d "secrets" ]; then
    echo "📁 Creating secrets directory..."
    ./scripts/generate-secrets.sh
else
    echo "📁 Secrets directory already exists"
fi

# Validate required secrets exist and are not empty
required_secrets=("database_url.txt" "redis_url.txt" "secret_key.txt" "llm_api_url.txt")
missing_secrets=()

for secret in "${required_secrets[@]}"; do
    if [ ! -f "secrets/$secret" ] || [ ! -s "secrets/$secret" ]; then
        missing_secrets+=("$secret")
    fi
done

if [ ${#missing_secrets[@]} -ne 0 ]; then
    echo "❌ Missing or empty required secrets:"
    for secret in "${missing_secrets[@]}"; do
        echo "   - secrets/$secret"
    done
    echo ""
    echo "Please create these files with actual values before proceeding."
    exit 1
fi

# Validate secret file permissions
echo "🔒 Checking secret file permissions..."
find secrets -name "*.txt" -exec chmod 600 {} \;

echo "✅ Secrets setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review secret values in ./secrets/"
echo "  2. Run: docker-compose up -d"
echo "  3. Check health: curl http://localhost:8000/api/v1/health"