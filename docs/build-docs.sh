#!/bin/bash
# Build script for tachi documentation

set -e

echo "🚀 Building tachi documentation..."

cd tachi-site

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the site
echo "🔨 Building documentation site..."
npm run build

echo "✅ Documentation built successfully!"
echo "📁 Output in: tachi-site/build/"
echo ""
echo "To preview locally, run:"
echo "  cd tachi-site && npm run serve"
echo ""
echo "To start development server:"
echo "  cd tachi-site && npm start"
echo ""
echo "To deploy to GitHub Pages:"
echo "  cd tachi-site && npm run deploy"
echo ""
echo "Note: Docs-only mode - documentation served at root path"