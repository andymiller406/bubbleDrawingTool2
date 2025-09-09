# Bubble Drawing Tool - GitHub + Heroku Deployment Guide

This guide will walk you through deploying the Bubble Drawing Tool to Heroku via GitHub.

## 🚀 Quick Deployment Steps

### 1. Create GitHub Repository

1. **Go to GitHub** and create a new repository:
   - Repository name: `bubble-drawing-tool`
   - Description: `AI-powered tool for adding numbered bubbles to technical drawing dimensions`
   - Make it public (or private if you prefer)
   - Don't initialize with README (we have our own files)

2. **Upload your files** to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Bubble Drawing Tool"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/bubble-drawing-tool.git
   git push -u origin main
   ```

### 2. Deploy to Heroku

#### Option A: Heroku Dashboard (Recommended)

1. **Sign up for Heroku** at [heroku.com](https://heroku.com) (free account)

2. **Create new app**:
   - Click "New" → "Create new app"
   - App name: `your-bubble-tool` (must be unique)
   - Region: Choose closest to your users
   - Click "Create app"

3. **Connect to GitHub**:
   - Go to "Deploy" tab
   - Select "GitHub" as deployment method
   - Connect your GitHub account
   - Search for your repository: `bubble-drawing-tool`
   - Click "Connect"

4. **Add Buildpacks** (Important!):
   - Go to "Settings" tab
   - Click "Add buildpack"
   - Add in this order:
     1. `heroku-community/apt` (for poppler-utils)
     2. `heroku/python`

5. **Deploy**:
   - Go back to "Deploy" tab
   - Scroll to "Manual deploy"
   - Select `main` branch
   - Click "Deploy Branch"

6. **Enable automatic deploys** (optional):
   - Check "Enable Automatic Deploys"
   - Now every GitHub push will auto-deploy

#### Option B: Heroku CLI

```bash
# Install Heroku CLI first
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create your-bubble-tool

# Add buildpacks
heroku buildpacks:add --index 1 heroku-community/apt
heroku buildpacks:add --index 2 heroku/python

# Deploy
git push heroku main
```

### 3. Configure Environment Variables (Optional)

In Heroku Dashboard → Settings → Config Vars, add:
- `SECRET_KEY`: `your-random-secret-key-here`
- `FLASK_ENV`: `production`

### 4. Test Your Deployment

Your app will be available at: `https://your-bubble-tool.herokuapp.com`

Test both:
- File upload functionality
- Demo feature

## 📁 Repository Structure

Your GitHub repository should contain:

```
bubble-drawing-tool/
├── web_app_heroku.py          # Main Flask application
├── improved_bubble_tool.py    # Core processing logic
├── Procfile                   # Heroku process definition
├── requirements.txt           # Python dependencies
├── runtime.txt               # Python version
├── Aptfile                   # System dependencies
├── .gitignore               # Git ignore rules
├── test_drawing.pdf         # Sample file for demo
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   └── demo.html
├── static/                  # CSS and JS files
│   ├── css/style.css
│   └── js/app.js
└── README.md               # Project documentation
```

## 🔧 Key Files Explained

- **`Procfile`**: Tells Heroku how to run your app
- **`requirements.txt`**: Lists all Python packages needed
- **`runtime.txt`**: Specifies Python version
- **`Aptfile`**: System packages (poppler-utils for PDF processing)
- **`web_app_heroku.py`**: Heroku-optimized Flask app

## 🌟 Features

- **Web Interface**: Clean, responsive design
- **File Upload**: Drag-and-drop PDF upload
- **AI Processing**: Automatic dimension detection
- **Demo Mode**: Try without uploading files
- **Download Results**: Get annotated drawings as ZIP

## 🛠️ Troubleshooting

### Common Issues:

**Build fails with "No module named 'cv2'":**
- Make sure `opencv-python-headless` is in requirements.txt

**PDF processing fails:**
- Ensure Aptfile contains `poppler-utils`
- Check buildpacks are in correct order

**App crashes on startup:**
- Check Heroku logs: `heroku logs --tail`
- Verify all files are committed to Git

**File upload doesn't work:**
- Check file size (16MB limit)
- Ensure uploads/ directory permissions

### Getting Logs:
```bash
heroku logs --tail --app your-bubble-tool
```

## 💰 Cost

- **Heroku Free Tier**: 550-1000 dyno hours/month
- **Heroku Hobby**: $7/month for always-on app
- **GitHub**: Free for public repositories

## 🔄 Making Updates

1. **Make changes** to your code locally
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
3. **Auto-deploy** (if enabled) or manually deploy from Heroku dashboard

## 🎯 Next Steps

After successful deployment:

1. **Custom Domain**: Add your own domain in Heroku settings
2. **SSL Certificate**: Automatic with custom domains
3. **Monitoring**: Set up logging and error tracking
4. **Scaling**: Upgrade dyno type for better performance
5. **Database**: Add PostgreSQL for user accounts (future feature)

## 📞 Support

If you encounter issues:
- Check Heroku documentation
- Review application logs
- Test locally first
- GitHub Issues for code problems

Your bubble drawing tool will be live and accessible to anyone with the URL!

