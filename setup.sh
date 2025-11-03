#!/bin/bash

# Contact Form Automation Tool - Setup Script for Mac OS

echo "=========================================="
echo "Contact Form Automation Tool - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

echo "✓ Playwright browsers installed"
echo ""

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your email, phone, and other settings"
else
    echo "✓ .env file already exists"
fi

# Create sample CSV if it doesn't exist
if [ ! -f contacts.csv ]; then
    echo "Creating sample contacts.csv..."
    cp contacts.csv.example contacts.csv
    echo "✓ contacts.csv created"
    echo ""
    echo "⚠️  IMPORTANT: Edit contacts.csv and add your actual contacts"
else
    echo "✓ contacts.csv already exists"
fi

# Create logs directory
mkdir -p logs
echo "✓ Logs directory created"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your email, phone, and settings:"
echo "   nano .env"
echo ""
echo "2. Edit contacts.csv with your contacts:"
echo "   nano contacts.csv"
echo ""
echo "3. Activate the virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "4. Run the tool:"
echo "   python main.py"
echo ""
echo "For more information, see README.md"
echo ""
