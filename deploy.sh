#!/bin/bash
# SEB OPS SYSTEM v5 - Deployment Script for PythonAnywhere
# Run this script in your PythonAnywhere bash console

set -e  # Exit on error

echo "🚀 Starting deployment of SEB OPS SYSTEM v5..."

# Step 1: Navigate to project directory
echo "📁 Step 1: Navigating to project directory..."
cd /home/Naskaus/TASKS

# Step 2: Backup current database
echo "💾 Step 2: Backing up current database..."
mkdir -p backups
BACKUP_FILE="backups/ops_backup_$(date +%Y%m%d_%H%M%S).db"
if [ -f "instance/ops.db" ]; then
    cp instance/ops.db "$BACKUP_FILE"
    echo "✅ Database backed up to: $BACKUP_FILE"
else
    echo "⚠️  No existing database found, skipping backup"
fi

# Step 3: Pull latest code from GitHub
echo "📥 Step 3: Pulling latest code from GitHub..."
git fetch origin
git pull origin main

# Step 4: Verify tag
echo "🏷️  Step 4: Verifying version tag..."
git tag | grep v0.21
echo "✅ Tag v0.21 found"

# Step 5: Activate virtual environment
echo "🐍 Step 5: Activating virtual environment..."
source .venv/bin/activate

# Step 6: Install/update dependencies
echo "📦 Step 6: Installing dependencies..."
pip install -r requirements.txt

# Step 7: Initialize database (if needed)
echo "🗄️  Step 7: Ensuring database is initialized..."
python << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database tables initialized")
EOF

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Go to PythonAnywhere Web tab"
echo "   2. Click the green 'Reload' button for TASKS-Naskaus.pythonanywhere.com"
echo "   3. Visit: https://TASKS-Naskaus.pythonanywhere.com/app"
echo "   4. Restore your data using the Restore button"
echo ""
echo "💡 Your database backup is at: $BACKUP_FILE"
