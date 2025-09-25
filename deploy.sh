#!/bin/bash

# PPT AI Analyzer - Vercel Deployment Script

echo "🚀 Preparing PPT AI Analyzer for Vercel deployment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "   npm i -g vercel"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ vercel.json not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Vercel CLI found"
echo "✅ Configuration files present"

# Show deployment info
echo ""
echo "📋 Deployment Configuration:"
echo "   - Runtime: Python"
echo "   - Entry point: api/index.py"
echo "   - Static files: static/"
echo "   - Templates: templates/"
echo ""

echo "🔧 Optimizing for serverless deployment..."

# Create .vercelignore if it doesn't exist
if [ ! -f ".vercelignore" ]; then
    cat > .vercelignore << EOF
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
uploads/
analysis_results/
test.py
run.py
.env
.DS_Store
*.log
EOF
    echo "✅ Created .vercelignore"
fi

echo "📦 Files prepared for deployment"
echo ""
echo "🌍 Ready to deploy to Vercel!"
echo ""
echo "Next steps:"
echo "1. Run: vercel login (if not already logged in)"
echo "2. Run: vercel --prod"
echo ""
echo "Or for development deployment:"
echo "   vercel"
echo ""
echo "Features included in deployment:"
echo "   ✨ Web-based PPT analysis"
echo "   🎨 Color palette extraction"
echo "   🖼️  Image analysis with dominant colors"
echo "   🤖 AI-powered insights (if Groq API works)"
echo "   📊 Comprehensive reporting"
echo "   📱 Responsive design"
echo ""
echo "Environment considerations:"
echo "   - File uploads use temporary files"
echo "   - Large files may hit serverless limits"
echo "   - Some AI features may be limited"
echo ""
echo "API Endpoints available:"
echo "   GET  / - Main interface"
echo "   POST /upload - File upload"
echo "   POST /api/analyze - Programmatic analysis"
echo "   GET  /health - Health check"
