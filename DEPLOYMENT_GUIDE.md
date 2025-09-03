# Vercel Deployment Guide for Music @ Mood

## Prerequisites Complete ✅
- [x] Created `vercel.json` configuration
- [x] Created `api/index.py` for serverless deployment  
- [x] Created `.vercelignore` to exclude unnecessary files
- [x] Installed Vercel CLI

## Steps to Complete Deployment

### 1. Login to Vercel
```bash
vercel login
```
- Choose your preferred authentication method (GitHub recommended)
- Complete the authentication in your browser

### 2. Deploy to Vercel
```bash
vercel --prod
```
- Answer the setup questions:
  - **Set up and deploy?** → `Y`
  - **Which scope?** → Choose your account/team
  - **Link to existing project?** → `N` (for first deployment)
  - **What's your project's name?** → `music-mood` (or your preferred name)
  - **In which directory is your code located?** → `./` (current directory)

### 3. Deployment Configuration
The system will automatically:
- Detect it's a Python project
- Use the `vercel.json` configuration
- Install dependencies from `requirements.txt`
- Deploy the Flask app as serverless functions

### 4. Post-Deployment
After successful deployment, you'll get:
- **Live URL**: Your app will be live at `https://your-project-name.vercel.app`
- **Dashboard**: Manage your deployment at `https://vercel.com/dashboard`

## Important Notes

### Database Limitation
- SQLite will reset on each deployment on Vercel
- For production, consider using Vercel Postgres or external database
- Current setup creates temporary SQLite in `/tmp` on Vercel

### Audio Files
- All audio files in `static/audio/` will be served correctly
- Howler.js will work for audio playback

### Model Files
- TensorFlow model will be included if present
- Falls back to rule-based prediction if model not found

## Troubleshooting

### If deployment fails:
1. Check `vercel` logs in the dashboard
2. Ensure all dependencies in `requirements.txt` are compatible
3. Verify file paths are relative in the code

### If app doesn't work after deployment:
1. Check browser console for errors
2. Verify static files are loading
3. Test API endpoints individually

## Commands Quick Reference
```bash
# Check deployment status
vercel ls

# View deployment logs  
vercel logs [deployment-url]

# Redeploy
vercel --prod

# Remove deployment
vercel rm [project-name]
```
