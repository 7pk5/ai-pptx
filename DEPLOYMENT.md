# Vercel Deployment Guide for PPT AI Analyzer

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally with `npm i -g vercel`
3. **Git Repository**: Push your code to GitHub, GitLab, or Bitbucket

## Quick Deployment

### Method 1: Command Line (Recommended)

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy from project directory**:
   ```bash
   cd /path/to/PPTAI
   vercel --prod
   ```

3. **Follow the prompts**:
   - Set up and deploy? `Y`
   - Which scope? Choose your account
   - Link to existing project? `N` (for first deployment)
   - What's your project's name? `ppt-ai-analyzer`
   - In which directory is your code located? `./`

### Method 2: GitHub Integration

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/ppt-ai-analyzer.git
   git push -u origin main
   ```

2. **Connect on Vercel Dashboard**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import from GitHub
   - Select your repository

## Configuration

### Environment Variables

Set these in your Vercel dashboard (Settings > Environment Variables):

```env
GROQ_API_KEY=your_actual_groq_api_key
FLASK_SECRET_KEY=your_super_secret_production_key
MAX_FILE_SIZE=52428800
ENVIRONMENT=production
```

### Build Settings

Vercel will automatically detect the Python project and use these settings:

- **Framework Preset**: Other
- **Build Command**: (leave empty)
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`

## File Structure for Deployment

```
PPTAI/
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
├── .vercelignore           # Files to ignore during deployment
├── api/
│   └── index.py            # Main Flask app for Vercel
├── src/                    # Source code
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
└── .env.example           # Environment variables template
```

## Key Features of Serverless Version

### ✅ What Works Well
- Web-based file upload and analysis
- Color palette extraction
- Basic image analysis
- Font detection
- Layout analysis
- Responsive UI
- API endpoints

### ⚠️ Limitations in Serverless Environment
- File uploads limited by Vercel's 50MB request limit
- No persistent file storage (uses temporary files)
- Some image processing features may be limited
- AI analysis depends on Groq API availability

### 🔧 Optimizations Made
- Uses `opencv-python-headless` instead of full OpenCV
- Graceful fallbacks when optional dependencies aren't available
- Temporary file handling for uploads
- Reduced memory footprint
- Error handling for serverless constraints

## Deployment Commands

### Development Deployment
```bash
vercel
```

### Production Deployment
```bash
vercel --prod
```

### View Logs
```bash
vercel logs [deployment-url]
```

### Remove Deployment
```bash
vercel remove [project-name]
```

## Post-Deployment

### Test Your Deployment

1. **Health Check**:
   ```bash
   curl https://your-app.vercel.app/health
   ```

2. **Upload Test**:
   - Visit your deployed URL
   - Upload a small PowerPoint file
   - Verify analysis results

### Monitor Performance

- Check Vercel dashboard for function execution times
- Monitor memory usage
- Watch for timeout errors (Vercel has 10s limit for Hobby plan)

## Custom Domain (Optional)

1. **Add Domain in Vercel Dashboard**:
   - Go to Project Settings > Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **SSL Certificate**:
   - Vercel automatically provides SSL certificates
   - Your site will be available at `https://yourdomain.com`

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check `requirements.txt` for incompatible versions
   - Ensure all imports are available in serverless environment

2. **Function Timeouts**:
   - Large PowerPoint files may exceed time limits
   - Consider upgrading to Vercel Pro for longer timeouts

3. **Memory Errors**:
   - Optimize image processing
   - Reduce concurrent operations

4. **Import Errors**:
   - Use conditional imports for optional dependencies
   - Check Python version compatibility

### Debug Commands

```bash
# View function logs
vercel logs --follow

# Check deployment status
vercel ls

# Inspect specific deployment
vercel inspect [deployment-url]
```

## Security Considerations

1. **API Keys**:
   - Never commit API keys to version control
   - Use Vercel environment variables
   - Rotate keys regularly

2. **File Uploads**:
   - File validation is implemented
   - Temporary files are cleaned up
   - Consider adding rate limiting

3. **CORS**:
   - Configure if needed for API access
   - Set appropriate headers

## Cost Considerations

### Vercel Pricing Tiers

1. **Hobby (Free)**:
   - 100 GB-hours of function execution
   - 12 serverless functions
   - 100 GB bandwidth

2. **Pro ($20/month)**:
   - 1000 GB-hours function execution
   - Unlimited serverless functions
   - 1 TB bandwidth
   - Longer function timeouts

3. **Enterprise**:
   - Custom pricing
   - Enhanced security
   - Priority support

### Optimization Tips

- Use efficient image processing
- Implement caching where possible
- Monitor function execution times
- Consider batching operations

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Support**: [vercel.com/support](https://vercel.com/support)

## Example URLs

After deployment, your app will be available at:
- `https://ppt-ai-analyzer.vercel.app/` (auto-generated)
- `https://your-custom-domain.com/` (if configured)

API endpoints:
- `GET /` - Main interface
- `POST /upload` - File upload
- `POST /api/analyze` - Programmatic analysis
- `GET /health` - Health check
