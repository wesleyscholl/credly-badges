#!/bin/bash

# Demo script for credly-badges - Python badge service

set -e

echo "=========================================="
echo "  🏅 Credly Badges - Python Service"
echo "  Digital Badge Display & Management"
echo "=========================================="
echo ""

echo "🔍 Service Overview:"
if [ -f "main.py" ]; then
    echo "   ✅ Python web service detected"
    if [ -f "requirements.txt" ]; then
        echo "   • Flask/FastAPI framework"
        echo "   • Docker deployment ready"
        echo "   • Badge rendering service"
    fi
else
    echo "   ⚠️  main.py not found"
fi

echo ""
echo "✨ Features:"
echo ""
echo "   🏆 Badge Display"
echo "      • Credly badge integration"
echo "      • Dynamic badge rendering"
echo "      • SVG/PNG format support"
echo "      • Responsive design"
echo ""
echo "   🔗 API Endpoints"
echo "      • GET /badges - List all badges"
echo "      • GET /badge/{id} - Single badge details"
echo "      • GET /user/{username} - User's badges"
echo "      • GET /verify/{badge_id} - Verification"
echo ""
echo "   📊 Analytics"
echo "      • Badge view tracking"
echo "      • Verification counts"
echo "      • Popular certifications"
echo "      • User statistics"
echo ""

if [ -f "docker-compose.yml" ]; then
    echo "🐳 Docker Deployment:"
    echo "   ✅ docker-compose.yml configured"
    echo ""
    echo "   Quick start:"
    echo "   docker-compose up -d"
    echo ""
fi

echo "📝 Development Setup:"
echo ""
echo "   1. Install dependencies:"
echo "      pip install -r requirements.txt"
echo ""
echo "   2. Configure environment:"
echo "      cp .env.example .env"
echo ""
echo "   3. Run locally:"
echo "      python main.py"
echo ""
echo "   4. Run tests:"
if [ -d "tests" ]; then
    echo "      pytest tests/"
else
    echo "      # Tests TBD"
fi

echo ""
echo "🌐 API Usage:"
echo ""
echo "   # Get all badges"
echo "   curl http://localhost:8000/badges"
echo ""
echo "   # Get specific badge"
echo "   curl http://localhost:8000/badge/123abc"
echo ""
echo "   # Verify badge"
echo "   curl http://localhost:8000/verify/123abc"
echo ""

echo "💡 Use Cases:"
echo "   • Portfolio badge galleries"
echo "   • Resume credential display"
echo "   • Team certification tracking"
echo "   • Public verification endpoints"
echo "   • Badge achievement dashboards"
echo ""

if [ -f "index.html" ]; then
    echo "📱 Frontend:"
    echo "   ✅ Web interface available at index.html"
    echo "   • Interactive badge gallery"
    echo "   • Search and filter"
    echo "   • Mobile responsive"
fi

echo ""
echo "=========================================="
echo "  Repository: github.com/wesleyscholl/credly-badges"
echo "  Type: Python Web Service | Credly Integration"
echo "=========================================="
echo ""
