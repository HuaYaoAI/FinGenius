#!/bin/bash

# FinGenius Automatic Installation Script
# This script automates the installation process for the FinGenius project

set -e  # Exit immediately if a command exits with a non-zero status

echo "=== FinGenius Automatic Installation ==="
echo "This script will install the FinGenius project with all its dependencies."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "Found Python version: $PYTHON_VERSION"
        
        # Check if Python version is 3.12 or higher
        IFS='.' read -ra VERSION_PARTS <<< "$PYTHON_VERSION"
        MAJOR=${VERSION_PARTS[0]}
        MINOR=${VERSION_PARTS[1]}
        
        if [[ $MAJOR -gt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -ge 12 ]]; then
            echo "✓ Python version is compatible (3.12+)"
            return 0
        else
            echo "✗ Python version is too old. FinGenius requires Python 3.12 or higher."
            return 1
        fi
    else
        echo "✗ Python 3 is not installed. Please install Python 3.12 or higher."
        return 1
    fi
}

# Function to install uv
install_uv() {
    echo "Installing uv package manager..."
    
    if command_exists uv; then
        echo "✓ uv is already installed"
        return 0
    fi
    
    # Try to install uv
    if command_exists curl; then
        echo "Downloading and installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command_exists wget; then
        echo "Downloading and installing uv..."
        wget -O - https://astral.sh/uv/install.sh | sh
    else
        echo "✗ Neither curl nor wget is available. Please install one of them to download uv."
        return 1
    fi
    
    # Add uv to PATH if needed
    if ! command_exists uv; then
        echo "Adding uv to PATH..."
        export PATH="$HOME/.local/bin:$PATH"
        
        # Try to source shell configuration files
        if [ -f "$HOME/.bashrc" ]; then
            source "$HOME/.bashrc"
        elif [ -f "$HOME/.zshrc" ]; then
            source "$HOME/.zshrc"
        fi
        
        # Check again if uv is available
        if ! command_exists uv; then
            echo "⚠️  uv was installed but is not in PATH. Please restart your terminal or add ~/.local/bin to your PATH."
        fi
    fi
    
    echo "✓ uv installation completed"
}

# Function to clone the repository
clone_repository() {
    echo "Cloning FinGenius repository..."
    
    if [ -d "FinGenius" ]; then
        echo "✓ FinGenius directory already exists"
        cd FinGenius
    else
        if command_exists git; then
            git clone https://github.com/HuaYaoAI/FinGenius.git
            cd FinGenius
        else
            echo "✗ Git is not installed. Please install Git to clone the repository."
            return 1
        fi
    fi
    
    echo "✓ Repository cloned/verified"
}

# Function to create virtual environment
create_virtual_environment() {
    echo "Creating virtual environment..."
    
    if ! command_exists uv; then
        echo "✗ uv is not available. Please install uv first."
        return 1
    fi
    
    uv venv --python 3.12
    echo "✓ Virtual environment created"
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    echo "Installing project dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        echo "✗ requirements.txt not found. Make sure you are in the FinGenius directory."
        return 1
    fi
    
    uv pip install -r requirements.txt
    echo "✓ Dependencies installed"
}

# Function to create configuration file
create_config() {
    echo "Creating configuration file..."
    
    if [ ! -f "config/config.example.toml" ]; then
        echo "✗ config/config.example.toml not found."
        return 1
    fi
    
    cp config/config.example.toml config/config.toml
    echo "✓ Configuration file created: config/config.toml"
    echo "  Please edit this file to add your API keys and customize settings."
}

# Function to verify installation
verify_installation() {
    echo "Verifying installation..."
    
    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        echo "✗ main.py not found. Installation may be incomplete."
        return 1
    fi
    
    # Try to import required modules
    source .venv/bin/activate
    if python -c "import src.config" 2>/dev/null; then
        echo "✓ Python modules imported successfully"
    else
        echo "⚠️  Some Python modules could not be imported. There might be an issue with the installation."
    fi
    
    echo "✓ Installation verification completed"
}

# Main installation process
main() {
    echo "Starting FinGenius installation..."
    echo ""
    
    # Check Python version
    if ! check_python_version; then
        echo ""
        echo "Please install Python 3.12 or higher and run this script again."
        exit 1
    fi
    
    echo ""
    
    # Install uv
    if ! install_uv; then
        echo ""
        echo "Failed to install uv. Please install it manually and run this script again."
        exit 1
    fi
    
    echo ""
    
    # Clone repository
    if ! clone_repository; then
        echo ""
        echo "Failed to clone repository. Please check your internet connection and try again."
        exit 1
    fi
    
    echo ""
    
    # Create virtual environment
    if ! create_virtual_environment; then
        echo ""
        echo "Failed to create virtual environment. Please check the error message above."
        exit 1
    fi
    
    echo ""
    
    # Install dependencies
    if ! install_dependencies; then
        echo ""
        echo "Failed to install dependencies. Please check the error message above."
        exit 1
    fi
    
    echo ""
    
    # Create configuration file
    if ! create_config; then
        echo ""
        echo "Failed to create configuration file. Please check the error message above."
        exit 1
    fi
    
    echo ""
    
    # Verify installation
    if ! verify_installation; then
        echo ""
        echo "Installation verification failed. Please check the error message above."
        exit 1
    fi
    
    echo ""
    echo "=== Installation Completed Successfully ==="
    echo ""
    echo "Next steps:"
    echo "1. Edit config/config.toml to add your API keys and customize settings"
    echo "2. Activate the virtual environment: source .venv/bin/activate"
    echo "3. Run the application: python main.py STOCK_CODE"
    echo ""
    echo "Example: python main.py 000001"
    echo ""
    echo "For more information, please read the INSTALLATION_GUIDE.md file."
}

# Run main function
main "$@"