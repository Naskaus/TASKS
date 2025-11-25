# SEB OPS SYSTEM v5 - Deployment Guide

## 📋 JSON Compatibility Verification

✅ **Your JSON backup is FULLY COMPATIBLE with v0.21**

The JSON structure matches perfectly:
- **Categories**: `id`, `name`, `color`, `order` ✅
- **People**: `id`, `name` ✅
- **Tasks**: `id`, `category_id`, `person_id`, `text`, `done`, `order` ✅
- **Notes**: `id`, `task_id`, `date`, `content` ✅

All fields are supported by the current database schema and restore endpoint.

---

## 🚀 Deployment to PythonAnywhere

Based on your screenshot, you already have the app deployed at `TASKS-Naskaus.pythonanywhere.com`. Here's how to update it:

### **Step 1: Access Your PythonAnywhere Console**

1. Go to [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Login to your account
3. Navigate to **Consoles** → Click on **Bash**

### **Step 2: Update Your Code**

```bash
# Navigate to your project directory
cd /home/Naskaus/TASKS

# Pull the latest changes from GitHub
git fetch origin
git pull origin main

# Verify you have the latest tag
git tag
# Should show v0.21
```

### **Step 3: Install/Update Dependencies**

```bash
# Activate your virtual environment
source .venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt
```

### **Step 4: Backup Current Database (Important!)**

Before making any changes, backup your current production database:

```bash
# Navigate to your app directory
cd /home/Naskaus/TASKS

# Create a backup directory if it doesn't exist
mkdir -p backups

# Backup current database
cp instance/ops.db backups/ops_backup_$(date +%Y%m%d_%H%M%S).db
```

### **Step 5: Reload Your Web App**

1. Go to **Web** tab in PythonAnywhere
2. Find your web app: `TASKS-Naskaus.pythonanywhere.com`
3. Click the green **Reload** button

Your app should now be running the latest v0.21 code!

---

## 📥 Restoring Your Data from JSON

You have two options to restore your data:

### **Option A: Using the Web Interface (Recommended)**

1. Open your app: `https://TASKS-Naskaus.pythonanywhere.com/app`
2. Click the **Restore** button (📥 icon)
3. Paste your JSON data
4. Click **Restore**

### **Option B: Using API Directly**

```bash
# Save your JSON to a file
cat > restore_data.json << 'EOF'
{
  "categories": [...],
  "people": [...],
  "tasks": [...],
  "notes": [...]
}
EOF

# Use curl to restore
curl -X POST https://TASKS-Naskaus.pythonanywhere.com/api/restore \
  -H "Content-Type: application/json" \
  -d @restore_data.json
```

---

## 🔍 Verification Steps

After deployment, verify everything works:

1. ✅ Visit `https://TASKS-Naskaus.pythonanywhere.com/app`
2. ✅ Check all 8 categories are displayed
3. ✅ Verify all 40 tasks are visible
4. ✅ Test adding a new task
5. ✅ Test marking a task as done
6. ✅ Test adding notes to tasks
7. ✅ Test PDF export functionality
8. ✅ Test backup functionality

---

## 📊 Your Current Data Summary

Your JSON contains:
- **8 Categories**: Urgent/Important, Seb Focus, Shark, Red Dragon, Mandarin, Admin/Office, Finance, Parties/Marketing
- **15 People**: Seb, Phil, Nils, Narongchai, Aew, Tai, June, Thong, Man, Nata, Eddy, MascotTeam, Charlie, Chris RCA, Manfred
- **40 Tasks**: All marked as `done: false`
- **9 Notes**: Across various tasks

---

## 🛠️ Troubleshooting

### If the reload fails:

1. Check error logs in PythonAnywhere:
   - **Web** tab → **Log files** → Click on error log
   
2. Verify Python version:
   ```bash
   python --version
   # Should be Python 3.10 or higher
   ```

3. Check WSGI configuration:
   - **Web** tab → **WSGI configuration file**
   - Make sure it points to your `app.py`

### If restore fails:

1. Check the JSON syntax is valid
2. Ensure all IDs are unique
3. Verify foreign key relationships (task.category_id and task.person_id must exist)

---

## 📝 Post-Deployment Checklist

- [ ] Code updated to v0.21
- [ ] Dependencies installed
- [ ] Database backed up
- [ ] Web app reloaded
- [ ] Data restored from JSON
- [ ] All functionality tested
- [ ] PDF export working
- [ ] Backup/Restore tested

---

## 🔗 Quick Links

- **Your App**: https://TASKS-Naskaus.pythonanywhere.com/app
- **GitHub Repo**: https://github.com/Naskaus/TASKS
- **Latest Tag**: https://github.com/Naskaus/TASKS/tags

---

## 💡 Tips

1. **Regular Backups**: Use the backup button weekly to download your data as JSON
2. **Test Locally First**: Always test changes locally before deploying
3. **Version Tags**: Keep creating tags for each significant update
4. **Database Backups**: Keep multiple database backups before major updates

---

*Last Updated: 2025-11-25 | Version: v0.21*
