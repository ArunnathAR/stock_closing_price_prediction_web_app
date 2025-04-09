#!/bin/bash

# Color codes for terminal output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting StockAnalyzer setup...${NC}"

echo -e "\n${YELLOW}NOTE: This script assumes you have already installed:${NC}"
echo -e "- Python 3.10+ with pip"
echo -e "- Node.js 16+ with npm"
echo -e "- Required Python packages (fastapi, uvicorn, pandas, numpy, yfinance, etc.)"
echo -e "- Required Node.js packages for React"

# Start FastAPI backend
echo -e "\n${YELLOW}Starting FastAPI backend...${NC}"
python server.py &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Start React frontend
echo -e "\n${YELLOW}Starting React frontend...${NC}"
cd frontend && npm start &
FRONTEND_PID=$!

# Function to handle exit
function cleanup {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Register the cleanup function for when Ctrl+C is pressed
trap cleanup SIGINT SIGTERM

echo -e "\n${GREEN}Servers started!${NC}"
echo -e "${YELLOW}FastAPI backend is running at:${NC} http://localhost:5000"
echo -e "${YELLOW}React frontend is running at:${NC} http://localhost:3000"
echo -e "${YELLOW}API documentation is available at:${NC} http://localhost:5000/docs"
echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID