#!/bin/bash

# Fraud Detection System Startup Script
# This script starts both the FastAPI backend and React frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if port_in_use $1; then
        print_warning "Port $1 is in use. Attempting to free it..."
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install -r backend/requirements.txt
    
    print_success "Python environment ready!"
}

# Function to setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    else
        print_status "Node.js dependencies already installed"
    fi
    
    cd ..
    print_success "Node.js environment ready!"
}

# Function to start backend
start_backend() {
    print_status "Starting FastAPI backend..."
    
    # Kill any existing process on port 8000
    kill_port 8000
    
    # Activate virtual environment and start backend
    source venv/bin/activate
    cd backend
    
    # Start backend in background
    python main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/ >/dev/null 2>&1; then
            print_success "Backend started successfully on http://localhost:8000"
            return 0
        fi
        sleep 1
    done
    
    print_error "Backend failed to start within 30 seconds"
    return 1
}

# Function to start frontend
start_frontend() {
    print_status "Starting React frontend..."
    
    # Kill any existing process on port 3000
    kill_port 3000
    
    cd frontend
    
    # Start frontend in background
    npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -s http://localhost:3000/ >/dev/null 2>&1; then
            print_success "Frontend started successfully on http://localhost:3000"
            return 0
        fi
        sleep 1
    done
    
    print_error "Frontend failed to start within 60 seconds"
    return 1
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend stopped"
        fi
        rm -f backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend stopped"
        fi
        rm -f frontend.pid
    fi
    
    # Also kill any remaining processes on the ports
    kill_port 8000
    kill_port 3000
}

# Function to show status
show_status() {
    echo
    print_status "=== Fraud Detection System Status ==="
    
    if port_in_use 8000; then
        print_success "✓ Backend running on http://localhost:8000"
    else
        print_error "✗ Backend not running"
    fi
    
    if port_in_use 3000; then
        print_success "✓ Frontend running on http://localhost:3000"
    else
        print_error "✗ Frontend not running"
    fi
    
    echo
    if port_in_use 8000 && port_in_use 3000; then
        print_success "🎉 Application is ready! Open http://localhost:3000 in your browser"
    else
        print_warning "⚠️  Some services are not running. Check the logs for details."
    fi
    echo
}

# Function to show logs
show_logs() {
    echo
    print_status "=== Recent Backend Logs ==="
    if [ -f "backend.log" ]; then
        tail -n 20 backend.log
    else
        print_warning "No backend logs found"
    fi
    
    echo
    print_status "=== Recent Frontend Logs ==="
    if [ -f "frontend.log" ]; then
        tail -n 20 frontend.log
    else
        print_warning "No frontend logs found"
    fi
}

# Main script logic
main() {
    echo
    print_status "🔍 Fraud Detection System Startup Script"
    echo
    
    # Check for required commands
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command_exists node; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    if ! command_exists npm; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    # Handle command line arguments
    case "${1:-start}" in
        "start")
            print_status "Starting Fraud Detection System..."
            
            # Setup environments
            setup_python_env
            setup_node_env
            
            # Start services
            if start_backend; then
                if start_frontend; then
                    show_status
                    
                    print_status "Press Ctrl+C to stop all services"
                    
                    # Wait for interrupt
                    trap stop_services INT TERM
                    
                    # Keep script running
                    while true; do
                        sleep 1
                    done
                else
                    print_error "Failed to start frontend"
                    stop_services
                    exit 1
                fi
            else
                print_error "Failed to start backend"
                exit 1
            fi
            ;;
        
        "stop")
            stop_services
            ;;
        
        "status")
            show_status
            ;;
        
        "logs")
            show_logs
            ;;
        
        "restart")
            print_status "Restarting services..."
            stop_services
            sleep 2
            $0 start
            ;;
        
        "setup")
            print_status "Setting up environments only..."
            setup_python_env
            setup_node_env
            print_success "Setup complete! Run './start.sh start' to start the application"
            ;;
        
        "help"|"-h"|"--help")
            echo "Fraud Detection System Startup Script"
            echo
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  start    Start both backend and frontend (default)"
            echo "  stop     Stop all services"
            echo "  restart  Restart all services"
            echo "  status   Show service status"
            echo "  logs     Show recent logs"
            echo "  setup    Setup environments without starting"
            echo "  help     Show this help message"
            echo
            echo "The application will be available at:"
            echo "  Frontend: http://localhost:3000"
            echo "  Backend:  http://localhost:8000"
            ;;
        
        *)
            print_error "Unknown command: $1"
            print_status "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"