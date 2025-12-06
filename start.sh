#!/bin/bash
# Startup script for Financial Document Parser services

echo "================================================"
echo " Financial Document Parser - Service Launcher"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Please run: python -m venv venv"
    echo "Then run: source venv/bin/activate"
    echo "And: pip install -r requirements.txt"
    exit 1
fi

echo "Select which service to run:"
echo ""
echo "1. Flask API only"
echo "2. Streamlit UI only"
echo "3. Both (Flask API + Streamlit UI)"
echo "4. Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting Flask API..."
        source venv/bin/activate
        python app.py
        ;;
    2)
        echo ""
        echo "Starting Streamlit UI..."
        echo "Note: Flask API must be running for the UI to work!"
        source venv/bin/activate
        streamlit run streamlit_app.py
        ;;
    3)
        echo ""
        echo "Starting Flask API in background..."
        source venv/bin/activate
        python app.py &
        API_PID=$!
        echo "Flask API started with PID: $API_PID"
        sleep 3
        echo ""
        echo "Starting Streamlit UI..."
        streamlit run streamlit_app.py
        # Kill Flask API when Streamlit exits
        kill $API_PID 2>/dev/null
        ;;
    4)
        echo ""
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac
