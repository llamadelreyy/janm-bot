#!/bin/bash

# Repository Cleanup Script
# This script helps clean up large files that were accidentally pushed to the repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo
print_status "🧹 Repository Cleanup Script"
echo

print_warning "This script will help clean up large files that were accidentally pushed to the repository."
print_warning "IMPORTANT: This will rewrite git history. Make sure all team members are aware!"
echo

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This is not a git repository. Please run this script from the project root."
    exit 1
fi

# Show current repository status
print_status "Current repository status:"
git status --porcelain

echo
print_status "Large files that should be removed from git history:"
echo "- venv/ (Python virtual environment)"
echo "- frontend/node_modules/ (Node.js dependencies)"
echo "- *.log files (application logs)"
echo "- *.pid files (process IDs)"
echo "- Large binary files (*.abi3.so, *.pack)"

echo
read -p "Do you want to proceed with cleaning up these files? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleanup cancelled."
    exit 0
fi

print_status "Starting cleanup process..."

# Remove files from current working directory
print_status "Removing large files from working directory..."

if [ -d "venv" ]; then
    rm -rf venv/
    print_success "Removed venv/"
fi

if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules/
    print_success "Removed frontend/node_modules/"
fi

if [ -f "backend.log" ]; then
    rm -f backend.log
    print_success "Removed backend.log"
fi

if [ -f "frontend.log" ]; then
    rm -f frontend.log
    print_success "Removed frontend.log"
fi

if [ -f "backend.pid" ]; then
    rm -f backend.pid
    print_success "Removed backend.pid"
fi

if [ -f "frontend.pid" ]; then
    rm -f frontend.pid
    print_success "Removed frontend.pid"
fi

# Remove from git history using git filter-branch
print_status "Removing files from git history..."

# Create a backup branch
git branch backup-before-cleanup 2>/dev/null || print_warning "Backup branch already exists"

# Remove large files from git history
git filter-branch --force --index-filter \
    'git rm -rf --cached --ignore-unmatch venv/ frontend/node_modules/ *.log *.pid' \
    --prune-empty --tag-name-filter cat -- --all

print_success "Files removed from git history"

# Clean up git references
print_status "Cleaning up git references..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

print_success "Git cleanup completed"

# Show new repository size
print_status "Repository cleanup completed!"
echo
print_status "Next steps:"
echo "1. Verify the cleanup worked: git log --oneline"
echo "2. Force push to update remote repository: git push --force-with-lease origin demo"
echo "3. Inform team members to re-clone the repository"
echo "4. Run ./start.sh setup to recreate venv and node_modules"

echo
print_warning "IMPORTANT: All team members will need to re-clone the repository after force push!"
print_warning "The backup branch 'backup-before-cleanup' contains the original history if needed."

echo
print_status "Repository size before and after:"
du -sh .git/ 2>/dev/null || echo "Could not calculate repository size"