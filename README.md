# Topic Standardization Service

Real-time progress dashboard for DNB topic standardization with tqdm-style progress bars.

## Features

- ✅ Real-time progress monitoring with visual progress bars
- ✅ tqdm-style progress display (questions/sec, ETA)
- ✅ Live activity logs
- ✅ Start/Stop controls
- ✅ Auto-resume functionality (processes only unprocessed questions)
- ✅ Runs 24/7 on Render (free tier)

## Deploy to Render

### Step 1: Push to GitHub

```bash
cd Projects/dnb-portal/topic_processor
git init
git add .
git commit -m "Initial commit: Topic standardization service"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/dnb-topic-processor.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [https://render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `dnb-topic-processor`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Step 3: Add Environment Variables

In Render dashboard, add these environment variables (get values from your .env file):

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_SERVICE_KEY=<your_supabase_service_key>
GROQ_API_KEY=<your_groq_api_key>
```

### Step 4: Deploy

Click "Create Web Service" - Render will automatically deploy your app!

Your dashboard will be available at: `https://dnb-topic-processor.onrender.com`

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Open browser
http://localhost:5000
```

## How It Works

1. **Auto-Resume**: Only processes questions where `topic_v2 IS NULL`
2. **Progress Tracking**: Real-time updates via Server-Sent Events (SSE)
3. **Rate Limiting**: 2s between questions, 60s pause every 25 questions
4. **AI Validation**: Ensures topics match master taxonomy
5. **Cross-Cutting Topics**: Handles Research/Biostat questions correctly

## Usage

1. Open the dashboard URL
2. Click "▶ Start Processing"
3. Monitor progress in real-time
4. Can stop/resume anytime
5. Close browser - processing continues on server!

## Monitoring

The dashboard shows:
- Overall progress (40 subjects)
- Current subject progress (tqdm-style)
- Processing rate (questions/second)
- ETA for current subject
- Real-time activity logs
- Current topic being mapped
- AI confidence scores

## Free Tier Limits

- **Render Free**: 750 hours/month (enough for 24/7)
- **Groq Free**: 30 requests/minute (handled by script)
- **Auto-resume**: If service restarts, it continues automatically

Enjoy! 🚀
