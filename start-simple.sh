#!/bin/bash

echo "🚀 Starting Trilogy AI Avatar Application (Simple)"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if environment file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please ensure environment variables are set."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Environment file found"
echo "✅ Node.js is installed"
echo ""

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend dependencies already installed"
fi

echo ""
echo "🔧 Starting backend in Docker..."
docker-compose -f docker-compose.simple.yml up --build -d

echo "⏳ Waiting for backend to be ready..."
sleep 10

echo "🌐 Starting frontend locally..."
echo "Backend: http://localhost:8080"
echo "Frontend: http://localhost:3000"
echo ""

# Start frontend in foreground
cd frontend && npm run dev

echo ""
echo "🛑 Stopping backend container..."
docker-compose -f docker-compose.simple.yml down

echo ""
echo "🎉 Application stopped. To restart, run:"
echo "   ./start-simple.sh"