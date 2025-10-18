# GitHub Actions Setup Guide

## Overview

This repository uses GitHub Actions to automatically update sector rotation data during market hours (Monday-Friday, 9:30 AM - 4:00 PM EST).

The workflow runs **every hour** during market hours to conserve API calls while keeping data fresh.

## Setup Instructions

### 1. Add API Key as GitHub Secret

You need to add your Alpha Vantage API key as a GitHub secret:

1. Go to your repository on GitHub: `https://github.com/GeorgeHategan/sector-rotation`
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the following secrets:
   
   **Required:**
   - Name: `ALPHAVANTAGE_API_KEY`
   - Value: Your Alpha Vantage API key (e.g., `75IGYUZ3C7AC2PBM`)
   
   **Optional (for AI analysis):**
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (e.g., `sk-proj-...`)
   
6. Click **Add secret** for each one

### 2. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. The workflow should now be enabled

### 3. Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/docs**
3. Click **Save**

## How It Works

### Automatic Updates

The GitHub Action runs automatically:
- **Every hour** during market hours (9:30 AM - 4:00 PM EST)
- **Monday through Friday only**
- Skips weekends and after-hours automatically

### What Happens Each Run

1. ✅ Checks if the US stock market is currently open
2. 📊 If open, runs `sector_rotation_scanner.py`
3. 🤖 Runs `ai_market_analysis.py` (if OPENAI_API_KEY is set)
4. 📈 Generates charts and heatmaps
5. 📝 Updates `docs/latest_data.json` with new data and AI analysis
6. 🚀 Commits and pushes changes to GitHub
7. 🌐 GitHub Pages automatically publishes the updated dashboard

### Manual Trigger

You can also run the workflow manually:
1. Go to **Actions** tab
2. Select **Update Sector Rotation Data**
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## Monitoring

### View Workflow Runs

1. Go to the **Actions** tab in your repository
2. You'll see a list of all workflow runs
3. Click on any run to see detailed logs

### Check Results

- **Dashboard**: https://georgehategan.github.io/sector-rotation/
- **Latest Data**: Check the `docs/` folder in your repository

## Troubleshooting

### Workflow Not Running

- Check that GitHub Actions are enabled (Actions tab)
- Verify the API key secret is set correctly
- Check workflow logs for errors

### API Rate Limits

- Free tier: 25 requests/day
- Premium tier: Higher limits
- The workflow respects market hours to conserve API calls

### Market Hours

The workflow automatically detects:
- ✅ Weekdays (Monday-Friday)
- ✅ Market hours (9:30 AM - 4:00 PM EST)
- ❌ Weekends (Saturday-Sunday)
- ❌ After hours (before 9:30 AM or after 4:00 PM EST)

## Cost

- GitHub Actions: **Free** for public repositories (2,000 minutes/month)
- GitHub Pages: **Free** for public repositories
- Alpha Vantage API: **Free tier** available (25 requests/day)
- OpenAI API: **~$0.02-0.05 per analysis** (optional, only if OPENAI_API_KEY is configured)

### Cost Estimates

If running every hour during market hours (7 times per day):
- Alpha Vantage: 7 requests/day (well within free tier)
- OpenAI (optional): ~$0.14-0.35 per day (~$3-8 per month)
- GitHub Actions: ~5 minutes/day (well within free tier)

## Customization

### Change Update Frequency

Edit `.github/workflows/update-sector-data.yml`:
- Add or remove cron schedules
- Adjust timing as needed

### Disable Automatic Updates

1. Go to **Actions** tab
2. Select the workflow
3. Click the "..." menu → **Disable workflow**

You can still run manually when needed.

## Security

✅ **API Key Protected**: Your API key is stored as an encrypted GitHub secret
✅ **Not Visible**: Secrets never appear in logs or commits
✅ **Secure**: Only the workflow can access the secret

## Support

If you encounter issues:
1. Check the Actions tab for error logs
2. Verify all secrets are set correctly
3. Ensure GitHub Pages is enabled
4. Check that your API key is valid and has remaining quota
