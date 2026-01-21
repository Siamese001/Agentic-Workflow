#!/bin/bash
# Docker Build Verification Script for Canon Validator Engine
# Tests the multi-stage build and security configuration

echo "🚢 Starting Docker Build Verification..."
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running or not accessible"
    exit 1
fi

# Clean up any existing containers/images
echo "🧹 Cleaning up previous builds..."
docker rm -f canon-validator canon-redis canon-workspace 2>/dev/null || true
docker rmi canon-validator:latest 2>/dev/null || true

# Build the Docker image
echo "🔨 Building Canon Validator image..."
echo "This will run all 88 tests during the build process..."

if docker build -t canon-validator:latest .; then
    echo "✅ Docker build successful!"
    echo ""

    # Check image size
    echo "📊 Image Information:"
    docker images canon-validator:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

    # Check security features
    echo ""
    echo "🔒 Security Verification:"

    # Check if running as non-root user
    USER_CHECK=$(docker run --rm canon-validator:latest whoami)
    if [ "$USER_CHECK" = "appuser" ]; then
        echo "✅ Container runs as non-root user: $USER_CHECK"
    else
        echo "❌ WARNING: Container running as root user: $USER_CHECK"
    fi

    # Check if Python dependencies are minimal
    echo ""
    echo "📦 Dependency Check:"
    DEPS_COUNT=$(docker run --rm canon-validator:latest pip list | wc -l)
    echo "Total Python packages installed: $DEPS_COUNT"

    # Test health check
    echo ""
    echo "🏥 Testing Health Check:"
    docker run --rm -e REDIS_HOST=mock -e REDIS_PASSWORD=mock canon-validator:latest python /app/healthcheck.py || echo "Health check failed (expected without Redis)"

    echo ""
    echo "✅ Docker build verification complete!"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.production.template to .env.production and fill in your API keys"
    echo "2. Run: docker-compose up --build"
    echo "3. Monitor logs: docker-compose logs -f validator"

else
    echo "❌ Docker build failed!"
    echo ""
    echo "Common issues:"
    echo "1. Missing requirements.txt or requirements-test.txt"
    echo "2. Test failures in tests/apps_cv/"
    echo "3. Missing canon_validator.py or other core files"
    echo ""
    echo "Check the build output above for specific errors."
    exit 1
fi
