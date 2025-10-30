# 🚀 Deploy to Render - Quick Guide

## Prerequisites
- GitHub account
- Render account (free) - https://render.com

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `dnb-topic-processor`
3. Description: "AI-powered topic standardization for DNB medical questions"
4. Keep it **Public** (required for Render free tier)
5. Click "Create repository"

---

## Step 2: Push Code to GitHub

Open Git Bash or terminal in this directory:

```bash
# Navigate to this directory
cd D:/Claude/Projects/dnb-portal/topic_processor

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/dnb-topic-processor.git

# Push code
git branch -M main
git push -u origin main
```

**Expected output:** Code should now be on GitHub!

---

## Step 3: Deploy on Render

### 3.1 Sign In
- Go to https://dashboard.render.com
- Click "Get Started" or "Sign In"
- Sign in with GitHub (easiest)

### 3.2 Create New Web Service
1. Click "New" (top right)
2. Select "Web Service"
3. Click "Connect account" if first time
4. Find your `dnb-topic-processor` repository
5. Click "Connect"

### 3.3 Configure Service

**Basic Settings:**
```
Name: dnb-topic-processor
Region: Oregon (US West)
Branch: main
Runtime: Python 3
```

**Build & Deploy:**
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

**Instance Type:**
```
Plan: Free (or Starter $7/month for better reliability)
```

### 3.4 Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add these 3 variables:

**1. SUPABASE_URL**
```
Key: SUPABASE_URL
Value: <your_supabase_project_url>
```

**2. SUPABASE_SERVICE_KEY**
```
Key: SUPABASE_SERVICE_KEY
Value: <your_supabase_service_role_key>
```

**3. GROQ_API_KEY**
```
Key: GROQ_API_KEY
Value: <your_groq_api_key>
```

### 3.5 Deploy!

Click "Create Web Service"

**Wait 2-3 minutes** while Render:
- ✅ Clones your repository
- ✅ Installs Python dependencies
- ✅ Starts the Flask app
- ✅ Assigns a public URL

---

## Step 4: Access Your Dashboard

Once deploy completes, your dashboard will be at:

```
https://dnb-topic-processor.onrender.com
```

**Note:** Free tier may take 30-60 seconds to wake up on first visit (cold start)

---

## Step 5: Start Processing

1. Open the dashboard URL
2. Click **"▶ Start Processing"** button
3. Watch the magic happen! ✨

**Features:**
- Real-time progress bars
- Live statistics
- Activity logs
- tqdm-style progress (questions/sec, ETA)

---

## 🎯 What Happens Next?

The service will:
- ✅ Process all 80,000+ questions across 40 subjects
- ✅ Run 24/7 (even when you close browser)
- ✅ Auto-resume if service restarts
- ✅ Take 3-5 days to complete

You can:
- ✅ Close browser - processing continues
- ✅ Shutdown your PC - processing continues
- ✅ Check progress anytime from dashboard
- ✅ Stop/restart processing if needed

---

## 🔧 Troubleshooting

### Deploy Failed?
**Check build logs:**
- Go to Render dashboard
- Click on your service
- Click "Logs" tab
- Look for error messages

**Common issues:**
- Missing dependency? Check `requirements.txt`
- Python version? Uses Python 3.11 by default
- Environment variables? Check they're all added

### Dashboard Not Loading?
- Wait 60 seconds (cold start on free tier)
- Check service status in Render dashboard
- Look at "Events" tab for errors

### Can't Push to GitHub?
```bash
# If you get authentication error, use GitHub CLI or Personal Access Token
gh auth login

# Or use SSH instead of HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/dnb-topic-processor.git
```

---

## 📊 Monitor Progress

### From Dashboard:
- Live progress bars
- Questions processed count
- Current subject and topic
- Processing rate (q/s)
- ETA for current subject

### From Database:
```bash
# On your local machine
cd D:/Claude/Projects/dnb-portal
python scripts/verify_migration_status.py
```

---

## 💰 Cost Breakdown

### Free Tier:
- **Render Free:** 750 hours/month (enough for 24/7 for 31 days)
- **Groq API:** Free tier (30 req/min, handled by script)
- **Supabase:** Free tier (sufficient)
- **Total Cost:** $0/month ✅

### Starter Tier (Optional, Recommended):
- **Render Starter:** $7/month
- **Benefits:**
  - No cold starts (instant dashboard access)
  - More reliable uptime
  - Faster processing
- **Total Cost:** $7/month

---

## ✅ Checklist

- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Created Render account
- [ ] Connected GitHub to Render
- [ ] Created web service
- [ ] Added 3 environment variables
- [ ] Deployed successfully
- [ ] Opened dashboard
- [ ] Started processing
- [ ] Bookmarked dashboard URL

---

## 🎉 You're Done!

The AI will now process all 80,000 questions over the next few days.

You can continue developing your DNB Next.js website while this runs in the background!

**Dashboard URL:** https://dnb-topic-processor.onrender.com

Happy coding! 🚀
